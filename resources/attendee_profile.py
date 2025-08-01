from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Event, Ticket, OrderItem, Order, db
from datetime import datetime

class UpcomingAttendeeEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        now = datetime.now()

        events = db.session.query(Event)\
            .join(Event.tickets)\
            .join(Ticket.order_items)\
            .join(OrderItem.order)\
            .filter(Order.attendee_id == user_id)\
            .filter(Event.start_time > now)\
            .distinct().all()

        return [e.to_dict(only=("id", "title", "start_time", "end_time", "location", "image_url")) for e in events], 200

class PastAttendeeEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        now = datetime.now()

        events = db.session.query(Event)\
            .join(Event.tickets)\
            .join(Ticket.order_items)\
            .join(OrderItem.order)\
            .filter(Order.attendee_id == user_id)\
            .filter(Event.start_time <= now)\
            .distinct().all()

        return [e.to_dict(only=("id", "title", "start_time", "end_time", "location", "image_url")) for e in events], 200
