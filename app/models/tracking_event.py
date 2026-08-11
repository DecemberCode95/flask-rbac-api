from datetime import datetime, timezone
from app.extensions import db

class TrackingEvent(db.Model):
    __tablename__ = 'tracking_events'

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id', ondelete='CASCADE'), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'location': self.location,
            'status': self.status,
            'description': self.description,
            'timestamp': self.created_at.isoformat()
        }
