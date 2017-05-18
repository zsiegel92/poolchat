from app import db
#from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field


#TODO: Create third model for "Registration". Then, the "engagement" or "participation" table will be a merge of all three tables on userid and carpoolid
#TODO: Some properties of this relation can't be stored in the user! Such as: time window, address, number of seats, need to arrive, must drive
#FOR NOW: It's as though every carpooler can have multiple pools, but all those pools have the exact same characteristics for the carpooler xD
#inputting names as lowercase makes them case-insensitive to SQLAlchemy (including even one uppercase character turns off this feature). So the lowercase class names refer to my classes whose names are uppercase! Confusing!
#,db.PrimaryKeyConstraint('participant_id', 'pool_id') #Possibly add this to constructor
participation = db.Table('participation', db.Column('carpooler_id', db.Integer, db.ForeignKey('carpooler.id')), db.Column('pool_id', db.Integer, db.ForeignKey('pool.id')))



##TODO: extend db.Column to have two types of metadata: a label, and a question (eg "What is your facebook id?")
class Carpooler(db.Model):
    __tablename__ = 'carpooler'
    
    id = db.Column(db.Integer, primary_key=True)
    fbId = db.Column(db.String()) #facebook id
    fields = {
        "email":("String()","your email","What is your email address?"),
        "name":("String()","your name","What isyour name?"),
        "address":("String()","the address you'll be coming from","What is the address you'll be coming from?"),
        "preWindow":("Integer","the earliest you can be ready to go","What is the earliest you can leave your house before the event?"),
        "on_time":("Integer","your ability to be late (1 or 0)","Do you have to arrive on time? Can you be 30 minutes late? Please answer 'yes' if you are an organizer of this event."),
        "must_drive":("Integer","your REQUIREMENT to drive (1 for \"have to drive\"; 0 for \"don't have to drive\")","Do you have to drive, or is catching a ride an option? Please answer Yes if you have to drive, or No otherwise."),
        "num_seats":("Integer","the number of seats in your car (0 if you have no car)","How many seats are there in your car? Please input a number; enter 0 if you cannot drive to the event.")
    }
    #If state needs to be more complex, store as JSON or as new column.
    fieldstate = db.Column(db.String()) #decision tree state, I guess
    engaged = db.Column(db.Integer) #Is this user fully plugged in?
    carpools = db.relationship('Pool',secondary=participation,backref=db.backref('carpoolers',lazy='dynamic'))
    ##    #NOTE:JSON type supported here:
    ##    result_all = db.Column(JSON)
    for field in fields:
        exec(field + "= db.Column(db." + fields[field][0] +")") #example: fbId = db.Column(db.String())
    del field


    def update(self,nextResponse=None,**kwargs):
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])
        if nextResponse:
            setattr(self,self.fieldvar,nextResponse)
        return self.next()

    def __init__(self, fbId,**kwargs):
        #        Construction equivalent to (thanks to SQLAlchemy.Model constructor):
        #        super(User, self).__init__(**kwargs)
        self.fbId = fbId #facebook id of user
        self.fieldstate = "email"
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])
                        

    def next(self):
        if getattr(self,self.fieldvar) is None:
            return self.fields[self.fieldvar][1:] #return description and question
        for field,value in vars(self).items():
            if value is None:
                self.fieldvar=field
                return self.fields[self.fieldvar][1:] #return description and question
        return ("Nothing else","You're all set!")

    def describe(self):
        unknown = '**Empty attributes**:\n'
        known = 'Known attributes:\n'
        for field in self.fields:
            if getattr(self,field) is None:
                unknown += field + '\n'
            else:
                known += field + ': ' + getattr(self,field) + '\n'
        status = unknown + known
        return status

    def printout(self):
        for field in self.fields:
            print(field + ": " + str(getattr(self,field)))


    def __repr__(self):
        return '<id {}>'.format(self.id)



class Pool(db.Model):
    __tablename__ = 'pool'
#    fields = {"id":("db.Integer,primary_key=True","tableId","Error"),
#        "poolName":("String()","name of your carpool group","What is the %s?"),
#        "eventDate":("db.Integer,primary_key=True","tableId","Error"),
#        "eventTime":("db.Integer,primary_key=True","tableId","Error"),
#        "eventAddress":("db.Integer,primary_key=True","tableId","Error"),
#        "eventContact":("db.Integer,primary_key=True","tableId","Error"),
#        "eventCoordinators":("db.Integer,primary_key=True","tableId","Error"),
#        "eventEmail":("db.Integer,primary_key=True","tableId","Error"),
#        "eventHostOrg":("db.Integer,primary_key=True","tableId","Error"),
#        "signature":("db.Integer,primary_key=True","tableId","Error"),
#        "solution":("db.Integer,primary_key=True","tableId","Error"),
#        "fireTime":("db.Integer,primary_key=True","tableId","Error")
#    }
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
    
    #participants = db.column(JSON) #Should I store participants in each pool, or just store the pool info?
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

