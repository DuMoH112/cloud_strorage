from app.error_handler import error_bp

from personal_area.auth import auth_bp
from personal_area.logout import logout_bp
from personal_area.users_list import users_list_bp
from personal_area.registration import registration_bp

from get_html import html_bp

from Drive.upload_page import cloud_drive_bp
from Drive.manage_storage import manage_storage_bp

def route(app):
    app.register_blueprint(error_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(users_list_bp)
    app.register_blueprint(registration_bp)

    app.register_blueprint(html_bp)

    app.register_blueprint(cloud_drive_bp)
    app.register_blueprint(manage_storage_bp)

    return True


def csrf_exempt(csrf):
    csrf.exempt(auth_bp)
    csrf.exempt(logout_bp)
    csrf.exempt(users_list_bp)
    csrf.exempt(registration_bp)

    csrf.exempt(html_bp)

    csrf.exempt(cloud_drive_bp)
    csrf.exempt(manage_storage_bp)

    return True