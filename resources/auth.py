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