from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from . import db, role_required
from .models import Topic

topic = Blueprint('topic', __name__)

@topic.route('/topics')
@login_required
def topic_list():
    if current_user.role.role_name == 'student':
        topics = Topic.query.filter(Topic.status =='active').all()
    elif current_user.role.role_name == 'teacher':
        topics = Topic.query.filter(Topic.status != 'deleted').all()
    else:
        topics = Topic.query.all()
    return render_template("topics.html", user=current_user, topics=topics)

@topic.route('/topic/edit/<int:topic_id>')
@login_required
@role_required(['teacher', 'super_admin'])
def edit_form(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    return render_template("edit_topic.html", topic=topic, user=current_user)

@topic.route('/topic/update/<int:topic_id>', methods=['POST', 'GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def update(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'POST':
        topic_name = request.form['topic_name']
        if topic_name != topic.topic_name and Topic.query.filter_by(topic_name=topic_name).first():
            flash('Topic with this name already exists!', 'error')
            return render_template("edit_topic.html", topic=topic, user=current_user)
        topic.topic_name = request.form['topic_name']
        topic.description = request.form['description']
        topic.max_mark = float(request.form['max_mark'])
        topic.status = request.form['status']
        for problem in topic.problems:
            problem.status = topic.status
        db.session.commit()
        flash('Topic update successfully', 'success')
        return redirect(url_for('topic.topic_list'))
        #flash('Max mark must be float value!', 'error')
    return redirect(url_for("edit_topic.html", topic=topic, user=current_user))

@topic.route('/topic/<int:topic_id>/delete', methods=['GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def delete(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    topic.status = 'deleted'
    db.session.commit()
    flash('Topic deleted successfully', 'success')
    return redirect(url_for('topic.topic_list'))

@topic.route('/topic/add', methods=['POST', 'GET'])
@login_required
@role_required(['teacher', 'super_admin'])
def add():
    if request.method == 'POST':
        topic_name = request.form.get('topic_name')
        description = request.form.get('description')
        max_mark = float(request.form.get('max_mark'))

        topic = Topic.query.filter_by(topic_name=topic_name).first()

        if topic:
            flash('Topic with this name already exists!', 'error')
            return redirect(url_for('topic.topic_list'))
        if max_mark < 0:
            flash('Max mark must be greater then 0', 'error')
            return redirect(url_for('topic.topic_list'))
        
        new_topic = Topic(topic_name=topic_name, description=description, max_mark=max_mark)
        db.session.add(new_topic)
        db.session.commit()
        flash('Topic created!', 'success')
    
    return redirect(url_for('topic.topic_list'))