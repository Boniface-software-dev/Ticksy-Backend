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

# ------------------ User ------------------
class User(db.Model, SerializerMixin):
    _tablename_ = "users"
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
    logs = db.relationship("Log", back_populates="user")
    reports = db.relationship("Report", back_populates="admin")

    def _repr_(self):
        return f"<User {self.first_name} {self.last_name}>"

    @validates("email")
    def validate_email(self, key, value):
        normalized = value.strip().lower()
        reg = r"[A-Za-z][A-Za-z0-9](\.[A-Za-z0-9]+)@[A-Za-z0-9]+\.[a-z]{2,}"
        if not re.match(reg, normalized):
            raise ValueError("Invalid email format")
        return normalized
