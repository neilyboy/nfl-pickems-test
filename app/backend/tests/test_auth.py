import pytest
import json
from flask_login import current_user
from app import db, User

def test_login_success(client):
    """Test successful login."""
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['is_admin'] is False
    assert data['first_login'] is False

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['success'] is False

def test_admin_login(client):
    """Test admin user login."""
    response = client.post('/api/login', json={
        'username': 'admin',
        'password': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['is_admin'] is True

def test_change_password(client):
    """Test password change functionality."""
    # First login
    client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    
    # Change password
    response = client.post('/api/change_password', json={
        'new_password': 'newpassword123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Try logging in with new password
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

def test_first_login_flag(client, app):
    """Test first login flag behavior."""
    with app.app_context():
        # Create a new user with first_login=True
        user = User(
            username='newuser',
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
    data = json.loads(response.data)
    assert data['first_login'] is True
    
    # Change password
    response = client.post('/api/change_password', json={
        'new_password': 'newpassword123'
    })
    assert response.status_code == 200
    
    # Login again to verify first_login is now False
    response = client.post('/api/login', json={
        'username': 'newuser',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['first_login'] is False
