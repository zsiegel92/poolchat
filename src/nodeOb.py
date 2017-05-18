#TODO: Store in a node a lambda function that checks whether it is valid input! The checking can happen in app, before it is sent to the models db functions
class nodeOb:
    def __init__(self,nType=None,nTitle = None,nQuestion=None):
        self.nType = nType
        self.nTitle = nTitle
        self.nQuestion = nQuestion
