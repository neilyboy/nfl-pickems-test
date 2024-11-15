import pytest
import json
from flask_login import current_user
from app.models import User, db

def test_login_success(client):
    """Test successful login."""
    with client:
        response = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'test_password'
        })
        assert response.status_code == 200
        assert current_user.is_authenticated
        assert current_user.username == 'testuser'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_admin_login(client):
    """Test admin user login."""
    with client:
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        assert response.status_code == 200
        assert current_user.is_authenticated
        assert current_user.is_admin

def test_change_password(client, app):
    """Test password change functionality."""
    with client:
        # First login
        login_response = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'test_password'
        })
        assert login_response.status_code == 200

        # Change password
        response = client.post('/api/change_password', json={
            'new_password': 'newpassword123'
        })
        assert response.status_code == 200

        # Try logging in with new password
        client.get('/api/logout')  # Logout first
        new_login = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'newpassword123'
        })
        assert new_login.status_code == 200

def test_first_login_flag(client, app):
    """Test first login flag behavior."""
    with app.app_context():
        # Create a new user with first_login=True
        user = User(
            username='newuser',
            email='newuser@test.com',
            password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5IMwxmsi6/Hu',
            first_login=True
        )
        db.session.add(user)
        db.session.commit()

        # Login with new user
        response = client.post('/api/login', json={
            'username': 'newuser',
            'password': 'password'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['first_login'] == True

        # Change password to clear first login flag
        client.post('/api/change_password', json={
            'new_password': 'newpassword123'
        })

        # Verify first_login is now False
        user = User.query.filter_by(username='newuser').first()
        assert user.first_login == False
