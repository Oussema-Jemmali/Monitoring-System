from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from app.main import bp
from app.models import Device, MonitoringResult, User
from app.decorators import admin_required
from app import db
import requests
from netaddr import IPNetwork
import psutil
import platform
import json
import wmi
import socket
import subprocess

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    devices = Device.query.filter_by(user_id=current_user.id).all()
    down_devices = [d for d in devices if d.status == 'DOWN']
    return render_template('main/index.html', 
                         title='Home',
                         devices=devices,
                         down_devices=down_devices)

@bp.route('/get_ip', methods=['GET'])
@login_required
def get_ip():
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # We don't actually connect to 8.8.8.8, we just use it to get the default route
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        return jsonify({'ip': local_ip})
    except Exception as e:
        print(f"Error getting IP: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/calculate_cidr', methods=['POST'])
@login_required
def calculate_cidr():
    try:
        ip = request.json.get('ip')
        if not ip:
            return jsonify({'error': 'IP address is required'}), 400
        
        network = IPNetwork(ip)
        return jsonify({
            'network': str(network.network),
            'broadcast': str(network.broadcast),
            'netmask': str(network.netmask),
            'size': network.size,
            'first_host': str(network.network + 1),
            'last_host': str(network.broadcast - 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/get_network_users')
@login_required
def get_network_users():
    try:
        # Get all users
        users = User.query.all()
        nodes = []
        edges = []
        
        # Add current user as central node
        nodes.append({
            'id': current_user.id,
            'label': current_user.username,
            'color': '#ff0000',  # Red for current user
            'size': 35
        })
        
        # Add other users
        for user in users:
            if user.id != current_user.id:
                # Add node for each user
                nodes.append({
                    'id': user.id,
                    'label': user.username,
                    'color': '#97C2FC',  # Default blue for other users
                    'size': 30
                })
                
                # Connect each user to the current user
                edges.append({
                    'from': current_user.id,
                    'to': user.id
                })
                
                # Add connections between users based on their devices
                user_devices = Device.query.filter_by(user_id=user.id).all()
                if user_devices:
                    for device in user_devices:
                        edges.append({
                            'from': user.id,
                            'to': device.id + 1000,  # Offset to avoid ID conflicts
                            'color': '#2ecc71'  # Green for device connections
                        })
                        nodes.append({
                            'id': device.id + 1000,
                            'label': device.hostname,
                            'color': '#2ecc71',
                            'size': 20
                        })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges
        })
    except Exception as e:
        print(f"Error in get_network_users: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@bp.route('/system_info', methods=['GET'])
@login_required
def get_system_info():
    try:
        # Get RAM info
        ram = psutil.virtual_memory()
        
        # Get Windows version
        os_info = platform.uname()

        # Get CPU info using WMI
        w = wmi.WMI()
        cpu = w.Win32_Processor()[0]

        # Get disk info
        disks = []
        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                disks.append({
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'total': f"{usage.total / (1024**3):.1f}GB",
                    'used': f"{usage.used / (1024**3):.1f}GB",
                    'free': f"{usage.free / (1024**3):.1f}GB",
                    'percent': f"{usage.percent}%"
                })
            except:
                continue

        system_info = {
            'os': {
                'name': os_info.system,
                'version': os_info.version,
                'architecture': platform.architecture()[0]
            },
            'cpu': {
                'brand': cpu.Name,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'usage': f"{psutil.cpu_percent()}%",
                'frequency': f"{cpu.MaxClockSpeed}MHz"
            },
            'ram': {
                'total': f"{ram.total / (1024**3):.1f}GB",
                'available': f"{ram.available / (1024**3):.1f}GB",
                'used': f"{ram.used / (1024**3):.1f}GB",
                'percent': f"{ram.percent}%"
            },
            'disks': disks
        }
        
        return jsonify(system_info)
    except Exception as e:
        print(f"Error in get_system_info: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@bp.route('/ping_user/<int:user_id>', methods=['GET'])
@login_required
def ping_user(user_id):
    try:
        target_user = User.query.get_or_404(user_id)
        # Get the last known device for the user
        device = Device.query.filter_by(user_id=user_id).order_by(Device.last_seen.desc()).first()
        
        if not device or not device.ip_address:
            return jsonify({'error': 'No IP address found for this user'}), 404
            
        # Run ping command
        try:
            # Run ping with a timeout of 2 seconds and 4 packets
            output = subprocess.check_output(['ping', '-n', '4', '-w', '2000', device.ip_address], 
                                          universal_newlines=True)
            
            # Parse ping results
            lines = output.split('\n')
            stats = lines[-3:-1]  # Get the last few lines containing statistics
            
            return jsonify({
                'success': True,
                'target_user': target_user.username,
                'ip_address': device.ip_address,
                'results': stats
            })
        except subprocess.CalledProcessError:
            return jsonify({
                'success': False,
                'target_user': target_user.username,
                'ip_address': device.ip_address,
                'error': 'Host unreachable'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ping_ip', methods=['POST'])
@login_required
def ping_ip():
    try:
        ip = request.json.get('ip', '127.0.0.1')  # Default to localhost if no IP provided
        
        # Run ping command with timeout
        try:
            output = subprocess.check_output(
                ['ping', '-n', '4', '-w', '2000', ip],
                universal_newlines=True,
                stderr=subprocess.STDOUT  # Capture error output as well
            )
            
            return jsonify({
                'success': True,
                'ip_address': ip,
                'output': output
            })
        except subprocess.CalledProcessError as e:
            return jsonify({
                'success': False,
                'ip_address': ip,
                'error': 'Host unreachable'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
