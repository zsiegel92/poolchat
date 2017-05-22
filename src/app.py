# -*- coding: utf-8 -*-
import os
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
#from rq.job import Job  #FOR Redis jobs
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #(or False) #Note: I have this in config.py. If it fails, I will remove that and uncomment this.
db = SQLAlchemy(app) #SQLAlchemy(app,session_options={'autocommit': True})
#in Result, we have: from main import app, db,
#so be careful not to move this aboe defining app and db!
q = Queue(connection=conn)
from models import  Carpooler#, Pool, participation



#from messengerbot import MessengerClient, messages, attachments, templates, elements
with app.test_request_context('/'):
	from messengerbot import messenger  #set up request context so that I can use current_app in messengerbot/__init__.py to get environment variable for access token.
	messenger.subscribe_app()

@app.route("/", methods=["GET"])
def root():
#    assert app.debug == False
	try:
#        messenger.say('1512768535401609','booting now')
		return 'WUTWUTWUT10', 200
	except Exception as exc:
		return str(exc)

#TODO: Flip through users in db, message them their table has been dropped :)
@app.route('/dropTabs', methods=["GET"])
def drop_table():
	try:
		db.drop_all()
		db.create_all()
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc)
	else:
		return "Dropped and re-created all tables!", 200



# webhook for facebook to initialize the bot
@app.route('/webhook', methods=['GET'])
def get_webhook():
	if not 'hub.verify_token' in request.args or not 'hub.challenge' in request.args:
		abort(400)
	return request.args.get('hub.challenge')




@app.route('/webhook', methods=['POST'])
def post_webhook():
	data = request.json
	if data["object"] == "page":
		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				sender_id = messaging_event["sender"]["id"]
				referral_text = None
				if "referral" in messaging_event:
					referral_text = messaging_event["referral"]["ref"]
				if "message" in messaging_event:
					if "text" in messaging_event["message"]:
						message_text = messaging_event["message"]["text"]
						if "quick_reply" in messaging_event["message"]:
							quick_rules(sender_id,messaging_event["message"]["quick_reply"]["payload"])
						else:
							text_rules(sender_id,message_text=message_text)
				elif "postback" in messaging_event:
					postback_text = messaging_event["postback"]["payload"]
					#referral is in special postbacks see docs
					if "referral" in messaging_event["postback"]:
						referral_text = messaging_event["postback"]["referral"]["ref"]
						process_referral(sender_id,postback_text,referral_text)
				elif referral_text:
					process_referral(sender_id,referral_text=referral_text)
	return "ok", 200

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
	messenger.say(sender_id,"Referring from m.me/" + app.config['APP_NAME'] + "?ref=" + referral_text) #Do nothing with referral for now.
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
					messenger.say(sender_id,carpooler.afterSet(response))
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



if __name__ == '__main__':
	app.run(debug = app.debug)
