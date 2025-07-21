from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import create_access_token
from models import db, User
from utils.logger import log_action
from datetime import timedelta
import bcrypt  # BCRYPT USED HERE
import re