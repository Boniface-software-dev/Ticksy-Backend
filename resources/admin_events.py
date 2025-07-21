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
