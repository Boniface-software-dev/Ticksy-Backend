# resources/admin_analytics.py
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, User, Event, Ticket, Order, OrderItem
from sqlalchemy import func, extract
from datetime import datetime
import calendar
from utils.logger import log_action


class AdminSummary(Resource):
    @jwt_required()
    def get(self):
        admin = User.query.get(get_jwt_identity())
        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        users = User.query.count()
        events = Event.query.count()
        tickets = Ticket.query.count()
        revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar()

        return {
            "total_users": users,
            "total_events": events,
            "total_tickets": tickets,
            "total_revenue": revenue
        }, 200


class TicketSalesTrends(Resource):
    @jwt_required()
    def get(self):
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)

        if not admin or admin.role != "admin":
            return {"message": "Admins only."}, 403

        try:
           
            results = (
                db.session.query(
                    extract("month", Event.start_time).label("month"),
                    func.sum(OrderItem.quantity).label("sales")
                )
                .join(OrderItem.ticket)
                .join(Ticket.event)
                .group_by("month")
                .order_by("month")
                .all()
            )

            trends = [
                {
                    "month": calendar.month_abbr[int(month)],
                    "sales": int(sales)
                }
                for month, sales in results
            ]

            log_action(
                user_id=admin_id,
                action="Viewed Ticket Sales Trends",
                target_type="Analytics",
                target_id=None,
                status="Success",
                ip_address=request.remote_addr
            )

            return trends, 200

        except Exception as e:
            log_action(
                user_id=admin_id,
                action="Viewed Ticket Sales Trends",
                target_type="Analytics",
                target_id=None,
                status="Failed",
                ip_address=request.remote_addr,
                extra_data={"error": str(e)}
            )
            return {"message": "Could not generate sales trends."}, 500


class RevenueByTicketType(Resource):
    @jwt_required()
    def get(self):
        data = db.session.query(
            Ticket.type,
            func.coalesce(func.sum(OrderItem.quantity * Ticket.price), 0).label('revenue')
        ).join(OrderItem).group_by(Ticket.type).all()

        return [
            {"type": ticket_type, "revenue": revenue}
            for ticket_type, revenue in data
        ], 200


class TopEventTypes(Resource):
    @jwt_required()
    def get(self):
        data = db.session.query(
            Event.category,
            func.count(Event.id).label('count')
        ).group_by(Event.category).order_by(func.count(Event.id).desc()).limit(5).all()

        return [
            {"category": category or "Uncategorized", "count": count}
            for category, count in data
        ], 200


class TopEventsByRevenue(Resource):
    @jwt_required()
    def get(self):
        data = db.session.query(
            Event.title,
            func.sum(OrderItem.quantity * Ticket.price).label('revenue')
        ).join(Ticket, Ticket.event_id == Event.id)\
         .join(OrderItem, OrderItem.ticket_id == Ticket.id)\
         .group_by(Event.title)\
         .order_by(func.sum(OrderItem.quantity * Ticket.price).desc())\
         .limit(5).all()

        return [
            {"title": title, "revenue": revenue}
            for title, revenue in data
        ], 200
