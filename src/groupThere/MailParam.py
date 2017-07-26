import os
import re
from groupThere.helpers import sayname
#re.match(r"[^@]+@[^@]+\.[^@]+",inputted_email)

## Preferentially gets login info from environment variables 'EMAIL' and 'EMAIL_PASSWORD'
## Gets email login info from file, default 'login_info.txt'

class MailParam:
	def __init__(self,*args,login_filename=None,eventDate=None,eventTime=None,eventName=None,eventLocation = None,eventAddress=None,eventContact=None,eventEmail=None,eventHostOrg=None,signature="We look forward to your successful trip!",latenessWindow=None,email_user=None,email_password=None,**kwargs):
		self.eventDate = eventDate
		self.eventTime = eventTime
		self.eventName = eventName
		self.eventLocation = eventLocation
		self.eventAddress=eventAddress
		self.eventContact = eventContact
		self.eventEmail = eventEmail
		self.eventHostOrg = eventHostOrg
		self.signature = signature
		self.latenessWindow=latenessWindow
		self.login_filename = login_filename

		self.email_user = email_user
		self.email_password = email_password
		if ((email_user is None) or (email_password is None)):
			self.get_login_info(login_filename=login_filename,email_user=email_user,email_password=email_password)


	def strip_email_newlines(f):
		def email_stripped_f(self,*args,**kwargs):
			f(self,*args,**kwargs)
			if self.email_user:
				while self.email_user[-1]=='\n':
					self.email_user = self.email_user[0:-1]
				while self.email_user[0]=='\n':
					self.email_user = self.email_user[1:]
			if self.email_password:
				while self.email_password[-1]=='\n':
					self.email_password = self.email_password[0:-1]
				while self.email_password[0]=='\n':
					self.email_password = self.email_password[1:]
			if re.match(r"[^@]+@[^@]+\.[^@]+",self.email_user):
				print("Email verified as " + str(self.email_user))
			else:
				print("Email badly formatted as "  + str(self.email_user))
		return email_stripped_f


	@strip_email_newlines
	@sayname
	def get_login_info(self,login_filename=None,email_user=None,email_password=None):
		emailSet = False
		pwordSet = False
		if not email_user:
			email_user = self.email_user
			emailSet = True
		if not email_password:
			email_password = self.email_password
			pwordSet = True
		if not login_filename:
			login_filename=self.login_filename
		if not login_filename:
			envEmail = os.environ.get('EMAIL')
			envPassword = os.environ.get('EMAIL_PASSWORD')
			envLoginFilename = os.environ.get('EMAIL_CREDENTIALS_FILENAME')
			if (envEmail is not None) and (envPassword is not None):
				self.email_user = envEmail
				self.email_password = envPassword
				emailSet = True
				pwordSet = True
				print("Successfully set email username and password from environment variables.")
				return
			elif envEmail is not None:
				email_user = envEmail
				emailSet = True
			if envLoginFilename is not None:
				login_filename = envLoginFilename
			else:
				print("No login filename given as function argument or environment variable")
				return
		try:
			if (not emailSet) or (not pwordSet):
				if ((email_user) and (not email_password)):
						with open(login_filename,'r') as loginInfo:
							line = loginInfo.readline()
							while (line != email_user) and (line !=''):
								line = loginInfo.readline()
							else:
								print("password not found in file '{0}'".format(login_filename))
								return
							self.email_user = email_user
							self.email_password =loginInfo.readline()
							print("Successfully set email username and password - username was given as argument, and password was obtained from filename " + str(login_filename))
							return
				elif not email_user:
					with open(login_filename,'r') as loginInfo:
						email_user = loginInfo.readline()
						email_password =loginInfo.readline()
						if ((email_user != '') and (email_password != '')):
							self.email_user = email_user
							self.email_password=email_password
							print("Successfully set email username and password - neither username nor password were given as arguments, and so they were read from " + str(login_filename))
						else:
							print("Could not set email username and password. Ensure file '"+ str(login_filename) + "'' holds two lines with those two pieces of information.")
							return
				elif ((email_user is not None) and (email_password is not None)):
					self.email_user = email_user
					self.email_password = email_password
					print("Successfully set email username and password - both were given as arguments.")
				else:
					print("Could not set email username and password. Only password was given.")
					return
		except FileNotFoundError as exc:
			print("Could not open email credential file. Does the file '{0}'' exist?".format(login_filename))
			print(str(exc))
		except Exception as exc:
			print("Something went wrong while reading file.")
			print(str(exc))









