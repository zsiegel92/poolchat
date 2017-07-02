# from app import messenger, db,app,Job,conn,q #,Queue
import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
import re
import smtplib
#FOR TESTING ONLY,IMPORT SYS
import sys
import os
import config
from database import db

import numpy as np #INTERACTIONS MOVEMENT!
from messengerbot import messenger #INTERACTIONS MOVEMENT!
from rq import Queue #INTERACTIONS MOVEMENT!
from rq.job import Job  #FOR Redis jobs #INTERACTIONS MOVEMENT!
from worker import conn #INTERACTIONS MOVEMENT!
from flask_sqlalchemy import SQLAlchemy
q = Queue(connection=conn) #INTERACTIONS MOVEMENT!
from models import  Carpooler,Pool, Trip

#TODO: Don't create dicts at function call! Initialize them earlier.
def postback_rules(recipient_id,postback_text,referral_text=None,carpooler=None,fromUnPrefixer=False):
	print("in interactions.postback_rules. postback_text = " + str(postback_text) +", fromUnPrefixer = " + str(fromUnPrefixer),file=sys.stderr)
	key_and_args = postback_text.split('/')
	key = key_and_args[0]
	keyPayload = key_and_args[-1]
	#IMPLEMENT 'MULTI'
	rules = {
		"RESPONSE":(lambda obField,*RESP: fillField(recipient_id, "/".join(RESP),obField,carpooler)),
		# "PREFIXED":(lambda *args: prefixprocess(recipient_id,carpooler,*args)),
		"PREFIXED":(lambda *args: postback_rules(recipient_id,"/".join(args),carpooler=carpooler,fromUnPrefixer=True)),
		"EMAIL_INPUT":(lambda prefix,*inputted_email: input_email(recipient_id,prefix,"/".join(inputted_email),carpooler)),
		"SET_DATE":(lambda *inputted_date: findDate(recipient_id,"/".join(inputted_date),carpooler)),
		"SWITCH_AM_PM":(lambda mode,field_to_switch: ampmSwitch(recipient_id,field_to_switch,mode,carpooler)),
		"TEST":(lambda *args: test(recipient_id,"/".join(args),carpooler)),
		# "SWITCH_AM_PM":(lambda: 5),
		"GET_STARTED_PAYLOAD":(lambda: getStarted(recipient_id,referral_text)),
		"CREATE_NEW_POOL":(lambda: newPool(recipient_id,carpooler)),
		"FIND_ADDRESS":(lambda *inputted_address_args: findAddress(recipient_id,"/".join(inputted_address_args),carpooler)),
		"FIRENOTICE":(lambda firenotice: set_fire_notice(recipient_id,firenotice,carpooler)),
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


def process_referral(sender_id,referral_text,postback_text=None):
	#Triggered by visit to m.me/GroupThere?ref=myparam
	#INTERACTIONS MOVEMENT
	# messenger.say(sender_id,"Referring to "+ referral_text + " through: m.me/" + app.config['APP_NAME'] + "?ref=" + referral_text) #Do nothing with referral for now.
	appname=getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).APP_NAME
	messenger.say(sender_id,"Referring to "+ referral_text + " through: m.me/" + str(appname) + "?ref=" + referral_text)
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






def test(recipient_id,response,carpooler=None):
	print("in interactions.test",file=sys.stderr)
	messenger.say(recipient_id,"In interactions.test")
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=recipient_id).first()

	fillField(recipient_id,response,carpooler=carpooler)
	db.session.commit()

def set_fire_notice(recipient_id,firenotice,carpooler=None):
	print("in interactions.set_fire_notice",file=sys.stderr)
	fillField(recipient_id,firenotice,carpooler=carpooler,afterText=False)
	db.session.commit()
	pool = carpooler.getCurrentPool()
	fireDT = pool.eventDateTime + relativedelta(hours=-int(firenotice))
	date = str(fireDT.date().strftime("%B") + " " + fireDT.date().strftime("%d") + ", " + fireDT.date().strftime("%Y"))
	time = str(fireDT.time().strftime("%I:%M %p"))
	message = "OK, now I know that instructions should be sent out " + str(firenotice) + " hours before the event starts on " + str(pool.eventDate) + " at " + str(pool.eventTime) + ".\n\nInstructions will be send out on: " + date + " at " + time + "."
	messenger.say(recipient_id,message)

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

