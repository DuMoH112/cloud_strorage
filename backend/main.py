from apscheduler.schedulers.background import BackgroundScheduler

from socketio_app import socketio, app, redis

scheduler = BackgroundScheduler()

scheduler.add_job(func=redis.check_actual_users_redis, trigger="interval", minutes=30)

scheduler.start()

def run_server(host=None):
    if host:
        socketio.run(app, host=host)
    else:
        socketio.run(app)

if __name__ == "__main__":
    run_server('0.0.0.0')