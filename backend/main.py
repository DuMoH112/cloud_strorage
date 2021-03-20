from time import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app import create_flask_app
from Database.redis import check_actual_users_redis

scheduler = BackgroundScheduler()

scheduler.add_job(func=check_actual_users_redis, trigger="interval", minutes=60)

scheduler.start()

if __name__ == "__main__":
    create_flask_app().run(host='0.0.0.0')
