from app import db
#from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field
from nodeOb import *
from fieldTrees import fields
#from decision_trees import poolertree as fields
import sys

#TODO: Create third model for "Registration". Then, the "engagement" or "participation" table will be a merge of all three tables on userid and carpoolid
#TODO: Some properties of this relation can't be stored in the user! Such as: time window, address, number of seats, need to arrive, must drive
#FOR NOW: It's as though every carpooler can have multiple pools, but all those pools have the exact same characteristics for the carpooler xD

#NOTE: inputting names as lowercase makes them case-insensitive to SQLAlchemy (including even one uppercase character turns off this feature). So the lowercase class names refer to my classes whose names are uppercase! Confusing!
#,db.PrimaryKeyConstraint('participant_id', 'pool_id') #Possibly add this to constructor
participation = db.Table('participation', db.Column('carpooler_id', db.Integer, db.ForeignKey('carpooler.id')), db.Column('pool_id', db.Integer, db.ForeignKey('pool.id')))

print('Hello from MODELS.PY!', file=sys.stderr)

class Carpooler(db.Model):
    __tablename__ = 'carpooler'
    
#    NOT SURE if sqlalchemy column definitions HAVE TO occur outside __init__.
    id = db.Column(db.Integer, primary_key=True)
    fbId = db.Column(db.String()) #facebook id
    doneNode = nodeOb("NA","Nothing else","You're all set!")
    fieldstate = db.Column(db.String()) #decision tree state, I guess
    engaged = db.Column(db.Integer) #Is this user fully plugged in?
    carpools = db.relationship('Pool',secondary=participation,backref=db.backref('carpoolers',lazy='dynamic'))
    for field in fields:
        exec(field + "= db.Column(db." + fields[field].nType +"())") #example: fbId = db.Column(db.String())
    del field


    def __init__(self, fbId,**kwargs):
        super().__init__()
        self.fbId = fbId #facebook id of user
        self.fieldstate = "name"
        self.menu = "fieldstate"
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])

#   @Return: nodeOb
#    Can update fields directly, or can update based on current fieldstate with input.
    def update(self,input=None,**kwargs):
        print("Beginning update(input) - self.fieldstate: " + self.fieldstate + ", self.menu: " + self.menu + ", self." + self.fieldstate + ": " + str(getattr(self,self.fieldstate,None)) + ", input: " + input, file=sys.stderr)
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])
        if input:
            setattr(self,self.fieldstate,input) #Assign input to the variable whose name is stored in fieldstate. fieldstate is unchanged.
        return self.next(input)

#    Do this so that I can, eg, edit prompts with rich data from models!
    def getField(self,field):
        node = fields[field]
        return node

    def head(self):
        return self.getField(self.fieldstate) #return nodeOb(type, description, and question). If field being queried is blank, stay the course and query for it.
    
    def nextField(self,input =None):
        print("Next field is: " + str(self.head().nextNode(input)), file=sys.stderr)
        return self.head().nextNode(input)

#    @POST: field state is updated

    def next(self,input=None):
            print("Beginning next(input) - self.fieldstate: " + self.fieldstate + ", self.menu: " + self.menu + ", self." + self.fieldstate + ": " + getattr(self,self.fieldstate,None) + ", input: " + input, file=sys.stderr)
            if self.returnToMenu():
                self.fieldstate = self.menu
                self.menu = 'menu'
                return self.head()
            print("self.nextField(" + input + ") ==" + self.nextField(input), file=sys.stderr)
            newFieldState = self.nextField(input)
            newNode = self.getField(newFieldState)
            print("Changing self.fieldstate from " + str(self.fieldstate) + " to " + str(newFieldState), file=sys.stderr)
            print("self.menu: " + str(self.menu))
            self.fieldstate = newFieldState
            print("Returning new node.", file=sys.stderr)
            return newNode

    
    def returnToMenu(self):
        return (self.menu !='fieldstate')

#    @Post: prints description of self
    def printout(self):
        for field in fields:
            print(field + ": " + str(getattr(self,field)))


#    @Return: String description of carpooler
    def describe(self):
        unknown = '**Empty attributes**:\n'
        known = 'Known attributes:\n'
        for field in fields:
            if getattr(self,field) is None:
                unknown += field + '\n'
            else:
                known += field + ': ' + getattr(self,field) + '\n'
        status = unknown + known
        return status

#    @Return: String description of carpooler
    def __repr__(self):
        return '<id {}>'.format(self.id)



class Pool(db.Model):
    __tablename__ = 'pool'
    
    id = db.Column(db.Integer, primary_key=True) #id of group carpooling
    poolName = db.Column(db.String())
    eventDate = db.Column(db.Date())
    eventTime = db.Column(db.Time) #Time of event encoded as int?
    latenessWindow = db.Column(db.Integer)
    eventAddress = db.Column(db.String())
    eventContact = db.Column(db.String())#1 or 0
    eventEmail = db.Column(db.String())
    eventHostOrg = db.Column(db.String()) #Is this user fully plugged in?
    signature = db.Column(db.String()) #decision tree state, I guess
    solution = db.column(JSON) #Should I store this in a separate db?
    fireTime = db.column(db.Integer) #Number of minutes before event that a solution is automatically generated (maybe need plugin or package - cron?)
    eventCoordinators = db.column(JSON) #List of sender_id's for hosts, to enable editing of event, triggering solutions, etc.
    #distMatrix = db.column(JSON) #Can I store this as a 2d array?
    
    def update(self,**kwargs):
        for arg in kwargs:
            if (hasattr(self,arg)):
                setattr(self,arg,kwargs[arg])

    def __repr__(self):
        return '<id {}>'.format(self.userId)

    def __init__(**kwargs):
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])
        #participants = participants
        #distMatrix = distMatrix


