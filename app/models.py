from datetime import datetime
from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import ipaddress

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    ip_address = db.Column(db.String(15))
    subnet_mask = db.Column(db.String(15))
    department = db.Column(db.String(64))
    role = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    devices = db.relationship('Device', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_network_info(self):
        if self.ip_address and self.subnet_mask:
            try:
                network = ipaddress.IPv4Network(f"{self.ip_address}/{self.subnet_mask}", strict=False)
                return {
                    'network_address': str(network.network_address),
                    'broadcast_address': str(network.broadcast_address),
                    'netmask': str(network.netmask),
                    'cidr': network.prefixlen,
                    'num_hosts': network.num_addresses - 2
                }
            except ValueError:
                return None
        return None

    def to_dict(self):
        network_info = self.get_network_info()
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'subnet_mask': self.subnet_mask,
            'network_info': network_info,
            'department': self.department,
            'role': self.role,
            'is_online': self.is_online,
            'last_seen': self.last_seen.strftime('%Y-%m-%d %H:%M:%S') if self.last_seen else None
        }

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    mac_address = db.Column(db.String(17))
    device_type = db.Column(db.String(32))
    status = db.Column(db.String(16), default='unknown')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    monitoring_results = db.relationship('MonitoringResult', backref='device', lazy='dynamic')

    def __repr__(self):
        return f'<Device {self.hostname}>'

class MonitoringResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MonitoringResult {self.device_id} {self.status}>'
