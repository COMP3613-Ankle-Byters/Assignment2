from flask_jwt_extended import create_access_token
from App.models import db, Student, Staff
from .student import create_student
from .staff import create_staff
from functools import wraps

def login(first_name, last_name, password):
    user = Student.query.filter_by(first_name=first_name).first()
    if not user:
        user = Staff.query.filter_by(last_name=last_name).first()

    if not user or not user.check_password(password):
        return None

    token = create_access_token(identity={
        "id": user.id,
        "type": "student" if isinstance(user, Student) else "staff"
    })
    return token


def initialize():
    db.drop_all()
    db.create_all()
    staff = create_staff("Alice", "Smith", "staffpass")
    student = create_student("Bob", "Brown", "studentpass")
    print(f"Created sample users: {staff.first_name}, {student.first_name}")
