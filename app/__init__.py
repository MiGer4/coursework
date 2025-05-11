from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config

from functools import wraps

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
        
        if models.Topic.query.count() == 0:
            topic = models.Topic(topic_name='test', description='qwodqwkodqkw dopqw kowdqp qpo owpd kqpwo dpoq opwd opqw dop ', max_mark=5.5)
            db.session.add(topic)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    from .views import views
    from .auth import auth
    from .topics import topic
    from .problems import problem
    from .tests import test
    from .users import users
    from .submissions import submissions
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(topic, url_prefix='/')
    app.register_blueprint(problem, url_prefix='/topic')
    app.register_blueprint(test, url_prefix='/problem')
    app.register_blueprint(users, url_prefix='/')
    app.register_blueprint(submissions, url_prefix='/')
    return app

def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            from app import models

            role = models.Role.query.filter_by(id=current_user.role_id).first()

            if role.role_name not in required_role:
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return wrapper