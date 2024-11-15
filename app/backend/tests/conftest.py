import os
import sys
import pytest
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app after setting up the path
from app import app as flask_app, db
from app.models import User, Game, Pick

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Configure app for testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',  # Pure in-memory database
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key'
    }

    # Update app config
    flask_app.config.update(test_config)

    # Create application context
    with flask_app.app_context():
        # Create tables
        db.create_all()
        
        # Add test data
        _populate_test_data()
        
        yield flask_app
        
        # Cleanup
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def _populate_test_data():
    """Populate test data."""
    # Create test users
    admin = User(
        username='admin',
        email='admin@test.com',
        is_admin=True,
        first_login=False
    )
    admin.set_password('admin_password')
    db.session.add(admin)

    user = User(
        username='testuser',
        email='test@test.com',
        is_admin=False,
        first_login=False
    )
    user.set_password('test_password')
    db.session.add(user)

    db.session.commit()  # Commit users first to get their IDs

    # Create test games
    game1 = Game(
        espn_id='401547417',
        home_team='KC',
        away_team='DET',
        start_time=datetime.utcnow() + timedelta(days=1),
        week=1,
        season=2023,
        final_score_home=0,
        final_score_away=0,
        winner=None
    )
    db.session.add(game1)

    game2 = Game(
        espn_id='401547418',
        home_team='NYG',
        away_team='DAL',
        start_time=datetime.utcnow() - timedelta(hours=2),
        week=1,
        season=2023,
        final_score_home=0,
        final_score_away=0,
        winner=None
    )
    db.session.add(game2)

    db.session.commit()  # Commit games to get their IDs

    # Create test picks
    pick1 = Pick(
        user_id=user.id,  # Use the actual user ID
        game_id=game1.id,  # Use the actual game ID
        picked_team='KC',
        mnf_total_points=None,
        week=1
    )
    db.session.add(pick1)

    db.session.commit()
