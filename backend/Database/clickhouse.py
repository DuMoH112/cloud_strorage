from time import time

from clickhouse_driver import dbapi, errors

from app.config import config


class Clickhouse_db:
    conn = None
    error = None

    def __init__(self):
        conn = self.connect(config)
        try:
            self.check_connect(conn)
            self.conn = conn
        except errors.NetworkError as e:
            self.print_error(e)
            print("Нет подключения к Clickhouse Database")
            self.error = "Нет подключения к Clickhouse Database"
        except dbapi.errors.OperationalError as e:
            try:
                result = self.__create_new_schema(config)

                if not result:
                    self.print_error(e)
                    self.error = "Ошибка при подключении к Clickhouse Database"
                else:
                    self.check_connect(conn)
                    self.conn = conn
            except Exception as e:
                self.print_error(e)
                self.error = str("Ошибка при подключении к Clickhouse Database")

        except Exception as e:
            self.print_error(e)
            self.error = str("Ошибка при подключении к Clickhouse Database")

        self.db_name = str(config['CLICKHOUSE']['CLICKHOUSE_DATABASE_NAME'])

    def connect(self, config):
        """Open connect with database"""
        conn = dbapi.connect(
                host=str(config['CLICKHOUSE']['CLICKHOUSE_HOST']),
                port=str(config['CLICKHOUSE']['CLICKHOUSE_PORT']),
                user=str(config['CLICKHOUSE']['CLICKHOUSE_USERNAME']),
                password=str(config['CLICKHOUSE']['CLICKHOUSE_PASSWORD']),
                database=str(config['CLICKHOUSE']['CLICKHOUSE_DATABASE_NAME']),
                compression=bool(config['CLICKHOUSE']['CLICKHOUSE_COMPRESSION'])
            )

        return conn

    def close(self):
        """Close connect with database"""
        if self.conn:
            self.conn.close()
        return True

    def print_error(self, e, bad_query=None):
        if bad_query:
            print(f"""
===============CLICKHOUSE_ERROR===============
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()},
    bad_query: {bad_query}
==============================================
                """)
        else:
            print(f"""
===============CLICKHOUSE_ERROR===============
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()}
==============================================
                """)

    def __init_cursor(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            cursor = None
            try:
                cursor = self.conn.cursor()
            except errors.NetworkError as e:
                self.print_error(e)

                return "Нет подключения к Clickhouse Database"

            try:
                return func(self, *args, **kwargs, cursor=cursor)
            except errors.NetworkError:
                return "Нет подключения к Clickhouse Database"
            except Exception as e:
                bad_query = None
                if args:
                    bad_query = args[0]

                self.print_error(e, bad_query)
                return "Ошибка при обращении к Clickhouse Database"
            finally:
                if cursor:
                    cursor.close()

        return the_wrapper_around_the_original_function

    @__init_cursor
    def select_data(self, query, cursor):
        cursor.execute(query)

        return cursor.fetchall()

    @__init_cursor
    def insert_data(self, query, cursor):
        cursor.execute(query)

        return True

    @__init_cursor
    def insert_many_data(self, query, seq_of_parameters, cursor):
        cursor.executemany(query, seq_of_parameters)

        return True

    def check_connect(self, conn):
        cursor = conn.cursor()

        cursor.execute("SELECT now()")

    def __create_new_schema(self, config):
        conn = dbapi.connect(
                host=str(config['CLICKHOUSE']['CLICKHOUSE_HOST']),
                port=str(config['CLICKHOUSE']['CLICKHOUSE_PORT']),
                user=str(config['CLICKHOUSE']['CLICKHOUSE_USERNAME']),
                password=str(config['CLICKHOUSE']['CLICKHOUSE_PASSWORD']),
                database="default",
                compression=bool(config['CLICKHOUSE']['CLICKHOUSE_COMPRESSION'])
            )

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {str(config['CLICKHOUSE']['CLICKHOUSE_DATABASE_NAME'])};")
        conn.close()

        return True
