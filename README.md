# Network Monitoring System

A comprehensive network monitoring system built with Flask that allows administrators to monitor network devices, manage users, and send alerts in real-time.

## Features

### User Management
- User registration and authentication
- Role-based access control (Admin/User)
- User online/offline status tracking
- Department-based organization

### Network Monitoring
- Real-time network topology visualization
- Device status monitoring
- IP address tracking
- Network tools:
  - IP Information display
  - CIDR Calculator
  - Ping Test functionality
  - Network visualization with interactive graph

### Alert System
- Real-time alerts from admin to users
- Unread alerts counter
- Mark as read functionality
- Alert history tracking

### Admin Features
- User management dashboard
- Send alerts to specific users
- Monitor connected devices
- View system-wide statistics

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy
- **Frontend**: 
  - Bootstrap 5
  - Font Awesome icons
  - Vis.js for network visualization
  - JavaScript for real-time updates
- **Authentication**: Flask-Login
- **Network Tools**: Python's netaddr, socket, and psutil libraries

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Monitoring-System.git
cd Monitoring-System
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python create_db.py
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

### First Time Setup
1. Register an admin account
2. Log in with admin credentials
3. Start adding users and managing the network

### For Administrators
- Access the admin dashboard at `/admin`
- Manage users through the user management interface
- Send alerts to specific users
- Monitor network topology and device status

### For Users
- View network status and personal device information
- Receive and manage alerts
- Use network tools (CIDR calculator, ping test)
- View network topology

## Project Structure

```
Monitoring-System/
├── app/
│   ├── admin/             # Admin routes and views
│   ├── auth/              # Authentication routes
│   ├── main/             # Main application routes
│   ├── static/           # Static files (CSS, JS)
│   ├── templates/        # HTML templates
│   └── models.py         # Database models
├── migrations/           # Database migrations
├── venv/                # Virtual environment
├── config.py            # Configuration file
├── create_db.py         # Database initialization
├── requirements.txt     # Project dependencies
└── run.py              # Application entry point
```

## Security Features

- Password hashing
- Session management
- CSRF protection
- Role-based access control
- Secure alert system

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework and its extensions
- Bootstrap for the UI components
- Vis.js for network visualization
- Font Awesome for icons
