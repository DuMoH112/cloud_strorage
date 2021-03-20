from flask import Blueprint, request, jsonify
from psycopg2 import sql

from app.models import check_auth
from app.postgres import Database

personal_area_bp = Blueprint('personal_area', __name__)


@personal_area_bp.route('/get_personal_data', methods=['GET', 'POST'])
def get_personal_data():
    """User`s personal data get"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    database = None
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500

    fields = [
        "firstname",
        "lastname",
        "patronymic",
        "gender",
        "username",
        "email",
        "number_phone"
    ]

    query = "SELECT {fields} FROM users WHERE id={user_id};"

    vozvrat = {}

    user_id = None
    if request.method == 'POST' and user.get_role() in ["Admin", "Executor"]:
        user_id = request.get_json(silent=True)
        if not user_id:
            return jsonify({"message": "JSON не найден"}), 204
        user_id = user_id.get("user_id")
    else:
        user_id = user.get_id()

    user_data = database.select_data(sql.SQL(query).format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
        user_id=sql.Literal(user_id) 
    ))

    if user_data:
        for field in fields:
            vozvrat[field] = user_data[0][field]
    else:
        vozvrat = {"message": "Пользователь не найден"}

    return jsonify(vozvrat)


@personal_area_bp.route('/update_personal_data', methods=['PUT'])
def update_personal_data():
    """User`s personal data update"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    database = None
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500        

    user_data = request.get_json(silent=True)
    if not user_data:
        return jsonify({"message": "JSON не найден"}), 204

    isValid = valid_biometric_information(user_data)
    if isValid != True:
        return jsonify(isValid), 400

    fields = [
        "firstname",
        "lastname",
        "patronymic",
        "gender",
        "username",
        "email",
        "number_phone"
    ]

    query = "UPDATE users SET ({fields})=({values}) WHERE id={user_id};"

    access_fields = [i for i in user_data if i in fields and user_data[i]]
    values = {
        "fields": sql.SQL(",").join(sql.Identifier(i) for i in access_fields),
        "values": sql.SQL(",").join(sql.Literal(user_data[i]) for i in access_fields),
        "user_id": sql.Literal(user.get_id())
    }

    if len(access_fields) == 1:
        query = "UPDATE biometric_information SET {fields}={values} WHERE user_id={user_id};"     

    isValid = database.insert_data(sql.SQL(query).format(**values))

    return jsonify(isValid)


@personal_area_bp.route('/get_biometric_information', methods=['GET', 'POST'])
def get_biometric_information():
    """User`s biometric information get"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    database = None
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500        

    fields = [
        "body_mass",
        "growth",
        "age"
    ]

    query = "SELECT {fields} FROM biometric_information WHERE user_id={user_id};"

    vozvrat = {}

    user_id = None
    if request.method == 'POST' and user.get_role() in ["Admin", "Executor"]:
        user_id = request.get_json(silent=True)
        if not user_id:
            return jsonify({"message": "JSON не найден"}), 204
        user_id = user_id.get("user_id")
    else:
        user_id = user.get_id()

    user_data = database.select_data(sql.SQL(query).format(
        fields=sql.SQL(",").join(sql.Identifier(i) for i in fields),
        user_id=sql.Literal(user_id) 
    ))

    if user_data:
        for field in fields:
            vozvrat[field] = user_data[0][field]
    else:
        vozvrat = {"message": "Пользователь не найден"}

    return jsonify(vozvrat)


@personal_area_bp.route('/update_biometric_information', methods=['PUT'])
def update_biometric_information():
    """User`s biometric information update"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    database = None
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500        

    user_data = request.get_json(silent=True)
    if not user_data:
        return jsonify({"message": "JSON не найден"}), 204

    isValid = valid_biometric_information(user_data)
    if isValid != True:
        return jsonify(isValid), 400

    fields = [
        "body_mass",
        "growth",
        "age"
    ]

    query = "UPDATE biometric_information SET ({fields})=({values}) WHERE user_id={user_id};"

    access_fields = [i for i in user_data if i in fields]
    values = {
        "fields": sql.SQL(",").join(sql.Identifier(i) for i in access_fields),
        "values": sql.SQL(",").join(sql.Literal(user_data[i]) for i in access_fields),
        "user_id": sql.Literal(user.get_id())
    }

    if len(access_fields) == 1:
        query = "UPDATE biometric_information SET {fields}={values} WHERE user_id={user_id};"     

    isValid = database.insert_data(sql.SQL(query).format(**values))

    return jsonify(isValid)


@personal_area_bp.route('/get_history_of_orders', methods=['GET'])
def get_history_of_orders():
    """User`s history of orders get"""
    user = check_auth(request.headers, __name__)
    try:
        if user[0] != True:
            return user
    except KeyError:
        return user
    user = user[1]

    database = None
    try:
        database = Database()
    except TypeError:
        return jsonify({"messageError": "Нет подключения к БД"}), 500        

    fields = [
        ("hoo", "id"),
        ("hoo", "title"),
        ("so", "title")
    ]

    query = "SELECT {fields} FROM history_of_orders hoo LEFT JOIN status_orders so on so.id = hoo.status_order_id WHERE client_id={user_id};"

    if user.get_role() == "Executor":
        query = "SELECT {fields} FROM history_of_orders hoo LEFT JOIN status_orders so on so.id = hoo.status_order_id WHERE executor_id={user_id};"
    elif user.get_role() == "Admin":
        query = "SELECT {fields} FROM history_of_orders hoo LEFT JOIN status_orders so on so.id = hoo.status_order_id" 

    vozvrat = []

    values = {
        "fields": sql.SQL(",").join(sql.Identifier(table, fields) for table, fields in fields)
    }
    if user.get_role() in ["Client", "Executor"]:
        values["user_id"] = sql.Literal(user.get_id())

    for id, title, status in database.select_data(sql.SQL(query).format(**values)):
        vozvrat.append({
            "id": id,
            "title": title,
            "status": status
        })

    return jsonify(vozvrat)


def valid_biometric_information(data):
    vozvrat = []
    int_fields = [
        "body_mass", 
        "growth", 
        "age"
    ]
    str_fields = [
        "firstname",
        "lastname",
        "patronymic",
        "gender",
        "username",
        "email",
        "number_phone",
        "body_mass", 
        "growth", 
        "age"
    ]
    for row in data:
        if row in str_fields and type(data[row]) == str:
            pass
        elif row in int_fields and type(data[row]) == int:
            pass
        else:
            vozvrat.append({"error": f"Неверный тип данных в {row}"})
        
    return True if len(vozvrat) == 0 else vozvrat
