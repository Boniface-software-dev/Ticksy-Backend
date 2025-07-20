import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta


