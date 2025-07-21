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
