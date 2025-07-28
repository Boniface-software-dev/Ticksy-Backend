import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from dotenv import load_dotenv
from datetime import timedelta

from models import db
from resources.auth import Signup, Login
from resources.events import (
    EventList, SingleEvent, CreateEvent, UpdateEvent, DeleteEvent, MyEvents
)
from resources.admin_events import PendingEvents, ApproveRejectEvent
from resources.saved_events import SaveEvent, MySavedEvents
from resources.admin_users import AllUsers, BanOrUnbanUser, UpdateUserRole
from resources.admin_dashboard import AdminDashboard, AdminReports, AdminAuditLogs
from resources.orders import CreateOrder, ConfirmPayment, MyOrders, SingleOrder
from resources.tickets import CreateTicket, EventTickets
from resources.reviews import PostReview, EventReviews
from resources.profile import MyProfile, UpdateProfile
from resources.profile_events import MyUpcomingEvents, MyPastEvents

from models import User

from resources.admin_analytics import (
    AdminSummary,
    TicketSalesTrends,
    RevenueByTicketType,
    TopEventTypes,
    TopEventsByRevenue
)

from resources.attendee_profile import UpcomingAttendeeEvents, PastAttendeeEvents

from resources.attendees import EventAttendees,CheckInAttendee

load_dotenv()


load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your_jwt_secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Allow frontend dev port (Vite: 5173) to communicate with backend


CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])


api = Api(app)

@app.route("/")
def home():
    return {"message": "Event Ticketing Backend running"}

@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }), 200
    return jsonify({"message": "User not found"}), 404

@jwt.unauthorized_loader
def missing_token(error):
    return {
        "message": "Authorization required",
        "success": False,
        "errors": ["Authorization token is required"],
    }, 401

# AUTH
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")

# ADMIN
api.add_resource(AllUsers, "/admin/users")
api.add_resource(BanOrUnbanUser, "/admin/users/<int:id>/status")
api.add_resource(UpdateUserRole, "/admin/users/<int:id>/role")
api.add_resource(AdminDashboard, "/admin/dashboard")
api.add_resource(AdminReports, "/admin/reports")
api.add_resource(AdminAuditLogs, "/admin/logs")

# EVENTS
api.add_resource(EventList, "/events")
api.add_resource(SingleEvent, "/events/<int:id>")
api.add_resource(CreateEvent, "/events")
api.add_resource(UpdateEvent, "/events/<int:id>")
api.add_resource(DeleteEvent, "/events/<int:id>")
api.add_resource(MyEvents, "/my-events")
api.add_resource(PendingEvents, "/admin/pending")
api.add_resource(ApproveRejectEvent, "/admin/<int:id>")

# SAVED EVENTS
api.add_resource(SaveEvent, "/events/<int:id>/save")
api.add_resource(MySavedEvents, "/my-saved-events")

# ORDERS
api.add_resource(CreateOrder, "/orders")
api.add_resource(ConfirmPayment, "/orders/<int:id>/pay")
api.add_resource(MyOrders, "/orders")
api.add_resource(SingleOrder, "/orders/<int:id>")

# TICKETS
api.add_resource(CreateTicket, "/events/<int:event_id>/tickets")
api.add_resource(EventTickets, "/events/<int:event_id>/tickets")

# REVIEWS
api.add_resource(PostReview, "/events/<int:id>/review")
api.add_resource(EventReviews, "/events/<int:id>/reviews")

# PROFILE
api.add_resource(MyProfile, "/profile/me")
api.add_resource(UpdateProfile, "/profile/me")
api.add_resource(MyUpcomingEvents, "/profile/my-upcoming-events")
api.add_resource(MyPastEvents, "/profile/my-past-events")



api.add_resource(AdminSummary, '/admin/analytics/summary')
api.add_resource(TicketSalesTrends, '/admin/analytics/ticket-sales-trends')
api.add_resource(RevenueByTicketType, '/admin/analytics/revenue-by-ticket-type')
api.add_resource(TopEventTypes, '/admin/analytics/top-event-types')
api.add_resource(TopEventsByRevenue, '/admin/analytics/top-events-by-revenue')

api.add_resource(UpcomingAttendeeEvents, "/attendee/upcoming-events")
api.add_resource(PastAttendeeEvents, "/attendee/past-events")

api.add_resource(EventAttendees, '/organizer/events/<int:event_id>/attendees')
api.add_resource(CheckInAttendee, "/organizer/checkin/<int:pass_id>")



if __name__ == "__main__":
    app.run(port=5000, debug=True)
