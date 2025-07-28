from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Event, EventPass, OrderItem, Ticket, User
from utils.logger import log_action

class EventAttendees(Resource):
    @jwt_required()
    def get(self, event_id):
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Access denied"}, 403

        event = Event.query.get(event_id)
        if not event:
            return {"message": "Event not found"}, 404

        if event.organizer_id != organizer.id:
            return {"message": "You can only view attendees for your own events."}, 403

        passes = (
            db.session.query(EventPass)
            .join(OrderItem)
            .join(Ticket)
            .filter(Ticket.event_id == event_id)
            .all()
        )

        attendees = [
            {
                "ticket_code": ep.ticket_code,
                "first_name": ep.attendee_first_name,
                "last_name": ep.attendee_last_name,
                "email": ep.attendee_email,
                "phone": ep.attendee_phone,
                "checked_in": ep.att_status
            }
            for ep in passes
        ]

        log_action(
            user_id=user_id,
            action="Viewed Attendees",
            target_type="Event",
            target_id=event_id,
            status="Success"
        )

        return {"attendees": attendees}, 200
