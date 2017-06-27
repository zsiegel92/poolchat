from app import messenger, db,app
import requests
from models import  Carpooler,Pool, Trip
#FOR TESTING ONLY,IMPORT SYS
import sys


#TODO: Don't create dicts at function call! Initialize them earlier.
def postback_rules(recipient_id,postback_text,referral_text=None,carpooler=None,fromUnPrefixer=False):
	print("in interactions.postback_rules, fromUnPrefixer = " + str(fromUnPrefixer),file=sys.stderr)
	key_and_args = postback_text.split('/')
	key = key_and_args[0]
	keyPayload = key_and_args[-1]
	rules = {
		"RESPONSE":(lambda obField,*RESP: fillField(recipient_id, "/".join(RESP),obField,carpooler)),
		# "PREFIXED":(lambda *args: prefixprocess(recipient_id,carpooler,*args)),
		"PREFIXED":(lambda *args: postback_rules(recipient_id,"/".join(args),carpooler=carpooler,fromUnPrefixer=True)),
		"GET_STARTED_PAYLOAD":(lambda: getStarted(recipient_id,referral_text)),
		"CREATE_NEW_POOL":(lambda: newPool(recipient_id,carpooler)),
		"FIND_ADDRESS":(lambda inputted_address: findAddress(recipient_id,inputted_address,carpooler)),
		"FIND_POOL":(lambda inputted_pool_id: findPool(recipient_id,inputted_pool_id,carpooler)),
		"SWITCH_MODE":(lambda mode: switchMode(recipient_id,mode,carpooler)),
		"GOTO_NODE":(lambda nodeName: go_to_node(recipient_id,nodeName,carpooler)),
		"MENU_RETURN":(lambda nodeName: menu_go_to_node(recipient_id,nodeName,carpooler)),
		"Hello":(lambda: messenger.say(recipient_id,'World_PB2')),
		"thing1":(lambda: messenger.say(recipient_id,'thing2_PB2'))
	}

	if key in rules:
		rules[key](*key_and_args[1:])
		if key!="PREFIXED":
			pester(recipient_id,carpooler)
		else:
			pass#key=="PREFIXED",looping silently one time only to strip prefix
	else:
		if not fromUnPrefixer:
			noPrefixResponse(recipient_id,response=keyPayload)
		else:
			print("ERROR IN interactions.postback_rules - loop detected.",file=sys.stderr)
			messenger.say(recipient_id, "I didn't understand your input!")


def quick_rules(recipient_id,qr_text):
	postback_rules(recipient_id,qr_text)


def text_rules(recipient_id, message_text=""):
	print("in interactions.text_rules - message_text = " + str(message_text),file =sys.stderr)
	rules = {
		"Hello": "World",
		"Foo": "Bar",
		"Menu":"sendmenu",
		"Unsubscribe":"unsubscribe"
	}
	specialRules = {"CREATE_POOL":"It looks like you want to create a carpool!"}
	if message_text in specialRules:
		messenger.say(recipient_id,"You just did something amazing (but I'm not doing anything about it yet)!")
		messenger.say(recipient_id,specialRules[message_text])
	elif message_text in rules:
		messenger.say(recipient_id, rules[message_text])
	else:
		noPrefixResponse(recipient_id,response=message_text)

def go_to_node(recipient_id,nodeName,carpooler=None):
	print("in interactions.go_to_node", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=recipient_id).first()
	carpooler.fieldstate = nodeName
	db.session.commit()

def menu_go_to_node(recipient_id,nodeName,carpooler=None):
	print("in interactions.menu_go_to_node",file=sys.stderr)
	if not carpooler:
		carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()
	carpooler.menu = nodeName
	carpooler.update()
	db.session.commit()


# @Pre: carpooler with fbId = recipient_id exists!
def switchMode(recipient_id,mode,carpooler=None):
	print("in interactions.switchMode", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=recipient_id).first()
	carpooler.switch_modes(mode)
	db.session.commit()



# @Pre: carpooler with fbId = recipient_id exists!
def newPool(recipient_id,carpooler=None):
	print("in interactions.newPool",file=sys.stderr)
	if not carpooler:
		carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()

	trip=Trip()
	trip.pool=Pool()
	carpooler.pools.append(trip)
	#Have to populate carpooler.pools and trip.pool (at least) before adding/committing due to non-null constraint!

	# db.session.add(trip) #MAY NEED THIS, MAYBE NOT!
	db.session.commit()

	#Have to commit before this is populated! This is why this function should be external to models.py, maybe.
	carpooler.current_pool_id = trip.pool.id

	carpooler.switch_modes('poolfields')

	db.session.commit()

	tripstring = carpooler.describe_trips()

	messenger.say(recipient_id,"You just created a carpool! Your NEW carpool's 'Pool ID' is " + str(trip.pool.id) + ". Don't forget about your other trips! " + tripstring)

