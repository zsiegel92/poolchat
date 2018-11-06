# from app import db #INTERACTIONS MOVEMENT
from database import db#INTERACTIONS MOVEMENT
import json
from collections import OrderedDict
#from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.dialects.postgresql import JSON #Import if we use JSON in field
from sqlalchemy.ext.hybrid import hybrid_property
# from flask_bcrypt import generate_password_hash
from encryption import bcrypt

from fieldTrees import fields,poolfields,findPool,tripfields,modesFirst
#from decision_trees import poolertree as fields
import sys

from uuid import uuid1




#TODO: Create third model for "Registration". Then, the "engagement" or "participation" table will be a merge of all three tables on userid and carpoolid
#TODO: Some properties of this relation can't be stored in the user! Such as: time window, address, number of seats, need to arrive, must drive
#FOR NOW: It's as though every carpooler can have multiple pools, but all those pools have the exact same characteristics for the carpooler xD

#NOTE: inputting names as lowercase makes them case-insensitive to SQLAlchemy (including even one uppercase character turns off this feature). So the lowercase class names refer to my classes whose names are uppercase! Confusing!
def random_uuid():
	rand = str(uuid1())
	while Carpooler.query.filter_by(session_id=rand).first() is not None:
		rand = str(uuid1())
	return rand


print('Hello from MODELS.PY!', file=sys.stderr)

def safeformat(str, **kwargs):
		class SafeDict(dict):
				def __missing__(self, key):
						return '{' + key + '}'
		replacements = SafeDict(**kwargs)
		return str.format_map(replacements)


team_membership=db.Table('team_membership',
							 db.Column('carpooler_id', db.Integer,db.ForeignKey('carpooler.id'), nullable=False),
							 db.Column('team_id',db.Integer,db.ForeignKey('teams.id'),nullable=False),
							 db.PrimaryKeyConstraint('carpooler_id', 'team_id') )
team_affiliation=db.Table('team_affiliation',
							 db.Column('pool_id', db.Integer,db.ForeignKey('pool.id'), nullable=False),
							 db.Column('team_id',db.Integer,db.ForeignKey('teams.id'),nullable=False),
							 db.PrimaryKeyConstraint('pool_id', 'team_id') )


	##Module: models.py
	#

class Carpooler(db.Model):
	__tablename__ = 'carpooler'

