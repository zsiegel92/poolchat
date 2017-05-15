from app import db
#from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field

#TODO:
#How to specify UNIQUE NOT NULL for userId?
#TODO:
#Make Carpooler constructor field carpoolGroupId default (unspecified) value a NEW incremented value.  

class Carpooler(db.Model):
    __tablename__ = 'carpoolers'
    
    tabId = db.Column(db.Integer, primary_key=True) #db user id
    userId = db.Column(db.String()) #facebook id of user
    carpoolGroupId = db.Column(db.Integer) #id of group carpooling
    email = db.Column(db.String())
    name = db.Column(db.String())
    address = db.Column(db.String())
    preWindow = db.Column(db.Integer) #Number of minutes available before event start
    need_to_arrive_on_time = db.Column(db.Integer)#1 or 0
    num_seats = db.Column(db.Integer)
    engaged = db.Column(db.Integer) #Is this user fully plugged in?
    state = db.Column(db.Integer) #decision tree state, I guess
    
#    #NOTE:JSON type supported here:
#    result_all = db.Column(JSON)


    def update(self,**kwargs):
        for arg in kwargs:
            if (hasattr(self,arg)):
                setattr(self,arg,kwargs[arg])

    def __init__(self, userId,carpoolGroupId=None,address=None,email=None,name="YOU",preWindow=0,need_to_arrive_on_time=1,num_seats = 0,engaged = 0,state=0,**kwargs):
        self.userId = userId #facebook id of user
        self.carpoolGroupId = carpoolGroupId #id of group carpooling
        self.email = email
        self.name = name
        self.address = address
        self.preWindow = preWindow
        self.need_to_arrive_on_time = need_to_arrive_on_time
        self.num_seats = num_seats
        self.engaged = engaged
        self.state = state
        for arg in kwargs:
            if hasattr(self,arg):
                setattr(self,arg,kwargs[arg])
    
    def __repr__(self):
        return '<id {}>'.format(self.userId)

#Carpooler(self, userId,carpoolGroupId=None,address=None,email=None,name="YOU",preWindow=0,need_to_arrive_on_time=1,num_seats = 0,engaged = 0,state=0)
