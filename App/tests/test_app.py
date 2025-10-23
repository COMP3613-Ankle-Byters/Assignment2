import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import *

from App.main import create_app
from App.database import db, create_db
from App.models import Staff, Student, Accolade, HoursCompleted
from App.controllers.student import *
from App.controllers.staff import *
from App.controllers.accolade import *
from App.controllers.auth import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''


class UnitTests(unittest.TestCase):

    def test_new_student(self):
        student = Student("Alice", "Smith", "AlicePass")
        assert student.first_name == "Alice"
        assert student.last_name == "Smith"
        
    
    def test_student_hashed_password(self):
        password = "studentpass"
        student = Student("Alice", "Smith", password)
        assert student.password != password

    def test_student_check_password(self):
        password = "studentpass"
        student = Student("Alice", "Smith", password)
        assert student.check_password(password)

    def test_student_set_password(self):
        student = Student("Alice", "Smith", "OldPass")
        old_hashed_password = student.password
        student.set_password("NewPass")
        assert student.password != old_hashed_password



    def test_new_staff(self):
        staff = Staff("John", "Doe", "JohnPass")
        assert staff.first_name == "John"
        assert staff.last_name == "Doe"

    def test_staff_hashed_password(self):
        password = "staffpass"
        staff = Staff("John", "Doe", password)
        assert staff.password != password

    def test_staff_check_password(self):
        password = "staffpass"
        staff = Staff("John", "Doe", password)
        assert staff.check_password(password)

    def test_staff_set_password(self):
        staff = Staff("John", "Doe", "OldPass")
        old_hashed_password = staff.password
        staff.set_password("NewPass")
        assert staff.password != old_hashed_password




    def test_new_accolade(self):
        accolade = Accolade(1, 10)
        assert accolade.student_id == 1
        assert accolade.accolade_level == 10
        assert accolade.date_rewarded is not None



    def test_new_hours_completed(self):
        hours_completed = HoursCompleted(student_id=1, hours=5, activity="Community Service")
        assert hours_completed.student_id == 1
        assert hours_completed.hours == 5
        assert hours_completed.activity == "Community Service"
        assert hours_completed.status == "pending"
        assert hours_completed.staff_id is None

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class IntegrationTests(unittest.TestCase):
    def test_student_login(self):
        student = create_student("teststudent", "lastname", "studentpass")
        token = login("teststudent", "lastname", "studentpass")
        assert token is not None

    def test_staff_login(self):
        staff = create_staff("teststaff", "lastname", "staffpass")
        token = login("teststaff", "lastname", "staffpass")
        assert token is not None

    def test_invalid_login(self):
        token = login("nonexistent", "nolastname", "wrongpass")
        assert token is None



    def test_create_student(self):
        student = create_student("alice", "smith", "alicepass")
        assert student.first_name == "alice"
        assert student.last_name == "smith"
        assert student.check_password("alicepass")
        

    def test_request_hours(self):
        student = create_student("bob", "brown", "bobpass")
        record = request_hours(student.id, 5, "Tutoring")
        assert record.hours == 5
        assert record.activity == "Tutoring"
        assert record.status == "pending"

    def test_view_profile(self):
        student = create_student("charlie", "davis", "charliepass")
        request_hours(student.id, 10, "Library Help")
        profile = view_profile(student.id, "charliepass")
        assert profile["first_name"] == "charlie"
        assert profile["total_hours"] == 0  # hours are pending, not confirmed


    def test_create_staff(self):
        staff = create_staff("david", "roberts", "davidpass")
        assert staff.first_name == "david"
        assert staff.last_name == "roberts"
        assert staff.check_password("davidpass")

    def test_review_hours(self):
        staff = create_staff("eve", "johnson", "evepass")
        student = create_student("frank", "wilson", "frankpass")
        record = request_hours(student.id, 8, "Food Drive")
        reviewed_record = review_hours(staff.id, student.id, record.id, confirm=True)
        
        assert reviewed_record.staff_id == staff.id
    
    def test_delete_student(self):
        staff = create_staff("grace", "lee", "gracepass")
        student = create_student("henry", "martin", "henrypass")
        request_hours(student.id, 6, "Tree Planting")
        deleted_student = delete_student(staff.id, student.id)
        assert deleted_student.id == student.id



    def test_accolade_award(self):
        student = create_student("isabel", "clark", "isabelpass")
        staff = create_staff("jack", "walker", "jackpass")
        # Simulate confirmed hours
        for _ in range(5):
            record = request_hours(student.id, 10, "Community Service")
            record.status = "confirmed"
            record.staff_id = staff.id
            db.session.commit()
        
        profile = view_profile(student.id, "isabelpass")
        assert profile["accolade"] == "Gold"  # 50 confirmed hours should yield Silver accolade




    def test_leaderboard_ranking(self):
        student1 = create_student("kate", "hall", "katepass")
        student2 = create_student("liam", "allen", "liampass")
        staff = create_staff("mike", "young", "mikepass")

        # Student 1: 60 confirmed hours
        for _ in range(6):
            record = request_hours(student1.id, 10, "Beach Cleanup")
            record.status = "confirmed"
            record.staff_id = staff.id
            db.session.commit()

        # Student 2: 70 confirmed hours
        for _ in range(7):
            record = request_hours(student2.id, 10, "Tree Planting")
            record.status = "confirmed"
            record.staff_id = staff.id
            db.session.commit()

        profile1 = view_profile(student1.id, "katepass")
        profile2 = view_profile(student2.id, "liampass")

        assert profile2["rank"] == 1
        assert profile1["rank"] == 2
        
            
            
        
        
    