#    NOT SURE if sqlalchemy column definitions HAVE TO occur outside __init__.
	id = db.Column(db.Integer, primary_key=True,autoincrement=True)

	session_id = db.Column(db.String(length=36),default=random_uuid,unique=True)
	# session_id=db.Column(db.Integer,unique=True)

	_password = db.Column(db.String(128))
	authenticated = db.Column(db.Boolean())
	# Note: pools[0] is the current pool!
	# Note: EVERY member OWNS their pools!
	pools = db.relationship("Trip",back_populates ='member')
	# owned_pools = db.relationship("pool",back_populates = 'owners')
	current_pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'))

	teams = db.relationship('Team',secondary=team_membership,back_populates="members")#carpooler's teams

	fbId = db.Column(db.String()) #facebook id


	selfRep = db.Column(db.Text)
	selfFormalRep = db.Column(db.Text)

	fieldstate = db.Column(db.String()) #decision tree state
	mode = db.Column(db.Text)

	firstname = db.Column(db.String())
	lastname = db.Column(db.String())

	name = db.Column(db.String())
	email = db.Column(db.String(),unique=True)
	menu = db.Column(db.String())
	mode = db.Column(db.String())

	def __init__(self, fbId="",password="",**kwargs):
		super().__init__()
		self.authenticated=False
		self.fbId = fbId #facebook id of user
		self.fieldstate = "name"
		self.menu = "fieldstate"
		self.selfRep = "{}"
		self.selfFormalRep="{}"
		self.mode = "fields"
		print("Trying to set password")
		self.password = password
		print("Successfully set password")
		for arg in kwargs:
			print("setting attribute {}: {}".format(arg, kwargs[arg]))
			if hasattr(self,arg):
				setattr(self,arg,kwargs[arg])
	@hybrid_property
	def password(self):
		return self._password

	@password.setter
	def _set_password(self, plaintext):
		print("setting a password")
		self._password = bcrypt.generate_password_hash(plaintext).decode('utf-8')
		print("password set")

	def is_correct_password(self, plaintext):
		return bcrypt.check_password_hash(self._password, plaintext)

	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.session_id

	def to_copy_dict(self):
		return {"password":self.password,"fbId":self.fbId,"firstname":self.firstname,"lastname":self.lastname,"name":self.name,"email":self.email,"session_id":self.session_id}
	# @Return: nodeOb
	# Can update fields directly, or can update based on current fieldstate with input.
	# based on some field of fields[self.fieldstate] (aka self.quickhead()), such as "is_field", we should either do this, or do something else! Like, maybe, it could be "multi_field". Seems like an "intake_format" nodeOb field is necessary!
	def update(self,input=None,**kwargs):
		print('in Carpooler.update - self.fieldstate = ' + str(self.fieldstate) + ', self.mode = ' + str(self.mode) + ', self.menu = ' + str(self.menu),file=sys.stderr)
		if input:
			if self.fieldstate =='mode':
				self.switch_modes(input)
				return
			#DO STUFF BASED ON Carpooler.mode!!
			if self.mode =='fields':
				for arg in kwargs:
					self.set(fieldstate=arg,value=kwargs[arg])
				self.set(value=input)#default field is self.fieldstate
				self.next(input= input)
			elif self.mode == 'poolfields':
				for arg in kwargs:
					self.setForCurrentPool(fieldstate=arg,value=kwargs[arg])
				self.setForCurrentPool(value=input)
				self.next(input= input)
			elif self.mode == 'tripfields':
				for arg in kwargs:
					self.setForCurrentTrip(fieldstate=arg,value=kwargs[arg])
				self.setForCurrentTrip(value=input)
				self.next(input=input)
			elif self.mode == 'findPool':
				self.next(input=input)
			else:
				print("Error in update! self.mode = " + str(self.mode) + ", self.fieldstate = " + str(self.fieldstate) + ", self.menu = " + str(self.menu),file=sys.stderr)
		else:
			#no input
			self.next()

	# @RETURN: next nodeOb
	# @POST: field state is updated
	# @POST: self.head() will return what this returns
	def next(self,input=None,delayMenuReturn=False):
		print('in next',file=sys.stderr)
		if self.menu == 'fieldstate':
			self.fieldstate = self.nextField(input)
		elif self.menu =='menu':
			self.fieldstate = 'menu'
			self.menu = 'fieldstate'
		#went somewhere from the menu.
		#self.menu = (some field)
		else:
			if not delayMenuReturn:
				self.fieldstate = self.menu
				self.menu = 'menu'
			else:
				self.fieldstate=self.nextField(input)


	def switch_modes(self,input):
		print("in Carpooler.switch_modes. input = " + str(input),file=sys.stderr)
		if input in modesFirst:
			self.mode = input
			self.menu = 'fieldstate'
			self.fieldstate=modesFirst[input]
		else:
			print("ERROR in Carpooler.switch_modes",file=sys.stderr)
			self.next(input)

	def describe_trips(self):
		print("in Carpooler.describe_trips",file=sys.stderr)
		# cartrips = []
		# for cartrip in self.pools:
		# 	cartrips.append(cartrip.pool.id)
		cartrips=[cartrip.pool.id for cartrip in self.pools]

		if len(cartrips) > 1:
			tripstring = "Your carpools have IDs: "
			for ii in range(0,len(cartrips)-1):
				tripstring = tripstring + str(cartrips[ii]) + ", "
			tripstring = tripstring + " and " + str(cartrips[-1]) + "."
		elif len(cartrips)==1:
			tripstring = "Your only carpool has ID: " + str(cartrips[0]) + "."
		else:
			tripstring = "You have no carpools."
		return tripstring

	def getCurrentPool(self):
		print("in getCurrentPool. self.current_pool_id = " +str(self.current_pool_id),file=sys.stderr)
		#checks if self.pools is empty
		if not self.pools:
			trip = Trip()
			pool = Pool()
			trip.pool=pool
			self.pools.append(trip)
			self.current_pool_id=pool.id
			return pool
		else:
			#pools stores ASSOCIATIONS
			for trip in self.pools:
				if trip.pool.id == self.current_pool_id:
					return trip.pool
			#SHOULD NOT GET HERE
			print("Something went wrong in Carpooler.getCurrentPool",file=sys.stderr)
			return Pool()


	def setForCurrentPool(self,value,fieldstate=None):
		print('in self.setForCurrentPool', file=sys.stderr)
		pool=self.getCurrentPool()
		if not fieldstate:
			fieldstate = self.fieldstate
		if hasattr(pool,fieldstate):
			setattr(pool,fieldstate,value)
			pool.updateSelfRepresentations(fieldstate,value)
			print("setting self.getGurrentPool()." + str(fieldstate) + " = " + str(value))
	def getCurrentTrip(self):
		print('in getCurrentTrip',file=sys.stderr)
		#checks if self.pools is empty
		return Trip.query.filter_by(carpooler_id=self.id,pool_id=self.getCurrentPool().id).first()


	def setForCurrentTrip(self,value,fieldstate=None):
		print('in self.setForCurrentTrip', file=sys.stderr)
		trip=self.getCurrentTrip()
		if not trip:
			print("TRIP NOT FOUND",file=sys.stderr)
			return
		if not fieldstate:
			fieldstate = self.fieldstate
		if hasattr(trip,fieldstate):
			setattr(trip,fieldstate,value)
			trip.updateSelfRepresentations(fieldstate,value)
			print("setting self.getCurrentTrip()." + str(fieldstate) + " = " + str(value))

	def getTree(self,mode=None):
		namespace = __import__(__name__)
		if not mode:
			mode = self.mode
		return getattr(namespace,mode,None)#tripfields, poolfields, findPool, or fields

	# @RETURN: a nodeOb, not necessarily the current node.
	def quickField(self,field):
		print('in quickField: mode = ' + self.mode + ', getting field: ' + field + ', self.fieldstate = ' + self.fieldstate + ', self.menu =' + self.menu,file=sys.stderr)
		tree = self.getTree()
		try:
			print("tree= " + str(self.mode) + ", field = " + str(field),file=sys.stderr)
			print("tree[field].next = " + str(tree[field].next),file=sys.stderr)
			return tree[field]
		except Exception as inst:
			print("Error in Carpooler.quickField",file=sys.stderr)
			print(inst,file=sys.stderr)


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
		# CHANGE THIS SHIT
		return self.quickHead().process(response)

	def prefix(self,response): #format time for storage, etc.
		print('in Carpooler.prefix',file=sys.stderr)
		# CHANGE THIS SHIT
		node = self.quickHead()
		return node.prefixer(response)


	def isValid(self,response,obField=None):
		print('in Carpooler.isValid',file=sys.stderr)
		return self.quickHead().isValid(response,obField)


	# TODO: copy and mark up fields of node with data before calling afterSet!
	def afterUpdate(self,response):
		print('in afterUpdate',file=sys.stderr)
		return self.head().afterSet(response) #Has formatted fields
	#called by messengerbot.poolerSay() (in __init__.py)
	def payload(self):
		print('in Carpooler.payload',file=sys.stderr)
		return self.head().payload()


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
		print('in Carpooler.quickHead',file=sys.stderr)
		return self.quickField(self.fieldstate)
	# @RETURN: a nodeOb for the current field, formatted with user data.
	def head(self):
		print('in Carpooler.head',file=sys.stderr)
		return self.format(self.quickHead())

	# Returns the (String) name of the next field
	def nextField(self, input=None):
		print('in Carpooler.nextField',file=sys.stderr)
		return self.quickHead().nextNode(input)


	def format(self, node):
		print("in Carpooler.format",file=sys.stderr)
		if not node:
			print("ERROR",file = sys.stderr)
			return node
		if node.verboseNode:
			if (node.obField=='Carpooler'):
				todict = self.to_dict()
			elif (node.obField=='Trip'):
				todict=self.getCurrentTrip().to_dict()
			elif (node.obField == 'Pool'):
				# return self.getCurrentPool().to_dict()
				todict=self.getCurrentPool().to_dict()
			elif (node.obField == 'findPool'):
				# return self.getCurrentPool().to_dict()
				todict=self.to_dict()
			else:
				todict=self.getCurrentTrip().to_dict()
			node = node.copy()
			if node.nTitle:
				node.nTitle = safeformat(node.nTitle,**todict)
			if node.nQuestion:
				node.nQuestion = safeformat(node.nQuestion,**todict)
			if node.customAfterText:
				node.customAfterText = safeformat(node.customAfterText,**todict)
		return node

	def externalUpdate(self,nextFieldState=None,setForMode=None,**kwargs):
		print('in Carpooler.externalUpdate',file=sys.stderr)
		if not setForMode:
			setForMode = self.mode

		if setForMode =='fields':
			for arg in kwargs:
				self.set(fieldstate=arg,value=kwargs[arg])
		elif setForMode == 'poolfields':
			for arg in kwargs:
				self.setForCurrentPool(fieldstate=arg,value=kwargs[arg])
		elif setForMode == 'tripfields':
			for arg in kwargs:
				self.setForCurrentTrip(fieldstate=arg,value=kwargs[arg])
		else:
			print("Error in externalUpdate! self.mode = " + str(self.mode) + ", self.fieldstate = " + str(self.fieldstate) + ", self.menu = " + str(self.menu) + ", setForMode = " + str(setForMode),file=sys.stderr)

		# Set this last
		if nextFieldState:
			self.set(fieldstate='fieldstate',value=nextFieldState)



	# @POST: If the current node self.quickHead() has a nodeName, the self-representation fields are updated. These can be used to format templates stored in nodeOb's with user data, such as a string field containing greeting = "Hi, {name}", which can be formatted as greeting.format(**json.loads(self.selfRep))
	# Note that only outwards-facing fields should have a nodeName! Otherwise they will land in here, which is a problem because self.to_dict creates an "_all" field containing all fields as text, which should not contain private fields such as "menu" or "fieldstate"
	# @PRE: MAKE SURE 'fieldstate in fields'! There is a check here, but it's mostly bad practice otherwise
	def updateSelfRepresentations(self,input=None,fieldstate=None):
		print('in Carpooler.updateSelfRepresentations',file=sys.stderr)
		if not fieldstate:
			fieldstate = self.fieldstate
		if input:
			if fieldstate in fields:
				if getattr(self.quickField(fieldstate),'nodeName',None):
					tmp = json.loads(self.selfRep, object_pairs_hook=OrderedDict)
					tmp[fieldstate]=str(input)
					self.selfRep = json.dumps(tmp)
					if not getattr(self.quickField(fieldstate),'internalOnly',False):
						tmp = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
						tmp[self.quickField(fieldstate).nodeName]=str(input)
						self.selfFormalRep = json.dumps(tmp)


	def to_dict(self):
		print('in Carpooler.to_dict',file=sys.stderr)
		todict = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
		print("todict: " + str(todict),file=sys.stderr)
		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		todict.update(json.loads(self.selfRep, object_pairs_hook=OrderedDict))
		todict['_property']= self.fieldstate
		todict['tripstring']=self.describe_trips()
		return todict

	def to_dict_formal(self):
		print('in Carpooler.to_dict_formal',file=sys.stderr)
		todict = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
		todict['Trips']=self.describe_trips()
		return todict

	# @Return: String description of carpooler
	def __repr__(self):
		return '<id {}>'.format(self.id)

