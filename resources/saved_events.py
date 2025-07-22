# resources/saved_events.py

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, SavedEvent, Event, User
from utils.logger import log_action

class SaveEvent(Resource):
    @jwt_required()
    def post(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "attendee":
            return {"message": "Only attendees can save events."}, 403

        event = Event.query.get(id)
        if not event or not event.is_approved:
            return {"message": "Event not found or not approved."}, 404

        existing = SavedEvent.query.filter_by(user_id=user_id, event_id=id).first()

        try:
            if existing:
                db.session.delete(existing)
                action = "Unsave"
                message = "Event removed from saved list."
            else:
                saved = SavedEvent(user_id=user_id, event_id=id)
                db.session.add(saved)
                action = "Save"
                message = "Event saved successfully."

            db.session.commit()

            log_action(
                user_id=user_id,
                action=f"{action} Event",
                target_type="Event",
                target_id=id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": message}, 200

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user_id,
                action="Save/Unsave Event",
                target_type="Event",
                target_id=id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "An error occurred."}, 500
    
class MySavedEvents(Resource):
        @jwt_required()
        def get(self):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
    
            if not user or user.role != "attendee":
                return {"message": "Only attendees can view saved events."}, 403
    
            saved = SavedEvent.query.filter_by(user_id=user_id).all()
    
            return [
                s.to_dict(only=(
                    "event.id", "event.title", "event.location", "event.start_time",
                    "event.status", "event.image_url"
                )) for s in saved
            ], 200

        

