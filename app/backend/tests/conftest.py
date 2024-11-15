import pytest
from app import app as flask_app
from app import db, User, Game, Pick
from datetime import datetime, timedelta

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Configure app for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    # Push an application context
    ctx = flask_app.app_context()
    ctx.push()

    # Create tables and populate test data
    db.create_all()
    _populate_test_data()
    db.session.commit()

    yield flask_app

    # Cleanup after test
    db.session.remove()
    db.drop_all()
    ctx.pop()

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
    admin = User(username='admin', email='admin@test.com', is_admin=True)
    admin.set_password('admin_password')
    db.session.add(admin)

    user = User(username='testuser', email='test@test.com', is_admin=False)
    user.set_password('test_password')
    db.session.add(user)

    # Create test games
    game1 = Game(
        espn_id='401547417',
        home_team='KC',
        away_team='DET',
        start_time=datetime.utcnow() + timedelta(days=1),
        week=1,
        season=2023,
        home_score=0,
        away_score=0,
        status='scheduled'
    )
    db.session.add(game1)

    game2 = Game(
        espn_id='401547418',
        home_team='NYG',
        away_team='DAL',
        start_time=datetime.utcnow() - timedelta(hours=2),
        week=1,
        season=2023,
        home_score=0,
        away_score=0,
        status='in_progress'
    )
    db.session.add(game2)

    # Create test picks
    pick1 = Pick(
        user_id=2,  # testuser's ID
        game_id=1,  # game1's ID
        pick='KC',
        points=None,
        week=1,
        season=2023
    )
    db.session.add(pick1)

    db.session.commit()
