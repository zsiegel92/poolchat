import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#usage:
# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn)
# from emailer import Emailer
#emailer=Emailer(q)
# emailer.email(toAddress,message="",subject="")
# emailer.self_email(message=message,subject=subject)

class Emailer:


	def __init__(self,queue=None):
		self.queue=queue
		self.gmail_user = os.environ['EMAIL']
		self.gmail_password=os.environ['EMAIL_PASSWORD']

	def get_email(self):
		return self.gmail_user
	def self_email(self,message="",subject=""):
		self.email(self.gmail_user,message,subject)

	def email(self,toAddress=None,message="generic_emailer_message",subject="generic_emailer_subject"):
		if toAddress is None:
			toAddress=self.gmail_user
		if self.queue is None:
			self.direct_email(toAddress,self.gmail_user,self.gmail_password,message,subject)
		else:
			self.queue.enqueue_call(func=self.direct_email,args=(str(toAddress),str(self.gmail_user),str(self.gmail_password),str(message),str(subject),),result_ttl=5000)

	@classmethod
	def direct_email(cls,sent_to,sent_from,password,message="",subject="",error=False):
		print("in Emailer.direct_email")
		if sent_to.split("@")[-1]== 'notARealThing.com':

			message = "Blocked from sending to " + str(sent_to) + ":\n"+str(message)
			subject = "REDIRECTED: " + str(subject)
			sent_to=sent_from
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
			if error is False:
				cls.direct_email(sent_from,sent_from,password,message="ERROR SENDING message to " + str(sent_to) +"!\n" + str(message),subject="ERROR MESSAGE for: " + str(subject),error=True)
		else:
			print("Message sent successfully.")


	@classmethod
	def send_from_server(cls,fromAddress,password,toAddress,message):
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(fromAddress, password)
			server.sendmail(fromAddress, toAddress, message)
			server.close()

	def send_html_body(self,toAddress,html_body,subject="",text_message=""):
		print("in Emailer.send_html_body")
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		return self.send_html(toAddress,html,subject,text_message)

	def self_send_html_body(self,html_body,subject="",text_message=""):
		self.send_html_body(self.gmail_user,html_body,subject,text_message)

	def send_html(self,toAddress,html_message,subject="",text_message=""):
		print("in Emailer.send_html")
		if toAddress.split("@")[-1]== 'notARealThing.com':
			subject = subject + " REDIRECTED from " + str(toAddress)
			toAddress = self.gmail_user

		msg = MIMEMultipart('alternative')
		msg['Subject']=subject
		msg['From']=self.gmail_user
		msg['To']=toAddress
		html = html_message
		if text_message=="":
			text = html_message
		else:
			text=text_message

		part1 = MIMEText(text,'plain')
		part2 = MIMEText(html,'html')

		msg.attach(part1)
		msg.attach(part2)

		if self.queue is None:
			self.send_from_server(msg['From'],self.gmail_password,msg['To'],msg.as_string())
		else:
			self.queue.enqueue_call(func=self.send_from_server,args=(msg['From'],self.gmail_password,msg['To'],msg.as_string(),),result_ttl=5000)


