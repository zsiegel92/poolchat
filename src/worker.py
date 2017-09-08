import os
import sys

import redis
from rq import Worker, Queue, Connection
listen = ['default']




from utils import test_env

testing=False
for arg in sys.argv:
	if 'test' in arg:
		testing = True
if testing:
	print("Worker in Testing Mode")
	with test_env():
		from app_factory import create_app
		redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6380')
else:
	print("Worker in Regular Mode")
	from app_factory import create_app
	redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')


conn = redis.from_url(redis_url)


def main():
	with create_app().app_context():
		with Connection(conn):
			worker = Worker(list(map(Queue, listen)))
			worker.work()

if __name__ == '__main__':
	if testing:
		with test_env():
			print("IN testing mode! $EMAIL is " + str(os.environ.get('EMAIL')))
			main()
	else:
		print("IN regular mode! $EMAIL is " + str(os.environ.get('EMAIL')))
		main()
