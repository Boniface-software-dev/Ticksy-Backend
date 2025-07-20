import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_serialize import SerializerMixin


class SavedEvent(db.Model, SerializerMixin):
    __tablename__ = "saved_events"
    serialize_rules = ("-user.saved_events", "-event.saved_events")

    id = db.Column(db.Integer, primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    user = db.relationship("User", back_populates="saved_events")
    event = db.relationship("Event", back_populates="saved_events")