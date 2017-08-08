from scheduler_tasks import email_carpoolers



if __name__ == '__main__':
	print("Trying to send email")
	# send_test_email('zsiegel92@gmail.com')
	email_carpoolers(localTesting=True)
	print("email sent!")
