import os
import subprocess
import datetime
import uuid
import hashlib
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from . import db, role_required
from .models import Topic, Problem, Submission, TestResult

problem = Blueprint('problem', __name__)

@problem.route('/<int:topic_id>/problems')
@login_required
def problem_list_of_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if current_user.role.role_name == 'student':
        problems = Problem.query.filter(Problem.status == 'active', Problem.topic_id == topic_id).all()
    elif current_user.role.role_name == 'teacher':
        problems = Problem.query.filter(Problem.status != 'deleted', Problem.topic_id == topic_id).all()
    else:
        problems = Problem.query.filter(Problem.topic_id == topic_id).all()
    return render_template("problems.html", user=current_user, problems=problems, topic=topic)

@problem.route('/<int:topic_id>/problem/add', methods=['POST', 'GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def add(topic_id):
    if request.method == "POST":
        topic = Topic.query.get_or_404(topic_id)
        problem_name = request.form.get('problem_name')
        description = request.form.get('description')

        problem = Problem.query.filter_by(problem_name=problem_name).first()

        if problem:
            flash('Problem with this name already exists!', 'error')
            return redirect(url_for('problem.problem_list_of_topic', topic_id=topic_id))
        
        new_problem = Problem(problem_name=problem_name, description=description, status=topic.status, topic_id=topic_id)
        db.session.add(new_problem)
        db.session.commit()
        flash('Problem created!', 'success')
    return redirect(url_for('problem.problem_list_of_topic', topic_id=topic_id))

@problem.route('/problems/<int:problem_id>')
@login_required
def show_problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return render_template("problem.html", user=current_user, problem=problem)

@problem.route('/problems/<int:problem_id>/edit')
@login_required
@role_required(['teacher', 'super_admin'])
def edit_form(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return render_template("edit_problem.html", user=current_user, problem=problem)

@problem.route('/problems/<int:problem_id>/update', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def update(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    problem_name = request.form.get('problem_name')
    status = request.form.get('status')
    if problem_name != problem.problem_name and Problem.query.filter_by(problem_name=problem_name).first():
        flash('Problem with this name already exist', 'error')
        return redirect(url_for('problem.edit_form', problem_id=problem_id))
    problem.problem_name = problem_name
    problem.description = request.form.get('description')
    problem.status = status
    db.session.commit()
    return redirect(url_for('problem.show_problem', topic_id=problem.topic.id, problem_id=problem.id))

@problem.route('/problems/<int:problem_id>/delete', methods=['GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def delete(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    problem.status = 'deleted'
    db.session.commit()
    flash('Problem deleted!', 'success')
    return redirect(url_for('problem.problem_list_of_topic', topic_id=problem.topic_id))
