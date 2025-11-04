from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    
    # وضعیت کاربر - تغییرات جدید
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, active
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    rejected_by = db.Column(db.Integer, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # اطلاعات پروفایل
    profile_picture = db.Column(db.String(255), default='default_avatar.png')
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    def get_profile_picture_url(self):
        """دریافت آدرس کامل تصویر پروفایل"""
        if self.profile_picture:
            return f'/static/uploads/profiles/{self.profile_picture}'
        return '/static/uploads/profiles/default_avatar.png'
    
    @property
    def status_display(self):
        """نمایش وضعیت کاربر"""
        status_names = {
            'pending': 'در انتظار تایید',
            'approved': 'تایید شده',
            'rejected': 'رد شده',
            'active': 'فعال'
        }
        return status_names.get(self.status, self.status)
    
    @property
    def status_badge(self):
        """بدج وضعیت کاربر"""
        badge_classes = {
            'pending': 'bg-warning',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'active': 'bg-info'
        }
        return f'<span class="badge {badge_classes.get(self.status, "bg-secondary")}">{self.status_display}</span>'
    
    @property
    def role_display(self):
        """نمایش نقش کاربر"""
        role_names = {
            'user': 'کاربر عادی',
            'admin': 'مدیر',
            'super_admin': 'سوپر ادمین'
        }
        return role_names.get(self.role, self.role)
    
    def approve(self, approved_by_user):
        """تایید کاربر توسط ادمین"""
        self.status = 'approved'
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        self.approved_by = approved_by_user.id
    
    def reject(self, rejected_by_user, reason=None):
        """رد کاربر توسط ادمین"""
        self.status = 'rejected'
        self.is_approved = False
        self.is_active = False
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejected_by_user.id
        self.rejection_reason = reason
    
    def activate(self):
        """فعال کردن کاربر پس از اولین لاگین"""
        self.status = 'active'