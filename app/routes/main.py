from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('security.dashboard'))
    return render_template('landing.html')