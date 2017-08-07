import os
import config
import smtplib
from rq import Queue #INTERACTIONS MOVEMENT!
from rq.job import Job  #FOR Redis jobs #INTERACTIONS MOVEMENT!
from worker import conn #INTERACTIONS MOVEMENT!
from flask_sqlalchemy import SQLAlchemy
q = Queue(connection=conn) #INTERACTIONS MOVEMENT!


def send_email(sent_to,sent_from,password,message="",subject=""):
	try:
		fullMessage = "\r\n".join([
			"From: " + sent_from,
			"To: " + sent_to,
			"Subject: " + subject,
			"",
			message
		])
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(sent_from, password)
		server.sendmail(sent_from, sent_to, fullMessage)
		server.close()
		# messenger.say(recipient_id,"You just got an email from GroupThere!")
	except Exception as exc:
		print('Something went wrong with login.')
		print("exception: " + str(exc))



def send_test_email(toAddress):
	message = "SENDING A TEST EMAIL FROM CRON JOB"
	subject = "a message from cron!"
	gmail_user =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).EMAIL
	gmail_password=getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).EMAIL_PASSWORD
	send_email(toAddress,gmail_user,gmail_password,message,subject)



if __name__ == '__main__':
	print("Trying to send email")
	send_test_email('zsiegel92@gmail.com')
	print("email sent!")
