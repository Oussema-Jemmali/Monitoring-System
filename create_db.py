from app import db, create_app
from app.models import User, Device, MonitoringResult, Alert
from datetime import datetime
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Delete existing database file
        if os.path.exists('app.db'):
            os.remove('app.db')
            
        # Create all tables
        db.drop_all()
        db.create_all()
        
        try:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                ip_address='192.168.1.1',
                subnet_mask='255.255.255.0',
                department='IT',
                role='Administrator',
                is_admin=True,
                is_online=True,
                last_seen=datetime.utcnow()
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.flush()

            # Create regular users
            user1 = User(
                username='user1',
                email='user1@example.com',
                ip_address='192.168.1.10',
                subnet_mask='255.255.255.0',
                department='Sales',
                role='User',
                is_online=True,
                last_seen=datetime.utcnow()
            )
            user1.set_password('user1')
            db.session.add(user1)
            db.session.flush()

            user2 = User(
                username='user2',
                email='user2@example.com',
                ip_address='192.168.1.20',
                subnet_mask='255.255.255.0',
                department='Marketing',
                role='User',
                is_online=False,
                last_seen=datetime.utcnow()
            )
            user2.set_password('user2')
            db.session.add(user2)
            db.session.flush()

            # Create some devices
            device1 = Device(
                hostname='laptop1',
                ip_address='192.168.1.100',
                mac_address='00:11:22:33:44:55',
                device_type='Laptop',
                status='UP',
                user_id=user1.id
            )
            db.session.add(device1)
            db.session.flush()

            device2 = Device(
                hostname='desktop1',
                ip_address='192.168.1.101',
                mac_address='00:11:22:33:44:66',
                device_type='Desktop',
                status='DOWN',
                user_id=user2.id
            )
            db.session.add(device2)
            db.session.flush()

            # Create some alerts
            alert1 = Alert(
                device_id=device1.id,
                user_id=user1.id,
                alert_type='connection',
                message='Connection lost to device',
                severity='high',
                timestamp=datetime.utcnow()
            )
            db.session.add(alert1)
            db.session.flush()

            alert2 = Alert(
                device_id=device2.id,
                user_id=user2.id,
                alert_type='security',
                message='Unauthorized access attempt',
                severity='critical',
                timestamp=datetime.utcnow()
            )
            db.session.add(alert2)
            
            # Commit all changes
            db.session.commit()
            print("Database created successfully with sample data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating database: {str(e)}")
            raise

if __name__ == '__main__':
    init_db()
