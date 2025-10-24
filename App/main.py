from flask import Flask
from flask_cors import CORS
from flask_uploads import UploadSet, configure_uploads, TEXT, DOCUMENTS, IMAGES
from flask_jwt_extended import JWTManager  # ✅ Add this import

from App.database import init_db
from App.config import load_config

from App.views.auth import auth_views
from App.views.index import index_views
from App.views.student import student_views
from App.views.staff import staff_views
from App.views.leaderboard import leaderboard_views

jwt = JWTManager()

def add_views(app):
    views = [auth_views, index_views, student_views, staff_views, leaderboard_views]
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)

    # Uploads
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)

    # Database initialization
    init_db(app)

   
    jwt.init_app(app)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        
        if isinstance(identity, dict):
            user_id = identity.get("id")
            user_type = (identity.get("type") or identity.get("role"))
        else:
            try:
                user_id = int(identity) if identity is not None else None
            except (TypeError, ValueError):
                user_id = None
            user_type = None

        if user_id is None:
            return None

        from App.models.student import Student
        from App.models.staff import Staff

       
        if user_type:
            t = user_type.lower()
            if t in ("student", "s"):
                return Student.query.get(user_id)
            if t in ("staff", "dstaff", "d_staff", "tutor", "teacher"):
                return Staff.query.get(user_id)

        
        user = Student.query.get(user_id)
        if user:
            return user
        return Staff.query.get(user_id)

    add_views(app)

    
    app.app_context().push()

    return app
