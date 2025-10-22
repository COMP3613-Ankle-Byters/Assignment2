import click
from flask.cli import AppGroup
from App.main import create_app
from App.database import db, get_migrate

from App.models.user import User
from App.models.student import Student
from App.models.staff import Staff
from App.models.hours_completed import HoursCompleted
from App.models.accolade import Accolade
from App.controllers.student import create_student, request_hours, view_profile
from App.controllers.staff import create_staff, review_hours, delete_student
from App.controllers.leaderboard import get_leaderboard
from App.models import Student, Staff, HoursCompleted, Accolade

app = create_app()
migrate = get_migrate(app)


# ================================
# Init Command
# ================================
@app.cli.command("init", help="Creates and initializes the database with sample data")
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
        (st1.id, 14, "Beach Cleanup"),
        (st1.id, 12, "Tree Planting"),
        (st1.id, 11, "Community Tutoring"),
        (st1.id, 8, "Library Assistance"),
        (st1.id, 7, "Food Drive"),
        (st2.id, 8, "Tree Planting"),
        (st2.id, 10, "Food Drive"),
        (st2.id, 8, "Library Assistance"),
        (st3.id, 5, "Food Drive"),
        (st3.id, 6, "Library Assistance"),
        (st4.id, 2, "Tutoring")
    ]

    for sid, hrs, act in sample_hours:
        record = HoursCompleted(student_id=sid, hours=hrs, activity=act, status="confirmed")
        db.session.add(record)

    db.session.commit()
    print("Database initialized successfully!")


@app.cli.command("list_students", help="List all students")
def list_students():
    students = Student.query.all()
    print("___________Students___________\n")

    for s in students:
        print(f"[{s.id}] {s.first_name} {s.last_name}")

    print("\n_______________________________")



@app.cli.command("list_staff", help="List all staff")
def list_staff_cli():
    staff_members = Staff.query.all()
    if not staff_members:
        print("No staff found.")
        return

    print("______________Staff______________\n")

    for s in staff_members:

        print(f"[{s.id}] {s.first_name} {s.last_name}")

    print("\n_________________________________")



# ================================
# Student CLI
# ================================
student_cli = AppGroup("student", help="Student commands")


@student_cli.command("create", help="Create a student account")
def student_create():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    password = input("Enter password: ")
    student = create_student(first_name, last_name, password)
    print(f"Student created: {student.first_name} {student.last_name} (ID: {student.id})")


@student_cli.command("profile", help="View student profile")
def student_profile():
    student_id = int(input("Enter student ID: "))
    password = input("Enter password: ")
    profile = view_profile(student_id, password)
    if not profile:
        print("Invalid student credentials.")
        return

    print(f"\n_____{profile['first_name']} {profile['last_name']}'s Profile______")
    if profile['pending_hours']:
        print("\nPending Hours:")
        for act, hrs in profile['pending_hours']:
            print(f"- {act}: {hrs} hours")
    else:
        print("\nNo pending hours.")

    if profile['confirmed_hours']:
        print("\nConfirmed Hours:")
        for act, hrs in profile['confirmed_hours']:
            print(f"- {act}: {hrs} hours")
    else:
        print("\nNo confirmed hours.")

    print(f"\nTotal Confirmed Hours: {profile['total_hours']}")
    print(f"Accolade: {profile['accolade']} (Awarded on: {profile['date_awarded']})")
    print(f"Leaderboard Rank: #{profile['rank']}")


@student_cli.command("request_hours", help="Request volunteer hours")
def student_request_hours():
    student_id = int(input("Enter student ID: "))
    hours = int(input("Enter number of hours: "))
    activity = input("Enter activity: ")
    record = request_hours(student_id, hours, activity)
    if record:
        print(f"Request submitted: {hours} hours for {activity}")
    else:
        print("Invalid student ID.")


app.cli.add_command(student_cli)


# ================================
# Staff CLI
# ================================

staff_cli = AppGroup("staff", help="Staff commands")


@staff_cli.command("create", help="Create staff account")
def staff_create():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    password = input("Enter password: ")
    staff = create_staff(first_name, last_name, password)
    print(f"Staff created: {staff.first_name} {staff.last_name} (ID: {staff.id})")


@staff_cli.command("review_hours", help="Confirm or deny a student's pending hours (staff only)")
def review_hours_cli():
    staff_id = int(input("Enter staff ID: "))
    password = input("Enter your password: ")

    staff = Staff.query.get(staff_id)
    if not staff or not staff.check_password(password):
        print("Invalid staff credentials.")
        return

    student_id = int(input("Enter student ID to review: "))
    student = Student.query.get(student_id)
    if not student:
        print("Invalid student ID.")
        return

    pending = HoursCompleted.query.filter_by(student_id=student.id, status="pending").all()
    if not pending:
        print(f"No pending requests for {student.first_name} {student.last_name}.")
        return

    print(f"\nPending requests for {student.first_name} {student.last_name}:")
    for record in pending:
        print(f"[Request ID: {record.id}] {record.hours}h - {record.activity}")

    hour_request_id = int(input("Enter the Hour Request ID to review: "))
    record = HoursCompleted.query.filter_by(id=hour_request_id, student_id=student.id, status="pending").first()

    if not record:
        print("Invalid Hour Request ID.")
        return

    action = input("Do you want to confirm or deny? (c/d): ").lower()
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


@staff_cli.command("delete_student", help="Delete a student")
def staff_delete_student():
    staff_id = int(input("Enter your staff ID: "))
    password = input("Enter your password: ")

    staff = Staff.query.get(staff_id)
    if not staff or not staff.check_password(password):
        print("Invalid staff credentials.")
        return

    student_id = int(input("Enter student ID to delete: "))
    student = delete_student(staff_id, student_id)
    if student:
        print(f"Deleted student: {student.first_name} {student.last_name}")
    else:
        print("Invalid staff or student ID.")


app.cli.add_command(staff_cli)


# ================================
# Leaderboard
# ================================

@app.cli.command("leaderboard", help="View student leaderboard")
def leaderboard():
    lb = get_leaderboard()
    print("\n_____ Leaderboard_____")
    for entry in lb:
        print(f"{entry['rank']}. {entry['name']} [{entry['accolade']}] - {entry['total_hours']} hours")
    print()
