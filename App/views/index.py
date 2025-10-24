from flask import Blueprint, jsonify, render_template
from App.database import db
from App.controllers.staff import create_staff
from App.controllers.student import create_student
from App.models.hours_completed import HoursCompleted
from App.models.student import Student
from App.models.staff import Staff

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()

    #seeds
    s1 = create_staff("Locke", "Smith", "smithpass")
    s2 = create_staff("Lorry", "Jones", "jonespass")


    st1 = create_student("Alice", "Brown", "alicepass")
    st2 = create_student("Bob", "Green", "bobpass")
    st3 = create_student("Jane", "Doe", "janepass")
    st4 = create_student("Joe", "Mama", "jopass")


    sample_hours = [
        (st1.id, 14, "Beach Cleanup", "confirmed"),
        (st1.id, 12, "Tree Planting", "confirmed"),
        (st1.id, 11, "Community Tutoring", "confirmed"),
        (st1.id, 8, "Library Assistance", "confirmed"),
        (st1.id, 7, "Food Drive", "confirmed"),
        (st2.id, 8, "Tree Planting", "confirmed"),
        (st2.id, 10, "Food Drive", "confirmed"),
        (st2.id, 8, "Library Assistance", "confirmed"),
        (st3.id, 5, "Food Drive", "confirmed"),
        (st3.id, 6, "Library Assistance", "confirmed"),
        (st4.id, 2, "Tutoring", "confirmed"),
        (st1.id, 3, "Community Service", "pending")  #unconfirmed hours for testing 
    ]

    for sid, hrs, act, status in sample_hours:
        record = HoursCompleted(student_id=sid, hours=hrs, activity=act, status=status)
        db.session.add(record)

    db.session.commit()
    return jsonify("Database initialized successfully!")

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@index_views.route('/api/list_students', methods=['GET'])
def list_students_api():
    students = Student.query.all()
    student_list = [{'id': s.id, 'first_name': s.first_name, 'last_name': s.last_name} for s in students]
    return jsonify(student_list)

@index_views.route('/api/list_staff', methods=['GET'])
def list_staff_api():
    staffs = Staff.query.all()
    staff_list = [{'id': s.id, 'first_name': s.first_name, 'last_name': s.last_name} for s in staffs]
    return jsonify(staff_list)
