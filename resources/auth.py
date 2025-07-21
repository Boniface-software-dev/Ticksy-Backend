from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import create_access_token
from models import db, User
from utils.logger import log_action
from datetime import timedelta
import bcrypt  # BCRYPT USED HERE
import re


signup_parser = reqparse.RequestParser()
signup_parser.add_argument("first_name", type=str, required=True)
signup_parser.add_argument("last_name", type=str, required=True)
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("phone", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)
signup_parser.add_argument("role", type=str, required=True)

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", type=str, required=True)
login_parser.add_argument("password", type=str, required=True)