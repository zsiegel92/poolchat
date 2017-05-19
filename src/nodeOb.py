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



typeCheckers = {"String":(lambda stringArg:True),"Integer":(lambda stringArg: stringArg.isdigit())}

class nodeOb:

    def __init__(self,nType=None,nTitle = None,nQuestion=None,Next=None,choices=None,customAfterText=None):
        self.nType = nType
        self.nTitle = nTitle
        self.nQuestion = nQuestion
        self.Next = Next
        self.choices = choices
        self.customAfterText=customAfterText
    
    def isValid(self,userInput):
        return typeCheckers[self.nType](userInput)
    def prompt(self):
        return "Now I need to know more about {1}. Please respond with a(n) {0}.".format(self.nType,self.nTitle)
    def afterSet(self,response):
        if self.customAfterText:
            return self.customAfterText.format(self.nTitle,self.nQuestion,self.nType)
        else:
            return "OK, now I know that " + self.nTitle + " is " + response + "."
    def ask(self):
        return "{}".format(self.nQuestion)
    def nextNode(self):
        return self.Next
    
    #TODO: send multiple text messages in one request (prompt AND question).
    #Choices is of the form {text1:postbacktext1,text2:postbacktext2}
    def payload(self):
        if self.choices is not None:
            buttons = []
            for choice in self.choices:
                buttons.append(elements.PostbackButton(title=choice,payload=self.choices[choice]))
            myTemplate = templates.ButtonTemplate(text=self.nQuestion, buttons=buttons)
            myAttachment = attachments.TemplateAttachment(template=myTemplate)
            myMessage = messages.Message(attachment=myAttachment)
    #        myRequest = messages.MessageRequest(recipient=recipient, message=myMessage)#To be done from messengerbot.
        else:
            myMessage = messages.Message(text=self.prompt())
        return myMessage

#Eventually add more checks, like isEmail, etc.


#TODO: import nodeOb in messengerbot/__init__.py and implement a sendNode(sender_id,node) function that does messengerbot.send(sender_id,node.payload)



