from time import time
import pickle

import redis

from app.config import config


class Redis_db:
    def __init__(self):
        self.connect = redis.Redis(
            host=config['REDIS']['REDIS_HOST'],
            port=config['REDIS']['REDIS_PORT'],
            password=config['REDIS']['REDIS_PASSWORD'],
            db=config['REDIS']['REDIS_DB_REPLIC']
        )
        self.error = None

        try:
            self.check_connect(self.connect)
        except Exception as e:
            self.print_error(e)
            self.error = "Ошибка при подключении к Redis"

    def check_connect(self, conn):
        conn.get("ping")

    def close_connection(self):
        del self.connect

        return True

    def __byte_to_str(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if func.__name__ == 'select_data':
                return result.decode()
            elif func.__name__ == 'pipeline_query':
                decode_result = []
                lists = result['result'] if type(result['result']) == list else [result['result']]
                for row in lists:
                    if type(row) == bytes:
                        decode_result.append(row.decode('utf-8'))
                    else:
                        decode_result.append(row)

                result['result'] = decode_result
                return result

        return the_wrapper_around_the_original_function

    def __handler_exceptions(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            result = None
            try:
                result = func(self, *args, **kwargs)
            except Exception as e:
                self.print_error(e)

            return result

        return the_wrapper_around_the_original_function

    def print_error(self, e):
        print(f"""
===============REDIS_ERROR===============
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()}
==============================================
                """)

    @__handler_exceptions
    def insert_data(self, field, value):
        self.connect.set(field, value)

        return True

    @__handler_exceptions
    def del_data(self, field):
        res = self.connect.delete(field)

        return res

    @__handler_exceptions
    def insert_user(self, field, value):
        self.connect.hset("users", field, pickle.dumps(value))

        return True

    @__handler_exceptions
    def select_user(self, field):
        res = self.connect.hget("users", field)

        return res

    @__handler_exceptions
    def del_user(self, field):
        self.connect.hdel("users", field)

        return True

    @__handler_exceptions
    @__byte_to_str
    def select_data(self, field):
        res = self.connect.get(field)

        return res

    @__handler_exceptions
    @__byte_to_str
    def pipeline_query(self, pipe_list):
        """
            pipe is list. Items expected (method, field, value)
            methods: set, get
            returned: {'logs_set': [], 'result': []}
        """
        pipe = self.connect.pipeline()
        indx_get = []
        indx_set = []
        for indx, elem in enumerate(pipe_list):
            if elem[0] == 'set':
                pipe.set(elem[1], elem[2])
                indx_set.append(indx)
            elif elem[0] == 'get':
                pipe.get(elem[1])
                indx_get.append(indx)

        result = pipe.execute()
        return {
            "logs_set": [row for i, row in enumerate(result) if i in indx_set],
            "result": [row for i, row in enumerate(result) if i in indx_get]
        }


def check_actual_users_redis():
    try:
        r = redis.StrictRedis(
            host=config['REDIS']['REDIS_HOST'],
            port=config['REDIS']['REDIS_PORT'],
            password=config['REDIS']['REDIS_PASSWORD'],
            db=config['REDIS']['REDIS_DB_REPLIC']
        )

        for row in r.hgetall("users"):
            user = pickle.loads(r.hget("users", row))
            if not user.token_check():
                r.hdel("users", row)

        print("Cleaning old auth users is True")
    except Exception as e:
        print(f"""
===============REDIS_ERROR(check_actual_users_redis)===============
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()}
===================================================================
                """)
