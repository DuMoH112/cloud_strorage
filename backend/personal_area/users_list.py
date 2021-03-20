from flask import Blueprint, request, jsonify
from psycopg2 import sql

from Database.postgres import Postgres_db
from app.auth_utils import auth_user

users_list_bp = Blueprint('users_list', __name__)


@users_list_bp.route('/back/users_list', methods=['GET'])
@auth_user(name_func='users_list')
def users_list(user):

    database = Postgres_db()

    fields = [
        "id",
        "username",
        "firstname",
        "lastname",
        "size_space_kbyte",
        "status_active"
    ]
    users = database.select_data(sql.SQL("""
        SELECT 
            {}
        FROM users
        WHERE role=1;
    """).format(sql.SQL(",").join(sql.Identifier(i) for i in fields)))

    vozvrat = []
    if type(users) == list and users:
        for user_ in users:
            us_ = {}
            for index, field in enumerate(fields):
                us_[field] = user_[index]
            vozvrat.append(us_)

    return jsonify(vozvrat)
