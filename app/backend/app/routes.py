from flask import jsonify, request, send_file
from flask_login import login_required, current_user, login_user, logout_user
from app import app, db, bcrypt, User, Game, Pick
from datetime import datetime, timedelta
import json
from sqlalchemy import case, func
from app.utils import require_admin
from app import db_manager

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({
            'success': True,
            'is_admin': user.is_admin,
            'first_login': user.first_login
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_user.password_hash = bcrypt.generate_password_hash(data['new_password'])
    current_user.first_login = False
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/picks', methods=['GET', 'POST'])
@login_required
def picks():
    if request.method == 'POST':
        data = request.get_json()
        week = data['week']
        
        # Check if picks can be modified
        first_game = Game.query.filter_by(week=week).order_by(Game.start_time).first()
        if first_game and datetime.utcnow() > first_game.start_time - timedelta(hours=2):
            if not current_user.is_admin:
                return jsonify({'success': False, 'message': 'Picks are locked'}), 403

        # Process picks
        for pick in data['picks']:
            game_pick = Pick.query.filter_by(
                user_id=current_user.id,
                game_id=pick['game_id']
            ).first()
            
            if not game_pick:
                game_pick = Pick(
                    user_id=current_user.id,
                    game_id=pick['game_id'],
                    week=week
                )
                db.session.add(game_pick)
            
            game_pick.picked_team = pick['team']
            if 'mnf_total_points' in pick:
                game_pick.mnf_total_points = pick['mnf_total_points']
        
        db.session.commit()
        return jsonify({'success': True})

    # GET request
    week = request.args.get('week', type=int)
    picks = Pick.query.filter_by(user_id=current_user.id, week=week).all()
    return jsonify({
        'picks': [{
            'game_id': pick.game_id,
            'picked_team': pick.picked_team,
            'mnf_total_points': pick.mnf_total_points
        } for pick in picks]
    })

@app.route('/api/admin/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@require_admin
def manage_users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            } for user in users]
        })

    if request.method == 'POST':
        data = request.get_json()
        new_user = User(
            username=data['username'],
            password_hash=bcrypt.generate_password_hash('password'),
            is_admin=data.get('is_admin', False)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'id': new_user.id})

    if request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(data['id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if 'username' in data:
            user.username = data['username']
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'password' in data:
            user.password_hash = bcrypt.generate_password_hash(data['password'])
            user.first_login = True
        
        db.session.commit()
        return jsonify({'success': True})

    if request.method == 'DELETE':
        user = User.query.get(request.args.get('id', type=int))
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/admin/backup', methods=['POST'])
@login_required
@require_admin
def create_backup():
    try:
        backup_path = db_manager.create_backup()
        return jsonify({
            'success': True,
            'backup_path': backup_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/backup/restore', methods=['POST'])
@login_required
@require_admin
def restore_backup():
    data = request.get_json()
    backup_path = data.get('backup_path')
    
    if not backup_path:
        return jsonify({
            'success': False,
            'message': 'Backup path not provided'
        }), 400
    
    try:
        db_manager.restore_backup(backup_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/backups', methods=['GET'])
@login_required
@require_admin
def list_backups():
    try:
        backups = db_manager.list_backups()
        return jsonify({
            'success': True,
            'backups': backups
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    week = request.args.get('week', type=int)
    
    # Get all picks for the week
    picks_query = db.session.query(
        Pick.user_id,
        func.count(case([(Pick.picked_team == Game.winner, 1)])).label('correct_picks'),
        func.count(Pick.id).label('total_picks')
    ).join(Game).filter(Pick.week == week)
    
    if week is None:
        picks_query = picks_query.group_by(Pick.user_id)
    else:
        picks_query = picks_query.filter(Pick.week == week).group_by(Pick.user_id)
    
    picks_results = picks_query.all()
    
    # Calculate accuracy and create leaderboard
    leaderboard = []
    for user_id, correct_picks, total_picks in picks_results:
        user = User.query.get(user_id)
        accuracy = (correct_picks / total_picks * 100) if total_picks > 0 else 0
        leaderboard.append({
            'username': user.username,
            'correct_picks': correct_picks,
            'total_picks': total_picks,
            'accuracy': round(accuracy, 2)
        })
    
    # Sort by correct picks (descending) and username (ascending)
    leaderboard.sort(key=lambda x: (-x['correct_picks'], x['username']))
    
    return jsonify({'leaderboard': leaderboard})

@app.route('/api/stats', methods=['GET'])
@login_required
def stats():
    user_id = request.args.get('user_id', type=int) or current_user.id
    
    # Get user's picks
    picks_query = db.session.query(
        Pick.week,
        func.count(case([(Pick.picked_team == Game.winner, 1)])).label('correct_picks'),
        func.count(Pick.id).label('total_picks')
    ).join(Game).filter(Pick.user_id == user_id).group_by(Pick.week)
    
    picks_results = picks_query.all()
    
    # Calculate weekly and overall stats
    weekly_stats = []
    total_correct = 0
    total_picks = 0
    
    for week, correct_picks, total_week_picks in picks_results:
        accuracy = (correct_picks / total_week_picks * 100) if total_week_picks > 0 else 0
        weekly_stats.append({
            'week': week,
            'correct_picks': correct_picks,
            'total_picks': total_week_picks,
            'accuracy': round(accuracy, 2)
        })
        total_correct += correct_picks
        total_picks += total_week_picks
    
    # Calculate overall accuracy
    overall_accuracy = (total_correct / total_picks * 100) if total_picks > 0 else 0
    
    return jsonify({
        'weekly_stats': weekly_stats,
        'overall_stats': {
            'correct_picks': total_correct,
            'total_picks': total_picks,
            'accuracy': round(overall_accuracy, 2)
        }
    })
