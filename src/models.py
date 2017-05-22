from app import db
#from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field
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
	engaged = db.Column(db.Integer) #Is this user fully plugged in?
	fieldstate = db.Column(db.String()) #decision tree state
	# selfRep = db.Column(JSON)
	# selfFormalRep = db.Column(JSON)

	carpools = db.relationship('Pool',secondary=participation,backref=db.backref('carpoolers',lazy='dynamic'))
	for field in fields:
		exec(field + "= db.Column(db." + fields[field].nType +"())") #example: fbId = db.Column(db.String())
	del field


	def __init__(self, fbId,**kwargs):
		super().__init__()
		self.fbId = fbId #facebook id of user
		self.fieldstate = "name"
		self.menu = "fieldstate"
		# self.selfRep = {}
		# self.selfFormalRep={}
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
			# self.selfRep[self.fieldstate]=str(input)
			#formal name key - NOTE: this doesn't exist for every node that is updated here.
			# try:
			# 	self.selfFormalRep[fields[self.fieldstate].nodeName]=str(input)
			# except:
			# 	pass
		return self.next(input)

#    @RETURN: a nodeOb, not necessarily the current node.
	def getField(self,field):
		node = fields[field]
		node = node.copy()
		todict = self.to_dict()
		node.nTitle = node.nTitle.format(**todict)
		node.nQuestion = node.nQuestion.format(**todict)
		return node

	def quickField(self,field):
		return fields[field]

	#slower version of head for external use. Fields are replaced in prompt, etc.
	def head(self):
		node = self.quickHead()
		return self.format(node)

	def format(self, node):
		node = node.copy()
		todict = self.to_dict()
		if node.nTitle:
			node.nTitle = node.nTitle.format(**todict)
		if node.nQuestion:
			node.nQuestion = node.nQuestion.format(**todict)
		if node.customAfterText:
			node.customAfterText = node.customAfterText.format(**todict)
		return node

	#quick version of head for internal use
	def quickHead(self):
		return fields[self.fieldstate]

	def nextField(self, input=None):
		print("Next field is: " + str(self.quickHead().nextNode(input)), file=sys.stderr)
		return self.quickHead().nextNode(input)

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


	def isValid(self,response):
		return self.quickHead().isValid(response)
	def process(self,response): #format time for storage, etc.
		return self.quickHead().process(response)

	#TODO: copy and mark up fields of node with data before calling afterSet!
	def afterSet(self,response):
		return self.head().afterSet(response) #Has formatted fields

	def payload(self):
		return self.head().payload()

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
	#excluded = ["menu","confirming"]
	def to_dict(self):
		print('returning a dict!', file=sys.stderr)
		todict = {}
		#Compile all named fields with formal name (nodeName):
		for field in fields:
			if fields[field].nodeName:
				todict[fields[field].nodeName]=getattr(self,field,None)
		# todict={"Name":self.name,"Email Address":self.email,"address":self.address,"Number of Seats":self.num_seats,"Minutes available for driving":self.preWindow,"Have to arrive on time":self.on_time,"Have to drive self":self.must_drive}
		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		#Add all fields with dictionary name:
		for field in fields:
			if fields[field].nodeName:
				todict[field]=getattr(self,field,None)
		todict['_property']=self.fieldstate
		return todict


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
	# solution = db.column(JSON) #Should I store this in a separate db?
	fireTime = db.column(db.Integer) #Number of minutes before event that a solution is automatically generated (maybe need plugin or package - cron?)
	# eventCoordinators = db.column(JSON) #List of sender_id's for hosts, to enable editing of event, triggering solutions, etc.
	#distMatrix = db.column(JSON) #Can I store this as a 2d array?

	def update(self,**kwargs):
		for arg in kwargs:
			if (hasattr(self,arg)):
				setattr(self,arg,kwargs[arg])

	def __repr__(self):
		return '<id {}>'.format(self.userId)


	def __init__(self,**kwargs):
		for arg in kwargs:
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])
		#participants = participants
		#distMatrix = distMatrix


