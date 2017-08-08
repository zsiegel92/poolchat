import os
import smtplib

class Emailer:

	def __init__(self,queue=None):
		self.queue=queue
		self.gmail_user = os.environ['EMAIL']
		self.gmail_password=os.environ['EMAIL_PASSWORD']

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
