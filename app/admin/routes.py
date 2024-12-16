from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User, Alert
from app.decorators import admin_required
from app import db
from datetime import datetime

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
    return render_template('admin/users.html', title='Users', users=users)

@bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', title='User Management', users=users)

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
        return jsonify({'success': False, 'error': 'You cannot delete your own account.'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/user/<int:user_id>/alert', methods=['POST'])
@login_required
@admin_required
def send_alert(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    
    try:
        # Store the alert in the database
        alert = Alert(
            user_id=user.id,
            sender_id=current_user.id,
            message=data['message'],
            timestamp=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        # You can implement real-time notification here using WebSocket or similar
        
        return jsonify({
            'success': True,
            'message': f'Alert sent to {user.username}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/connected_users')
@login_required
@admin_required
def connected_users():
    users = User.query.filter_by(is_online=True).all()
    return render_template('admin/connected_users.html', title='Connected Users', users=users)
