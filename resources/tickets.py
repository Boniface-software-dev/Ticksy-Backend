# resources/tickets.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Ticket, Event, User, db
from utils.logger import log_action

# ---------- Parser for Ticket ----------
ticket_parser = reqparse.RequestParser()
ticket_parser.add_argument("type", type=str, required=True)      # e.g. VIP, Regular
ticket_parser.add_argument("price", type=float, required=True)
ticket_parser.add_argument("quantity", type=int, required=True)

# ---------- POST: Create Ticket ----------
class CreateTicket(Resource):
    @jwt_required()
    def post(self, event_id):
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can create tickets."}, 403

        event = Event.query.get(event_id)
        if not event or event.organizer_id != user_id:
            return {"message": "Event not found or unauthorized."}, 404

        data = ticket_parser.parse_args()

        try:
            ticket = Ticket(
                type=data["type"],
                price=data["price"],
                quantity=data["quantity"],
                event_id=event_id
            )

            db.session.add(ticket)
            db.session.commit()

            log_action(
                user_id=user_id,
                action="Created Ticket",
                target_type="Ticket",
                target_id=ticket.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": "Ticket created successfully.", "ticket_id": ticket.id}, 201

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user_id,
                action="Create Ticket",
                target_type="Ticket",
                target_id=None,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Failed to create ticket."}, 500

# ---------- GET: List Tickets for an Event ----------
class EventTickets(Resource):
    def get(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            return {"message": "Event not found."}, 404

        tickets = Ticket.query.filter_by(event_id=event_id).order_by(Ticket.price.asc()).all()

        return [
            t.to_dict(only=("id", "type", "price", "quantity", "sold", "created_at"))
            for t in tickets
        ], 200