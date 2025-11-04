# app/blueprints/influencers/__init__.py
from flask import Blueprint

bp = Blueprint('influencers', __name__)

from app.blueprints.influencers import routes