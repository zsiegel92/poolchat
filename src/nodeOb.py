from messengerbot import messages
from messengerbot import templates
from messengerbot import attachments
from messengerbot import elements
from messengerbot import quick_replies

import sys

#from sqlalchemy import (all the abstract type checking functions I need, like email checking, etc. Maybe even put a Google Maps-querying address-checker in the node object).

#TODO: store next state in a node.
#TODO: Store in a node a function that checks whether it is valid input! The checking can happen in app, before it is sent to the models db functions. That is, each node has a property "Checker", that takes input of type self.nType, and returns whether or not it is valid input. Those functions need not go in app.py.
##TODO: A postback doesn't necessarily need a checker, I guess...unless it checks that it is an appropriate time to click that button...

#TODO: Each node shouldn't carry a nTitle and nQuestion, but should carry a "payload", which can be things to say, or a postback button. It should also carry a "payload_type", but, generally, payloads should be formatted so that, rather than messenger.say(), messenger.send() can be used.

typeCheckers ={"String": (lambda stringArg: isinstance(stringArg,str)),"Integer": (lambda stringArg: stringArg.isdigit())}

typeWrappers = {"String":str,"Integer":int}

node_args = ['nType','nTitle','nQuestion','next','nextChoices','quickChoices','choices','customAfterText','nodeName','verboseNode','validator','postProcessor','obField','pre_toggle','fieldname','prefix','internalOnly']

def safeformat(str, **kwargs):
		class SafeDict(dict):
				def __missing__(self, key):
						return '{' + key + '}'
		replacements = SafeDict(**kwargs)
		return str.format_map(replacements)


class nodeOb:

	def __init__(self,nType=None,nTitle = None,nQuestion=None,next=None,nextChoices=None,quickChoices=None,choices=None,customAfterText=None,nodeName=None,verboseNode=False,validator = None,postProcessor=None,obField=None,pre_toggle=None,fieldname=None,prefix = None,internalOnly=False):
		self.nType = nType
		self.nTitle = nTitle
		self.fieldname = None
		self.nodeName = nodeName
		if not nQuestion:
			if nTitle:
				nQuestion = "What is " + str(nTitle) + "?"
		self.nQuestion = nQuestion
		self.customAfterText=customAfterText
		self.verboseNode=verboseNode
		self.validator = validator
		self.postProcessor = postProcessor #Custom formatting for database storage
		self.obField = obField #eg 'Carpooler','Trip'
		self.pre_toggle = pre_toggle
		self.internalOnly = internalOnly
		if (quickChoices and (not next) and (not nextChoices)):
			self.next='quick_menu'
		else:
			self.next=next
		self.nextChoices = nextChoices
		self.choices = choices
		self.quickChoices = quickChoices

		self.default_prefix = "RESPONSE/"+ str(obField) +"/"

		if prefix:
			self.prefix = prefix
		else:
			self.prefix = self.default_prefix


		self.quick_choice_buttons = []
		if next == 'quick_menu':
			self.nextChoices = {}

		#Populate Quick Choice Buttons and Next Choices list with prefixed quick-replies (unless disable_prefix, in which case prefix = "")
		if quickChoices:
			if next == 'quick_menu':
				for choice, pay in quickChoices.items():
					self.quick_choice_buttons.append(quick_replies.QuickReplyItem(content_type='text',title=choice,payload=pay))

					self.nextChoices[str(pay)]=str(pay)
			else:
				for choice, pay in quickChoices.items():
					self.quick_choice_buttons.append(quick_replies.QuickReplyItem(content_type='text',title=choice,payload= pay))

		if nextChoices:
			if not 'default' in nextChoices:
				if self.next != 'quick_menu':
					self.nextChoices['default']=next

		if choices:
			self.choice_buttons = []
			for choice,pay in choices.items():
				self.choice_buttons.append(elements.PostbackButton(title=choice,payload=pay))



	#TODO: validation functions that are more than type-checkers, as optional arguments
	def isValid(self,userInput,obField =None):
		print("in nodeOb.isValid. self.nTitle = " + str(self.nTitle)+", self.fieldname = " + str(self.fieldname),file = sys.stderr)
		# if obField:
		# 	if obField != self.obField:
		# 		return False

		if self.validator:
			return self.validator(userInput)

		if self.next =='quick_menu':
			return userInput in self.nextChoices

		if not typeCheckers[self.nType](userInput):
			return False

		return True

	def process(self,userInput):
		if self.postProcessor:
			return self.postProcessor(userInput)
		else:
			return typeWrappers[self.nType](userInput)

	def prefixer(self,userInput):
		print("in nodeOb.prefix",file = sys.stderr)
		return self.prefix + userInput


	def prompt(self):
		return "Now I need to know more about {0}.".format(self.nTitle)

	def afterSet(self,response):
		if self.customAfterText:
			return safeformat(self.customAfterText,title=self.nTitle,question=self.nQuestion,type=self.nType,response = response)
		elif self.next=='quick_menu':
			#TODO: nextNode(response) returns a field name. Instead, return a field title.
			return "OK, now I know you want to go to " + self.nextNode(response)
		elif response:
			return "OK, now I know that " + self.nTitle + " is " + response + "."
		else:
			return "Ready to keep moving. (nodeOb.afterSet, no response)"

#TODO: send multiple text messages in one request (prompt AND question).
	#Choices is of the form {text1:postbacktext1,text2:postbacktext2}
#    Choices is of the form {text1:postbacktext1,text2:postbacktext2}
	def payload(self):
		if self.choices is not None:
			myTemplate = templates.ButtonTemplate(text=self.ask(), buttons=self.choice_buttons)
			myAttachment = attachments.TemplateAttachment(template=myTemplate)
			myMessage = messages.Message(attachment=myAttachment)
		elif self.quickChoices is not None:
			myReplies = quick_replies.QuickReplies(quick_replies = self.quick_choice_buttons)
			myMessage = messages.Message(text=self.ask(),quick_replies=myReplies)
		else:
			myMessage = messages.Message(text=self.prompt() + "\n" + self.ask())
		return myMessage

	def ask(self):
		return str(self.nQuestion)

	def nextNode(self,input=None):
		print("in nodeOb.nextNode",file = sys.stderr)
		try:
			if (self.nextChoices and input):
				return self.nextChoices[input]
			else:
				assert (self.next != 'quick_menu')
				return self.next
		except Exception as exc:
			print("ERROR in nodeOb.nextNode.")
			print(str(exc))
			return self.nextChoices['default']


	def copy(self):
		copied_args ={}
		for arg in node_args:
			copied_args[arg]=getattr(self,arg,None)

		print("copying node")
		newNode = nodeOb(**copied_args)
		return newNode

	def represent(self):
		return str(vars(self))

	def __repr__(self):
		return self.nType
#Eventually add more checks, like isEmail, etc.


#TODO: import nodeOb in messengerbot/__init__.py and implement a sendNode(sender_id,node) function that does messengerbot.send(sender_id,node.payload)
