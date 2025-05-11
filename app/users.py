from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from . import db, role_required
from .models import User, Role, Problem, UserProblems

users = Blueprint('users', __name__)

@users.route('/users')
@login_required
@role_required(['teacher', 'super_admin'])
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users, user=current_user)

@users.route('/users/edit_role/<user_id>/')
@login_required
@role_required(['super_admin'])
def edit_form_role(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    return render_template('edit_user_role.html', us=user, user=current_user, roles=roles)

@users.route('/users/update_role/<user_id>', methods=['POST'])
@login_required
@role_required(['super_admin'])
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    role_id = request.form.get('role_id')
    user.role_id = int(role_id)
    db.session.commit()
    flash('User updated successfully', 'success')
    return redirect(url_for('users.show_users'))

@users.route('/users/edit_status/<user_id>/')
@login_required
@role_required(['teacher', 'super_admin'])
def edit_form_status(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('edit_user_status.html', us=user, user=current_user)

@users.route('/users/update_status/<user_id>', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    status = request.form.get('status')
    user.status = status
    db.session.commit()
    flash('User updated successfully', 'success')
    return redirect(url_for('users.show_users'))

def unassigned_problems(user_id):
    user_problem_ids = db.session.query(UserProblems.problem_id).filter_by(user_id=user_id).subquery()
    unassigned_problems = db.session.query(Problem).filter(
        Problem.id.notin_(user_problem_ids)
    ).all()

    return unassigned_problems

@users.route('users/<user_id>/problems')
@login_required
@role_required(['teacher', 'super_admin'])
def show_user_problems(user_id):
    user = User.query.get_or_404(user_id)
    unassigned_problems_list = unassigned_problems(user.id)
    return render_template('user_problems.html', user=current_user, us=user, unassigned_problems=unassigned_problems_list)

@users.route('users/<user_id>/problems/add', methods=['POST'])
@login_required
@role_required(['teacher', 'super_admin'])
def add_problem(user_id):
    user = User.query.get_or_404(user_id)
    problem = Problem.query.get_or_404(request.form.get('problem_id'))
    if user.id not in problem.assigned_users:
        user_problem = UserProblems(user_id=user.id, problem_id=problem.id)
        db.session.add(user_problem)
        db.session.commit()
        flash('Problem added successfully', 'success')
    else:
        flash('Problem already assigned to this user', 'error')
    
    return redirect(url_for('users.show_user_problems', user_id=user.id))

@users.route('users/<user_id>/problems/<problem_id>/delete', methods=['GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def delete_problem(user_id, problem_id):
    user = User.query.get_or_404(user_id)
    problem = Problem.query.get_or_404(problem_id)
    user_problem = UserProblems.query.filter_by(user_id=user.id, problem_id=problem.id).first()
    
    if user_problem:
        db.session.delete(user_problem)
        db.session.commit()
        flash('Problem removed successfully', 'success')
    else:
        flash('Problem not found for this user', 'error')
    
    return redirect(url_for('users.show_user_problems', user_id=user.id))