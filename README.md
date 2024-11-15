# NFL Pick'em Application

A web-based NFL Pick'em pool management system that allows users to make weekly game picks and compete with others in their office pool.

## Features

- User authentication with admin and limited user roles
- Weekly NFL game picks with automatic data updates from ESPN
- Leaderboard tracking with weekly and season statistics
- Monday Night Football total points tiebreaker
- Mobile-first responsive design
- Automated game data updates
- Backup and restore functionality

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository
2. Navigate to the project directory
3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Default Credentials

- Admin:
  - Username: admin
  - Password: admin
- New Users:
  - Default Password: password
  - Users will be prompted to change password on first login

## Development

The application uses:
- Backend: Python/Flask
- Frontend: React
- Database: SQLite
- Container: Docker

## API Endpoints

- `/api/login` - User authentication
- `/api/picks` - Manage weekly picks
- `/api/leaderboard` - View standings
- `/api/stats` - View detailed statistics
- `/api/admin/*` - Admin-only endpoints

## Data Updates

The application automatically fetches game data from ESPN's API every 10 minutes to keep scores and game information current.

## Security Notes

- Change the default admin password immediately after deployment
- All passwords are hashed using bcrypt
- Picks are locked 2 hours before Thursday night games
- Only admins can modify locked picks
