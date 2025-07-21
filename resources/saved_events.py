# resources/saved_events.py

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, SavedEvent, Event, User
from utils.logger import log_action