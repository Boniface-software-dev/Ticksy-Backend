import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

from models import db
from resources.auth import Signup, Login
from resources.admin_events import PendingEvents, ApproveRejectEvent

load_dotenv()


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"  # dev only
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"  # temp secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)




db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
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

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')


api.add_resource(PendingEvents, "/admin/pending")
api.add_resource(ApproveRejectEvent, "/admin/approve/<int:id>")


if __name__ == "__main__":
    app.run(debug=True)