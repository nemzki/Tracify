from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from extensions import db
from app.models.visitor import Visitor
from app.models.visitor_log import VisitorLog
from app.models.task import Task
from app.forms import VisitorLogForm

security_bp = Blueprint('security', __name__, url_prefix='/security')


def security_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role not in ('security', 'admin'):
            flash('Access denied.', 'error')
            return redirect(url_for('main.landing'))
        return f(*args, **kwargs)
    return decorated


def get_pending_task_count():
    return Task.query.filter_by(
        assigned_to=current_user.user_id,
        status='assigned'
    ).count()


@security_bp.route('/dashboard')
@security_required
def dashboard():
    my_tasks = Task.query.filter_by(
        assigned_to=current_user.user_id
    ).order_by(Task.created_at.desc()).all()

    recent_logs = VisitorLog.query.filter_by(
        recorded_by=current_user.user_id
    ).order_by(VisitorLog.time_in.desc()).limit(10).all()

    pending_task_count = sum(1 for t in my_tasks if t.status == 'assigned')

    return render_template('security_dashboard.html',
                           my_tasks=my_tasks,
                           recent_logs=recent_logs,
                           pending_task_count=pending_task_count)


@security_bp.route('/visitors')
@security_required
def visitor_logs():
    query = request.args.get('q', '').strip()
    if query:
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


@security_bp.route('/log-visitor', methods=['GET', 'POST'])
@security_required
def log_visitor():
    form = VisitorLogForm()

    if form.validate_on_submit():
        # Create or find visitor
        visitor = Visitor.query.filter_by(
            contact_number=form.contact_number.data
        ).first()

        if not visitor:
            visitor = Visitor(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                contact_number=form.contact_number.data,
                email=form.email.data or None
            )
            db.session.add(visitor)
            db.session.flush()  # get visitor_id

        log = VisitorLog(
            visitor_id=visitor.visitor_id,
            recorded_by=current_user.user_id,
            purpose_of_visit=form.purpose_of_visit.data,
            status='active'
        )
        db.session.add(log)
        db.session.commit()
        flash('Visitor logged successfully.', 'success')
        return redirect(url_for('security.dashboard'))

    return render_template('visitor_log_form.html', form=form)


@security_bp.route('/checkout/<int:log_id>', methods=['POST'])
@security_required
def checkout_visitor(log_id):
    log = VisitorLog.query.get_or_404(log_id)
    log.time_out = datetime.utcnow()
    log.status = 'out'
    db.session.commit()
    flash('Visitor checked out.', 'success')
    return redirect(url_for('security.dashboard'))


@security_bp.route('/tasks')
@security_required
def my_tasks():
    tasks = Task.query.filter_by(
        assigned_to=current_user.user_id
    ).order_by(Task.created_at.desc()).all()
    pending_count = sum(1 for t in tasks if t.status == 'assigned')

    return render_template('my_tasks.html', tasks=tasks, pending_count=pending_count)


@security_bp.route('/tasks/complete/<int:task_id>', methods=['POST'])
@security_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.assigned_to != current_user.user_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('security.my_tasks'))
    task.status = 'done'
    db.session.commit()
    flash('Task marked as done.', 'success')
    return redirect(url_for('security.my_tasks'))