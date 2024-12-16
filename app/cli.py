import click
from flask.cli import with_appcontext
from app import db
from app.models import User

@click.command('create-test-data')
@with_appcontext
def create_test_data():
    """Create test users."""
    # Create admin user
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('admin')
    db.session.add(admin)

    # Create regular user
    user = User(username='user', email='user@example.com')
    user.set_password('user')
    db.session.add(user)

    db.session.commit()
    print('Test data created successfully.')
