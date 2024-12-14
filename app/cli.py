import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Device

@click.command()
@with_appcontext
def create_test_data():
    """Create test users and devices for development."""
    # Create test users
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',
            'is_admin': True,
            'department': 'IT',
            'ip_address': '192.168.1.1',
            'subnet_mask': '255.255.255.0'
        },
        {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'user123',
            'department': 'Sales',
            'ip_address': '192.168.1.2',
            'subnet_mask': '255.255.255.0'
        },
        {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'user123',
            'department': 'Marketing',
            'ip_address': '192.168.1.3',
            'subnet_mask': '255.255.255.0'
        }
    ]

    for user_data in users_data:
        if User.query.filter_by(username=user_data['username']).first() is None:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                department=user_data['department'],
                is_admin=user_data.get('is_admin', False),
                ip_address=user_data['ip_address'],
                subnet_mask=user_data['subnet_mask']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()

    # Create test devices for users
    users = User.query.all()
    for user in users:
        # Add a test device for each user
        if not user.devices.first():
            device = Device(
                hostname=f'{user.username}-pc',
                ip_address=f'192.168.1.{10 + user.id}',
                mac_address=f'00:1A:2B:3C:4D:{user.id:02d}',
                device_type='Workstation',
                status='online',
                user_id=user.id
            )
            db.session.add(device)
    
    db.session.commit()
    click.echo('Test data created successfully!')
