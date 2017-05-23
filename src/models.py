from app import db,json
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
	selfRep = db.Column(db.Text)
	selfFormalRep = db.Column(db.Text)
	carpools = db.relationship('Pool',secondary=participation,backref=db.backref('carpoolers',lazy='dynamic'))
	for field in fields:
		exec(field + "= db.Column(db." + fields[field].nType +"())") #example: fbId = db.Column(db.String())
	del field


	def __init__(self, fbId,**kwargs):
		super().__init__()
		self.fbId = fbId #facebook id of user
		self.fieldstate = "name"
		self.menu = "fieldstate"
		self.selfRep = "{}"
		self.selfFormalRep="{}"
		self.selfAllRep="{}"
		for arg in kwargs:
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])

	# @Return: nodeOb
	# Can update fields directly, or can update based on current fieldstate with input.
	# based on some field of fields[self.fieldstate] (aka self.quickhead()), such as "is_field", we should either do this, or do something else! Like, maybe, it could be "multi_field". Seems like an "intake_format" nodeOb field is necessary!
	def update(self,input=None,**kwargs):
		for arg in kwargs:
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])
		if input:
			#Assign input to the variable whose name is stored in fieldstate. fieldstate is unchanged.
			setattr(self,self.fieldstate,input)
			self.updateSelfRepresentations(input)
		return self.next(input)
	# @RETURN: next nodeOb
	# @POST: field state is updated
	# @POST: self.head() will return what this returns
	def next(self,input=None):
		if self.menu == 'fieldstate':
			self.fieldstate = self.nextField(input)
			return self.head()
		else:
			self.fieldstate = self.menu
			self.menu = 'menu'
			return self.head()

	def returnToMenu(self):
		return (self.menu !='fieldstate')
	def isValid(self,response):
		return self.quickHead().isValid(response)
	def process(self,response): #format time for storage, etc.
		return self.quickHead().process(response)
	# TODO: copy and mark up fields of node with data before calling afterSet!
	def afterUpdate(self,response):
		return self.head().afterSet(response) #Has formatted fields

	# @RETURN: a nodeOb, not necessarily the current node.
	def quickField(self,field):
		return fields[field]
#    @RETURN: a nodeOb formatted with user data.
	def getField(self,field):
		node = fields[field]
		return self.format(node)

	# @RETURN: a nodeOb for the current field
	def quickHead(self):
		return fields[self.fieldstate]
	# @RETURN: a nodeOb for the current field, formatted with user data.
	def head(self):
		node = self.quickHead()
		return self.format(node)
	# Returns the (String) name of the next field
	def nextField(self, input=None):
		print("Next field is: " + str(self.quickHead().nextNode(input)), file=sys.stderr)
		return self.quickHead().nextNode(input)


	def payload(self):
		return self.head().payload()
	def format(self, node):
		if node.verboseNode:
			node = node.copy()
			todict = self.to_dict()
			if node.nTitle:
				node.nTitle = node.nTitle.format(**todict)
			if node.nQuestion:
				node.nQuestion = node.nQuestion.format(**todict)
			if node.customAfterText:
				node.customAfterText = node.customAfterText.format(**todict)
		return node

	# @POST: If the current node self.quickHead() has a nodeName, the self-representation fields are updated. These can be used to format templates stored in nodeOb's with user data, such as a string field containing greeting = "Hi, {name}", which can be formatted as greeting.format(**json.loads(self.selfRep))
	# Note that only outwards-facing fields should have a nodeName! Otherwise they will land in here, which is a problem because self.to_dict creates an "_all" field containing all fields as text, which should not contain private fields such as "menu" or "fieldstate"
	def updateSelfRepresentations(self,input=None):
		if input:
			if self.quickHead().nodeName:
				tmp = json.loads(self.selfRep)
				tmp[self.fieldstate]=str(input)
				self.selfRep = json.dumps(tmp)

				tmp = json.loads(self.selfFormalRep)
				tmp[fields[self.fieldstate].nodeName]=str(input)
				self.selfFormalRep = json.dumps(tmp)

	def to_dict(self):
		todict = json.loads(self.selfFormalRep)
		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		todict.update(json.loads(self.selfRep))
		todict['_property']= self.fieldstate
		print(json.dumps(todict), file=sys.stderr)
		return todict


	# @POST: prints description of self
	def printout(self):
		for field in fields:
			print(field + ": " + str(getattr(self,field)))

	# @RETURN: String description of carpooler
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

	# @Return: String description of carpooler
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


