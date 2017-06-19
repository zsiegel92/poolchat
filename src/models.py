from app import db,json
#from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field
from fieldTrees import fields,poolfields,findPool,tripfields,modesFirst
#from decision_trees import poolertree as fields
import sys

#TODO: Create third model for "Registration". Then, the "engagement" or "participation" table will be a merge of all three tables on userid and carpoolid
#TODO: Some properties of this relation can't be stored in the user! Such as: time window, address, number of seats, need to arrive, must drive
#FOR NOW: It's as though every carpooler can have multiple pools, but all those pools have the exact same characteristics for the carpooler xD

#NOTE: inputting names as lowercase makes them case-insensitive to SQLAlchemy (including even one uppercase character turns off this feature). So the lowercase class names refer to my classes whose names are uppercase! Confusing!



print('Hello from MODELS.PY!', file=sys.stderr)

class Carpooler(db.Model):
	__tablename__ = 'carpooler'

#    NOT SURE if sqlalchemy column definitions HAVE TO occur outside __init__.
	id = db.Column(db.Integer, primary_key=True)

	# Note: pools[0] is the current pool!
	# Note: EVERY member OWNS their pools!
	pools = db.relationship("Trip",back_populates = 'member')
	# owned_pools = db.relationship("pool",back_populates = 'owners')


	fbId = db.Column(db.String()) #facebook id


	selfRep = db.Column(db.Text)
	selfFormalRep = db.Column(db.Text)

	fieldstate = db.Column(db.String()) #decision tree state
	mode = db.Column(db.Text)



	for field in fields:
		if fields[field].obField == 'Carpooler':
			exec(field + "= db.Column(db." + fields[field].nType +"())") #example: fbId = db.Column(db.String())
	del field


	def __init__(self, fbId,**kwargs):
		super().__init__()
		self.fbId = fbId #facebook id of user
		self.fieldstate = "name"
		self.menu = "fieldstate"
		self.selfRep = "{}"
		self.selfFormalRep="{}"
		self.mode = "fields"
		for arg in kwargs:
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])




	# @Return: nodeOb
	# Can update fields directly, or can update based on current fieldstate with input.
	# based on some field of fields[self.fieldstate] (aka self.quickhead()), such as "is_field", we should either do this, or do something else! Like, maybe, it could be "multi_field". Seems like an "intake_format" nodeOb field is necessary!
	def update(self,input=None,**kwargs):
		print('in update',file=sys.stderr)
		for arg in kwargs:
			self.set(fieldstate=arg,value=kwargs[arg])
		if input:
			if self.fieldstate =='mode':
				print("In models.update,fieldstate='mode'.",file=sys.stderr)
				if input in modesFirst:
					print("In models.update changing modes,input in modesFirst. modesFirst[input] = " + modesFirst[input],file=sys.stderr)
					self.mode = input
					self.fieldstate=modesFirst[input]
					return
				else:
					print("In models.update changing modes,input NOT in modesFirst.",file=sys.stderr)
					self.next(input=input)
					return

			if self.quickHead().obField=='Carpooler':
				self.set(value=input)#default field is self.fieldstate
				self.next(input= input)
			elif self.quickHead().obField=='Pool':
				self.setForCurrentPool(value=input)
				self.next(input= input)
			elif self.quickHead().obField=='Trip':
				#Do Trip stuff
				#Look up "SQLAlchemy "
				self.next(input=input)
			elif self.quickHead().obField=='findPool':
				self.next(input=input)
			elif self.quickHead().obField=='tripfields':
				self.next(input=input)
			else:
				self.next(input=input)
			return

	def getCurrentPool(self):
		print('in getCurrentPool',file=sys.stderr)
		#checks if self.pools is empty
		if not self.pools:
			#DON'T DO THIS HERE! Instead, trigger Interactions.newPool or return message saying "no such pool"
			pool = Pool(carpooler=self)
			# self.pool = pool.id #if self.pool is int
			self.pools.insert(0,pool)
		#pools stores ASSOCIATIONS
		return self.pools[0].pool
		#Find and return the current pool, based on carpooler fields...

	def setForCurrentPool(self,value,fieldstate=None):
		print('in self.setForCurrentPool', file=sys.stderr)
		pool=self.getCurrentPool()
		if not fieldstate:
			fieldstate = self.fieldstate
		if hasattr(pool,fieldstate):
			print('setting pool.'+fieldstate+' to ' + value, file=sys.stderr)
			setattr(pool,fieldstate,value)

	# @RETURN: next nodeOb
	# @POST: field state is updated
	# @POST: self.head() will return what this returns
	def next(self,input=None):
		print('in next',file=sys.stderr)
		if self.menu == 'fieldstate':
			self.fieldstate = self.nextField(input)
		elif self.menu =='menu':
			self.fieldstate = 'menu'
			self.menu = 'fieldstate'
		#went somewhere from the menu.
		else:
			self.fieldstate = self.menu
			self.menu = 'menu'

	# @RETURN: a nodeOb, not necessarily the current node.
	def quickField(self,field):
		print('in quickField: mode = ' + self.mode + ', getting field: ' + field + ', self.fieldstate = ' + self.fieldstate + ', self.menu =' + self.menu,file=sys.stderr)
		namespace = __import__(__name__) #get current namespace
		tree = getattr(namespace,self.mode,None)
		try:
			return tree[field]
		except Exception as inst:
			print()
			print(inst,file=sys.stderr)
			print(
				'trying to get a node that is not in tree',
				file=sys.stderr
				)

	# Call afterset from here?
	#Assign input to the variable whose name is stored in fieldstate. fieldstate is unchanged.
	def set(self,value,fieldstate=None):
		print('in self.set', file=sys.stderr)
		if not fieldstate:
			fieldstate = self.fieldstate
		if hasattr(self,fieldstate):
			print('setting carpooler.'+fieldstate+' to ' + value, file=sys.stderr)
			setattr(self,fieldstate,value)
			self.updateSelfRepresentations(fieldstate=fieldstate,input=value)




	# Unused
	def returnToMenu(self):
		print('in returnToMenu',file=sys.stderr)
		return (self.menu !='fieldstate')



	def process(self,response): #format time for storage, etc.
		print('in process',file=sys.stderr)
		if (self.quickHead().findPool):
			pool = Pool.query.filter_by(response).first()
			return pool.poolName
		return self.quickHead().process(response)


	def isValid(self,response):
		print('in isValid',file=sys.stderr)
		return self.quickHead().isValid(response)


	# TODO: copy and mark up fields of node with data before calling afterSet!
	def afterUpdate(self,response):
		print('in afterUpdate',file=sys.stderr)
		return self.head().afterSet(response) #Has formatted fields

