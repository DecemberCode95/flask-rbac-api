import uuid
from datetime import datetime, timezone
from app.extensions import db

class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(36), unique=True, nullable=False, default=lambda: f"TRK-{str(uuid.uuid4())[:8].upper()}")
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_name = db.Column(db.String(120), nullable=False)
    origin_address = db.Column(db.String(255), nullable=False)
    destination_address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='CREADO', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    sender = db.relationship('User', backref=db.backref('shipments', lazy=True))
    tracking_events = db.relationship('TrackingEvent', backref='shipment', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username if self.sender else None,
            'recipient_name': self.recipient_name,
            'origin_address': self.origin_address,
            'destination_address': self.destination_address,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'tracking_history': [event.to_dict() for event in self.tracking_events]
        }
