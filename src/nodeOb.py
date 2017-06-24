from messengerbot import messages
from messengerbot import templates
from messengerbot import attachments
from messengerbot import elements
from messengerbot import quick_replies

#from sqlalchemy import (all the abstract type checking functions I need, like email checking, etc. Maybe even put a Google Maps-querying address-checker in the node object).

#TODO: store next state in a node.
#TODO: Store in a node a function that checks whether it is valid input! The checking can happen in app, before it is sent to the models db functions. That is, each node has a property "Checker", that takes input of type self.nType, and returns whether or not it is valid input. Those functions need not go in app.py.
##TODO: A postback doesn't necessarily need a checker, I guess...unless it checks that it is an appropriate time to click that button...

#TODO: Each node shouldn't carry a nTitle and nQuestion, but should carry a "payload", which can be things to say, or a postback button. It should also carry a "payload_type", but, generally, payloads should be formatted so that, rather than messenger.say(), messenger.send() can be used.

typeCheckers ={"String": (lambda stringArg: isinstance(stringArg,str)),"Integer": (lambda stringArg: stringArg.isdigit())}

node_args = ['nType','nTitle','nQuestion','next','nextChoices','quickChoices','choices','customAfterText','nodeName','verboseNode','validator','processor','obField','findPool','disable_prefix']

class nodeOb:

	def __init__(self,nType=None,nTitle = None,nQuestion=None,nodeName=None,next=None,nextChoices=None,quickChoices=None,choices=None,customAfterText=None,verboseNode=False,validator = None,processor=None,obField=None,findPool=False,disable_prefix=False):
		self.nType = nType
		self.nTitle = nTitle
		self.nodeName = nodeName
		self.nQuestion = nQuestion
		self.customAfterText=customAfterText
		self.verboseNode=verboseNode
		self.validator = validator
		self.processor = processor #Custom formatting for database storage
		self.obField = obField #eg 'Carpooler'
		self.findPool = findPool

		self.next = next
		self.nextChoices = nextChoices

		self.choices = choices
		self.quickChoices = quickChoices

		self.disable_prefix=disable_prefix
		if not (self.disable_prefix):
			prefix = "RESPONSE/"+ str(obField) +"/"
		else:
			prefix = ""



		if quickChoices:
			self.quick_choice_buttons = []
			for choice, pay in quickChoices.items():
				self.quick_choice_buttons.append(quick_replies.QuickReplyItem(content_type='text',title=choice,payload=prefix+ pay))
		if choices:
			self.choice_buttons = []
			for choice,pay in choices.items():
				self.choice_buttons.append(elements.PostbackButton(title=choice,payload=pay))

		if next == 'quick_menu':
			self.nextChoices = {}
			for key,value in quickChoices.items():
				self.nextChoices[str(value)]=str(value)

		elif next =='mode_menu':
			self.nextChoices = {}
			for key, value in quickChoices.items():
				self.nextChoices[str(value)]=str(value)

		if nextChoices:
			if not 'default' in nextChoices:
				self.nextChoices['default']=next

	#TODO: validation functions that are more than type-checkers, as optional arguments
	def isValid(self,userInput):
		if self.next =='quick_menu':
			if userInput not in self.nextChoices:
				return False
			else:
				return True
		if not typeCheckers[self.nType](userInput):
			return False
		#Optional validator argument
		if self.validator:
			return self.validator(userInput)
		return True

	def process(self,userInput):
		if self.processor:
			return self.processor(userInput)
		else:
			return userInput

	def prompt(self):
		return "Now I need to know more about {1}. Please respond with a(n) {0}.".format(self.nType,self.nTitle)

	def afterSet(self,response):
		if self.customAfterText:
			return self.customAfterText.format(title=self.nTitle,question=self.nQuestion,type=self.nType)
		elif self.next=='quick_menu':
			#TODO: nextNode(response) returns a field name. Instead, return a field title.
			return "OK, now I know you want to go to " + self.nextNode(response)
		elif response:
			return "OK, now I know that " + self.nTitle + " is " + response + "."
		else:
			return "Ready to keep moving. (nodeOb.afterSet, no response)"


	def ask(self):
		return "{}".format(self.nQuestion)
	def nextNode(self,input=None):
		if self.nextChoices:
			if input:
				if input in self.nextChoices:
					return self.nextChoices[input]
			return self.nextChoices['default']
		else:
			return self.next
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

	def copy(self):
		copied_args ={}
		for arg in node_args:
			copied_args[arg]=getattr(self,arg,None)

		print("copying node")
		newNode = nodeOb(**copied_args)

		print("finished copying node")
		return newNode

	def represent(self):
		return str(vars(self))

	def __repr__(self):
		return self.nType
#Eventually add more checks, like isEmail, etc.


#TODO: import nodeOb in messengerbot/__init__.py and implement a sendNode(sender_id,node) function that does messengerbot.send(sender_id,node.payload)
