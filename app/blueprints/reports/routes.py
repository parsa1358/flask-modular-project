from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from . import bp

# reports routes will be added here

@bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')
