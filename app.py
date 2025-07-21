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
from resources.events import EventList, SingleEvent, CreateEvent, UpdateEvent, DeleteEvent, MyEvents

from resources.admin_events import PendingEvents, ApproveRejectEvent

from resources.saved_events import SaveEvent, MySavedEvents


from resources.admin_users import AllUsers, BanOrUnbanUser, UpdateUserRole
from resources.admin_dashboard import AdminDashboard, AdminReports, AdminAuditLogs


from resources.orders import CreateOrder, ConfirmPayment, MyOrders, SingleOrder

from resources.tickets import CreateTicket, EventTickets
from resources.reviews import PostReview, EventReviews







from resources.profile import MyProfile, UpdateProfile

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
    
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(AllUsers, "/admin/users")
api.add_resource(BanOrUnbanUser, "/admin/users/<int:id>/status")
api.add_resource(UpdateUserRole, "/admin/users/<int:id>/role")
api.add_resource(AdminDashboard, "/admin/dashboard")
api.add_resource(AdminReports, "/admin/reports")
api.add_resource(AdminAuditLogs, "/admin/logs")






api.add_resource(PendingEvents, "/admin/pending")
api.add_resource(ApproveRejectEvent, "/admin/<int:id>")

api.add_resource(SaveEvent, "/events/<int:id>/save")
api.add_resource(MySavedEvents, "/my-saved-events")

api.add_resource(PendingEvents, "/admin/pending")
api.add_resource(ApproveRejectEvent, "/admin/<int:id>")

api.add_resource(EventList, "/events")
api.add_resource(SingleEvent, "/events/<int:id>")
api.add_resource(CreateEvent, "/events")
api.add_resource(UpdateEvent, "/events/<int:id>")
api.add_resource(DeleteEvent, "/events/<int:id>")
api.add_resource(MyEvents, "/my-events")


api.add_resource(CreateOrder, "/orders")
api.add_resource(ConfirmPayment, "/orders/<int:id>/pay")
api.add_resource(MyOrders, "/orders")
api.add_resource(SingleOrder, "/orders/<int:id>")

api.add_resource(CreateTicket, "/events/<int:event_id>/tickets")
api.add_resource(EventTickets, "/events/<int:event_id>/tickets")

api.add_resource(PostReview, "/events/<int:id>/review")
api.add_resource(EventReviews, "/events/<int:id>/reviews")




api.add_resource(MyProfile, "/profile/me")
api.add_resource(UpdateProfile, "/profile/me")




if __name__ == "__main__":
    app.run(debug=True)