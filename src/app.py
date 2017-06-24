# -*- coding: utf-8 -*-
import os
from flask import Flask, request, abort, json
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
#from rq.job import Job  #FOR Redis jobs
from worker import conn
import numpy as np


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

#NOTE: SQLALCHEMY_TRACK_MODIFICATIONS prints model object fields when they are edited!
#SQLAlchemy(app,session_options={'autocommit': True})
db = SQLAlchemy(app)


#in Result, we have: from main import app, db,
#so be careful not to move this above defining app and db!
q = Queue(connection=conn)


#set up request context so that I can use flask current_app in messengerbot/__init__.py to get environment variable for access token.
with app.test_request_context('/'):
	from messengerbot import messenger #imported by interactions


#NOTE: Have to import webhookviews at the END because of circular import.
#webhookviews imports from interactions which imports from app.
from webhookviews import root, drop_table, get_webhook,post_webhook
from pageviews import

#Webhook views can be placed here

#Interactions can be placed here


if __name__ == '__main__':
	app.run(debug = app.debug)
