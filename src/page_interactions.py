# from app import messenger, db,app,Job,conn,q #,Queue
import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import random
from datetime import datetime
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
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone

from interactions import newPool

#TODO: Display information regarding all participants of this pool.
def view_pool(number):
	pool = Pool.query.filter_by(id=number).first()
	if pool:
		return pool.to_dict()
	else:
		return "There is no carpool with id " + str(number) + " :("

def view_pool_formal(number):
	pool = Pool.query.filter_by(id=number).first()
	if pool:
		return pool.to_dict_formal()
		db.session.commit()
	else:
		return "There is no carpool with id " + str(number) + " :("

def populate_group_test():
	sender_id=5
	carpooler = Carpooler(fbId=sender_id)
	db.session.add(carpooler)
	#def externalUpdate(self,nextFieldState=None,setForMode=None,**kwargs)
	#possible_modes = ['fields','poolfields','tripfields']
	#	"
	#	if not setForMode:
	#		setForMode = self.mode
	#	"
	carpooler.externalUpdate(name="Zach Siegel",firstname = "Zach",lastname="Siegel",email='thesouroaf@gmail.com',nextFieldState='email')
	# carpooler.switch_modes('poolfields')
	db.session.commit()
	newPool(sender_id,carpooler=carpooler,verbose=False)

	carpooler.externalUpdate(poolName = "Ifnotnow party",eventDate = 'April 24, 2017',eventTime = '4:30 pm',eventDateTime = parse("April 24, 2017 at 4:30 pm"),latenessWindow=20,eventAddress='100 W 1st St, LA, CA',eventContact='9144003675',eventEmail = 'zsiegel92@gmail.com',eventHostOrg='IfNotNow LA',signature='Thank you!!',fireNotice='12',setForMode='poolfields')
	carpooler.externalUpdate(address='153 N New Hampshire Ave, LA, CA 90004',num_seats=4,preWindow=30,on_time=0,must_drive=0,setForMode='tripfields')
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


