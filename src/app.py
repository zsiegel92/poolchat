# -*- coding: utf-8 -*-
import os
from flask import Flask, request, abort, json
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
#from rq.job import Job  #FOR Redis jobs
from worker import conn


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #(or False) #Note: I have this in config.py. If it fails, I will remove that and uncomment this.
#NOTE: SQLALCHEMY_TRACK_MODIFICATIONS prints model object fields when they are edited!
db = SQLAlchemy(app) #SQLAlchemy(app,session_options={'autocommit': True})
#in Result, we have: from main import app, db,
#so be careful not to move this aboe defining app and db!
q = Queue(connection=conn)


#set up request context so that I can use flask current_app in messengerbot/__init__.py to get environment variable for access token.
with app.test_request_context('/'):
	from messengerbot import messenger #imported by interactions
	# messenger.subscribe_app() #Causing issues...

# from interactions import postback_rules,quick_rules,text_rules,process_referral,getStarted,pester,getInfo,toDB #imported by webhookviews

#NOTE: Have to import webhookviews at the END because of circular import.
from webhookviews import root, drop_table, get_webhook,post_webhook
#webhookviews imports from interactions which imports from app.


#Webhook views can be placed here

#Interactions can be placed here


if __name__ == '__main__':
	app.run(debug = app.debug)
