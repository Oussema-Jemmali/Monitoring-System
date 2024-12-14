from app import create_app, db
from app.models import User, Device, MonitoringResult

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Device': Device,
        'MonitoringResult': MonitoringResult
    }

if __name__ == '__main__':
    app.run(debug=True)
