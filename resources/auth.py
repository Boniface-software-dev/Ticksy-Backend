# resources/auth.py

from flask_restful import Resource, reqparse
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User
from utils.logger import log_action
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
import re


signup_parser = reqparse.RequestParser()
signup_parser.add_argument("first_name", type=str, required=True)
signup_parser.add_argument("last_name", type=str, required=True)
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("phone", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)
signup_parser.add_argument("role", type=str, required=True)


class Signup(Resource):
    def post(self):
        data = signup_parser.parse_args()

        email = data["email"].strip().lower()
        phone = data["phone"].strip()
        role = data["role"].strip().lower()

        if role not in ["attendee", "organizer"]:
            return {"message": "Role must be either 'attendee' or 'organizer'."}, 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"message": "Invalid email format."}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists."}, 400

        if User.query.filter_by(phone=phone).first():
            return {"message": "Phone number already in use."}, 400

        try:
            user = User(
                first_name=data["first_name"].strip(),
                last_name=data["last_name"].strip(),
                email=email,
                phone=phone,
                password=generate_password_hash(data["password"]),
                role=role
            )

            db.session.add(user)
            db.session.commit()

            log_action(
                user_id=user.id,
                action="Signed up",
                target_type="User",
                target_id=user.id,
                status="Success",
                ip_address=request.remote_addr
            )

            return {"message": f"{role.capitalize()} account created successfully."}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            log_action(
                user_id=None,
                action="Signup",
                target_type="User",
                target_id=None,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data=str(e)
            )
            return {"message": "Signup failed due to a server error."}, 500