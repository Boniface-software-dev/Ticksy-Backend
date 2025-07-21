from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import re

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    serialize_rules = ("-attendee.reviews", "-event.reviews")


    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    attendee = db.relationship("User", back_populates="reviews")
    event = db.relationship("Event", back_populates="reviews")


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    serialize_rules = (
        "-password",
        "-events.organizer",
        "-orders.attendee",
        "-reviews.attendee",
        "-saved_events.user",
        "-logs.user",
        "-reports.admin"
    )

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="attendee")  
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.now)

    events = db.relationship("Event", back_populates="organizer", cascade="all, delete")
    orders = db.relationship("Order", back_populates="attendee", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="attendee", cascade="all, delete")
    saved_events = db.relationship("SavedEvent", back_populates="user", cascade="all, delete")
    logs = db.relationship("AuditLog", backref="user")
    reports = db.relationship("Report", back_populates="admin")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    @validates("email")
    def validate_email(self, key, value):
        normalized = value.strip().lower()
        reg = r"[A-Za-z][A-Za-z0-9]*(\.[A-Za-z0-9]+)*@[A-Za-z0-9]+\.[a-z]{2,}"
        if not re.match(reg, normalized):
            raise ValueError("Invalid email format")
        return normalized


class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"
    serialize_rules = ("-attendee.orders", "-order_items.order")

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.String, default="pending")
    mpesa_receipt = db.Column(db.String)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    attendee = db.relationship("User", back_populates="orders")
    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete")

class OrderItem(db.Model, SerializerMixin):
    __tablename__ = "order_items"
    serialize_rules = ("-order.order_items", "-ticket.order_items")

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))

    order = db.relationship("Order", back_populates="order_items")
    ticket = db.relationship("Ticket", back_populates="order_items")

    event_passes = db.relationship("EventPass", back_populates="order_item", cascade="all, delete-orphan")

class EventPass(db.Model, SerializerMixin):
    __tablename__ = "event_passes"
    serialize_rules = ("-order_item.event_passes",)

    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(50), unique=True, nullable=False)
    attendee_first_name = db.Column(db.String(100), nullable=False)
    attendee_last_name = db.Column(db.String(100), nullable=False)
    attendee_email = db.Column(db.String(150), nullable=False)
    attendee_phone = db.Column(db.String(20), nullable=False)
    att_status = db.Column(db.Boolean, default=False)

    order_item_id = db.Column(db.Integer, db.ForeignKey("order_items.id"), nullable=False)
    order_item = db.relationship("OrderItem", back_populates="event_passes")
class AuditLog(db.Model, SerializerMixin):
    __tablename__ = "audit_logs"
    serialize_rules = ("-user.logs",)

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(100), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="Success", nullable=False)
    ip_address = db.Column(db.String(100), nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)

    user = db.relationship("User", backref="logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id} at {self.timestamp}>"



class SavedEvent(db.Model, SerializerMixin):
    __tablename__ = "saved_events"
    serialize_rules = ("-user.saved_events", "-event.saved_events")

    id = db.Column(db.Integer, primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user = db.relationship("User", back_populates="saved_events")
    event = db.relationship("Event", back_populates="saved_events")

class Report(db.Model, SerializerMixin):
    __tablename__ = "reports"
    serialize_rules = ("-admin.reports", "-event.reports")

    id = db.Column(db.Integer, primary_key=True)
    generated_at = db.Column(db.DateTime, default=datetime.now)
    report_data = db.Column(db.Text)

    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    admin = db.relationship("User", back_populates="reports")
    event = db.relationship("Event", back_populates="reports")
    

class Ticket(db.Model, SerializerMixin):
    __tablename__ = "tickets"
    serialize_rules = ("-event.tickets", "-order_items.ticket")

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    event = db.relationship("Event", back_populates="tickets")
    order_items = db.relationship("OrderItem", back_populates="ticket")

class Event(db.Model, SerializerMixin):
    __tablename__= "events"
    serialize_rules = (
        "-organizer.events",
        "-tickets.event",
        "-reviews.event",
        "-saved_events.event",
        "-reports.event"
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String)
    tags = db.Column(db.String)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String, default="pending")
    image_url = db.Column(db.String)
    attendee_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    organizer = db.relationship("User", back_populates="events")
    tickets = db.relationship("Ticket", back_populates="event", cascade="all, delete")
    reviews = db.relationship("Review", back_populates="event", cascade="all, delete")
    saved_events = db.relationship("SavedEvent", back_populates="event", cascade="all, delete")
    reports = db.relationship("Report", back_populates="event")

