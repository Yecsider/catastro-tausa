from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from app.models import User 


db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
login_manager.login_view = 'routes.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))