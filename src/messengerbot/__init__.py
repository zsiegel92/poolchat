from messengerbot import messages
from messengerbot import templates
from messengerbot import attachments
from messengerbot import elements
#or:
#from . import messsages

import os
import json
import requests




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
        except messengerException as err:
            errors.append("Error sending buttons.")
            return err
    def say(self,recipient_id,message_text):
        recipient = messages.Recipient(recipient_id=recipient_id)
        myMessage = messages.Message(text=message_text)
        myRequest = messages.MessageRequest(recipient, myMessage)
        try:
            myResponse = self.send(myRequest)
            return myResponse
        except MessengerException:
            raise
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
            errorstuff['myMessage']=json.dumps(message.to_dict())
#            MessengerError(**response.json()).raise_exception()
            MessengerError(**errorstuff).raise_exception()
        return response.json()

    def subscribe_app(self):
        """
        Subscribe an app to get updates for a page.
        """
        response = requests.post(
            '%s/subscribed_apps' % self.GRAPH_API_URL,
            params={
                'access_token': self.access_token
            }
        )
        return response.status_code == 200


from flask import current_app as app
messenger = MessengerClient(access_token=app.config['MESSENGER_PLATFORM_ACCESS_TOKEN'])
