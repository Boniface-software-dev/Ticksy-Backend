from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, User, Event, OrderItem, Ticket, Order, Review
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

class PastEventDetail(Resource):
    @jwt_required()
    def get(self, event_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can access this."}, 403

        event = Event.query.get(event_id)

        if not event:
            return {"message": "Event not found"}, 404

        # Check that this event is a *past* event the user attended
        now = datetime.now()
        if event.end_time > now:
            return {"message": "Event is not yet over."}, 400

        has_attended = (
            db.session.query(OrderItem)
            .join(OrderItem.order)
            .join(OrderItem.ticket)
            .filter(Order.attendee_id == user_id)
            .filter(Ticket.event_id == event_id)
            .first()
        )

        if not has_attended:
            return {"message": "You did not attend this event."}, 403

        # Get tickets + quantity
        ticket_data = (
            db.session.query(Ticket.type, OrderItem.quantity, Ticket.price)
            .join(OrderItem, OrderItem.ticket_id == Ticket.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.attendee_id == user_id, Ticket.event_id == event_id)
            .all()
        )

        tickets = []
        total_amount = 0
        for ticket_type, quantity, price in ticket_data:
            tickets.append({
                "type": ticket_type,
                "quantity": quantity,
                "price": price,
                "subtotal": quantity * price
            })
            total_amount += quantity * price

        # Fetch attendee review if exists
        review = (
            Review.query
            .filter_by(attendee_id=user_id, event_id=event_id)
            .first()
        )

        review_data = review.to_dict(only=("rating", "comment", "created_at")) if review else None

        log_action(
            user_id=user_id,
            action="Viewed Past Event Detail",
            target_type="Event",
            target_id=event_id,
            status="Success",
            ip_address=request.remote_addr
        )

        return {
            "event": event.to_dict(only=("id", "title", "description", "start_time", "end_time", "location", "image_url")),
            "tickets": tickets,
            "total_amount": total_amount,
            "review": review_data
        }, 200
class UpcomingEventDetail(Resource):
    @jwt_required()
    def get(self, event_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can access this."}, 403

        event = Event.query.get(event_id)

        if not event:
            return {"message": "Event not found"}, 404

        # Check that this event is an *upcoming* event the user is attending
        now = datetime.now()
        if event.end_time <= now:
            return {"message": "Event has already ended."}, 400

        has_ticket = (
            db.session.query(OrderItem)
            .join(OrderItem.order)
            .join(OrderItem.ticket)
            .filter(Order.attendee_id == user_id)
            .filter(Ticket.event_id == event_id)
            .first()
        )

        if not has_ticket:
            return {"message": "You do not have a ticket for this event."}, 403

        # Get ticket details
        ticket_data = (
            db.session.query(Ticket.type, OrderItem.quantity, Ticket.price)
            .join(OrderItem, OrderItem.ticket_id == Ticket.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.attendee_id == user_id, Ticket.event_id == event_id)
            .all()
        )

        tickets = []
        total_amount = 0
        for ticket_type, quantity, price in ticket_data:
            tickets.append({
                "type": ticket_type,
                "quantity": quantity,
                "price": price,
                "subtotal": quantity * price
            })
            total_amount += quantity * price

        log_action(
            user_id=user_id,
            action="Viewed Upcoming Event Detail",
            target_type="Event",
            target_id=event_id,
            status="Success",
            ip_address=request.remote_addr
        )

        return {
            "event": event.to_dict(only=("id", "title", "description", "start_time", "end_time", "location", "image_url")),
            "tickets": tickets,
            "total_amount": total_amount
        }, 200
