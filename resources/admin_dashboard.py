from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, Event, Report, AuditLog, Order, db
from utils.logger import log_action
from sqlalchemy import func

class AdminDashboard(Resource):
    @jwt_required()
    def get(self):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        total_users = User.query.count()
        total_events = Event.query.count()
        active_events = Event.query.filter_by(status="approved").count()
        pending_events = Event.query.filter_by(status="pending").count()
        rejected_events = Event.query.filter_by(status="rejected").count()

        total_revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar()

        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()

        log_action(
            user_id=admin.id,
            action="Viewed Dashboard Summary",
            target_type="Dashboard",
            target_id=None,
            status="Success",
            ip_address=request.remote_addr
        )

        return {
            "summary": {
                "total_users": total_users,
                "total_events": total_events,
                "active_events": active_events,
                "pending_events": pending_events,
                "rejected_events": rejected_events,
                "total_revenue": total_revenue,
            },
            "recent_users": [
                u.to_dict(only=("id", "first_name", "last_name", "email", "role", "created_at"))
                for u in recent_users
            ],
            "recent_events": [
                e.to_dict(only=("id", "title", "status", "start_time", "location", "created_at"))
                for e in recent_events
            ]
        }, 200

class AdminReports(Resource):
    @jwt_required()
    def get(self):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        reports = Report.query.order_by(Report.generated_at.desc()).all()

        log_action(
            user_id=admin.id,
            action="Viewed Reports",
            target_type="Report",
            target_id=None,
            status="Success",
            ip_address=request.remote_addr
        )

        return [
            r.to_dict(only=("id", "report_data", "generated_at", "event_id", "admin_id"))
            for r in reports
        ], 200
