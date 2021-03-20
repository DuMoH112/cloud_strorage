from flask import Blueprint, request, jsonify

from Database.redis import Redis_db
from app.auth_utils import auth_user

logout_bp = Blueprint('logout', __name__)


@logout_bp.route('/back/logout', methods=['GET'])
@auth_user(name_func='logout')
def logout(user):
    """Logout Page"""
    r = Redis_db()

    r.del_user(user.get_token())
    return jsonify({'message': 'Пользователь вышел'}), 401