#    @RETURN: a nodeOb formatted with user data.
	def getField(self,field):
		print('in getField',file=sys.stderr)
		try:
			# node = fields[field]
			node = self.quickField(field)
			return self.format(node)
		except Exception as inst:
			print(inst,file=sys.stderr)
			print('trying to get a field that is not in fields',file=sys.stderr)

	# @RETURN: a nodeOb for the current field
	def quickHead(self):
		print('in quickHead',file=sys.stderr)
		return self.quickField(self.fieldstate)
	# @RETURN: a nodeOb for the current field, formatted with user data.
	def head(self):
		print('in head',file=sys.stderr)
		return self.format(self.quickHead())

	# Returns the (String) name of the next field
	def nextField(self, input=None):
		print('in nextField',file=sys.stderr)
		print("Next field is: " + str(self.quickHead().nextNode(input)), file=sys.stderr)
		return self.quickHead().nextNode(input)


	#called by messengerbot.poolerSay() (in __init__.py)
	def payload(self):
		print('in payload. self.fieldstate = ' + self.fieldstate,file=sys.stderr)
		return self.head().payload()

	def format(self, node):
		print('in format',file=sys.stderr)
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

	def externalUpdate(self,nextFieldState=None,**kwargs):
		print('in externalUpdate',file=sys.stderr)
		#check hasattr?
		for arg in kwargs:
			self.set(fieldstate=arg,value=kwargs[arg])
		# Set this last
		if nextFieldState:
			self.set(fieldstate='fieldstate',value=nextFieldState)



	# @POST: If the current node self.quickHead() has a nodeName, the self-representation fields are updated. These can be used to format templates stored in nodeOb's with user data, such as a string field containing greeting = "Hi, {name}", which can be formatted as greeting.format(**json.loads(self.selfRep))
	# Note that only outwards-facing fields should have a nodeName! Otherwise they will land in here, which is a problem because self.to_dict creates an "_all" field containing all fields as text, which should not contain private fields such as "menu" or "fieldstate"
	# @PRE: MAKE SURE 'fieldstate in fields'! There is a check here, but it's mostly bad practice otherwise
	def updateSelfRepresentations(self,input=None,fieldstate=None):
		print('in updateSelfRepresentations',file=sys.stderr)
		if not fieldstate:
			fieldstate = self.fieldstate
		if input:
			if fieldstate in fields:
				if getattr(self.quickField(fieldstate),'nodeName',None):
					tmp = json.loads(self.selfRep)
					tmp[fieldstate]=str(input)
					self.selfRep = json.dumps(tmp)

					tmp = json.loads(self.selfFormalRep)
					tmp[self.quickField(fieldstate).nodeName]=str(input)
					self.selfFormalRep = json.dumps(tmp)


	def to_dict(self):
		print('in to_dict',file=sys.stderr)
		todict = json.loads(self.selfFormalRep)
		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		todict.update(json.loads(self.selfRep))
		todict['_property']= self.fieldstate
		print(json.dumps(todict), file=sys.stderr)
		return todict


	# @Return: String description of carpooler
	def __repr__(self):
		return '<id {}>'.format(self.id)



class Pool(db.Model):
	__tablename__ = 'pool'

	id = db.Column(db.Integer, primary_key=True) #id of group carpooling

	# owners = db.relationship("carpooler",back_populates="owned_pools")
	members = db.relationship("Trip",back_populates="pool") #JSON dump

	poolName = db.Column(db.String())
	eventDate = db.Column(db.Date())
	eventTime = db.Column(db.String())#db.Column(db.Time) #Time of event encoded as int?
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


	def __init__(self,carpooler = None,**kwargs):
		for arg in kwargs:
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])
		if carpooler:
			self.owner = carpooler
			self.members = carpooler


		#participants = participants
		#distMatrix = distMatrix


class Trip(db.Model):
	__tablename__ = 'trips'

	carpooler_id = db.Column(db.Integer, db.ForeignKey('carpooler.id'), primary_key=True)
	pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'), primary_key=True)

	member = db.relationship("Carpooler", back_populates="pools")
	pool = db.relationship("Pool", back_populates="members")

	address = db.Column(db.String())
	num_seats = db.Column(db.Integer)
	preWindow = db.Column(db.Integer)
	on_time = db.Column(db.Integer)
	must_drive = db.Column(db.Integer)


