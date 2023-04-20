from datetime import datetime, timedelta
from typing import Union, Callable
from redis import Redis
from rq import Queue
from rq.job import Job
from app.settings import settings


class JobScheduler:
    def __init__(self, queque_name):
        self.connection = Redis(
            host=settings.REDIS_HOST, port=6379, db=0
        )  # TODO: Create env variables for redis connection.
        self.queue = Queue(queque_name, connection=self.connection)

    def add_to_queue_condition(
        self, func: Callable, condition: Union[timedelta, datetime], args
    ) -> Job:
        job = self.queue.enqueue_in(condition, func, args)
        return job

    def add_to_queue(self, func: Callable, args) -> Job:
        job = self.queue.enqueue(func, args)
        return job

    def update_queue_job(self, job: Job):
        job = Job.fetch(job.id, connection=self.connection)
        # update job
        return job

    def remove_from_queue(self, job: Job):
        job = Job.fetch(job.id, connection=self.connection)
        return job.delete()

    def consume_from_queue(self):
        pass
        # cant set a worker with a queue in the same process
