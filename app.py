import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"  # dev only
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"  # temp secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)




