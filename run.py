from app import create_app, db
from app.models import User, Alert
from flask import jsonify, request, render_template
from flask_login import login_required, current_user
import psutil

app = create_app()
app.config['DEBUG'] = True

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

def get_system_info():
    try:
        print("Starting system info collection...")
        cpu_info = "11th Gen Intel(R) Core(TM) i5-11300H @ 3.10GHz"
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = {
            'os_name': psutil.os.uname().system,
            'os_version': f"{psutil.os.uname().release} ({psutil.os.uname().version})",
            'processor': cpu_info,
            'ram': f"{memory.total / (1024**3):.1f}GB (Used: {memory.percent}%)",
            'disk_space': [f"C:\\: {disk.total / (1024**3):.1f}GB ({disk.percent}% used)"],
            'network_interfaces': [f"{interface}: {addr.address}" 
                                 for interface, addrs in psutil.net_if_addrs().items() 
                                 for addr in addrs if addr.family == psutil.AF_INET],
            'default_gateway': 'Not found',
            'mac_address': next((addr.address 
                               for interface, addrs in psutil.net_if_addrs().items() 
                               for addr in addrs if addr.family == psutil.AF_LINK), None)
        }
        print(f"Returning system info: {system_info}")
        return jsonify(system_info), 200
    except Exception as e:
        print(f"Error getting system info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/system_info')
@login_required
def system_info():
    return get_system_info()

@app.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    try:
        alerts = Alert.query.filter_by(user_id=current_user.id)\
                          .order_by(Alert.timestamp.desc())\
                          .all()
        return jsonify([alert.to_dict() for alert in alerts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/unread', methods=['GET'])
@login_required
def get_unread_alerts():
    try:
        unread_alerts = Alert.query.filter_by(
            user_id=current_user.id,
            read=False
        ).count()
        return jsonify({'unread_count': unread_alerts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/mark-read/<int:alert_id>', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    try:
        alert = Alert.query.get_or_404(alert_id)
        if alert.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        alert.read = True
        db.session.commit()
        return jsonify({'message': 'Alert marked as read'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/mark-all-read', methods=['POST'])
@login_required
def mark_all_alerts_read():
    try:
        Alert.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/send', methods=['POST'])
@login_required
def send_alert():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({'error': 'Missing required fields'}), 400
        
        alert = Alert(
            user_id=user_id,
            sender_id=current_user.id,
            message=message
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({'message': 'Alert sent successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts-page')
@login_required
def alerts_page():
    return render_template('alerts.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
