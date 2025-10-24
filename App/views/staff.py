from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from App.controllers.staff import create_staff, review_hours, delete_student
from App.controllers.student import create_student
from flask_jwt_extended import get_jwt_identity, get_jwt


staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

#api routes
@staff_views.route('/api/staff/create', methods=['POST'])
def create_staff_api():
    data = request.json
    staff = create_staff(data['first_name'], data['last_name'], data['password'])
    return jsonify({'id': staff.id, 'name': f"{staff.first_name} {staff.last_name}"}), 201

@staff_views.route('/api/staff/<int:staff_id>/review_hours', methods=['POST'])
@jwt_required()
def review_hours_api(staff_id):

    
    claims = get_jwt()
    if claims.get('type') != 'staff':
        return jsonify({'message': 'Only staff can access this endpoint'}), 403

    data = request.json
    required = ('password', 'student_id', 'request_index', 'action')
    if not all(k in data for k in required):
        return jsonify({'message': 'Missing required fields'}), 400
    
    record = review_hours(staff_id, data['password'], data['student_id'], data['request_index'], data['action'])
    if not record:
        return jsonify({'message': 'Invalid request'}), 404
    return jsonify({'message': f"{record.status} hours for request index {data['request_index']}"}), 200

@staff_views.route('/api/staff/<int:staff_id>/delete_student', methods=['DELETE'])
@jwt_required()
def delete_student_api(staff_id):
    claims = get_jwt()
    if claims.get('type') != 'staff':
        return jsonify({'message': 'Only staff can access this endpoint'}), 403

    student_id = request.json.get('student_id')

    student = delete_student(staff_id, student_id)
    if not student:
        return jsonify({'message': 'Invalid staff or student ID'}), 404
    return jsonify({'message': f"Deleted student {student.first_name} {student.last_name}"}), 200

