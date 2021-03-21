import os
from time import time
import zipfile

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from psycopg2 import sql

from app.config import config
from app.auth_utils import auth_user
from Database.postgres import Postgres_db

cloud_drive_bp = Blueprint('cloud_drive', __name__)


@cloud_drive_bp.route('/upload_file', methods=['POST'])
@auth_user(name_func='cloud_drive')
def cloud_drive(user):
    """Cloud drive Page"""
    try:
        file = request.files['file']
    except KeyError:
        return jsonify({"messageError": "Файл не найден"})

    try:
        database = Postgres_db()
    except TypeError:
        return jsonify({"message": "Нет подключения к БД"})

    file_path = request.form.get('file_path')
    filename = secure_filename(file.filename)
    
    free_space_kbyte = database.select_data(
        sql.SQL("SELECT free_space_kbyte FROM users WHERE id={user_id}").format(
            user_id=sql.Literal(user.get_id())
    ))
    if type(free_space_kbyte) != list:
        return jsonify(free_space_kbyte)

    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if free_space_kbyte[0][0] < file_length // 1024:
        return jsonify({
            "messageError": "Недостаточно места"
        })
    
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")
    os.makedirs(path, exist_ok=True)

    file.save(os.path.join(path, filename))

    if filename.split('.')[-1] != 'zip':
        with zipfile.ZipFile(os.path.join(path, filename + '.zip'), 'w') as zip_f:
            zip_f.write(os.path.join(path, filename))

        os.remove(os.path.join(path, filename))

    file_size = os.stat(os.path.join(path, filename + '.zip')).st_size
    free_space_kbyte = database.select_data(sql.SQL("""
        UPDATE users 
        SET free_space_kbyte = (
            SELECT free_space_kbyte 
            FROM users 
            WHERE id={user_id}
        ) - {file_size} 
        WHERE id={user_id} RETURNING  free_space_kbyte;""").format(
            user_id=sql.Literal(user.get_id()),
            file_size=sql.Literal(file_size)
        ))
    if type(free_space_kbyte) == list:
        return jsonify({
            "free_space_kbyte": free_space_kbyte[0][0]
        })
    else:
        return jsonify(free_space_kbyte)
