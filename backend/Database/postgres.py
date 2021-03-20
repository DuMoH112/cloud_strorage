from time import time
from uuid import uuid4

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

from app.config import config


class Postgres_db:
    conn = None

    def __init__(self):
        conn = self.connect(config)
        if conn:
            self.conn = conn
        else:
            print("Нет подключения к БД")
            raise TypeError

    def __init_named_cursor(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            cursor = None
            try:
                cursor = self.conn.cursor(str(uuid4()))
            except AttributeError:
                return "Нет подключения к БД"

            try:
                return func(self, *args, **kwargs, cursor=cursor)
            except AttributeError:
                return "Нет подключения к БД"
            except Exception as e:
                bad_query = None
                if type(args[0]) == sql.Composed:
                    bad_query = args[0].as_string(self.conn)
                elif type(args[0]) == str:
                    bad_query = args[0]
                cursor = self.conn.cursor(cursor_factory=DictCursor)
                self.__write_logs(bad_query, cursor=cursor)

                self.print_error(e, bad_query)

                return "Ошибка при обращении к БД"

        return the_wrapper_around_the_original_function

    def __init_dict_cursor(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            cursor = None
            try:
                cursor = self.conn.cursor(cursor_factory=DictCursor)
            except AttributeError:
                return "Нет подключения к БД"

            try:
                return func(self, *args, **kwargs, cursor=cursor)
            except AttributeError:
                return "Нет подключения к БД"
            except Exception as e:
                bad_query = None
                if type(args[0]) == sql.Composed:
                    bad_query = args[0].as_string(self.conn)
                elif type(args[0]) == str:
                    bad_query = args[0]
                self.__write_logs(bad_query, cursor=cursor)

                self.print_error(e, bad_query)

                return "Ошибка при обращении к БД"

        return the_wrapper_around_the_original_function

    def __write_logs(self, bad_query, cursor):
        query = "INSERT INTO {table}({fields}) VALUES({values});"
        values = {
            "table": sql.Identifier("logs_bad_query"),
            "fields": sql.Identifier("query"),
            "values": sql.Literal(bad_query)
        }
        cursor.execute(sql.SQL(query).format(**values))

    def connect(self, config):
        """Connect to database PostgreSQL"""
        try:
            path_schema = f"{str(config['POSTGRES']['POSTGRES_SCHEMA'])}" if str(config['POSTGRES']['POSTGRES_SCHEMA']) != 'public' else "public"
            conn = psycopg2.connect(
                dbname=str(config['POSTGRES']['POSTGRES_DATABASE_NAME']),
                user=str(config['POSTGRES']['POSTGRES_USERNAME']),
                password=str(config['POSTGRES']['POSTGRES_PASSWORD']),
                host=str(config['POSTGRES']['POSTGRES_HOST']),
                port=str(config['POSTGRES']['POSTGRES_PORT']),
                options=f"-c search_path={path_schema}")
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError:
            return False

    def close(self):
        """Close connect with database"""
        if self.conn:
            self.conn.close()
        return True

    @__init_dict_cursor
    def select_data(self, execute, cursor):
        # Если присылаемым значение было error, то вызывается исключение
        if execute == "error":
            raise AttributeError
        cursor.execute(execute)

        return cursor.fetchall()

    @__init_dict_cursor
    def insert_data_with_returning(self, execute, cursor):
        # Если присылаемым значение было error, то вызывается исключение
        if execute == "error":
            raise AttributeError
        cursor.execute(execute)

        return cursor.fetchall()

    @__init_named_cursor
    def copy_to(self, file, table, columns, sep, cursor):
        cursor.copy_to(file, table, columns=columns, sep=sep)

        return True

    @__init_dict_cursor
    def insert_data(self, execute, cursor, name_file=None):
        try:
            # Если присылаемым значение было error, то вызывается исключение
            if execute == "error":
                raise AttributeError

            cursor.execute(execute)
        except psycopg2.errors.UniqueViolation:
            if str(name_file).find('.') != -1:
                if name_file.split('.')[-1] == 'registration':
                    return "Пользователь с таким никнеймом уже существует"

        return True

    @__init_dict_cursor
    def login(self, username, cursor):
        cursor.execute(sql.SQL("SELECT * FROM get_data_login({})").format(sql.Literal(username)))
        psw = cursor.fetchone()
        if psw != None:
            return {
                "id": psw[0],
                "password": psw[1],
                "role": psw[2],
                "status_active": psw[3],
                "salt": psw[4]
            }

        return False

    def print_error(self, e, bad_query=None):
        if bad_query:
            print(f"""
================POSTGRES_ERROR================
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()},
    bad_query: {bad_query}
==============================================
                """)
        else:
            print(f"""
================POSTGRES_ERROR================
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()}
==============================================
                """)