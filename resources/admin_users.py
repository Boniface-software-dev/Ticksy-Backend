from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, db
from utils.logger import log_action

status_parser = reqparse.RequestParser()
status_parser.add_argument("status", type=str, required=True)  #active/banned

role_parser = reqparse.RequestParser()
role_parser.add_argument("role", type=str, required=True)  #attendee,organizer,admin

class AllUsers(Resource):
    @jwt_required()
    def get(self):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        users = User.query.order_by(User.created_at.desc()).all()
        return [
            u.to_dict(only=(
                "id", "first_name", "last_name", "email", "phone", "role", "status", "created_at"
            ))
            for u in users
        ], 200

