from flask import Blueprint

bp = Blueprint('letters', __name__, template_folder='templates')

from app.blueprints.letters import routes
