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



class Order(db.Model, SerializerMixin):
    __tablename__="orders"
    serialize_rules = ("-attendee.orders", "-order_items.order")

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.String, default="pending")
    mpesa_receipt = db.Column(db.String)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class OrderItem(db.Model, SerializerMixin):
    __tablename__ = "order_items"
    serialize_rules = ("-order.order_items", "-ticket.order_items")

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))


