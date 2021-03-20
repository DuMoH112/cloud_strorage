import pickle

from flask import jsonify, request

from Database.redis import Redis_db as Redis
from app.config import config


PERMISSION_AUTHORIZATION = {
    # 0 - Admin
    # 1 - Client
    "logout": [0, 1],
    "users_list": [0],
    "registration": [0]
}


def auth_user(name_func):
    def auth_user_(func):
        def the_wrapper_around_the_original_function(*args, **kwargs):
            user = check_auth(request.headers, name_func)
            try:
                if user[0] != True:
                    return user
            except KeyError:
                return user
            user = user[1]
            return func(user=user, *args, **kwargs)

        the_wrapper_around_the_original_function.__name__ = func.__name__
        return the_wrapper_around_the_original_function
    return auth_user_


def check_auth(headers, name, disable_Token=False):
    r = Redis()

    if not disable_Token:
        if headers.get('Token') != str(config['FLASK_APP']['FLASK_APP_SECRET_KEY']):
            return jsonify({'message': 'Не верный Token'}), 401

    if not headers.get('UserToken'):
        return jsonify({'message': 'Не верный UserToken'}), 401

    byte_user = r.select_user(headers.get('UserToken'))
    r.close_connection()

    if byte_user == None:
        return jsonify({'message': 'Не верный UserToken'}), 401
    user = pickle.loads(byte_user)
    if user == None:
        return jsonify({'message': 'Не верный UserToken'}), 401

    allowed = user.allow(name.rsplit('.')[-1])
    if allowed != True:
        return allowed

    return True, user