class Instruction(db.Model):
	__tablename='instructions'
	id = db.Column(db.Integer,primary_key=True)
	pool_id = db.Column(db.Integer,db.ForeignKey('pool.id'))
	instruction=db.Column(db.Text) #stored as json with flask.json.dumps
	dateTime = db.Column(db.DateTime()) #dateTime solution was generated
	success=db.Column(db.String())



class Pool(db.Model):
	__tablename__ = 'pool'

	id = db.Column(db.Integer, primary_key=True) #id of group carpooling

	# owners = db.relationship("carpooler",back_populates="owned_pools")
	members = db.relationship("Trip",back_populates="pool") #JSON dump

	teams = db.relationship('Team',secondary=team_affiliation,back_populates="pools")#pool's teams


	poolName = db.Column(db.String())
	eventDate = db.Column(db.String())
	eventTime = db.Column(db.String())#db.Column(db.Time) #Time of event encoded as int?
	eventDateTime = db.Column(db.DateTime(timezone=True))
	latenessWindow = db.Column(db.Integer())
	eventAddress = db.Column(db.String())
	eventContact = db.Column(db.String())
	eventEmail = db.Column(db.String())
	eventHostOrg = db.Column(db.String()) #Is this user fully plugged in?
	signature = db.Column(db.String()) #decision tree state, I guess
	fireNotice = db.Column(db.String()) #Number of minutes before event that a solution is automatically generated (maybe need plugin or package - cron?)
	# eventCoordinators = db.column(JSON) #List of sender_id's for hosts, to enable editing of event, triggering solutions, etc.
	#distMatrix = db.column(JSON) #Can I store this as a 2d array?
	# solution = db.column(JSON) #Should I store this in a separate db?

	selfRep = db.Column(db.Text)
	selfFormalRep = db.Column(db.Text)

	noticeWentOut=db.Column(db.Boolean())
	optimizedYet = db.Column(db.Boolean())
	optimizationCurrent = db.Column(db.Boolean())

	def __init__(self):
		super().__init__()
		self.selfRep = "{}"
		self.selfFormalRep="{}"

		self.noticeWentOut=False
		self.optimizedYet=False
		self.optimizationCurrent=False


	def updateSelfRepresentations(self,fieldstate,input):
		print('in Pool.updateSelfRepresentations',file=sys.stderr)
		treename = 'poolfields'
		namespace = __import__(__name__) #get current namespace
		tree = getattr(namespace,treename,None)

		if fieldstate in tree: #Should be
			if getattr(tree[fieldstate],'nodeName',None):
				tmp = json.loads(self.selfRep, object_pairs_hook=OrderedDict)
				tmp[fieldstate]=str(input)
				tmp['pool_id']=self.id
				self.selfRep = json.dumps(tmp)

				tmp = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
				tmp['Pool ID']=self.id
				tmp[tree[fieldstate].nodeName]=str(input)
				self.selfFormalRep = json.dumps(tmp)

	def to_dict_formal(self):
		todict = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
		todict['noticeWentOut']=self.noticeWentOut
		todict['optimizedYet']=self.optimizedYet
		todict['optimizationCurrent']=self.optimizationCurrent
		self.selfFormalRep = json.dumps(todict)

		todict['Trips']= [trip.to_dict_formal() for trip in self.members]
		return todict

	def to_dict(self):
		print('in Trip.to_dict',file=sys.stderr)
		todict = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)

		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		todict.update(json.loads(self.selfRep, object_pairs_hook=OrderedDict))
		return todict

	def update(self,**kwargs):
		for arg in kwargs:
			if (hasattr(self,arg)):
				setattr(self,arg,kwargs[arg])

	def __repr__(self):
		return '<id {}>'.format(self.id)


		#participants = participants
		#distMatrix = distMatrix

