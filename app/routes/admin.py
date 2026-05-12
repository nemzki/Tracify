from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from extensions import db
from app.models.user import User
from app.models.task import Task
from app.models.visitor_log import VisitorLog
from app.forms import TaskForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admins only.', 'error')
            return redirect(url_for('security.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    today = date.today()

    # Stats
    total_visitors = VisitorLog.query.count()
    visitors_today = VisitorLog.query.filter(
        db.func.date(VisitorLog.time_in) == today
    ).count()
    active_visitors = VisitorLog.query.filter_by(status='active').count()
    personnel = User.query.filter_by(role='security').all()
    total_personnel = len(personnel)
    total_tasks = Task.query.count()
    pending_tasks = Task.query.filter_by(status='assigned').count()

    recent_logs = VisitorLog.query.filter(
        db.func.date(VisitorLog.time_in) == today
    ).order_by(VisitorLog.time_in.desc()).limit(10).all()

    tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()

    stats = {
        'total_visitors': total_visitors,
        'visitors_today': visitors_today,
        'active_visitors': active_visitors,
        'total_personnel': total_personnel,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
    }

    return render_template('admin_dashboard.html',
                           stats=stats,
                           recent_logs=recent_logs,
                           personnel=personnel,
                           tasks=tasks)


@admin_bp.route('/visitors')
@admin_required
def visitors():
    query = request.args.get('q', '').strip()
    if query:
        from app.models.visitor import Visitor
        logs = VisitorLog.query.join(VisitorLog.visitor).filter(
            db.or_(
                Visitor.first_name.ilike(f'%{query}%'),
                Visitor.last_name.ilike(f'%{query}%'),
                Visitor.contact_number.ilike(f'%{query}%'),
                VisitorLog.purpose_of_visit.ilike(f'%{query}%')
            )
        ).order_by(VisitorLog.time_in.desc()).all()
    else:
        logs = VisitorLog.query.order_by(VisitorLog.time_in.desc()).all()

    return render_template('visitor_logs.html', logs=logs, query=query)


@admin_bp.route('/personnel')
@admin_required
def personnel():
    personnel_list = User.query.filter_by(role='security').all()
    return render_template('visitor_logs.html',
                           logs=[],
                           query=None,
                           personnel_list=personnel_list)


@admin_bp.route('/tasks')
@admin_required
def tasks():
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('admin_dashboard.html',
                           stats={'total_visitors': 0, 'visitors_today': 0,
                                  'active_visitors': 0, 'total_personnel': 0,
                                  'total_tasks': len(all_tasks),
                                  'pending_tasks': sum(1 for t in all_tasks if t.status == 'assigned')},
                           recent_logs=[],
                           personnel=[],
                           tasks=all_tasks)


@admin_bp.route('/tasks/assign', methods=['GET', 'POST'])
@admin_required
def assign_task():
    form = TaskForm()
    personnel = User.query.filter_by(role='security').all()
    form.assigned_to.choices = [(p.user_id, p.username) for p in personnel]

    if form.validate_on_submit():
        task = Task(
            assigned_to=form.assigned_to.data,
            task_description=form.task_description.data,
            status='assigned'
        )
        db.session.add(task)
        db.session.commit()
        flash('Task assigned successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('task_form.html', form=form, task=None)


@admin_bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    personnel = User.query.filter_by(role='security').all()
    form.assigned_to.choices = [(p.user_id, p.username) for p in personnel]

    if form.validate_on_submit():
        task.assigned_to = form.assigned_to.data
        task.task_description = form.task_description.data
        task.status = form.status.data
        db.session.commit()
        flash('Task updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('task_form.html', form=form, task=task)


@admin_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('admin.dashboard'))