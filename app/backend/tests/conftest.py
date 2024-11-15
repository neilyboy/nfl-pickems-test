import pytest
import os
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
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key'
    })

    return flask_app

@pytest.fixture(scope='function')
def _db(app):
    """Create a database object."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app, _db):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def _init_database(app, _db):
    """Initialize database with test data."""
    with app.app_context():
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

        db.session.commit()

        # Create test picks
        pick1 = Pick(
            user_id=2,  # testuser's ID
            game_id=1,  # game1's ID
            picked_team='KC',
            mnf_total_points=None,
            week=1
        )
        db.session.add(pick1)

        db.session.commit()
