from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from . import db, role_required
from .models import Problem, Test, Topic

test = Blueprint('test', __name__)

@test.route('<int:problem_id>/tests/add', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def add(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    values = {
        "input" : request.form.get('input_data'),
        "output" : request.form.get('expected_output')
    }
    points = float(request.form.get('points'))
    new_test = Test(values=values, points=points, problem_id=problem_id)
    db.session.add(new_test)
    db.session.commit()
    
    topic = Topic.query.get_or_404(problem.topic_id)
    flash("Test is successfully added", 'success')
    return redirect(url_for('problem.show_problem', problem_id=problem_id, topic_id=topic.id))

@test.route('/tests/<int:test_id>/edit')
@login_required
@role_required(['teacher', 'super_admin'])
def edit_form(test_id):
    test = Test.query.get_or_404(test_id)
    return render_template("edit_test.html", test=test, user=current_user)

@test.route('/tests/<int:test_id>/update', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def update(test_id):
    test = Test.query.get_or_404(test_id)
    problem = Problem.query.get_or_404(test.problem_id)
    topic = Topic.query.get_or_404(problem.topic_id)
    status = request.form.get('status')
    test.values = {
        "input" : request.form.get('input_data'),
        "output" : request.form.get('expected_output')
    }
    test.points = float(request.form.get('points'))
    test.status = status
    db.session.commit()
    flash('Test updated successfully', 'success')
    return redirect(url_for('problem.show_problem', problem_id=problem.id, topic_id=topic.id))

@test.route('/tests/<int:test_id>/delete', methods=['GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def delete(test_id):
    test = Test.query.get_or_404(test_id)
    test.status = 'deleted'
    db.session.commit()
    flash('Test deleted successfully', 'success')
    return redirect(url_for('problem.show_problem', problem_id=test.problem_id, topic_id=test.problem.topic_id))