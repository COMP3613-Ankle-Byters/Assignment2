from flask import Blueprint, render_template, jsonify, request, flash, redirect
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.controllers.auth import login

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

# Page/HTML routes
@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password', 'error')
        return response, 401
    flash('Login successful', 'success')
    set_access_cookies(response, token)
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer)
    flash("Logged out!", 'info')
    unset_jwt_cookies(response)
    return response

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template(
        'message.html',
        title="Identify",
        message=f"You are logged in as {current_user.id} - {current_user.username}"
    )

# API routes
@auth_views.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    token = login(data['username'], data['password'])
    if not token:
        return jsonify({'message': 'Bad username or password'}), 401
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user_api():
    return jsonify({
        'username': current_user.username,
        'id': current_user.id
    })
