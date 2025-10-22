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

    # Initialize JWT
    jwt.init_app(app)

    # Register blueprints
    add_views(app)

    # Optional: push app context
    app.app_context().push()

    return app
