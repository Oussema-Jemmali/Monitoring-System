from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User
from app.decorators import admin_required
from app import db

@bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/index.html', title='Admin Dashboard', users=users)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='User Management', users=users)

@bp.route('/user/<int:id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    user = User.query.get_or_404(id)
    if user == current_user:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'success': True, 'is_admin': user.is_admin})

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))
