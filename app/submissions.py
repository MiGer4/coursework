import os
import subprocess
import datetime
import uuid
import hashlib
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from . import db, role_required
from .models import Problem, TestResult, User, Submission

submissions  = Blueprint('submissions', __name__)

@submissions.route('/submissions/users/<int:user_id>')
@login_required
def show_user_submissions(user_id):
    user = User.query.get_or_404(user_id)
    submissions = Submission.query.filter_by(user_id=user.id).all()
    return render_template('user_submissions.html', submissions=submissions, user=current_user)

@submissions.route('submissions/<int:submission_id>/code')
@login_required
def show_submission_code(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    file_path = submission.file_path
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            code = file.read()
        return render_template('submission_code.html', code=code, user=current_user)
    else:
        flash('File not found', 'error')
        return redirect(url_for('submissions.show_user_submissions', user_id=submission.user_id))
    
ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_file_name(username):
    now = datetime.datetime.now().isoformat()
    unique_id = str(uuid.uuid4())
    raw_string = f"{username}_{now}_{unique_id}"
    sha_name = hashlib.sha256(raw_string.encode()).hexdigest()
    return secure_filename(sha_name)

@submissions.route('/submissions/problems<int:problem_id>/add', methods=['POST'])
@login_required
def add_submission(problem_id):
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

    file_name = generate_file_name(current_user._get_current_object().get_user_name())
    file_path = os.path.join(upload_folder, file_name)
    file.save(file_path)

    problem = Problem.query.get_or_404(problem_id)
    new_submission = Submission(problem_id=problem_id, user_id=current_user.id, file_path=file_path)
    db.session.add(new_submission)
    db.session.commit()

    sum = 0
    solution_sum = 0
    for test in problem.tests:
        if test.status != 'active':
            continue
        sum += test.points
        try:
            result = subprocess.run(
                ['python3', file_path]
                , input=test.values['input']
                , text=True
                , capture_output=True
                , timeout=2
            )
            output = result.stdout.strip()
            
            passed = result.returncode == 0 and output == test.values['output']
            new_test_result = TestResult(test_id=test.id, submission_id=new_submission.id, passed=passed)
            if passed:
                solution_sum += test.points
            db.session.add(new_test_result)
            db.session.commit()
            new_submission.score = (solution_sum / sum) * 100
            db.session.commit()

        except:
            new_test_result = TestResult(test_id=test.id, submission_id=new_submission.id, passed=False)
            db.session.add(new_test_result)
            db.session.commit()
    return redirect(url_for('problem.show_problem', problem_id=problem_id, topic_id=problem.topic.id))