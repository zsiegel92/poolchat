# -*- coding: utf-8 -*-
import os
import json
from urllib import parse #only in Python 3
from flask import Flask, request, abort
import requests
from flask import Flask#, jsonify #for handling db solution outputs
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from rq.job import Job
from worker import conn


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #(or False) #Note: I have this in config.py. If it fails, I will remove that and uncomment this.
db = SQLAlchemy(app)
#in Result, we have: from main import app, db,
#so be careful not to move this aboe defining app and db!
q = Queue(connection=conn)
from models import * #previously from models import Carpooler





#from messengerbot import MessengerClient, messages, attachments, templates, elements
with app.test_request_context('/'):
    from messengerbot import messenger #set up request context so that I can use current_app in messengerbot/__init__.py to get environment variable for access token.
    messenger.subscribe_app()

@app.route("/", methods=["GET"])
def root():
    try:
#        messenger.say('1512768535401609','booting now')
        return "WUTWUTWUT10", 200
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
        return "Dropped and re-created all tables!"



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
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                messenger.say(sender_id,"making contact")
                toDB(sender_id)
                if 'message' in messaging_event: #message may be of the form
                    if 'text' in messaging_event['message']:
                        message_text = messaging_event['message']['text']
                        text_rules(sender_id,message_text)
                elif 'postback' in messaging_event:
                    postback_text = messaging_event['postback']['payload']
                    #referral is in special postbacks see docs
                    if 'referral' in messaging_event['postback']:
                        ref_text = messaging_event['postback']['referral']['ref']
                        process_referral(sender_id,postback_text,ref_text)
                    else:
                        postback_rules(sender_id,postback_text)
    return "ok", 200

def postback_rules(recipient_id,postback_text,referral_text=None):
    carpooler = Carpooler.query.filter_by(userId=recipient_id).first()
    newUser = (carpooler == None)
    
    rules = {
        "GET_STARTED_PAYLOAD":(lambda: getStarted(recipient_id,referral_text)),
        "Hello":(lambda: messenger.say(recipient_id,'World_PB2')),
        "thing1":(lambda: messenger.say(recipient_id,'thing2_PB2'))
    }
    if postback_text in rules:
        rules[postback_text]()
    else:
        messenger.say(recipient_id,"That button is non-functional!")

def text_rules(recipient_id, message_text):
    rules = {
        "Hello": "World",
        "Foo": "Bar"
    }
    if message_text in rules:
        messenger.say(recipient_id, rules[message_text])
    else:
        web_button1 = messenger.webButton('Show website1','https://www.google.com/')
        postback1 = messenger.postBackButton('Do this thing!','thing1')
        postback2 = messenger.postBackButton('Say hello!','Hello2')
        buts = [web_button1,postback1,postback2]
        messenger.give_choices(recipient_id,'Please pick one of these options',buts)

def process_referral(recipient_id,postback_text,ref_text):
    postback_rules(recipient_id,postback_text) #Do nothing with referral for now.

def getStarted(recipient_id,referral_text=None):
    #TODO:
    if recipient_id not in user_db:
        toDB(sender_id)
        messenger.say(recipient_id,'Hello, for the first time!')
    else:
        messenger.say(recipient_id,"I know you! Let's restart.")



def optimize_Group(sender_id):
    #TODO:
    #Create a "solution" model in models.py
    #TODO:
    #When calling this function:
#    job = q.enqueue_call(
#    func=optimize_Group, args=(sender_id,), result_ttl=5000
#    )
#    print(job.get_id()) #pass this around as job_id
#
    #TODO: When getting solution:
    #job = Job.fetch(job_id,connection=conn)
#    if job.is_finished:
#        return str(job.result), 200 #job.result may use a result model? And it may use a __repr__ method of the model class in models.py
#    else:
#        return "Nay!", 202
#

#   TODO: This function should write to the "solutions" table of database:
#    solution = Solution(parameters_for_solution_entry)
#    db.session.add(soultion)
#    db.session.commit()
#    return solution.id #solution has an id once it is added to the db!!
    solution = {}
#    return 1
#    TODO: send user who called this function (cf param sender_id) a button to "see optimal solution". Possibly along with a Google Maps link?
    messenger.say(sender_id,"Your group has been optimized! Ask me about it.")
    return "Solution committed"

#Add params argument! Dict? List?
#def toDB(sender_id,carpoolGroupId=None,address=None,email=None,name=None,preWindow=None,need_to_arrive_on_time=None,num_seats = None,engaged = None,state=None):
def toDB(sender_id,**kwargs):
    try:
        carpooler = Carpooler.query.filter_by(userId=sender_id).first()
        if carpooler == None:
            carpooler = Carpooler(sender_id,**kwargs)
            db.session.add(carpooler)
            messenger.say(sender_id,"Added you to my database.")
            print("Added you to my database.")
        else:
            carpooler.update(**kwargs)
            messenger.say(sender_id,"Updated my database.")
            print("Updated my database.")
        
        db.session.commit()
#            db.session.delete(me)
    except Exception as exc:
        messenger.say(sender_id,"Unable to access my database")
        print("Unable to add item to database.")
        print(str(exc))
    else:
            messenger.say(sender_id,'exiting db function')


if __name__ == '__main__':
    app.run()
