from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User

from . import main_bp

@main_bp.route('/')
@main_bp.route('/home')
@main_bp.route('/dashboard')
@login_required
def home():
    # فقط کاربران تایید شده می‌توانند وارد شوند
    if not current_user.is_approved and not current_user.is_admin:
        flash('❌ حساب کاربری شما هنوز تایید نشده است. لطفاً منتظر تایید ادمین باشید.', 'warning')
        return redirect(url_for('auth.logout'))
    
    dashboard_data = {
        'total_letters': 150,
        'approved_letters': 120,
        'pending_letters': 30,
        'total_users': User.query.filter_by(is_approved=True).count() if current_user.is_admin else None
    }
    return render_template('home.html', **dashboard_data)

@main_bp.route('/test')
def test():
    from datetime import datetime
    return render_template('test.html', now=datetime.now())