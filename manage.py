import redis
from rq import Connection, Worker

REDIS_URL = "redis://redis:6379/0"
QUEUES = ["default"]

def run_worker():
    redis_url = REDIS_URL
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker("default")
        worker.work()


if __name__ == "__main__":
    run_worker()