from app import create_app, db
from app.models.user import User, LoginLog, ActivityLog
from app.models.influencer import Influencer
from app.models.letter import Letter

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'LoginLog': LoginLog, 
        'ActivityLog': ActivityLog,
        'Influencer': Influencer,
        'Letter': Letter
    }

if __name__ == '__main__':
    app.run(debug=True)
