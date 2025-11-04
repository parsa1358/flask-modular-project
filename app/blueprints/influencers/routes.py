from flask import render_template
from flask_login import login_required
from app.models.influencer import Influencer
from . import bp

@bp.route('/')
@login_required
def influencers_list():
    """لیست اینفلوئنسرها"""
    influencers = Influencer.query.all()
    return render_template('influencers/list.html', influencers=influencers)
