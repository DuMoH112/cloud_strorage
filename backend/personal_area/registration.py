import re
import uuid
import hashlib
from json.decoder import JSONDecodeError

from flask import Blueprint, request, jsonify
from psycopg2 import sql
import requests
import difflib

from Database.postgres import Postgres_db
from app.auth_utils import auth_user

registration_bp = Blueprint('registration', __name__)


@registration_bp.route('/back/registration', methods=['POST'])
@auth_user(name_func='registration')
def registration(user):
    user_data = request.get_json(silent=True)
    if not user_data:
        return jsonify({"message": "JSON не найден"}), 204

    database = None
    try:
        database = Postgres_db()

        user_data['role'] = 1

        valid = valid_user_data(database, user_data)
        if valid != True:
            return jsonify(valid), 400

        salt = uuid.uuid4().hex
        user_data['password'] = hash_password(user_data['password'], salt)

        user_id = add_to_database(database, user_data)        
        if type(user_id) != int:
            return jsonify(user_id), 500

        user_data["id"] = user_id
        valid = insert_salt_for_user(database, user_data["id"], salt)
        if valid != True:
            return jsonify(valid), 500

    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500
    finally:
        if database:
            database.close()

    return jsonify(True)


def valid_user_data(database, user_data):
    """Checking user data"""
    vozvrat = []

    valid = valid_password(user_data.get('password'), user_data.get('confirm_password'))
    if valid != True:
        vozvrat.append({"field": "password", "message": valid})

    valid = valid_username(user_data.get('username'), user_data.get('password'))
    if valid != True:
        vozvrat.append({"field": "username", "message": valid})

    return True if len(vozvrat) == 0 else vozvrat

def valid_username(username, password):
    """Checking username"""
    if username == None:
        return "Логин не введён"
    if re.search(
            "^[A-Za-z\d\s\.\,\:\;\!\?\(\)\"\'\-\–\_]{1,40}$", username) == None:
        return "Логин не удовлетворяет требованиям"
    if username == password or similarity(username, password) > 0.4:
        return "Логин не удовлетворяет требованиям"
    return True


def valid_password(password, confirm_password):
    """Valid password"""
    VALID_CHARS = [
        "[A-Z]{1,70}",
        "[a-z]{1,70}",
        "[0-9]{1,70}",
        "[\!\@\#\$\%\^\&\*\(\)\_\-\+\:\;\,\.]{0,70}"
    ]
    if password != confirm_password:
        return "Пароли не совпадают"
    if password == None:
        return "Пароль не введён"
    if len(password) < 6:
        return "Пароль не удовлетворяет требованиям"

    for val in VALID_CHARS:
        if re.search(
                val, password) == None:
            return "Пароль не удовлетворяет требованиям"

    # Проверка на 3 подряд идущие одинаковые символы
    last_char = ""
    quantity = 0
    for char in password:       
        if char != last_char:
            last_char = char
        elif char == last_char and quantity < 1:
            quantity += 1
        else:
            return "Пароль не удовлетворяет требованиям"
    return True


def similarity(s1, s2):
    """Affinity check"""
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def add_to_database(database, user_data):
    query = "INSERT INTO users({fields}) VALUES({values}) RETURNING id;"

    values = {
        "username": user_data['username'],
        "password": user_data['password'],
        "firstname": user_data.get("firstname"),
        "lastname": user_data.get("lastname"),
        "patronymic": user_data.get("patronymic"),
        "number_phone": user_data.get("number_phone"),
        "size_space_kbyte": user_data['size_space_kbyte'],
        "role": user_data['role']
    }

    user_id = database.select_data(sql.SQL(query).format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in values if values.get(i)),
        values=sql.SQL(",").join(sql.Literal(values[i]) for i in values if values.get(i))
        )
    )
    
    if type(user_id) == list:
        user_id = user_id[0][0]
        
    return user_id


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)


def insert_salt_for_user(database, user_id, salt):
    query = "INSERT INTO users_salt(user_id, salt) VALUES({user_id}, {salt})"

    values = {
        "user_id": sql.Literal(user_id),
        "salt": sql.Literal(salt)
    }

    return database.insert_data(sql.SQL(query).format(**values))
