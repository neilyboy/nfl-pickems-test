from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import os
from app.utils import setup_logging, handle_error, DatabaseManager

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize logging
logger = setup_logging()

# Register error handler
app.register_error_handler(Exception, handle_error)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_this_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../../data/nfl_pickems.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize database manager
db_manager = DatabaseManager(app)

# Import models after db initialization to avoid circular imports
from app.models import User, Game, Pick

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def update_games():
    """Update games from ESPN API."""
    try:
        from app.espn_api import ESPNAPI
        espn_api = ESPNAPI()
        current_week = espn_api.get_current_week()
        games = espn_api.get_games(current_week)
        
        for game_data in games:
            game = Game.query.filter_by(espn_id=game_data['espn_id']).first()
            if not game:
                game = Game(espn_id=game_data['espn_id'])
                db.session.add(game)
            
            game.week = current_week
            game.home_team = game_data['home_team']
            game.away_team = game_data['away_team']
            game.start_time = game_data['start_time']
            
            if game_data['is_finished']:
                game.final_score_home = game_data['home_score']
                game.final_score_away = game_data['away_score']
                game.winner = game_data['home_team'] if game_data['home_score'] > game_data['away_score'] else game_data['away_team']
        
        db.session.commit()
        logger.info(f"Successfully updated games for week {current_week}")
        
    except Exception as e:
        logger.error(f"Error updating games: {str(e)}")
        db.session.rollback()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_games, trigger="interval", minutes=10)
scheduler.start()

# Import routes after everything is initialized
from app import routes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
