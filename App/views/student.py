from flask import Blueprint, request, jsonify, flash, redirect
from flask_jwt_extended import jwt_required
from App.controllers.student import create_student, view_profile, request_hours

student_views = Blueprint('student_views', __name__, template_folder='../templates')

# API routes
@student_views.route('/api/student/create', methods=['POST'])
def create_student_api():
    data = request.json
    student = create_student(data['first_name'], data['last_name'], data['password'])
    return jsonify({'id': student.id, 'name': f"{student.first_name} {student.last_name}"}), 201

@student_views.route('/api/student/<int:student_id>', methods=['GET'])
def view_student_profile(student_id):
    password = request.args.get('password')
    profile = view_profile(student_id, password)
    if not profile:
        return jsonify({'message': 'Invalid credentials'}), 401
    return jsonify(profile)

@student_views.route('/api/student/<int:student_id>/request_hours', methods=['POST'])
def student_request_hours_api(student_id):
    data = request.json
    record = request_hours(student_id, data['hours'], data['activity'])
    if not record:
        return jsonify({'message': 'Invalid student ID'}), 404
    return jsonify({'message': f"Request submitted: {record.hours}h for {record.activity}"}), 201
