from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Event, User, db
from utils.logger import log_action
from datetime import datetime
import cloudinary.uploader
from werkzeug.utils import secure_filename


event_parser = reqparse.RequestParser()
event_parser.add_argument("title", type=str, required=True)
event_parser.add_argument("description", type=str, required=True)
event_parser.add_argument("location", type=str, required=True)
event_parser.add_argument("start_time", type=str, required=True)
event_parser.add_argument("end_time", type=str, required=True)
event_parser.add_argument("category", type=str, required=True)
event_parser.add_argument("tags", type=str, required=True)
event_parser.add_argument("image_url", type=str, required=True)


class EventList(Resource):
    def get(self):
        now = datetime.utcnow()
        events = Event.query.filter(
            Event.status == "approved",
            Event.start_time > now
        ).order_by(Event.start_time.asc()).all()

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
            "tickets.id", "tickets.type", "tickets.price", 
            "tickets.quantity", "tickets.sold"
        )), 200


class CreateEvent(Resource):
    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        organizer = User.query.get(user_id)

        if not organizer or organizer.role != "organizer":
            return {"message": "Only organizers can create events."}, 403

        try:
            title = request.form.get("title")
            description = request.form.get("description")
            location = request.form.get("location")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            category = request.form.get("category")
            tags = request.form.get("tags")

            if not all([title, description, location, start_time, end_time]):
                return {"message": "Missing required fields."}, 400

            image_url = None
            image = request.files.get("image")
            if image:
                upload_result = cloudinary.uploader.upload(
                    image,
                    folder="events",
                    use_filename=True,
                    unique_filename=False
                )
                image_url = upload_result.get("secure_url")

            event = Event(
                title=title,
                description=description,
                location=location,
                start_time=datetime.fromisoformat(start_time),
                end_time=datetime.fromisoformat(end_time),
                category=category,
                tags=tags,
                image_url=image_url,
                organizer_id=user_id,
                status="pending"
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
            return {"message": "Event creation failed.", "error": str(e)}, 500


class UpdateEvent(Resource):
    @jwt_required()
    def put(self, id):
        user_id = int(get_jwt_identity())
        event = Event.query.get(id)

        if not event or event.organizer_id != user_id:
            return {"message": "Event not found or unauthorized."}, 403

        try:
            data = request.form.to_dict()
            image_file = request.files.get('image')

            for field in ['title', 'description', 'location', 'category', 'tags']:
                if field in data and data[field].strip():
                    setattr(event, field, data[field])

            if 'start_time' in data:
                event.start_time = datetime.fromisoformat(data["start_time"])
            if 'end_time' in data:
                event.end_time = datetime.fromisoformat(data["end_time"])

            if image_file and image_file.filename != "":
                filename = secure_filename(image_file.filename)
                result = cloudinary.uploader.upload(
                    image_file,
                    folder="events",
                    use_filename=True,
                    unique_filename=False,
                    resource_type="image"
                )
                event.image_url = result['secure_url']

            event.status = "pending"

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
        user_id = int(get_jwt_identity())
        events = Event.query.filter_by(organizer_id=user_id).order_by(Event.created_at.desc()).all()

        serialized = []
        for e in events:
            event_dict = e.to_dict(only=(
                "id", "title", "description", "location",
                "start_time", "end_time", "category", "tags", "image_url", "status"
            ))
            event_dict["start_time"] = e.start_time.isoformat() if e.start_time else None
            event_dict["end_time"] = e.end_time.isoformat() if e.end_time else None
            event_dict["tickets"] = [
                ticket.to_dict(only=("id", "type", "price", "quantity", "sold"))
                for ticket in e.tickets
            ]
            serialized.append(event_dict)

        return serialized, 200
