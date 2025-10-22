from flask import Blueprint, jsonify
from App.controllers.leaderboard import get_leaderboard

leaderboard_views = Blueprint('leaderboard_views', __name__)

@leaderboard_views.route('/api/leaderboard', methods=['GET'])
def leaderboard_api():
    lb = get_leaderboard()
    return jsonify(lb)
