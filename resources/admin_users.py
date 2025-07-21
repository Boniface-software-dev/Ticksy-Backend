from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, db
from utils.logger import log_action

status_parser = reqparse.RequestParser()
status_parser.add_argument("status", type=str, required=True)  #active/banned

role_parser = reqparse.RequestParser()
role_parser.add_argument("role", type=str, required=True)  #attendee,organizer,admin

