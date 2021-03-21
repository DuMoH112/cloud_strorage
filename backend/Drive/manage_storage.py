import os
import zipfile
import pathlib
from time import time
from io import BytesIO

import requests
from psycopg2 import sql
from flask import Blueprint, request, jsonify, send_file

from app.config import config
from app.auth_utils import auth_user
from Database.postgres import Postgres_db

from Drive.tools import allowed_file

manage_storage_bp = Blueprint('manage_storage', __name__)


@manage_storage_bp.route('/create_folder', methods=['POST'])
@auth_user(name_func='create_folder')
def create_folder(user):
    json = request.get_json(silent=True)
    if not json:
        return jsonify({"message": "JSON не найден"}), 204

    file_path = json.get('file_path')

    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")
    os.makedirs(path, exist_ok=True)

    return jsonify(True)


@manage_storage_bp.route('/get_file', methods=['POST'])
@auth_user(name_func='get_file')
def get_file(user):
    """Download a file."""
    json = request.get_json(silent=True)
    if not json:
        return jsonify({"message": "JSON не найден"}), 204

    file_path = json.get('file_path')
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")
    
    with zipfile.ZipFile(path, 'r') as z:
        for filename in z.namelist(  ):
            return send_file(
                BytesIO(z.read(filename)),
                attachment_filename=filename,
                as_attachment=True
            )


@manage_storage_bp.route('/get_files_in_directory', methods=['POST'])
@auth_user(name_func='get_files_in_directory')
def get_files_in_directory(user):
    json = request.get_json(silent=True)
    if not json:
        return jsonify({"message": "JSON не найден"}), 204

    file_path = json.get('file_path')
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")

    vozvrat = []
    with os.scandir(path) as listOfEntries:
        for entry in listOfEntries:
            if entry.is_file():                    
                vozvrat.append({
                    "title": entry.name,
                    "path": entry.path[len(config['APP']['PATH_STORAGE']) + len(user.get_username()):],
                    "size": entry.stat(follow_symlinks=False).st_size,
                    "type": "file"
                })
            elif entry.is_dir():
                vozvrat.append({
                    "title": entry.name,
                    "path": entry.path[len(config['APP']['PATH_STORAGE']) + len(user.get_username()):],
                    "size": entry.stat(follow_symlinks=False).st_size,
                    "type": "dir"
                })

    return jsonify(vozvrat)


@manage_storage_bp.route('/del_object', methods=['DELETE'])
@auth_user(name_func='del_object')
def del_object(user):
    json = request.get_json(silent=True)
    if not json:
        return jsonify({"message": "JSON не найден"}), 204

    try:
        database = Postgres_db()
    except TypeError:
        return jsonify({"message": "Нет подключения к БД"})

    file_path = json.get('file_path')
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")

    file_size = os.stat(path).st_size
    if os.path.isdir(path):    
        os.removedirs(path)
    elif os.path.isfile(path):
        os.remove(path)

    free_space_kbyte = database.select_data(sql.SQL("""
        UPDATE users 
        SET free_space_kbyte = (
            SELECT free_space_kbyte 
            FROM users 
            WHERE id={user_id}
        ) + {file_size} 
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


@manage_storage_bp.route('/share', methods=['POST'])
@auth_user(name_func='share_object')
def share_object(user):
    json = request.get_json(silent=True)
    if not json:
        return jsonify({"message": "JSON не найден"}), 204

    file_path = json.get('file_path')
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{user.get_username()}{file_path}")

    payload = {
        "route": f"/{user.get_username()}{file_path}"
    }
    if os.path.isdir(path):
        payload["type"] = "dir"
    elif os.path.isfile(path):
        payload["type"] = "file"

    r = requests.Request(method='GET', url=f"http://{config['APP']['URL_SERVICE']}/share", params=payload).prepare()

    return jsonify(r.url)


@manage_storage_bp.route('/share', methods=['GET'])
@auth_user(name_func='get_share_object')
def get_share_object(user):
    path = os.path.join(f"{config['APP']['PATH_STORAGE']}{request.args.get('route')}")
    type_obj = request.args.get('type')

    if type_obj == "dir" and os.path.isdir(path):
        vozvrat = []
        with os.scandir(path) as listOfEntries:
            for entry in listOfEntries:
                if entry.is_file():                    
                    vozvrat.append({
                        "title": entry.name,
                        "path": entry.path[len(config['APP']['PATH_STORAGE']) + len(user.get_username()):],
                        "size": entry.stat(follow_symlinks=False).st_size // 1024,
                        "type": "file"
                    })
                elif entry.is_dir():
                    vozvrat.append({
                        "title": entry.name,
                        "path": entry.path[len(config['APP']['PATH_STORAGE']) + len(user.get_username()):],
                        "size": entry.stat(follow_symlinks=False).st_size // 1024,
                        "type": "dir"
                    })
        return vozvrat
    elif type_obj == "file" and os.path.isfile(path):
        with zipfile.ZipFile(path, 'r') as z:
            for filename in z.namelist(  ):
                return send_file(
                    BytesIO(z.read(filename)),
                    attachment_filename=filename,
                    as_attachment=True
                )

    return jsonify(False), 404
