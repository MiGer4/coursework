from flask_login import UserMixin

from . import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password =  db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=1)
    status = db.Column(db.String(20), default='pending')  # pending, approved, deleted
    submissions = db.relationship('Submission', backref='user', cascade="all, delete-orphan")
    assigned_problems = db.relationship('UserProblems', backref='user', cascade="all, delete-orphan")
    #approved

    def get_user_name(self):
        return self.email.split('@')[0]

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True)
    users = db.relationship('User', backref='role')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    max_mark = db.Column(db.Float)
    problems = db.relationship('Problem', backref='topic')
    status = db.Column(db.String(20), default='active')  # active, archived, deleted

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    tests = db.relationship('Test', backref='problem', cascade="all, delete-orphan")
    submissions = db.relationship('Submission', backref='problem', cascade="all, delete-orphan")
    status = db.Column(db.String(20), default='active')  # active, archived, deleted
    assigned_users = db.relationship('UserProblems', backref='problem', cascade="all, delete-orphan")

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    values = db.Column(db.JSON)
    points = db.Column(db.Float)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    test_results = db.relationship('TestResult', backref='test', cascade="all, delete-orphan")
    status = db.Column(db.String(20), default='active')  # active, archived, deleted

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    score = db.Column(db.Float, default=0.0)
    test_results = db.relationship('TestResult', backref='submission', cascade="all, delete-orphan")

class TestResult(db.Model):
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), primary_key=True)
    passed = db.Column(db.Boolean)

class UserProblems(db.Model):
    __tablename__ = 'user_problems'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), primary_key=True)
    