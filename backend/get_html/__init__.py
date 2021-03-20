from flask import Blueprint, render_template, request

from Database.postgres import Postgres_db

html_bp = Blueprint('html', __name__)


@html_bp.route('/', methods=['GET'])
@html_bp.route('/auth', methods=['GET'])
def auth_html():
    return render_template('auth.html')

@html_bp.route('/admin_panel', methods=['GET'])
def register_html():
    return render_template('admin_panel.html')

@html_bp.route('/user_panel', methods=['GET'])
def menu_html():
    return render_template('user_panel.html')
