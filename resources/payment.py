from flask import request
from flask_restful import Resource
from models import db, Order, EventPass
import uuid

from mpesa import Mpesa

class PaymentResource(Resource):
    def post(self):
        data=request.get_json()
        order_id=data.get("order_id")
        phone=data.get("phone")

        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return {"message": "Order not found"}, 404

        mpesa_instance = Mpesa()
        
        mpesa_response = mpesa_instance.make_stk_push({
            "amount": int(order.total_amount),
            "phone": phone,
            "description": f"Payment for order {order_id}"
        })

        if mpesa_response.get("ResponseCode") == "0":
            checkout_id = mpesa_response.get("CheckoutRequestID")
            order.order_id = checkout_id  
            db.session.commit()

        return {"message": "STK Push initiated", "data": mpesa_response}, 200
    

class CheckPaymentResource(Resource):
    def get(self, checkout_request_id):
        mpesa_instance = Mpesa()

        res= mpesa_instance.check_transaction(checkout_request_id)

        return {"message": "ok", "data": res}
    

class PaymentCallbackResource(Resource):
    def get(self):
        return {"message": "callback registered"}

    def post(self):
        data = request.get_json()

        try:
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

            receipt = None
            for item in metadata:
                if item["Name"] == "MpesaReceiptNumber":
                    receipt = item["Value"]
                    break

            order = Order.query.filter_by(order_id=checkout_id).first()

            if not order:
                return {"message": "Order not found"}, 404

            if result_code == 0:
                order.status = "paid"
                order.mpesa_receipt = receipt if receipt else "N/A"

                # Create EventPasses and increment ticket.sold
                for item in order.order_items:
                    ticket = item.ticket
                    attendee_data_list = item.temp_attendee_data or []
                    
                    if (ticket.quantity - ticket.sold) < len(attendee_data_list):
                        return {"message": f"Not enough tickets left for ticket ID {ticket.id}"}, 400
                    
                    ticket.sold += len(attendee_data_list)

                    for att in attendee_data_list:
                        ep = EventPass(
                            ticket_code=str(uuid.uuid4())[:8].upper(),
                            attendee_first_name=att["first_name"],
                            attendee_last_name=att["last_name"],
                            attendee_email=att["email"],
                            attendee_phone=att["phone"],
                            order_item=item
                        )
                        db.session.add(ep)

                db.session.commit()

            else:
                order.status = "failed"
                order.mpesa_receipt = receipt if receipt else "N/A"
                db.session.commit()

            return {"message": "Callback received"}, 200

        except Exception as e:
            db.session.rollback()
            print("Callback error:", str(e))
            return {"message": "Error"}, 500
