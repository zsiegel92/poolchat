from app import messenger, db,app
import requests
from models import  Carpooler,Pool, Trip

#FOR TESTING ONLY,IMPORT SYS
import sys

#TODO: Don't create dicts at function call! Initialize them earlier.
def postback_rules(recipient_id,postback_text,referral_text=None):
	print("in interactions.postback_rules - postback_text = " + str(postback_text),file =sys.stderr)
	key_and_args = postback_text.split('/')
	key = key_and_args[0]
	keyPayload = key_and_args[-1]

	rules = {
		"RESPONSE":(lambda OF,RESP: toDB(recipient_id,RESP)),
		"GET_STARTED_PAYLOAD":(lambda: getStarted(recipient_id,referral_text)),
		"CREATE_NEW_POOL":(lambda: newPool(recipient_id)),
		"FIND_POOL":(lambda: 5),
		"JOIN_POOL":(lambda poolid: joinPool(recipient_id,poolid)),
		"Hello":(lambda: messenger.say(recipient_id,'World_PB2')),
		"thing1":(lambda: messenger.say(recipient_id,'thing2_PB2'))
	}

	if key in rules:
		rules[key](*key_and_args[1:])
	else:
		toDB(recipient_id,response=keyPayload)

def quick_rules(recipient_id,qr_text):
	postback_rules(recipient_id,qr_text)


def text_rules(recipient_id, message_text=""):
	print("in interactions.text_rules - message_text = " + str(message_text),file =sys.stderr)
	rules = {
		"Hello": "World",
		"Foo": "Bar",
		"Menu":"sendmenu"
	}
	specialRules = {"CREATE_POOL":"It looks like you want to create a carpool!"}
	if message_text in specialRules:
		messenger.say(recipient_id,"You just did something amazing!")
		messenger.say(recipient_id,specialRules[message_text])
	elif message_text in rules:
		messenger.say(recipient_id, rules[message_text])
	else:
		toDB(recipient_id,response=message_text)
def newPool(recipient_id):
	print("in interactions.newPool",file=sys.stderr)
	carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()

	trip=Trip()
	trip.pool=Pool()
	carpooler.pools.append(trip)
	#Have to populate carpooler.pools and trip.pool (at least) before adding/committing due to non-null constraint!

	# db.session.add(trip) #MAY NEED THIS, MAYBE NOT!
	db.session.commit()

	#Have to commit before this is populated! This is why this function should be external to models.py, maybe.
	carpooler.current_pool_id = trip.pool.id


	carpooler.fieldstate ='mode'
	carpooler.update(input='poolfields')


	db.session.commit()

	cartrips = []
	for cartrip in carpooler.pools:
		cartrips.append(cartrip.pool.id)
	if len(cartrips) > 1:
		tripstring = "Your carpools have IDs: "
		for ii in range(0,len(cartrips)-1):
			tripstring = tripstring + str(cartrips[ii]) + ", "
		tripstring = tripstring + " and " + str(cartrips[-1]) + "."
	else:
		tripstring = "Your only carpool has ID: " + str(cartrips[0]) + "."

	messenger.say(recipient_id,"You just created a carpool! Your NEW carpool's 'Pool ID' is " + str(trip.pool.id) + ". Don't forget about your other trips! " + tripstring)

	pester(recipient_id,carpooler)


def joinPool(recipient_id,poolId):
	carpooler = Carpooler.query.filter_by(fbId=recipient_id).first()
	pool = Pool.query.filter_by(id=poolId).first()
	trip = Trip()
	trip.member=pool
	carpooler.pools.insert(0,trip)

	messenger.say(recipient_id,"You just created a carpool! Your pool ID is " + str(poolId))
	pester(recipient_id,carpooler)


def findPool(recipient_id):
	messenger.say(recipient_id,"Are any of these the pool you'd like to join? (Build out interactions.findPool function)")
	pester(recipient_id)

def switchCurrentPool(recipient_id,more):
	pass

def process_referral(sender_id,referral_text,postback_text=None):
	#Triggered by visit to m.me/GroupThere?ref=myparam
	messenger.say(sender_id,"Referring to "+ referral_text + " through: m.me/" + app.config['APP_NAME'] + "?ref=" + referral_text) #Do nothing with referral for now.
	toDB(sender_id)

def getStarted(sender_id,referral_text=None,message_text=None):
	carpooler = Carpooler.query.filter_by(fbId=sender_id).first() #Should have been added already

	if referral_text:
		messenger.say(sender_id,"You have been referred by: " + referral_text)
	#Query Pool.query.filter_by(referral_text=referral_text).first()
	if carpooler is not None:
		messenger.say(sender_id,"Something weird happened - I already know you!")
		pester(sender_id, carpooler)
		return
	carpooler = Carpooler(fbId=sender_id)
	info = getInfo(sender_id)
	if 'first_name' in info:
		print('carpooler.name: ' + str(carpooler.name))
		# carpooler.fieldstate='email'
		carpooler.externalUpdate(name=str(info['first_name'])+" " + str(info['last_name']),nextFieldState='email')
		print('carpooler.name: ' + str(carpooler.name))
	if info['timezone'] != -7:
		messenger.say(sender_id,"You are probably in the wrong timezone for this!")
	db.session.add(carpooler)
	db.session.commit()
	messenger.say(sender_id,"Added you to my database, madude! =D")
	pester(sender_id,carpooler)

#TODO: Change from messenger.say to messenger.send, where the node stores a general-purpose payload (sans sender_id, though).
#def pester(sender_id,node):
##    messenger.say(sender_id,nextNode.prompt())
##    messenger.say(sender_id,nextNode.ask())
#    messenger.nodeSay(sender_id,node)

def pester(sender_id,carpooler=None):
	if carpooler:
		messenger.poolerSay(sender_id,carpooler)
	else:
		toDB(sender_id)

def getInfo(sender_id):
	access_token = app.config["MESSENGER_PLATFORM_ACCESS_TOKEN"]
	url = "https://graph.facebook.com/v2.6/" + sender_id
	#unused possible args:profile_pic
	querystring = {"fields":"first_name,last_name,locale,timezone,gender","access_token":access_token}

	# headers = {
	#     'cache-control': "no-cache",
	#     'postman-token': "917fd3a5-4af1-0bfa-17f3-d4ee11a7c690"
	#     }
	# headers=headers,
	response = requests.request("GET", url, params=querystring)

	# messenger.say(sender_id,response.text)
	return response.json()


#Add params argument! Dict? List?
#def toDB(sender_id,carpoolGroupId=None,address=None,email=None,name=None,preWindow=None,need_to_arrive_on_time=None,num_seats = None,engaged = None,state=None):
def toDB(sender_id,response=None,**kwargs):
	try:
		carpooler = Carpooler.query.filter_by(fbId=sender_id).first()
		if carpooler == None:
			getStarted(sender_id,message_text=response)
		else:
			if response:
				if carpooler.isValid(response):
					response = carpooler.process(response) #format time for storage, etc.
					messenger.say(sender_id, carpooler.afterUpdate(response))
					carpooler.update(input = response)
					db.session.commit()
				else:
					messenger.say(sender_id,"I need a valid response!")
			pester(sender_id,carpooler)
	except Exception as exc:
		messenger.say(sender_id,"Error accessing my database")
		print("Unable to add item to database.")
		print(str(exc))
	else:
		pass
#        messenger.say(sender_id,'exiting db function')
