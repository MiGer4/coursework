from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Submission, UserProblems, Problem
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from . import db

views = Blueprint('views', __name__)
@views.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template("index.html", user=current_user)
    user_problem_ids = db.session.query(UserProblems.problem_id).filter_by(user_id=current_user.id).all()
    problem_ids = [pid for (pid,) in user_problem_ids]

    task_progress = []
    for pid in problem_ids:
        problem = Problem.query.get(pid)
        best_submission = Submission.query.filter_by(user_id=current_user.id, problem_id=pid)\
            .order_by(Submission.score.desc(), Submission.created_at.desc())\
            .first()
        
        task_progress.append({
            "problem": problem,
            "submission": best_submission  # може бути None
        })

    return render_template("index.html", task_progress=task_progress, user=current_user)