# class Team_Membership(db.Model):
# 	__tablename__='team_membership'
# 	carpooler_id = db.Column(db.Integer, db.ForeignKey('carpooler.id'),primary_key=True)
# 	member = db.relationship("Carpooler",back_populates="teams")
# 	team = db.relationship("Team",back_populates="members")

# class Team_Affiliation(db.Model):
# 	__tablename__='team_affiliation'
# 	pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'),primary_key=True)
	# pools = db.relationship("Pool",order_by="Pool.id",back_populates="teams")#


class Team(db.Model):
	__tablename__='teams'

	id = db.Column(db.Integer, primary_key=True) #id of team
	name = db.Column(db.String(),unique=True)
	email = db.Column(db.String())
	members = db.relationship("Carpooler",secondary=team_membership,back_populates="teams") #team members
	pools= db.relationship("Pool",secondary=team_affiliation,back_populates="teams")#team pools
	password=db.Column(db.String())

	city = db.Column(db.String())

	def to_dict(self):
		return {'id':self.id,'email':self.email,'name':self.name,'codeword':self.password}
class TempTeam(db.Model):
	__tablename__='temp_teams'
	id = db.Column(db.String(length=36),default=random_uuid,unique=True,primary_key=True)
	name=db.Column(db.String(),unique=True)
	email=db.Column(db.String())
	password=db.Column(db.String())
	carpooler_id=db.Column(db.Integer,db.ForeignKey('carpooler.id'))
	confirmed_email = db.Column(db.Boolean)
	approved = db.Column(db.Boolean)

	def __init__(self):
		super().__init__()
		self.approved = False
		self.confirmed_email=False


