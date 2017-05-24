from app import messenger, db,app
import requests
from models import  Carpooler#, Pool, participation

#TODO: Don't create dicts at function call! Initialize them earlier.
def postback_rules(recipient_id,postback_text,referral_text=None):
	rules = {
		"GET_STARTED_PAYLOAD":(lambda: getStarted(recipient_id,referral_text)),
		"Hello":(lambda: messenger.say(recipient_id,'World_PB2')),
		"thing1":(lambda: messenger.say(recipient_id,'thing2_PB2'))
	}
	if postback_text in rules:
		rules[postback_text]()
	else:
		toDB(recipient_id,response=postback_text)

def quick_rules(recipient_id,qr_text):
	text_rules(recipient_id,qr_text)


def text_rules(recipient_id, message_text=""):
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

def process_referral(sender_id,referral_text,postback_text=None):
	#TODO: config var for app name
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
	carpooler.printout()
	db.session.add(carpooler)
	db.session.commit()
	messenger.say(sender_id,"Added you to my database! =D")
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
