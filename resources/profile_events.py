

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, User, Event, OrderItem, Ticket
from datetime import datetime
from utils.logger import log_action


def get_attendee_events(user_id, past=False):
    now = datetime.now()

    events_query = db.session.query(Event).join(Ticket).join(OrderItem).filter(
        OrderItem.order.has(attendee_id=user_id)
    )

    if past:
        events_query = events_query.filter(Event.end_time < now)
    else:
        events_query = events_query.filter(Event.start_time >= now)

    return events_query.order_by(Event.start_time.asc()).distinct().all()


class MyUpcomingEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can access this."}, 403

        events = get_attendee_events(user_id, past=False)

        log_action(
            user_id=user_id,
            action="Viewed Upcoming Events",
            target_type="Event",
            target_id=None,
            status="Success",
            ip_address=request.remote_addr
        )

        return [
            e.to_dict(only=("id", "title", "start_time", "location", "image_url", "status"))
            for e in events
        ], 200


class MyPastEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can access this."}, 403

        events = get_attendee_events(user_id, past=True)

        log_action(
            user_id=user_id,
            action="Viewed Past Events",
            target_type="Event",
            target_id=None,
            status="Success",
            ip_address=request.remote_addr
        )

        return [
            e.to_dict(only=("id", "title", "start_time", "location", "image_url", "status"))
            for e in events
        ], 200