class Trip_Distance(db.Model):
	__tablename__ = 'trip_dists'
	pool_id=db.Column(db.Integer,db.ForeignKey('pool.id'),primary_key=True)
	from_carpooler_id = db.Column(db.Integer,db.ForeignKey('carpooler.id'),primary_key=True)
	to_carpooler_id=db.Column(db.Integer,db.ForeignKey('carpooler.id'),primary_key=True)
	feet = db.Column(db.Integer)
	seconds = db.Column(db.Integer)

class Event_Distance(db.Model):
	__tablename__ = 'to_event_dists'
	pool_id=db.Column(db.Integer,db.ForeignKey('pool.id'),primary_key=True)
	carpooler_id = db.Column(db.Integer,db.ForeignKey('carpooler.id'),primary_key=True)
	feet = db.Column(db.Integer)
	seconds = db.Column(db.Integer)

	def to_dict(self):
		return {'pool_id':self.pool_id,'carpooler_id':self.carpooler_id,'feet':self.feet,'seconds':self.seconds}
	def __repr__(self):
		return str(self.to_dict())



class Trip(db.Model):
	__tablename__ = 'trips'

	carpooler_id = db.Column(db.Integer, db.ForeignKey('carpooler.id'),primary_key=True)
	pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'),primary_key=True)
	# , primary_key=True
	# __table_args__ = (db.ForeignKeyConstraint([pool_id],[Pool.id]), {})

	member = db.relationship("Carpooler", back_populates="pools") #trip member
	pool = db.relationship("Pool", back_populates="members")
	# team = db.relationship("Team")


	address = db.Column(db.String())

	num_seats = db.Column(db.Integer)
	preWindow = db.Column(db.Integer)
	on_time = db.Column(db.Integer)
	must_drive = db.Column(db.Integer)

	selfRep = db.Column(db.Text)
	selfFormalRep = db.Column(db.Text)
	poolRepLoaded = db.Column(db.Integer)
	carpoolerRepLoaded = db.Column(db.Integer)

	def __init__(self,carpooler_id=None,pool_id=None):
		super().__init__()
		if carpooler_id is not None:
			self.carpooler_id = carpooler_id
		if pool_id is not None:
			self.pool_id = pool_id
		self.selfRep = "{}"
		self.selfFormalRep="{}"
		self.poolRepLoaded=0
		self.carpoolerRepLoaded=0

	def loadCarpoolerRep(self):
		if (self.member):
			member_prefix = "member_"
			formal_member_prefix = "Traveler's "
			carpoolerFields = json.loads(self.member.selfRep, object_pairs_hook=OrderedDict)
			tripFields = json.loads(self.selfRep, object_pairs_hook=OrderedDict)
			for key, value in carpoolerFields.items():
				tripFields[member_prefix+key]=value
			self.selfRep = json.dumps(tripFields)

			carpoolerFormalFields = json.loads(self.member.selfFormalRep, object_pairs_hook=OrderedDict)
			tripFormalFields = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
			for key, value in carpoolerFormalFields.items():
				tripFormalFields[formal_member_prefix+key]=value
			self.selfFormalRep = json.dumps(tripFormalFields)

			self.carpoolerRepLoaded =1
		else:
			return

	def loadPoolRep(self):
		if (self.pool):
			pool_prefix = "pool_"
			formal_pool_prefix = "Carpool's "
			poolFields = json.loads(self.pool.selfRep, object_pairs_hook=OrderedDict)
			tripFields = json.loads(self.selfRep, object_pairs_hook=OrderedDict)
			for key, value in poolFields.items():
				tripFields[pool_prefix+key]=value
			self.selfRep = json.dumps(tripFields)

			poolFormalFields = json.loads(self.pool.selfFormalRep, object_pairs_hook=OrderedDict)
			tripFormalFields = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
			for key, value in poolFormalFields.items():
				tripFormalFields[formal_pool_prefix+key]=value
			self.selfFormalRep = json.dumps(tripFormalFields)

			self.poolRepLoaded =1
		else:
			return

	def updateSelfRepresentations(self,fieldstate,input):
		print('in Trip.updateSelfRepresentations',file=sys.stderr)
		# treename = 'tripfields'
		# namespace = __import__(__name__) #get current namespace
		# tree = getattr(namespace,treename,None)
		tree = tripfields
		if (self.poolRepLoaded ==0):
			self.loadPoolRep()
		if (self.carpoolerRepLoaded ==0):
			self.loadCarpoolerRep()

		if fieldstate in tree: #Should be
			if getattr(tree[fieldstate],'nodeName',None):
				tmp = json.loads(self.selfRep, object_pairs_hook=OrderedDict)
				tmp[fieldstate]=str(input)
				self.selfRep = json.dumps(tmp)

				tmp = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
				if (getattr(self,'member.name',None) and getattr(self,'pool.poolName',None)):
					tmp['Member']=self.member.name
					tmp['Pool']=self.pool.poolName
				tmp[tree[fieldstate].nodeName]=str(input)
				self.selfFormalRep = json.dumps(tmp)

	def to_dict_formal(self):
		return json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)


	def to_dict(self):
		print('in Trip.to_dict',file=sys.stderr)

		if (self.poolRepLoaded ==0):
			self.loadPoolRep()
		if (self.carpoolerRepLoaded ==0):
			self.loadCarpoolerRep()

		todict = json.loads(self.selfFormalRep, object_pairs_hook=OrderedDict)
		todict['_all']='\n'.join(['%s: %s' % (key, value) for (key, value) in todict.items()])
		todict.update(json.loads(self.selfRep, object_pairs_hook=OrderedDict))
		todict['tripstring']=self.member.describe_trips()
		return todict




from functools import wraps

def ensure_carpooler_notNone(fbId_index=999,carpooler_index=999):

	def wrapper(f):
		@wraps(f)
		def get_carpooler(*args,**kwargs):
			if len(args)>fbId_index:
				fbId = args[fbId_index]
			elif 'recipient_id' in kwargs:
				fbId = kwargs['recipient_id']
			elif 'sender_id' in kwargs:
				fbId=kwargs['sender_id']
			carpooler = Carpooler.query.filter_by(fbId=fbId).first()
			return carpooler

		def wrapped_f(*args,**kwargs):
			args = list(args)

			if len(args)>carpooler_index:
				if not args[carpooler_index]:
					args[carpooler_index]=get_carpooler(*args,**kwargs)
			# elif (len(args)==carpooler_index) and ('carpooler' not in kwargs):
			# 		args[carpooler_index]=get_carpooler(*args,**kwargs)
			elif 'carpooler' in kwargs:
				if not kwargs['carpooler']:
					kwargs['carpooler']=get_carpooler(*args,**kwargs)
			else:
				kwargs['carpooler'] = get_carpooler(*args,**kwargs)
			return(f(*args,**kwargs))
		return wrapped_f
	return wrapper

