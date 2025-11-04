from app import login_manager
from .user import User

@login_manager.user_loader
def load_user(user_id):
    """User loader برای Flask-Login"""
    try:
        return User.query.get(int(user_id))
    except:
        return None
