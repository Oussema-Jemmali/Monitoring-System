from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import login_required, current_user
from app.monitor import bp
from app.models import User, Device, MonitoringResult
from app.decorators import admin_required
from app import db
import socket
import platform
import psutil
import json
import requests

@bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('monitor/index.html', title='Monitor', users=users)

@bp.route('/devices')
@login_required
def devices():
    if current_user.is_admin:
        devices = Device.query.all()
    else:
        devices = Device.query.filter_by(owner=current_user).all()
    users = User.query.all()  # For the add device form
    return render_template('monitor/devices.html', title='Devices', devices=devices, users=users)

@bp.route('/device/add', methods=['POST'])
@login_required
@admin_required
def add_device():
    hostname = request.form.get('hostname')
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    device_type = request.form.get('device_type')
    user_id = request.form.get('user_id')

    if not hostname or not ip_address:
        flash('Hostname and IP address are required.', 'danger')
        return redirect(url_for('monitor.devices'))

    device = Device(
        hostname=hostname,
        ip_address=ip_address,
        mac_address=mac_address,
        device_type=device_type,
        user_id=user_id if user_id else None
    )
    
    db.session.add(device)
    db.session.commit()
    
    flash(f'Device {hostname} has been added.', 'success')
    return redirect(url_for('monitor.devices'))

@bp.route('/device/<int:device_id>')
@login_required
def device_details(device_id):
    device = Device.query.get_or_404(device_id)
    if not current_user.is_admin and device.user_id != current_user.id:
        abort(403)
    return render_template('monitor/device.html', title=f'Device - {device.hostname}', device=device)

@bp.route('/device/<int:device_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash(f'Device {device.hostname} has been deleted.', 'success')
    return redirect(url_for('monitor.devices'))

@bp.route('/device/<int:device_id>/test-connection', methods=['POST'])
@login_required
@admin_required
def test_device_connection(device_id):
    device = Device.query.get_or_404(device_id)
    
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', device.ip_address]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            device.status = 'UP'
            message = f"Connection to {device.hostname} ({device.ip_address}) successful"
            status = "UP"
        else:
            device.status = 'DOWN'
            message = f"Connection to {device.hostname} ({device.ip_address}) failed"
            status = "DOWN"
        
        # Update last seen time if online
        if device.status == 'UP':
            device.last_seen = datetime.utcnow()
            
        # Create a monitoring result
        monitoring_result = MonitoringResult(
            device_id=device.id,
            status=device.status,
            timestamp=datetime.utcnow()
        )
        db.session.add(monitoring_result)
        
        db.session.commit()
        
        return jsonify({
            'status': status,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f"Error testing connection: {str(e)}"
        }), 500

@bp.route('/get_network_users')
@login_required
def get_network_users():
    users = User.query.all()
    nodes = []
    edges = []
    
    # Create nodes for each user
    for user in users:
        node = {
            'id': user.id,
            'label': user.username,
            'title': f"""
                <div class='network-tooltip'>
                    <strong>{user.username}</strong><br>
                    IP: {user.ip_address}<br>
                    Status: {'Online' if user.is_online else 'Offline'}<br>
                    Department: {user.department or 'N/A'}<br>
                    Role: {user.role or 'N/A'}<br>
                    Last Seen: {user.last_seen.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            """,
            'online': user.is_online
        }
        nodes.append(node)
        
        # Create edges between admin and regular users
        if current_user.is_admin and not user.is_admin:
            edges.append({
                'from': current_user.id,
                'to': user.id
            })

    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

@bp.route('/user/<int:user_id>/test-connection', methods=['POST'])
@login_required
def test_user_connection(user_id):
    if not current_user.is_admin:
        return jsonify({'status': 'ERROR', 'message': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', user.ip_address]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            user.is_online = True
            message = f"Connection to {user.username} ({user.ip_address}) successful"
            status = "UP"
        else:
            user.is_online = False
            message = f"Connection to {user.username} ({user.ip_address}) failed"
            status = "DOWN"
        
        # Update last seen time if online
        if user.is_online:
            user.last_seen = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': status,
            'message': message,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f"Error testing connection: {str(e)}"
        }), 500

@bp.route('/user/<int:user_id>')
@login_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('monitor/user_details.html', title=f'User - {user.username}', user=user)

@bp.route('/get_my_ip', methods=['GET'])
@login_required
def get_my_ip():
    try:
        # Get the client's IP address
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.environ['REMOTE_ADDR']
        return jsonify({'status': 'success', 'ip': ip})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/get_host_ip', methods=['GET'])
@login_required
def get_host_ip():
    try:
        # Get the host's IP address
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return jsonify({'status': 'success', 'ip': ip_address})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
