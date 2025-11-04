from flask import render_template
from flask_login import login_required
from app.models.letter import Letter
from . import bp

@bp.route('/')
@login_required
def letters_list():
    """لیست نامه‌ها"""
    letters = Letter.query.all()
    return render_template('letters/list.html', letters=letters)

@bp.route('/create')
@login_required
def create_letter():
    """ایجاد نامه جدید"""
    return render_template('letters/create.html')