def findAddress(sender_id,inputted_address,carpooler=None):
	print("in interactions.findAddress",file=sys.stderr)
	messenger.say(sender_id,"Here is a picture of that address! If this isn't right, you can change it later.")

	GMAPS_GEOCODE_API_TOKEN = app.config['GMAPS_GEOCODE_API_TOKEN']

	geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
	querystring = {"address":inputted_address,"key":GMAPS_GEOCODE_API_TOKEN}
	response = requests.request("GET", geocode_url, params=querystring)
	response=response.json()

	formatted_address =response['results'][0]['formatted_address']
	lat = response['results'][0]['geometry']['location']['lat']
	lon = response['results'][0]['geometry']['location']['lng']


	GMAPS_STATIC_API_TOKEN = app.config['GMAPS_STATIC_API_TOKEN']
	marker_attributes="color:red|{lat},{lon}".format(lat=lat,lon=lon)
	static_maps_base_url = "https://maps.googleapis.com/maps/api/staticmap"
	querystring = {"center":str(lat)+","+str(lon),"zoom":"14","size":"400x400","markers":marker_attributes,"key":GMAPS_STATIC_API_TOKEN}
	response = requests.request("GET", static_maps_base_url, params=querystring,stream=True)
	full_url= response.url
	del response
	# img = response.content
	messenger.send_image(sender_id,full_url)
	fillField(sender_id,formatted_address,carpooler=carpooler)
	db.session.commit()

# @Pre: carpooler with fbId = recipient_id exists!
def findPool(recipient_id,pool_id,carpooler=None):
	print("in interactions.findPool", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=recipient_id).first()

	pool = Pool.query.filter_by(id=pool_id).first()
	if pool:
		trip = Trip.query.filter_by(carpooler_id=carpooler.id,pool_id=pool.id).first()
		if not trip:
			trip = Trip()
			trip.pool=pool
			carpooler.pools.append(trip)
			messenger.say(recipient_id,"You just joined the carpool with ID " + str(pool.id)+ "!")
		else:
			messenger.say(recipient_id,"You are already part of this carpool! We will go back and edit your information.")

		carpooler.current_pool_id= pool.id
		carpooler.switch_modes('tripfields')
	else:
		messenger.say(recipient_id,"There is no such carpool :(")

	db.session.commit()






def switchCurrentPool(recipient_id,more):
	print("in interactions.switchCurrentPool", file=sys.stderr)
	pass

def process_referral(sender_id,referral_text,postback_text=None):
	#Triggered by visit to m.me/GroupThere?ref=myparam
	messenger.say(sender_id,"Referring to "+ referral_text + " through: m.me/" + app.config['APP_NAME'] + "?ref=" + referral_text) #Do nothing with referral for now.
	pester(sender_id)

def getStarted(sender_id,referral_text=None,message_text=None):
	print("in interactions.getStarted", file=sys.stderr)
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
	print("in interactions.pester", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=sender_id).first()
	if not carpooler:
		messenger.say(sender_id,"unsuccessful pester")
		getStarted(sender_id)
	else:
		messenger.poolerSay(sender_id,carpooler)


def getInfo(sender_id):
	print("in interactions.getInfo", file=sys.stderr)
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


def fillField(sender_id,response,obField=None,carpooler=None):
	print("in interactions.fillField", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=sender_id).first()
	if carpooler:
		if carpooler.isValid(response,obField):
			response = carpooler.process(response) #format time for storage, etc.
			# messenger.say(sender_id,"Processed response is: " + str(response))
			messenger.say(sender_id, carpooler.afterUpdate(response))
			carpooler.update(input = response)
			db.session.commit()
		else:
			print("carpooler.isValid('"+response+"') = " + str(carpooler.isValid(response)),file=sys.stderr)
			messenger.say(sender_id,"I need a valid response!")
	else:
		getStarted(sender_id,message_text=response)


#        messenger.say(sender_id,'exiting db function')
#Add params argument! Dict? List?
#def toDB(sender_id,carpoolGroupId=None,address=None,email=None,name=None,preWindow=None,need_to_arrive_on_time=None,num_seats = None,engaged = None,state=None):
def noPrefixResponse(sender_id,response,**kwargs):
	print("in interactions.noPrefixResponse, response = " + str(response),file=sys.stderr)
	try:
		carpooler = Carpooler.query.filter_by(fbId=sender_id).first()

		if carpooler:
			response = carpooler.prefix(response) #format time for storage, etc.
			postback_rules(sender_id,'PREFIXED/' + response,carpooler=carpooler)
		else:
			getStarted(sender_id,message_text=response)
	except Exception as exc:
		messenger.say(sender_id,"Error accessing my database")
		print("Error in noPrefixResponse",file=sys.stderr)
		print(str(exc),file=sys.stderr)
