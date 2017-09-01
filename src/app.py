# -*- coding: utf-8 -*-
import os
from flask import Flask, request, abort, json
from itsdangerous import URLSafeTimedSerializer

# from database import db
from app_factory import create_app
from login import login_manager
from database import db
import models

# from flask_sqlalchemy import SQLAlchemy #INTERACTIONS MOVEMENT!
# from rq import Queue #INTERACTIONS MOVEMENT!
# from rq.job import Job  #FOR Redis jobs #INTERACTIONS MOVEMENT!
# from worker import conn #INTERACTIONS MOVEMENT!
# import numpy as np #INTERACTIONS MOVEMENT!


# app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
# db.init_app(app)
app = create_app(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

#NOTE: SQLALCHEMY_TRACK_MODIFICATIONS prints model object fields when they are edited!
#SQLAlchemy(app,session_options={'autocommit': True})

# db = SQLAlchemy(app) #INTERACTIONS MOVEMENT!


#in Result, we have: from main import app, db,
#so be careful not to move this above defining app and db!
# q = Queue(connection=conn) #INTERACTIONS MOVEMENT!


#INTERACTIONS MOVEMENT!
#set up request context so that I can use flask current_app in messengerbot/__init__.py to get environment variable for access token.
# with app.test_request_context('/'):
# 	from messengerbot import messenger #imported by interactions


from utils import KwargConverter
app.url_map.converters['kwarg'] = KwargConverter



#NOTE: Have to import webhookviews at the END because of circular import.
#webhookviews imports from interactions which imports from app.
import webhookviews
import pageviews
import registration_endpoints
import triggerviews
import GTviews

import unusedViews

import loginViews
# from interactions import db
#Webhook views can be placed here
#Interactions can be placed here







if __name__ == '__main__':
	# with app.app_context():
	# 	db.create_all()
	app.run(debug = app.debug)

