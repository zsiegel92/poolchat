from messengerbot import messages
from messengerbot import templates
from messengerbot import attachments
from messengerbot import elements
#from models import Carpooler #WHY DON'T I HAVE TO IMPORT THIS???
#or:
#from . import messsages

import os
import json
import requests

import config

class MessengerException(Exception):
	pass


class MessengerError(object):
	def __init__(self, *args, **kwargs):
		self.__dict__.update(**kwargs)

	def raise_exception(self):
		raise MessengerException(
#            getattr(self, 'error_data', self.message)
			json.dumps(self.__dict__)
		)

class MessengerClient(object):

	GRAPH_API_URL = 'https://graph.facebook.com/v2.6/me'

	def __init__(self, access_token):
		self.access_token = access_token
		self.errors = []
	def give_choices(self,recipient_id,choicetext,buttons):
		recipient=messages.Recipient(recipient_id=recipient_id)
		myTemplate = templates.ButtonTemplate(text=choicetext, buttons=buttons)
		myAttachment = attachments.TemplateAttachment(template=myTemplate)
		myMessage = messages.Message(attachment=myAttachment)
		myRequest = messages.MessageRequest(recipient=recipient, message=myMessage)
		try:
			myResponse = self.send(myRequest)
			return myResponse
		except MessengerException as err:
			self.errors.append("Error sending buttons.")
			return err
	def say(self,recipient_id,message_text):
		if len(message_text)>400:
			for k in range(0,int(len(message_text)/400)-1):
				self.say(recipient_id,message_text[k*600+1:(k+1)*600])
			k=k+1
			self.say(recipient_id,message_text[k*600+1:len(message_text)-1])
			return
		recipient = messages.Recipient(recipient_id=recipient_id)
		myMessage = messages.Message(text=message_text)
		myRequest = messages.MessageRequest(recipient, myMessage)
		try:
			myResponse = self.send(myRequest)
			return myResponse
		except MessengerException:
			raise
	def send_image(self,recipient_id,image_url):
		recipient = messages.Recipient(recipient_id=recipient_id)
		myAttachment = attachments.ImageAttachment(url=image_url)
		myMessage = messages.Message(attachment=myAttachment)
		myRequest = messages.MessageRequest(recipient, myMessage)
		try:
			myResponse = self.send(myRequest)
			return myResponse
		except MessengerException:
			raise
	def poolerSay(self,recipient_id,carpooler):
		recipient = messages.Recipient(recipient_id=recipient_id)
		myRequest = messages.MessageRequest(recipient=recipient, message=carpooler.payload())
		self.send(myRequest)

#    def nodeSay(self,recipient_id,node):
#        recipient = messages.Recipient(recipient_id=recipient_id)
#        myRequest = messages.MessageRequest(recipient=recipient, message=node.payload())
#        self.send(myRequest)
	#see: http://stackoverflow.com/questions/4730435/exception-passing-in-python
	def webButton(self,theTitle='Show this website',theUrl='http://www.google.com'):
		return elements.WebUrlButton(title=theTitle,url=theUrl)
	def postBackButton(self,title='Do this postback',action='USER_DEFINED_PAYLOAD'):
		return elements.PostbackButton(title=title,payload=action)
	def send(self, message):
		params = {
			'access_token': self.access_token
		}
		headers = {
			"Content-Type": "application/json"
		}
		#change below data to json to revert to original, and remove headers entirely
		response = requests.post(
			'%s/messages' % self.GRAPH_API_URL,
			params=params,
			headers=headers,
			data=json.dumps(message.to_dict())
		)
		if response.status_code != 200:
			errorstuff = response.json()
			print("error in process in __init__.send!")
			errorstuff['myMessage']=json.dumps(message.to_dict())
#            MessengerError(**response.json()).raise_exception()
			MessengerError(**errorstuff).raise_exception()
		return response.json()

	def subscribe_app(self):
		"""
		Subscribe an app to get updates for a page.
		"""
		headers = {
		'authorization': "Basic WlM6enMxMjM=",
		'cache-control': "no-cache",
		'postman-token': "2538b4d1-d981-0dcc-5651-9c6420c8de4f"
		}
		response = requests.post(
			'%s/subscribed_apps' % self.GRAPH_API_URL,
			headers=headers,
			params={
				'access_token': self.access_token
			}
		)
		return response.status_code == 200

#os.environ['APP_SETTINGS'] #returns 'config.DevelopmentConfig'
#Note: this may only be possible because this module is imported `with app.test_request_context`
access_token = getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).MESSENGER_PLATFORM_ACCESS_TOKEN
messenger = MessengerClient(access_token=access_token)

#from flask import current_app as app
#messenger = MessengerClient(access_token=app.config['MESSENGER_PLATFORM_ACCESS_TOKEN'])
