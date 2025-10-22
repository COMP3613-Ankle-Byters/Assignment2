from flask import Blueprint, request, jsonify
from App.controllers.staff import create_staff, review_hours, delete_student

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# API routes
@staff_views.route('/api/staff/create', methods=['POST'])
def create_staff_api():
    data = request.json
    staff = create_staff(data['first_name'], data['last_name'], data['password'])
    return jsonify({'id': staff.id, 'name': f"{staff.first_name} {staff.last_name}"}), 201

@staff_views.route('/api/staff/<int:staff_id>/review_hours', methods=['POST'])
def review_hours_api(staff_id):
    data = request.json
    record = review_hours(
        staff_id,
        data['student_id'],
        data['request_index'],
        confirm=data.get('confirm', True)
    )
    if not record:
        return jsonify({'message': 'Invalid request'}), 404
    return jsonify({'message': f"{record.status} hours for request ID {record.id}"}), 200

@staff_views.route('/api/staff/<int:staff_id>/delete_student', methods=['DELETE'])
def delete_student_api(staff_id):
    student_id = request.json.get('student_id')
    student = delete_student(staff_id, student_id)
    if not student:
        return jsonify({'message': 'Invalid staff or student ID'}), 404
    return jsonify({'message': f"Deleted student {student.first_name} {student.last_name}"}), 200
