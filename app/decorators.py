from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('This action requires administrator privileges.', 'danger')
            return redirect(url_for('monitor.devices'))
        return f(*args, **kwargs)
    return decorated_function
