import pytest
from App.models import Student , Staff, HoursCompleted, Accolade
from App.database import db, create_db
from App.controllers import view_profile, get_leaderboard, review_hours
from App.main import create_app
from App.controllers.staff import delete_student
from datetime import datetime

'''
   Unit Tests
'''

def test_create_student():
    new_student = Student(first_name="Annita", last_name="Pea", password="password123")
    assert new_student.first_name == "Annita"
    assert new_student.last_name == "Pea"
    assert new_student.password != "password123"
    assert new_student.id == None  # empty before being added to the database

def test_create_staff():
    new_staff = Staff(first_name="Ben", last_name="Dover", password="adminpass")
    assert new_staff.first_name == "Ben"
    assert new_staff.last_name == "Dover"
    assert new_staff.password != "adminpass"
    assert new_staff.id == None  # empty before being added to the database

def test_request_hours():
    hours_record = HoursCompleted(student_id=1, hours=5, activity="Volunteering", status="pending")
    assert hours_record.student_id == 1
    assert hours_record.hours == 5
    assert hours_record.activity == "Volunteering"
    assert hours_record.status == "pending"
    assert hours_record.id == None  


'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class

@pytest.fixture(autouse=True, scope="function")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

def test_view_profile(empty_db):
    with empty_db.application.app_context():
        test_student = Student(first_name="Big", last_name="Guy", password="bigpass")
        db.session.add(test_student)
        db.session.commit()
        
        pending_hours = HoursCompleted(student_id=test_student.id, activity="Volunteering", hours=3, status="pending")
        confirmed_hours = HoursCompleted(student_id=test_student.id, activity="Tutoring", hours=5, status="confirmed")
        db.session.add_all([pending_hours, confirmed_hours])
        db.session.commit()
        
        test_profile = view_profile(test_student.id, "bigpass")
        
        assert test_profile["first_name"] == "Big"
        assert test_profile["last_name"] == "Guy"
        assert test_profile["pending_hours"] == [("Volunteering", 3)]
        assert test_profile["confirmed_hours"] == [("Tutoring", 5)]
        assert test_profile["total_hours"] == 5
        assert test_profile["accolade"] in ["None", "Bronze", "Silver", "Gold"]
        assert test_profile["date_awarded"] == "N/A" or isinstance(test_profile["date_awarded"], str)
        assert test_profile["rank"] == 1 

def test_award_accolade(empty_db):
    with empty_db.application.app_context():
        test_student = Student(first_name="Hoo", last_name="Bo", password="hobopass")
        db.session.add(test_student)
        db.session.commit()
        
        hours_list = [
            HoursCompleted(student_id=test_student.id, activity="Beach Cleanup", hours=10, status="confirmed"),
            HoursCompleted(student_id=test_student.id, activity="Staring at the Sun", hours=15, status="confirmed"),
            HoursCompleted(student_id=test_student.id, activity="Walk through the Desert", hours=30, status="confirmed"),
        ]
        db.session.add_all(hours_list)
        db.session.commit()
        
        test_profile = view_profile(test_student.id, "hobopass")
        
        if test_profile["total_hours"] >= 50:
            assert test_profile["accolade"] == "Gold"
        elif test_profile["total_hours"] >= 25:
            assert test_profile["accolade"] == "Silver"
        else:
            assert test_profile["accolade"] == "Bronze"
            
        assert test_profile["date_awarded"] != "N/A"


def test_delete_student(empty_db):
    with empty_db.application.app_context():
        new_staff = Staff(first_name="Smol", last_name="Feet", password="staffpass")
        db.session.add(new_staff)
        db.session.commit()

        new_student = Student(first_name="Hugh", last_name="Feet", password="studentpass")
        db.session.add(new_student)
        db.session.commit()

        deleted_student = delete_student(new_staff.id, new_student.id)

        assert deleted_student.id == new_student.id
        assert Student.query.get(new_student.id) is None

def test_get_leaderboard(empty_db):
    with empty_db.application.app_context():
        tom = Student(first_name="Tom", last_name="Cat", password="tompass")
        jerry = Student(first_name="Jerry", last_name="Mouse", password="jerrypass")
        db.session.add_all([tom, jerry])
        db.session.commit()
        
        hours_list = [
            HoursCompleted(student_id=tom.id, activity="Chasing Jerry", hours=5, status="confirmed"),
            HoursCompleted(student_id=tom.id, activity="Cating Around", hours=10, status="confirmed"),
            HoursCompleted(student_id=jerry.id, activity="Mousing Up", hours=15, status="confirmed"),
        ]
        db.session.add_all(hours_list)
        db.session.commit()

        accolade_alice = Accolade(student_id=tom.id, accolade_level="Silver")
        accolade_alice.date_rewarded = datetime.today().date()
        db.session.add(accolade_alice)
        db.session.commit()

        leaderboard = get_leaderboard()

        assert len(leaderboard) == 2  
        assert leaderboard[0]["name"] in ["Tom Cat", "Jerry Mouse"]
        assert leaderboard[0]["total_hours"] == 15
        assert leaderboard[1]["total_hours"] == 15
        assert leaderboard[0]["accolade"] in ["Silver", "None", "Bronze", "Gold"]
        assert leaderboard[1]["accolade"] in ["Silver", "None", "Bronze", "Gold"]
        assert leaderboard[0]["rank"] == 1
        assert leaderboard[1]["rank"] == 2

def test_review_hours(empty_db):
    with empty_db.application.app_context():
        test_staff_member = Staff(first_name="Admin", last_name="User", password="admin123")
        db.session.add(test_staff_member)
        db.session.commit()

        test_student = Student(first_name="Test", last_name="Student", password="testpass")
        db.session.add(test_student)
        db.session.commit()

        hours_request = HoursCompleted(student_id=test_student.id, hours=8, activity="Library Help", status="pending")
        db.session.add(hours_request)
        db.session.commit()

        reviewed_record = review_hours(
            staff_id=test_staff_member.id,
            password="admin123",
            student_id=test_student.id,
            request_index=0,
            action="c"
        )

        assert reviewed_record is not None
        assert reviewed_record.staff_id == test_staff_member.id