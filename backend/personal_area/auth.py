import re
import uuid
import hashlib
from json.decoder import JSONDecodeError

from psycopg2 import sql
from flask import Blueprint, request, jsonify

from app.models import User
from app.config import config
from Database.redis import Redis_db
from Database.postgres import Postgres_db
from personal_area.registration import hash_password
from personal_area.registration import valid_password, valid_username

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/back/auth', methods=['POST'])
def authorization():
    if request.headers.get('Token') != str(config['FLASK_APP']['FLASK_APP_SECRET_KEY']):
        return jsonify({'message': 'Не верный токен'}), 401, {'ContentType': 'application/json'}
    try:
        database = Postgres_db()
    except TypeError:
        return jsonify({"message": "Нет подключения к БД"})
    redis_db = Redis_db()
    if redis_db.error:
        return jsonify(redis_db.error), 500

    username = request.get_json(silent=True).get("username")
    password = request.get_json(silent=True).get("password")

    if not (valid_username(username, password) or valid_password(password, password)):
        return jsonify("Неправильный логин или пароль"), 401

    user_data = database.login(username=username)
    if type(user_data) == str:
        return jsonify(user_data), 500

    if user_data:
        if user_data["status_active"] == True:
            if check_password(user_data, password):
                user = User(
                    id=user_data["id"],
                    username=username,
                    role=user_data["role"]
                )

                redis_db.insert_user(user.get_token(), user)

                return jsonify({"UserToken": user.get_token(), "role": user.get_role()})
        else:
            return jsonify({'message': 'Пользователь заблокирован'}), 401, {'ContentType': 'application/json'}
    
    return jsonify({'message': 'Неправильный логин или пароль'}), 401


def check_password(user_data, user_pass):
    new_pass = hash_password(user_pass, user_data['salt'])

    return user_data['password'].tobytes() == new_pass