def write_and_send_email(recipient_id,prefix,toAddress,carpooler=None,pool=None,trip=None):
	print("in interactions.write_and_send_email",file=sys.stderr)
	if not carpooler:
		return
	# if not carpooler:
	# 	carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()
	if prefix =="Carpooler":
		message = "Hey, " + str(carpooler.name) +",\nYou just registered as a user of GroupThere!\nCongratulations - you will be able to coordinate carpooling for events with up to 40 people very soon!"
	elif prefix == "Pool":
		message = "Hey, " + str(carpooler.name) + ",\nThis email address was just submitted as the primary contact email for a GroupThere event!\n"

		message = message + "\nPool Name: " + pool.poolName
		message = message + "\nEvent Date and Time: " + str(pool.eventDate) + " at " + str(pool.eventTime)
		message = message + "\nEvent Address: " + str(pool.eventAddress)
		message = message + "\nArrival Time Flexibility: " + str(pool.latenessWindow)
		message = message + "\nPhone Contact: " + str(pool.eventContact)
		message = message + "\nHost Organization: " + str(pool.eventHostOrg)
		message = message + "\nHours Notice Given to Participants: " + str(getattr(pool,'fireNotice',27))
		message = message + "\n Your email will be signed with the following:"+ "\n\n'" + str(pool.signature) + "'"
		message = message + "\n\nLooking forward to your trip on " + str(pool.eventDate) + ".\n\nBest Wishes,\nGroupThere"
	#Trip confirmation email
	elif prefix == "Confirm":
		message = ""
	else:
		message = ""
	# gmail_user = app.config['EMAIL'] #INTERACTIONS MOVEMENT!
	# gmail_password = app.config['EMAIL_PASSWORD'] #INTERACTIONS MOVEMENT!
	gmail_user =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).EMAIL
	gmail_password=getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).EMAIL_PASSWORD

	sent_from = gmail_user
	sent_to = toAddress
	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, sent_to, message)
		server.close()
		# messenger.say(recipient_id,"You just got an email from GroupThere!")
	except Exception as exc:
		messenger.say(recipient_id,"Tried and failed to send an email to you from " + str(gmail_user))
		# messenger.say(recipient_id,str(exc))
		print('Something went wrong with login.')

def input_email(recipient_id,prefix,inputted_email,carpooler=None,pool=None,trip=None):
	print("in interactions.input_email",file=sys.stderr)
	if not carpooler:
		carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()
	if not pool:
		pool=carpooler.getCurrentPool()
	if not trip:
		trip = carpooler.getCurrentTrip()
	if re.match(r"[^@]+@[^@]+\.[^@]+",inputted_email):
		fillField(recipient_id,inputted_email,carpooler=carpooler)
		db.session.commit()
		job=q.enqueue_call(
			func=write_and_send_email, args=(recipient_id,prefix,inputted_email,), kwargs = {'carpooler':carpooler,'pool':pool,'trip':trip},result_ttl=5000
		)
		print("SENT A REDIS JOB!!",file=sys.stderr)
		print("job.get_id() = " + str(job.get_id()),file=sys.stderr)
	else:
		messenger.say(recipient_id,"Please enter a valid email address.")


def ampmSwitch(recipient_id,field_to_switch=None,mode=None,carpooler=None):
	print("in interactions.ampmSwitch",file=sys.stderr)
	try:
		if not carpooler:
			carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()
		if not mode:
			mode = carpooler.mode
		if mode =='fields':
			return
		elif mode == 'poolfields':
			if not field_to_switch:
				field_to_switch = 'eventDateTime'
			parsed = getattr(carpooler.getCurrentPool(),field_to_switch,None)
			if not parsed:
				return
		elif mode == 'tripfields':
			return

		if parsed.time().hour < 12:
			parsed = parsed + relativedelta(hours=12)
		else:
			parsed = parsed - relativedelta(hours=12)

		date = parsed.date()
		time=parsed.time()
		# strdate=date.strftime("%d/%m/%Y")
		strdate = date.strftime("%B") + " " + date.strftime("%d") + ", " + date.strftime("%Y")
		strtime = str(time.strftime("%I:%M %p"))

		if (parsed > datetime.now()):
			carpooler.externalUpdate(nextFieldState='dateMenu',**{'eventDate':strdate,'eventTime':strtime,'eventDateTime':parsed})
			messenger.say(recipient_id,"Please confirm this date and time: " + str(strdate) + " at " + str(strtime))
		else:
			messenger.say(recipient_id,"Your stated event date and time (" + str(strdate) + " at " + str(strtime) + ") has already passed.\nPlease enter a valid date and time.")
		db.session.commit()
	except Exception as exc:
		messenger.say(recipient_id,"Error in ampmSwitch")
		print("Error in interactions.ampmSwitch",file=sys.stderr)
		print(str(exc),file=sys.stderr)

