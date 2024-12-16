import os
import psutil
import platform
import socket
import wmi
import subprocess
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.models import User, Alert
from app import db
import requests
from netaddr import IPNetwork
import json

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Get and update current user's IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        current_user.ip_address = local_ip
        db.session.commit()
    except Exception as e:
        print(f"Error updating IP address: {str(e)}")
    
    # Get system info for current user
    system_info = get_system_info()
    
    # Get all online users
    online_users = User.query.filter_by(is_online=True).all()
    
    # Get user's alerts
    alerts = Alert.query.filter_by(user_id=current_user.id).order_by(Alert.timestamp.desc()).limit(5).all()
    
    # Get information for each user
    users_info = []
    for user in online_users:
        try:
            user_info = {
                'username': user.username,
                'email': user.email,
                'ip_address': user.ip_address,
                'department': user.department,
                'last_seen': user.last_seen,
                'system_info': {
                    'is_online': user.is_online,
                    'username': user.username,
                    'ip_address': user.ip_address,
                    'last_seen': user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else None
                }
            }
            users_info.append(user_info)
        except Exception as e:
            print(f"Error getting info for {user.username}: {str(e)}")
            continue
    
    return render_template('main/index.html', 
                         title='Home',
                         system_info=system_info,
                         users_info=users_info,
                         alerts=alerts)

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
                # user_devices = Device.query.filter_by(user_id=user.id).all()
                # if user_devices:
                #     for device in user_devices:
                #         edges.append({
                #             'from': user.id,
                #             'to': device.id + 1000,  # Offset to avoid ID conflicts
                #             'color': '#2ecc71'  # Green for device connections
                #         })
                #         nodes.append({
                #             'id': device.id + 1000,
                #             'label': device.hostname,
                #             'color': '#2ecc71',
                #             'size': 20
                #         })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges
        })
    except Exception as e:
        print(f"Error in get_network_users: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@bp.route('/network_data')
@login_required
def network_data():
    try:
        # Get all users
        users = User.query.all()
        
        # Get default gateway
        gateway = get_default_gateway()
        
        # Prepare nodes and edges for visualization
        nodes = []
        edges = []
        
        # Add gateway node
        nodes.append({
            'id': 'gateway',
            'label': f'Gateway\n{gateway}',
            'group': 'gateway',
            'shape': 'diamond',
            'size': 30
        })
        
        # Add nodes for each user
        for user in users:
            node_data = {
                'id': user.id,
                'label': f'{user.username}\n{user.ip_address}',
                'group': 'user',
                'shape': 'dot',
                'size': 20
            }
            
            # Different colors for online/offline status
            if user.is_online:
                node_data['color'] = {
                    'background': '#28a745',
                    'border': '#1e7e34'
                }
            else:
                node_data['color'] = {
                    'background': '#dc3545',
                    'border': '#bd2130'
                }
            
            nodes.append(node_data)
            
            # Add edge between user and gateway
            edges.append({
                'from': 'gateway',
                'to': user.id,
                'length': 200,
                'color': {
                    'color': '#2196F3',
                    'opacity': 0.8
                },
                'arrows': {
                    'to': {
                        'enabled': True,
                        'scaleFactor': 0.5
                    }
                }
            })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/system_info', methods=['GET'])
@login_required
def get_system_info():
    try:
        print("Starting system info collection...")  # Debug print
        
        # Get the current user's system info
        user = current_user
        
        system_info = {
            'username': user.username,
            'ip_address': user.ip_address,
            'is_online': user.is_online,
            'last_seen': user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else None
        }
        
        print(f"Returning system info: {system_info}")  # Debug print
        return jsonify(system_info)
        
    except Exception as e:
        error_msg = f"Error in get_system_info: {str(e)}"
        print(error_msg)  # Debug print
        import traceback
        print(traceback.format_exc())  # Print full traceback
        return jsonify({
            'error': error_msg,
            'username': current_user.username,
            'ip_address': current_user.ip_address,
            'is_online': current_user.is_online,
            'last_seen': current_user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if current_user.last_seen else None
        }), 500

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

@bp.route('/ping', methods=['POST'])
@login_required
def ping():
    try:
        target_ip = request.json.get('ip_address')
        if not target_ip:
            return jsonify({'error': 'No IP address provided'}), 400

        # Run ping command with a timeout of 2 seconds and 4 packets
        output = subprocess.check_output(['ping', '-n', '4', '-w', '2000', target_ip], 
                                      universal_newlines=True)
        
        # Parse ping results
        lines = output.split('\n')
        stats = lines[-3:-1]  # Get the last few lines containing statistics
        
        return jsonify({
            'success': True,
            'target': target_ip,
            'results': stats
        })
    except subprocess.CalledProcessError:
        return jsonify({
            'success': False,
            'target': target_ip,
            'error': 'Host unreachable'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_default_gateway():
    try:
        # Run ipconfig command and capture output
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        # Look for default gateway
        for line in lines:
            if 'Default Gateway' in line and '.' in line:
                return line.split(':')[-1].strip()
    except:
        pass
    return 'Not found'

def get_mac_address():
    try:
        # Get the MAC address of the first network interface
        interfaces = psutil.net_if_addrs()
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    return addr.address
    except:
        pass
    return 'Not found'
