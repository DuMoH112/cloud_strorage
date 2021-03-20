from flask import Blueprint, render_template, request

from app.models import check_auth
from app.postgres import Database

html_bp = Blueprint('html', __name__)


@html_bp.route('/front/auth', methods=['GET'])
def auth_html():
    return render_template('auth.html')


@html_bp.route('/front/menu', methods=['GET'])
def menu_html():
    return render_template('menu.html')


@html_bp.route('/front/chat', methods=['GET'])
def chat_html():
    # user = check_auth(request.headers, __name__)
    # try:
    #     if user[0] != True:
    #         return user
    # except KeyError:
    #     return user
    # user = user[1]

    return render_template('chat.html', username="user.get_username()")