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

typeCheckers ={"String": (lambda stringArg: True),"Integer": (lambda stringArg: stringArg.isdigit())}

class nodeOb:

    def __init__(self,nType=None,nTitle = None,nQuestion=None,next=None,nextChoices=None,quickChoices=None,choices=None,customAfterText=None,verboseNode=False,validator = None,processor=None):
        self.nType = nType
        self.nTitle = nTitle
        self.nQuestion = nQuestion
        self.choices = choices
        self.customAfterText=customAfterText
        self.verboseNode=verboseNode
        self.validator = validator
        self.processor = processor #Custom formatting for database storage

        self.next = next
        self.nextChoices = nextChoices
        self.quickChoices = quickChoices
        if next == 'quick_menu':
#            self.next = 'fieldstate' #Change this to self.root!! Create root field.
            self.nextChoices = {}
            for key,value in quickChoices.items():
#                print(str(key) + str(value))
                self.nextChoices[str(value)]=str(value)
        if nextChoices:
            if not 'default' in nextChoices:
                self.nextChoices['default']=next

        print("Initializing new node with: self.nextChoices: " + str(self.nextChoices))

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
            return self.customAfterText.format(self.nTitle,self.nQuestion,self.nType)
        elif self.next=='quick_menu':
            return "OK, now I know you want to go to " + self.nextNode(response)
        else:
            return "OK, now I know that " + self.nTitle + " is " + response + "."


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
            buttons = []
            for choice,pay in self.choices.items():
                buttons.append(elements.PostbackButton(title=choice,payload=pay))
            myTemplate = templates.ButtonTemplate(text=self.nQuestion, buttons=buttons)
            myAttachment = attachments.TemplateAttachment(template=myTemplate)
            myMessage = messages.Message(attachment=myAttachment)
        elif self.quickChoices is not None:
            replies = []
            for choice, pay in self.quickChoices.items():
                replies.append(quick_replies.QuickReplyItem(content_type='text',title=choice,payload=pay))
            myReplies = quick_replies.QuickReplies(quick_replies = replies)
            myMessage = messages.Message(text=self.ask(),quick_replies=myReplies)
        else:
            myMessage = messages.Message(text=self.prompt() + "\n" + self.ask())
        return myMessage

    def copy(self):
        print("copying node")
        newNode = nodeOb(nType=self.nType,nTitle = self.nTitle,nQuestion=self.nQuestion,next=self.next,nextChoices=self.nextChoices,quickChoices=self.quickChoices,choices=self.choices,customAfterText=self.customAfterText)
        return newNode
    def represent(self):
        return str(vars(self))

    def __repr__(self):
        return self.nType
#Eventually add more checks, like isEmail, etc.


#TODO: import nodeOb in messengerbot/__init__.py and implement a sendNode(sender_id,node) function that does messengerbot.send(sender_id,node.payload)
