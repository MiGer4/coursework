from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app import models

    with app.app_context():
        db.create_all()

        if models.Role.query.count() == 0:
            student = models.Role(role_name='student')
            teacher = models.Role(role_name='teacher')
            super_admin = models.Role(role_name='super_admin')
            db.session.add_all([student, teacher, super_admin])
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
