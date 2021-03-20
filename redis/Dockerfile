FROM redis:6.0.10 as app
COPY redis.conf /etc/
USER 999
CMD ["sh", "-c", "exec redis-server /etc/redis.conf --requirepass \"$REDIS_PASSWORD\""]
