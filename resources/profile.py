# resources/profile.py

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, User
from utils.logger import log_action
from sqlalchemy.exc import IntegrityError

# ---------- Profile Update Parser ----------
profile_parser = reqparse.RequestParser()
profile_parser.add_argument("first_name", type=str)
profile_parser.add_argument("last_name", type=str)
profile_parser.add_argument("email", type=str)
profile_parser.add_argument("phone", type=str)

# ---------- GET: My Profile ----------
class MyProfile(Resource):
    @jwt_required()
    def get(self):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {"message": "User not found."}, 404

        return user.to_dict(only=(
            "id", "first_name", "last_name", "email", "phone", "role", "status", "created_at"
        )), 200

# ---------- PUT: Update Profile ----------
class UpdateProfile(Resource):
    @jwt_required()
    def put(self):
        user = User.query.get(get_jwt_identity())
        if not user:
            return {"message": "User not found."}, 404

        data = profile_parser.parse_args()

        if data["email"]:
            data["email"] = data["email"].lower().strip()

        try:
            for key in ["first_name", "last_name", "email", "phone"]:
                if data.get(key):
                    setattr(user, key, data[key])

            db.session.commit()

            log_action(
                user_id=user.id,
                action="Updated Profile",
                target_type="User",
                target_id=user.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": "Profile updated successfully."}, 200

        except IntegrityError:
            db.session.rollback()
            return {"message": "Email or phone number already in use."}, 400

        except Exception as e:
            db.session.rollback()
            log_action(
                user_id=user.id,
                action="Update Profile",
                target_type="User",
                target_id=user.id,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Failed to update profile."}, 500
