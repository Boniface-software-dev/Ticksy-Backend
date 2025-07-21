from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Event, User, db
from utils.logger import log_action
from datetime import datetime


event_parser = reqparse.RequestParser()
event_parser.add_argument("title", type=str, required=True)
event_parser.add_argument("description", type=str, required=True)
event_parser.add_argument("location", type=str, required=True)
event_parser.add_argument("start_time", type=str, required=True)
event_parser.add_argument("end_time", type=str, required=True)
event_parser.add_argument("category", type=str, required=False)
event_parser.add_argument("tags", type=str, required=False)
event_parser.add_argument("image_url", type=str, required=False)


class EventList(Resource):
    def get(self):
        events = Event.query.filter_by(is_approved=True).order_by(Event.start_time.asc()).all()
        return [e.to_dict(only=(
            "id", "title", "description", "location",
            "start_time", "end_time", "category", "tags", "image_url",
            "organizer.id", "organizer.first_name", "organizer.last_name"
        )) for e in events], 200


class SingleEvent(Resource):
    def get(self, id):
        event = Event.query.filter_by(id=id, is_approved=True).first()
        if not event:
            return {"message": "Event not found."}, 404

        return event.to_dict(only=(
            "id", "title", "description", "location",
            "start_time", "end_time", "category", "tags", "image_url",
            "organizer.id", "organizer.first_name", "organizer.last_name",
            "tickets.id", "tickets.type", "tickets.price"
        )), 200


class CreateEvent(Resource):
    @jwt_required()
    def post(self):
        data = event_parser.parse_args()
        user_id = get_jwt_identity()
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can create events."}, 403

        try:
            event = Event(
                title=data["title"],
                description=data["description"],
                location=data["location"],
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]),
                category=data.get("category"),
                tags=data.get("tags"),
                image_url=data.get("image_url"),
                organizer_id=user_id
            )
            db.session.add(event)
            db.session.commit()

            log_action(
                user_id=user_id,
                action="Created Event",
                target_type="Event",
                target_id=event.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": "Event created successfully.", "id": event.id}, 201

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user_id,
                action="Create Event",
                target_type="Event",
                target_id=None,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Event creation failed."}, 500


class UpdateEvent(Resource):
    @jwt_required()
    def put(self, id):
        data = event_parser.parse_args()
        user_id = get_jwt_identity()
        event = Event.query.get(id)

        if not event or event.organizer_id != user_id:
            return {"message": "Event not found or unauthorized."}, 403

        try:
            for field in data:
                if data[field]:
                    setattr(event, field, data[field])
            event.start_time = datetime.fromisoformat(data["start_time"])
            event.end_time = datetime.fromisoformat(data["end_time"])

            db.session.commit()

            log_action(
                user_id=user_id,
                action="Updated Event",
                target_type="Event",
                target_id=id,
                status="Success",
                ip_address=request.remote_addr
            )
            return {"message": "Event updated successfully."}, 200

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user_id,
                action="Update Event",
                target_type="Event",
                target_id=id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Event update failed."}, 500


class DeleteEvent(Resource):
    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        event = Event.query.get(id)

        if not event or event.organizer_id != user_id:
            return {"message": "Event not found or unauthorized."}, 403

        if event.status != "rejected":
            return {"message": "Only rejected events can be deleted."}, 400

        db.session.delete(event)
        db.session.commit()

        log_action(
            user_id=user_id,
            action="Deleted Event",
            target_type="Event",
            target_id=id,
            status="Success",
            ip_address=request.remote_addr
        )

        return {"message": "Event deleted successfully."}, 200


class MyEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        events = Event.query.filter_by(organizer_id=user_id).order_by(Event.created_at.desc()).all()
        return [e.to_dict(only=(
            "id", "title", "description", "location",
            "start_time", "end_time", "category", "tags", "image_url", "is_approved"
        )) for e in events], 200