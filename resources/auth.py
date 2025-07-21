# routes/auth.py
from flask_restful import Resource, reqparse
from flask import request
from werkzeug.security import generate_password_hash
from models import User, db
from utils.logger import log_action
from sqlalchemy.exc import IntegrityError
import re

signup_parser = reqparse.RequestParser()
signup_parser.add_argument("first_name", type=str, required=True)
signup_parser.add_argument("last_name", type=str, required=True)
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)
signup_parser.add_argument("role", type=str, required=True)  # attendee or organizer

class Signup(Resource):
    def post(self):
        data = signup_parser.parse_args()

        if data['role'] not in ['attendee', 'organizer']:
            return {"message": "Invalid role."}, 400

        # Simple email format check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return {"message": "Invalid email format."}, 400

        try:
            user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'].lower(),
                role=data['role'],
                password=generate_password_hash(data['password']),
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

            return {"message": f"{data['role'].capitalize()} account created successfully."}, 201

        except IntegrityError:
            db.session.rollback()
            return {"message": "Email already in use."}, 400

        except Exception as e:
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
            return {"message": "Signup failed. Please try again."}, 500
