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

        # Ensure the organizer owns the event
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