# App/controllers/auth.py
from App.models.student import Student
from App.models.staff import Staff
from flask_jwt_extended import create_access_token

def login(username, password):
    """
    Try to login a student or staff using first_name as username.
    Returns JWT token if successful, None otherwise.
    """
    user = Student.query.filter_by(first_name=username).first()
    if not user:
        user = Staff.query.filter_by(first_name=username).first()

    if not user or not user.check_password(password):
        return None

    token = create_access_token(identity={"id": user.id, "type": "student" if isinstance(user, Student) else "staff"})
    return token
