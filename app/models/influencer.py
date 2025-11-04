# app/models/influencer.py
from app import db
from datetime import datetime

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instagram_id = db.Column(db.String(100), unique=True)
    follower_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50))
    contact_info = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Influencer {self.name}>'