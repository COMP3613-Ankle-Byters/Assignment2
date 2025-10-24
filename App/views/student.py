from flask import Blueprint, request, jsonify, flash, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from App.controllers.student import create_student, view_profile, request_hours
from App.models import Student

student_views = Blueprint('student_views', __name__, template_folder='../templates')

# API routes
@student_views.route('/api/student/create', methods=['POST'])
def create_student_api():
    data = request.json
    student = create_student(data['first_name'], data['last_name'], data['password'])
    return jsonify({'id': student.id, 'name': f"{student.first_name} {student.last_name}"}), 201

@student_views.route('/api/student/<int:student_id>/request_hours', methods=['POST'])
@jwt_required()
def student_request_hours_api(student_id):
    identity = get_jwt_identity()
    claims = get_jwt()
    try:
        token_user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({'message': 'Invalid token identity'}), 401

    if token_user_id != student_id or claims.get('type') != 'student':
        return jsonify({'message': 'Unauthorized access'}), 403
    
    data = request.get_json()
    hours = data.get('hours')
    activity = data.get('activity')
    if hours is None or activity is None:
        return jsonify({'message': 'Missing hours or activity'}), 400
    
    record = request_hours(student_id, hours, activity)
    if not record:
        return jsonify({'message': 'Invalid student ID or could not create record'}), 404

    return jsonify({'message': f"Request submitted: {record.hours}h for {record.activity}"}), 201

@student_views.route('/api/student/<int:student_id>', methods=['GET'])
@jwt_required()
def view_student_profile(student_id):
    identity = get_jwt_identity()      
    claims = get_jwt()
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'Student not found'}), 404

    try:
        token_user_id = int(identity)
    except (TypeError, ValueError):
        return jsonify({'message': 'Invalid token identity'}), 401

    if token_user_id != student_id or claims.get('type') != 'student':
        return jsonify({'message': 'Unauthorized access'}), 403

    profile = view_profile(student_id)
    if not profile:
        return jsonify({'message': 'Invalid credentials'}), 401
    return jsonify(profile)
