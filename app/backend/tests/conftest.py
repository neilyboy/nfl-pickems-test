import os
import sys
import pytest
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_login import login_user

# Add the app directory to the Python path
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, app_path)

# Set test environment variables
os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite://'  # Force in-memory database

# Import the app after setting environment variables
from app import app as flask_app, db, bcrypt
from app.models import User, Game, Pick

@pytest.fixture(scope='session', autouse=True)
def app_context():
    """Create an application context for the entire test session."""
    # Configure app for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key',
        'LOGIN_DISABLED': False
    })

    # Push an application context
    ctx = flask_app.app_context()
    ctx.push()
    
    yield flask_app
    
    ctx.pop()

@pytest.fixture(scope='function')
def app(app_context):
    """Set up a clean database for each test."""
    # Create tables
    db.create_all()
    
    # Add test data
    _populate_test_data()
    
    yield flask_app
    
    # Clean up
    db.session.remove()
    db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client

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
    admin.password = 'admin_password'
    db.session.add(admin)

    user = User(
        username='testuser',
        email='test@test.com',
        is_admin=False,
        first_login=False
    )
    user.password = 'test_password'
    db.session.add(user)

    try:
        db.session.commit()  # Commit users first to get their IDs
    except:
        db.session.rollback()
        raise

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
        winner=None,
        is_mnf=True
    )
    db.session.add(game2)

    try:
        db.session.commit()  # Commit games to get their IDs
    except:
        db.session.rollback()
        raise

    # Create test picks
    pick1 = Pick(
        user_id=user.id,
        game_id=game1.id,
        picked_team='KC',
        mnf_total_points=None,
        week=1
    )
    db.session.add(pick1)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
