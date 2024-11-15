# NFL Pick'ems Application

A full-stack web application for NFL game predictions and pick'em competitions.

## Features

- User authentication and authorization
- Weekly NFL game picks
- Leaderboard tracking
- Admin dashboard for game management
- Automatic game updates via ESPN API
- Comprehensive logging system

## Technology Stack

- Backend: Python/Flask
- Frontend: React
- Database: SQLite
- Authentication: Flask-Login
- Task Scheduling: APScheduler
- Deployment: Docker

## Prerequisites

- Docker and Docker Compose
- Git
- Make (optional, for using Makefile commands)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
DATABASE_URL=sqlite:///data/nfl_pickems.db
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nfl-pickems.git
cd nfl-pickems
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
flask run
```

## Production Deployment (Ubuntu)

1. Install Docker and Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/nfl-pickems.git
cd nfl-pickems
```

3. Create necessary directories:
```bash
mkdir -p data logs
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your production settings
```

5. Build and start the containers:
```bash
sudo docker-compose up -d --build
```

6. Monitor the logs:
```bash
sudo docker-compose logs -f
```

## Directory Structure

```
nfl-pickems/
├── app/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   └── config/
│   │   │       └── logging_config.py
│   │   └── tests/
│   └── frontend/
├── data/
├── logs/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── requirements.txt
```

## Logging

Logs are stored in the `logs` directory:
- `nfl_pickems.log`: General application logs
- `auth.log`: Authentication-specific logs

Log files are automatically rotated when they reach 10MB, keeping 5 backup files.

## Security Notes

- The application runs with a non-root user in Docker
- All cookies are secure and HTTP-only
- Session protection is set to 'strong'
- Passwords are hashed using bcrypt
- Rate limiting is implemented for authentication attempts

## Maintenance

### Backup Database
```bash
docker-compose exec backend python -c "from app.utils import DatabaseManager; DatabaseManager.create_backup()"
```

### View Logs
```bash
# View application logs
tail -f logs/nfl_pickems.log

# View authentication logs
tail -f logs/auth.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
