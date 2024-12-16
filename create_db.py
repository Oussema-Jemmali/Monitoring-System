from app import db, create_app
from app.models import User
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

            # Commit all changes
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()
