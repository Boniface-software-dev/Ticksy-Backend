# resources/admin_events.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Event, User, db
from utils.logger import log_action

approve_parser = reqparse.RequestParser()
approve_parser.add_argument("status", type=str, required=True)  # 'approved' or 'rejected'


approve_parser = reqparse.RequestParser()
approve_parser.add_argument("status", type=str, required=True)  # 'approved' or 'rejected'


class PendingEvents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)

        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        events = Event.query.filter_by(status="pending").order_by(Event.created_at.desc()).all()
        return [
            event.to_dict(only=(
                "id", "title", "location", "start_time", "end_time",
                "category", "status", "is_approved", "organizer_id"
            ))
            for event in events
        ], 200

class ApproveRejectEvent(Resource):
    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)

        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        data = approve_parser.parse_args()
        new_status = data["status"].strip().lower()

        if new_status not in ["approved", "rejected"]:
            return {"message": "Status must be 'approved' or 'rejected'."}, 400

        event = Event.query.get(id)
        if not event:
            return {"message": "Event not found."}, 404

        try:
            event.status = new_status
            event.is_approved = True if new_status == "approved" else False

            db.session.commit()

            log_action(
                user_id=admin.id,
                action=f"{new_status.capitalize()} Event",
                target_type="Event",
                target_id=event.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": f"Event {new_status} successfully."}, 200

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=admin.id,
                action=f"Approve/Reject Event",
                target_type="Event",
                target_id=event.id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Action failed."}, 500
