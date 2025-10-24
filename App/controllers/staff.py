from App.database import db
from App.models.staff import Staff
from App.models.student import Student
from App.models.hours_completed import HoursCompleted
from App.models.accolade import Accolade

def create_staff(first_name, last_name, password):
    staff = Staff(first_name=first_name, last_name=last_name, password=password)
    db.session.add(staff)
    db.session.commit()
    return staff

def review_hours(staff_id, password, student_id, request_index, confirm=True):
    staff = Staff.query.get(staff_id)
    if not staff or not staff.check_password(password):
        print("Invalid staff credentials.")
        return None


    if student_id is None:
        student_id = int(input("Enter student ID to review: "))
    if request_index is None or action is None:
        student = Student.query.get(student_id)
        if not student:
            print("Invalid student ID.")
            return None
        pending = HoursCompleted.query.filter_by(student_id=student.id, status="pending").all()
        if not pending:
            print(f"No pending requests for {student.first_name} {student.last_name}.")
            return None
        print(f"\nPending requests for {student.first_name} {student.last_name}:")
        for i, record in enumerate(pending):
            print(f"[Index: {i}] {record.hours}h - {record.activity}")
        if request_index is None:
            request_index = int(input("Enter the request index to review: "))
        if action is None:
            action = input("Do you want to confirm or deny? (c/d): ").lower()

    
    
    student = Student.query.get(student_id)
    if not staff or not student:
        return None

    pending = HoursCompleted.query.filter_by(student_id=student.id, status="pending").all()
    if request_index < 0 or request_index >= len(pending):
        return None

    record = pending[request_index]
    if action == "c":
        record.status = "confirmed"
        record.staff_id = staff.id
        db.session.commit()
        print(f"Confirmed {record.hours}h - {record.activity} for {student.first_name} {student.last_name}.")
    elif action == "d":
        record.status = "denied"
        record.staff_id = staff.id
        db.session.commit()
        print(f"Denied {record.hours}h - {record.activity} for {student.first_name} {student.last_name}.")
    else:
        print("Invalid action. Please enter 'c' or 'd'.")
        return None
    
    return record

def delete_student(staff_id, student_id):
    staff = Staff.query.get(staff_id)
    student = Student.query.get(student_id)
    if not staff or not student:
        return None

    HoursCompleted.query.filter_by(student_id=student.id).delete()
    Accolade.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    return student

