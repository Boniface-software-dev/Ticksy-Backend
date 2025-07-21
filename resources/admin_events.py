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
