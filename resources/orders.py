from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, Order, OrderItem, Ticket, EventPass, User
from utils.logger import log_action
import uuid
from datetime import datetime
from resources.mpesaConfig import initiate_stk_push


order_parser = reqparse.RequestParser()
order_parser.add_argument("ticket_id", type=int, required=True)
order_parser.add_argument("quantity", type=int, required=True)
order_parser.add_argument("attendees", type=list, location="json", required=True)

class CreateOrder(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        attendee = User.query.get(user_id)

        if not attendee or attendee.role != "attendee":
            return {"message": "Only attendees can place orders."}, 403

        attendees = data.get("attendees", [])
        if not attendees:
            return {"message": "Attendee details are required."}, 400

        try:
            ticket_groups = {}
            total = 0

            for att in attendees:
                tid = att.get("ticket_id")
                if tid is None:
                    return {"message": "Each attendee must have a ticket_id."}, 400
                ticket_groups.setdefault(tid, []).append(att)

            order = Order(
                order_id=str(uuid.uuid4()),
                attendee_id=user_id,
                total_amount=0,
                created_at=datetime.utcnow()
            )
            db.session.add(order)
            db.session.flush()

            for ticket_id, group in ticket_groups.items():
                ticket = Ticket.query.get(ticket_id)
                if not ticket or ticket.quantity - ticket.sold < len(group):
                    return {"message": f"Not enough tickets for type ID {ticket_id}."}, 400

                total += ticket.price * len(group)
                ticket.sold += len(group)

                order_item = OrderItem(
                    order_id=order.id,
                    ticket_id=ticket.id,
                    quantity=len(group)
                )
                db.session.add(order_item)

                for att in group:
                    ep = EventPass(
                        ticket_code=str(uuid.uuid4())[:8].upper(),
                        attendee_first_name=att["first_name"],
                        attendee_last_name=att["last_name"],
                        attendee_email=att["email"],
                        attendee_phone=att["phone"],
                        order_item=order_item
                    )
                    db.session.add(ep)

            order.total_amount = total
            db.session.commit()

            # STK Push
            primary_phone = attendees[0]["phone"]
            stk_response = initiate_stk_push(primary_phone, int(total), order.order_id)

            log_action(
                user_id=user_id,
                action="Placed Order",
                target_type="Order",
                target_id=order.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {
                "message": "Order placed. Check your phone to complete M-Pesa payment.",
                "order": order.to_dict(only=("id", "order_id", "status", "total_amount", "created_at")),
                "payment_url": None,  # STK Push does not need a redirect
                "stk_response": stk_response
            }, 201

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user_id,
                action="Place Order",
                target_type="Order",
                target_id=None,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Order failed."}, 500


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