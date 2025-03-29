import os
import subprocess
import datetime
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
    return render_template("problems.html", user=current_user, topic=topic)

@problem.route('/<int:topic_id>/problem/add', methods=['POST', 'GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def add(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == "POST":
        problem_name = request.form.get('problem_name')
        description = request.form.get('description')

        problem = Problem.query.filter_by(problem_name=problem_name).first()

        if problem:
            flash('Problem with this name already exists!', 'error')
            return redirect(url_for('problem.problem_list_of_topic', topic_id=topic_id))
        
        new_problem = Problem(problem_name=problem_name, description=description, topic_id=topic_id)
        db.session.add(new_problem)
        db.session.commit()
        flash('Problem created!', 'success')
    return redirect(url_for('problem.problem_list_of_topic', topic_id=topic_id))

@problem.route('/<int:topic_id>/problems/<int:problem_id>')
@login_required
def show_problem(topic_id, problem_id):
    problem = Problem.query.get_or_404(problem_id)
    topic = Problem.query.get_or_404(topic_id)
    return render_template("problem.html", user=current_user, problem=problem, topic=topic)

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
    if problem_name != problem.problem_name and Problem.query.filter_by(problem_name=problem_name).first():
        flash('Problem with this name already exist', 'error')
        return redirect(url_for('problem.edit_form', problem_id=problem_id))
    problem.problem_name = problem_name
    problem.description = request.form.get('description')
    db.session.commit()
    return redirect(url_for('problem.show_problem', topic_id=problem.topic.id, problem_id=problem.id))

@problem.route('/problems/<int:problem_id>/delete', methods=['GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def delete(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    topic_id = problem.topic.id
    db.session.delete(problem)
    db.session.commit()
    return redirect(url_for('problem.problem_list_of_topic', topic_id=topic_id))

ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@problem.route('/problem/<int:problem_id>/submit', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def submit_solution(problem_id):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    if 'solution_file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['solution_file']
    if file.filename == "":
        flash('No selected files', 'error')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        flash('File must has .py extension', 'error')
        return redirect(request.url)

    file_name = secure_filename(datetime.datetime.now().__str__())
    file_path = os.path.join(upload_folder, file_name)
    file.save(file_path)

    problem = Problem.query.get_or_404(problem_id)
    new_submission = Submission(problem_id=problem_id, user_id=current_user.id, file_path=file_path)
    db.session.add(new_submission)
    db.session.commit()

    for test in problem.tests:
        try:
            result = subprocess.run(
                ['python3', file_path]
                , input=test.values['input']
                , text=True
                , capture_output=True
                , timeout=2
            )
            output = result.stdout.strip()
            
            new_test_result = TestResult(test_id=test.id, submission_id=new_submission.id, passed=output == test.values['output'])
            db.session.add(new_test_result)
            db.session.commit()

        except:
            new_test_result = TestResult(test_id=test.id, submission_id=new_submission.id, passed=False)
            db.session.add(new_test_result)
            db.session.commit()
    return redirect(url_for('problem.show_problem', problem_id=problem_id, topic_id=problem.topic.id))