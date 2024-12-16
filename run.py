from app import create_app, db
from app.models import User
import psutil
from flask import jsonify
from flask_login import login_required

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
