from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from models import db, Order, OrderItem, Ticket, EventPass, User
from utils.logger import log_action
import uuid
from datetime import datetime
from resources.mpesaConfig import initiate_stk_push
from mpesa import Mpesa

order_parser = reqparse.RequestParser()
order_parser.add_argument("ticket_id", type=int, required=True)
order_parser.add_argument("quantity", type=int, required=True)
order_parser.add_argument("attendees", type=list, location="json", required=True)


class CreateOrder(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        phone = data.get("phone")
        ticket_data_list = data.get("tickets")

        if not phone or not ticket_data_list:
            return jsonify({"message": "Phone and tickets are required"}), 400

        current_user_id = int(get_jwt_identity())
        attendee = User.query.get(current_user_id)

        if attendee.role != "attendee":
            return jsonify({"message": "Only attendees can make purchases"}), 403

        # Calculate total amount
        total_amount = 0
        for ticket_data in ticket_data_list:
            ticket = Ticket.query.get(ticket_data["ticket_id"])
            if not ticket:
                return jsonify({"message": f"Ticket with ID {ticket_data['ticket_id']} not found"}), 404
            total_amount += ticket.price * ticket_data["quantity"]

        # Create Order
        order = Order(
            order_id=str(uuid.uuid4()).replace("-", "").upper()[:12],
            attendee=attendee,
            total_amount=total_amount
        )
        db.session.add(order)

        # Create OrderItems and attach attendees
        for ticket_data in ticket_data_list:
            ticket_id = ticket_data["ticket_id"]
            quantity = ticket_data["quantity"]
            attendees_list = ticket_data.get("attendees", [])

            if len(attendees_list) != quantity:
                return jsonify({"message": f"Attendee info mismatch for ticket {ticket_id}"}), 400

            order_item = OrderItem(
                order=order,
                ticket_id=ticket_id,
                quantity=quantity,
                temp_attendee_data=attendees_list
            )
            db.session.add(order_item)

        db.session.commit()

        # Initiate STK Push
        mpesa = Mpesa()
        try:
            response = mpesa.make_stk_push({
                "amount": total_amount,
                "phone": phone,
                "description": "Payment for event tickets"
            })
            return {
                "message": "STK Push initiated",
                "checkoutRequestID": response.get("CheckoutRequestID"),
                "customerMessage": response.get("CustomerMessage"),
                "orderId": order.order_id
            }, 200
        except Exception as e:
            return {"message": "STK Push failed", "error": str(e)}, 500




class ConfirmPayment(Resource):
    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=id, attendee_id=user_id).first()

        if not order:
            return {"message": "Order not found or unauthorized."}, 404

        order.status = "paid"
        order.mpesa_receipt = str(uuid.uuid4())
        db.session.commit()

        log_action(
            user_id=user_id,
            action="Confirmed Payment",
            target_type="Order",
            target_id=order.id,
            status="Success",
            ip_address=request.remote_addr
        )

        return {"message": "Payment confirmed.", "receipt": order.mpesa_receipt}, 200


class MyOrders(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(attendee_id=user_id).order_by(Order.created_at.desc()).all()

        return [
            o.to_dict(only=(
                "id", "order_id", "status", "total_amount", "mpesa_receipt", "created_at"
            )) for o in orders
        ], 200


class SingleOrder(Resource):
    @jwt_required()
    def get(self, id):
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=id, attendee_id=user_id).first()

        if not order:
            return {"message": "Order not found."}, 404

        return order.to_dict(only=(
            "id", "order_id", "status", "total_amount", "mpesa_receipt", "created_at",
            "order_items.id", "order_items.quantity",
            "order_items.ticket.id", "order_items.ticket.type", "order_items.ticket.price",
            "order_items.ticket.event.id", "order_items.ticket.event.title"
        )), 200
