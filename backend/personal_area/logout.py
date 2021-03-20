from flask import Blueprint, request, jsonify

from app.models import check_auth
from app.redis import Redis

logout_bp = Blueprint('logout', __name__)


@logout_bp.route('/logout', methods=['GET'])
def logout():
    """Logout Page"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    r = Redis()

    r.del_user(user.get_token())
    return jsonify({'message': 'Пользователь вышел'}), 401
