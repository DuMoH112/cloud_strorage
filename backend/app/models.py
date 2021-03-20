import secrets
import time

from flask import jsonify

from Database.redis import Redis_db as Redis
from app.auth_utils import PERMISSION_AUTHORIZATION


class User ():
    def __init__(self, id, username, role, id_fsso=None):
        self.__id = id
        self.__id_fsso = id_fsso
        self.__username = username
        self.__role = role
        self.FSSO = None

        self.__generate_token()
        self.__time_auth = int(time.time()) + 1800
        self.__ttl = 1800

    def get_username(self):
        return self.__username

    def get_id(self):
        return self.__id

    def get_role(self):
        return self.__role

    def get_token(self):
        return self.__user_token

    def __generate_token(self):
        length = 256
        self.__user_token = secrets.token_urlsafe(length)

    def token_check(self):
        return True if (time.time() - self.__time_auth) < self.__ttl else False

    def allow(self, name_func):
        if self.__time_auth < time.time():
            r = Redis()
            r.del_data(self.__user_token)
            r.close_connection()
            return jsonify({'message': 'UserToken больше не действителен'}), 401
        permission_name = PERMISSION_AUTHORIZATION.get(name_func)
        if permission_name == None:
            return jsonify({'message': 'Нет доступа'}), 403
        if not self.__role in permission_name:
            return jsonify({'message': 'Нет доступа'}), 403

        return True


class MyForm(Form):
    file_ = FileField('image', validators=[
        FileRequired()
    ])
    path = None
    success = None
    orig = None
    copy = None
    time_seconds = None