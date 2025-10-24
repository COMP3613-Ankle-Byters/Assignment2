from App.database import db
from App.models.student import Student
from App.models.hours_completed import HoursCompleted
from App.models.accolade import Accolade
from App.controllers.accolade import award_accolade
from sqlalchemy import func

def create_student(first_name, last_name, password):
    student = Student(first_name, last_name, password)
    db.session.add(student)
    db.session.commit()
    return student

def request_hours(student_id, hours, activity):
    student = Student.query.get(student_id)
    if not student:
        return None
    record = HoursCompleted(student_id=student.id, hours=hours, activity=activity, status="pending")
    db.session.add(record)
    db.session.commit()
    return record

def view_profile(student_id):
    student = Student.query.get(student_id)
    if not student:
        return None

    pending = [(h.activity, h.hours) for h in HoursCompleted.query.filter_by(student_id=student.id, status="pending")]
    confirmed = [(h.activity, h.hours) for h in HoursCompleted.query.filter_by(student_id=student.id, status="confirmed")]
    total_hours = db.session.query(func.sum(HoursCompleted.hours)).filter_by(student_id=student.id, status="confirmed").scalar() or 0

    award_accolade(student)
    db.session.commit()
    accolade = Accolade.query.filter_by(student_id=student.id).first()
    accolade_level = accolade.accolade_level if accolade else "None"
    date_awarded = accolade.date_rewarded.strftime("%Y-%m-%d") if accolade else "N/A"

    leaderboard = db.session.query(
        Student.id,
        func.coalesce(func.sum(HoursCompleted.hours), 0).label("total_hours")
    ).outerjoin(HoursCompleted, (Student.id==HoursCompleted.student_id) & (HoursCompleted.status=='confirmed'))\
     .group_by(Student.id).order_by(db.desc("total_hours")).all()

    rank = next((i+1 for i, (sid, _) in enumerate(leaderboard) if sid == student.id), "N/A")

    return {
        "first_name": student.first_name,
        "last_name": student.last_name,
        "pending_hours": pending,
        "confirmed_hours": confirmed,
        "total_hours": total_hours,
        "accolade": accolade_level,
        "date_awarded": date_awarded,
        "rank": rank
    }

