from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

from models import db, User, EventPass, Ticket, Event, OrderItem
from utils.logger import log_action


class EventAttendees(Resource):
    @jwt_required()
    def get(self, event_id):
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can view attendees."}, 403

        event = Event.query.get(event_id)
        if not event or event.organizer_id != organizer.id:
            return {"message": "You can only view attendees for your own events."}, 403

        passes = (
            db.session.query(EventPass)
            .join(OrderItem)
            .join(Ticket)
            .filter(Ticket.event_id == event_id)
            .all()
        )

        attendees = [{
            "id": p.id,
            "ticket_code": p.ticket_code,
            "attendee_first_name": p.attendee_first_name,
            "attendee_last_name": p.attendee_last_name,
            "attendee_email": p.attendee_email,
            "attendee_phone": p.attendee_phone,
            "checked_in": p.att_status,
            "ticket_type": p.order_item.ticket.type if p.order_item and p.order_item.ticket else None,
        } for p in passes]

        return {"attendees": attendees}, 200


class CheckInAttendee(Resource):
    @jwt_required()
    def patch(self, pass_id):
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can check in attendees."}, 403

        event_pass = EventPass.query.get(pass_id)
        if not event_pass:
            return {"message": "Event pass not found."}, 404

        ticket = event_pass.order_item.ticket
        if not ticket or ticket.event.organizer_id != organizer.id:
            return {"message": "You can only check-in attendees for your own events."}, 403

        event_pass.att_status = True
        db.session.commit()

        log_action(
            user_id=user_id,
            action="Checked-in Attendee",
            target_type="EventPass",
            target_id=pass_id,
            status="Success",
            ip_address=request.remote_addr,
            extra_data={"ticket_code": event_pass.ticket_code}
        )

        return {"message": "Attendee checked in successfully."}, 200


class CheckOutAttendee(Resource):
    @jwt_required()
    def patch(self, pass_id):
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can check out attendees."}, 403

        event_pass = EventPass.query.get(pass_id)
        if not event_pass:
            return {"message": "Event pass not found."}, 404

        ticket = event_pass.order_item.ticket
        if not ticket or ticket.event.organizer_id != organizer.id:
            return {"message": "Unauthorized access to this event pass."}, 403

        event_pass.att_status = False
        db.session.commit()

        log_action(
            user_id=user_id,
            action="Checked-out Attendee",
            target_type="EventPass",
            target_id=pass_id,
            status="Success",
            ip_address=request.remote_addr,
            extra_data={"ticket_code": event_pass.ticket_code}
        )

        return {"message": "Attendee checked out successfully."}, 200
