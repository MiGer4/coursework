import random

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required

from .models import User, Topic, Problem, UserProblems
from . import db

auth = Blueprint('auth', __name__)
@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password, try again!', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("login.html", user=current_user)


def assign_one_problem_per_topic(user_id):
    topics = Topic.query.filter_by(status='active').all()
    for topic in topics:
        problems = Problem.query.filter_by(topic_id=topic.id, status='active').all()
        if problems:
            random_problem = random.choice(problems)
            user_problem = UserProblems(user_id=user_id, problem_id=random_problem.id)
            db.session.add(user_problem)
    db.session.commit()

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        domain = email.split('@')[-1]

        if user:
            flash('Email already exists.', category='error')
        elif domain != 'chnu.edu.ua':
            flash('Email must has @chnu.edu.ua domain.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            assign_one_problem_per_topic(new_user.id)
            return redirect(url_for('views.index'))
    return render_template("sign_up.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))