from flask_jwt_extended import create_access_token
from App.models import db, Student, Staff
from .student import create_student
from .staff import create_staff
from functools import wraps


def login(id, password):
    str_id = str(id)
   
    if str_id.startswith("816"):
        suffix = str_id[3:]  # → "001"
        student_id = int(suffix)
        user = Student.query.get(student_id)
    elif str_id.startswith("999"):
        suffix = str_id[3:]  # → "001"
        staff_id = int(suffix)
        user = Staff.query.get(staff_id)
    
    if not user or not user.check_password(password):
        return None
    token = create_access_token(
    identity=str(user.id),
    additional_claims={"type": "student" if isinstance(user, Student) else "staff"}
    )
    return token


def initialize():
    db.drop_all()
    db.create_all()
    staff = create_staff("Alice", "Smith", "staffpass")
    student = create_student("Bob", "Brown", "studentpass")
    print(f"Created sample users: {staff.first_name}, {student.first_name}")
