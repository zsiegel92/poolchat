from GTviews import email_all_carpoolers,do_all_gt
from app_factory import create_app
# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn)



scheduler_frequency=60


if __name__ == '__main__':
	print("Trying to send email")
	with create_app().app_context():
		# send_test_email('zsiegel92@gmail.com')
		do_all_gt(scheduler_frequency=scheduler_frequency)
		email_all_carpoolers()
		print("email sent!")