def findDate(recipient_id,inputted_date,carpooler=None):
	print("in interactions.findDate",file=sys.stderr)
	if not carpooler:
		carpooler=Carpooler.query.filter_by(fbId=recipient_id).first()
	try:
		parsed=parse(inputted_date,fuzzy=True,dayfirst=False)
	except:
		messenger.say(recipient_id,"Please enter a valid date!")
		return
	# dt.strftime("%d-%m-%Y %H:%M:%S")
	date = parsed.date()
	time=parsed.time()
	# strdate=date.strftime("%d/%m/%Y")
	strdate = date.strftime("%B") + " " + date.strftime("%d") + ", " + date.strftime("%Y")
	strtime = str(time.strftime("%I:%M %p"))

	if (parsed > datetime.now()):
		carpooler.externalUpdate(nextFieldState='dateMenu',**{'eventDate':strdate,'eventTime':strtime,'eventDateTime':parsed})
		messenger.say(recipient_id,"Please confirm this date and time: " + str(strdate) + " at " + str(strtime))
	else:
		messenger.say(recipient_id,"Your stated event date and time (" + str(strdate) + " at " + str(strtime) + ") has already passed.\nPlease enter a valid date and time.")
	db.session.commit()


def findAddress(sender_id,inputted_address,carpooler=None):
	print("in interactions.findAddress",file=sys.stderr)
	messenger.say(sender_id,"Here is a picture of that address! If this isn't right, you can change it later.")

	if not carpooler:
		carpooler=Carpooler.query.filter_by(fbId=sender_id).first()

	GMAPS_GEOCODE_API_TOKEN =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).GMAPS_GEOCODE_API_TOKEN #INTERACTIONS MOVEMENT
	# GMAPS_GEOCODE_API_TOKEN = app.config['GMAPS_GEOCODE_API_TOKEN']

	geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
	querystring = {"address":inputted_address,"key":GMAPS_GEOCODE_API_TOKEN}
	response = requests.request("GET", geocode_url, params=querystring)
	response=response.json()

	formatted_address =response['results'][0]['formatted_address']
	lat = response['results'][0]['geometry']['location']['lat']
	lon = response['results'][0]['geometry']['location']['lng']


	# GMAPS_STATIC_API_TOKEN = app.config['GMAPS_STATIC_API_TOKEN']
	GMAPS_STATIC_API_TOKEN =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).GMAPS_STATIC_API_TOKEN #INTERACTIONS MOVEMENT
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
	# access_token = app.config["MESSENGER_PLATFORM_ACCESS_TOKEN"]
	access_token =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).MESSENGER_PLATFORM_ACCESS_TOKEN #INTERACTIONS MOVEMENT
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


def fillField(sender_id,response,obField=None,carpooler=None,afterText=True):
	print("in interactions.fillField", file=sys.stderr)
	if not carpooler:
		carpooler = Carpooler.query.filter_by(fbId=sender_id).first()
	if carpooler:
		if carpooler.isValid(response,obField):
			response = carpooler.process(response) #format time for storage, etc.
			# messenger.say(sender_id,"Processed response is: " + str(response))
			if afterText:
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
	carpooler = Carpooler.query.filter_by(fbId=sender_id).first()

	if carpooler:
		response = carpooler.prefix(response) #format time for storage, etc.
		postback_rules(sender_id,'PREFIXED/' + response,carpooler=carpooler)
	else:
		getStarted(sender_id,message_text=response)
	# try:
	# 	pass
	# except Exception as exc:
	# 	messenger.say(sender_id,"Error accessing my database")
	# 	print("Error in noPrefixResponse",file=sys.stderr)
	# 	print(str(exc),file=sys.stderr)
