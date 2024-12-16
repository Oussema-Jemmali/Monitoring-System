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

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('alerts_received', lazy='dynamic'))
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('alerts_sent', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': self.sender.username,
            'read': self.read
        }

class SystemInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64))
    os = db.Column(db.String(64))
    cpu = db.Column(db.String(128))
    memory_total = db.Column(db.Float)
    memory_used = db.Column(db.Float)
    disk_total = db.Column(db.Float)
    disk_used = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SystemInfo {self.hostname}>'
