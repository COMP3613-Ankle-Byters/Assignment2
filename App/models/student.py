from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    hours_completed = db.relationship('HoursCompleted', backref='student', lazy=True)
    accolade = db.relationship('Accolade', backref='student', lazy=True)

    def __init__(self, first_name, last_name, password):
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
