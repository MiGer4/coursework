from flask_login import UserMixin

from . import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password =  db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=1)

    def get_user_name(self):
        return self.email.split('@')[0]

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True)
    users = db.relationship('User')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    max_mark = db.Column(db.Float)
