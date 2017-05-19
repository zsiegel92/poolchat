
#from sqlalchemy import (all the abstract type checking functions I need, like email checking, etc. Maybe even put a Google Maps-querying address-checker in the node object).


#TODO: Store in a node a lambda function that checks whether it is valid input! The checking can happen in app, before it is sent to the models db functions. That is, each node has a property "Checker", that takes input of type self.nType, and returns whether or not it is valid input. Those functions need not go in app.py.
class nodeOb:
    def __init__(self,nType=None,nTitle = None,nQuestion=None):
        self.nType = nType
        self.nTitle = nTitle
        self.nQuestion = nQuestion
