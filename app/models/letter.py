from app import db
from datetime import datetime

class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_letter = db.Column(db.String(200), nullable=False)
    sender_letter = db.Column(db.String(100), nullable=False)
    receiver_letter = db.Column(db.String(100))
    description = db.Column(db.Text)
    letter_type = db.Column(db.String(20), default='input')  # input/output
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected
    priority = db.Column(db.String(20), default='normal')  # low/normal/high/urgent
    file_path = db.Column(db.String(300))
    
    # روابط
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    
    # تاریخ‌ها
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    letter_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Letter {self.title_letter}>'
    
    @property
    def date_enter_shamsi(self):
        from app.utils.jalali_date import to_jalali
        return to_jalali(self.created_at)
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
