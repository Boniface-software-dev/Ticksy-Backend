import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta

from models import db
from extensions import bcrypt, jwt  # ✅ updated
from resources.auth import Signup, Login
from resources.events import (
    EventList, SingleEvent, CreateEvent, UpdateEvent, DeleteEvent, MyEvents
)

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# ✅ Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)
CORS(app)
api = Api(app)

@app.route("/")
def home():
    return {"message": "Event Ticketing Backend running"}

@jwt.unauthorized_loader
def missing_token(error):
    return {
        "message": "Authorization required",
        "success": False,
        "errors": ["Authorization token is required"],
    }, 401

# ✅ Routes
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')

api.add_resource(EventList, "/events")
api.add_resource(SingleEvent, "/events/<int:id>")
api.add_resource(CreateEvent, "/events")
api.add_resource(UpdateEvent, "/events/<int:id>")
api.add_resource(DeleteEvent, "/events/<int:id>")
api.add_resource(MyEvents, "/my-events")

if __name__ == "__main__":
    app.run(debug=True)
