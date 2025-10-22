from flask import Flask
from flask_cors import CORS
from flask_uploads import UploadSet, configure_uploads, TEXT, DOCUMENTS, IMAGES

from App.database import init_db
from App.config import load_config

from App.views.auth import auth_views
from App.views.index import index_views
from App.views.student import student_views
from App.views.staff import staff_views
from App.views.leaderboard import leaderboard_views
from App.views.user import user_views


def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)

    # Uploads
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)

    # Database initialization
    init_db(app)

    # Register blueprints
    app.register_blueprint(index_views)
    app.register_blueprint(auth_views)
    app.register_blueprint(student_views)
    app.register_blueprint(staff_views)
    app.register_blueprint(user_views)
    app.register_blueprint(leaderboard_views)

    # Optional: push app context
    app.app_context().push()

    return app
