from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, Review, Event, User, OrderItem, Ticket
from utils.logger import log_action

review_parser = reqparse.RequestParser()
review_parser.add_argument("rating", type=int, required=True)
review_parser.add_argument("comment", type=str, required=False)

class PostReview(Resource):
    @jwt_required()
    def post(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can leave reviews."}, 403

        event = Event.query.get(id)
        if not event or not event.is_approved:
            return {"message": "Event not found or not approved."}, 404

        ordered = db.session.query(OrderItem).join(Ticket).filter(
            OrderItem.order.has(attendee_id=user_id),
            Ticket.event_id == id
        ).first()

        if not ordered:
            return {"message": "You can only review events you've attended."}, 403

        existing = Review.query.filter_by(attendee_id=user_id, event_id=id).first()
        if existing:
            return {"message": "You have already reviewed this event."}, 400

        data = review_parser.parse_args()
        review = Review(
            rating=data["rating"],
            comment=data.get("comment"),
            attendee_id=user_id,
            event_id=id
        )

        db.session.add(review)
        db.session.commit()

        log_action(
            user_id=user_id,
            action="Reviewed Event",
            target_type="Event",
            target_id=id,
            status="Success",
            ip_address=request.remote_addr
        )

        return {"message": "Review submitted successfully."}, 201
