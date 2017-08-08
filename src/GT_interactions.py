from flask import jsonify,json
from database import db

import numpy as np

from datetime import datetime
from dateutil.relativedelta import relativedelta
from helpers import findRelativeDelta

from rq import Queue
from rq.job import Job
from worker import conn
from flask_sqlalchemy import SQLAlchemy,current_app
q = Queue(connection=conn)
import pickle

from models import Carpooler,Pool, Trip

from emailer import Emailer

from groupThere.GroupThere import GroupThere
from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups

from GT_manager import gt_fromBasicParams

from app_factory import create_app


#use carpooler_id (or email, which is also a unique key) to store distances in relational database
#update Pool.noticeWentOut, Pool.optimizedYet, Pool.optimizationCurrent
#Store pooling information in text in trip.
def post_optimization_update(pool_id,email_assignments,id_assignments,email,carpooler_id,success,dur_mat,durs_to_event):
	pass


def mailParamsFromPool(pool):
	assert(pool is not None)
	return MailParam(
						eventDate=str(pool.eventDate),
						eventTime=str(pool.eventTime),
						eventName = str(pool.poolName),
						eventLocation = str(pool.poolName) + " at " + str(pool.eventAddress),
						eventAddress= str(pool.eventAddress),
						eventContact= str(pool.eventContact),
						eventEmail = str(pool.eventEmail),
						email_password = "junk",
						email_user = "junk@junk.com",
						eventHostOrg = str(pool.eventHostOrg),
						signature = str(pool.signature),
						latenessWindow= str(pool.latenessWindow)
					)
def systemParamFromPool(pool):
	assert(pool is not None)
	# email = [trip.member.email for trip in pool.members]
	# name = [trip.member.name for trip in pool.members]
	# canLeaveAt = [trip.preWindow for trip in pool.members] #DIFFERENT FROM SP CONSTRUCTOR
	email = []
	name = []
	carpooler_id=[]
	address = []
	numberCarSeats =[]
	minsAvail=[]
	extra=[]
	must_drive= []
	for trip in pool.members:
		email.append(trip.member.email) #trip.member.email is String
		name.append(trip.member.name) #trip.member.name is String
		carpooler_id.append(trip.member.id)
		address.append(trip.address) #trip.address is String
		numberCarSeats.append(trip.num_seats) #trip.num_seats is int
		minsAvail.append(trip.preWindow) #CONVERT TO DATETIME #trip.preWindow is int
		extra.append(trip.on_time) #OPPOSITE/INVERTED #trip.on_time is int
		must_drive.append(trip.must_drive) #trip.must_drive is int


	params= SystemParam(email=email,name=name,carpooler_id=carpooler_id,address=address,numberCarSeats=numberCarSeats,minsAvail=minsAvail,extra=extra,must_drive=must_drive,pool_id=pool.id)
	params.numel = len(email)
	return params


# def enqueue_groupThere(pool_id=None):
# 	job = q.enqueue_call(func=doGroupThere,kwargs={'pool_id':pool_id},result_ttl=5000)
# 	# kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools}
# 	print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
# 	return job.get_id()


def doGroupThere(pool_id=None):
	if pool_id is not None:
		try:
			# with app.request_context:
			pool = Pool.query.filter_by(id=pool_id).first()
			pool.optimizedYet = True
			pool.optimizationCurrent=True
			pool.noticeWentOut=False
			db.session.commit()
			assert(pool is not None)
			mailParam=mailParamsFromPool(pool)
			params = systemParamFromPool(pool)
			params = gt_fromBasicParams(params,mailParam)
			#SHOULD DO SOME DATABASE MAINTENENCE HERE, OR AT LEAST ENQUEUE IT
			return params
		except Exception as exc:
			print("Error creating GT params. Returning from hardcoded dummy GroupThere params.")
			print(exc)
			print("ERROR ERROR ERROR")
			print("INFINITE ERROR")
			return "ERROR ERROR ERROR"


def get_all_pool_ids(pool_id=None):
	pool_ids=[]
	if pool_id is not None:
		pools = Pool.query.filter_by(id=pool_id)
	else:
		pools = Pool.query.all()
	for pool in pools:
		pool_ids.append(pool.id)
	return pool_ids

def email_carpoolers(pool_id=None,scheduler_frequency=60):
	for pool_id in get_all_pool_ids(pool_id):
		q.enqueue_call(func=email_aPool,kwargs={'pool_id':pool_id,'scheduler_frequency':scheduler_frequency},result_ttl=5000)
	return("All emails enqueued.")


def email_aPool(pool_id,scheduler_frequency=60):
	emailer=Emailer(q)
	nowish = datetime.now() - relativedelta(minutes=int(scheduler_frequency/2))
	pool=Pool.query.filter_by(id=pool_id).first()
	poolName = pool.poolName
	fireNotice = int(pool.fireNotice)
	eventDateTime= pool.eventDateTime
	eventEmail=pool.eventEmail
	[date,time,fireDateTime] = findRelativeDelta(eventDateTime,fireNotice,mode='hours',delta_after=-1)
	print("EXAMINING POOL: " + str(poolName))

	if (nowish> fireDateTime) and (not pool.noticeWentOut):
		emailer.email(eventEmail,message="Carpooling instructions going out for " + str(poolName) + "!",subject="GroupThere instructions en route for " + str(poolName) + "!")
		print("BETTER FIRE A NOTICE!")
		try:
			assert (pool.optimizedYet and pool.optimizationCurrent)
		except:
			message = "Pool with id " + str(pool.id) + " trying to send instructions, but not yet optimized! Ensure optimization is called by scheduler before emailing."
			subject = "ERROR with pool " + str(pool.id)
			print(message)
			emailer.self_email(message=message,subject=subject)#sent to self
			##FOR TESTING ONLY!
			for trip in pool.members:
				print("	trip")
				print("		trip.member.name: " + str(trip.member.name))
				print("		trip.pool.poolName: " + str(trip.pool.poolName))
				print("		trip.member.email: " + str(trip.member.email))
				print()
				message2 = message +"\n"
				message2+="Carpooler name: " + str(trip.member.name) + "\n"
				message2+="Carpooler email: " + str(trip.member.email) + "\n"
				message2+="Pool name: " + str(trip.pool.poolName) + "\n"

				subject2=subject + " --- CARPOOLNG instructions for " + str(trip.pool.poolName) + " on " + str(date) + " at " + str(time)
				emailer.email(trip.member.email,message=message2,subject=subject2)
			# FOR TESTING ONLY!

		else:
			print("Emailing all members of pool " + str(poolName))
			pool.noticeWentOut = True
			db.session.commit()
			for trip in pool.members:
				print("	trip")
				print("		trip.member.name: " + str(trip.member.name))
				print("		trip.pool.poolName: " + str(trip.pool.poolName))
				print("		trip.member.email: " + str(trip.member.email))
				print()
				message=""
				message+="Carpooler name: " + str(trip.member.name) + "\n"
				message+="Carpooler email: " + str(trip.member.email) + "\n"
				message+="Pool name: " + str(trip.pool.poolName) + "\n"

				subject="CARPOOLNG instructions for " + str(trip.pool.poolName) + " on " + str(date) + " at " + str(time)
				emailer.email(trip.member.email,message=message,subject=subject)

	elif (nowish>fireDateTime):
		print("Should have already fired a notice for pool " + str(poolName) + "!")
	else:
		print("We do not yet have to fire a notice for pool " + str(poolName) + "!")
		print("	Current time is " + datetime.now().strftime('%m/%d/%Y'))
		print("	Instructions to be sent on " + str(date) + " at " + str(time))
		print("	Event datetime: " + str(eventDateTime))







def do_all_gt(scheduler_frequency=60):
	emailer = Emailer(q)
	nowish = datetime.now() - relativedelta(minutes=int(scheduler_frequency/2))

	pools = Pool.query.all()
	for pool in pools:
		pool_id=pool.id
		poolName = pool.poolName
		fireNotice = int(pool.fireNotice)
		eventDateTime= pool.eventDateTime
		eventEmail=pool.eventEmail
		[date,time,fireDateTime] = findRelativeDelta(eventDateTime,fireNotice,mode='hours',delta_after=-1)
		print("EXAMINING POOL: " + str(poolName))

		if (nowish> fireDateTime) and (not (pool.optimizedYet and pool.optimizationCurrent)):
			emailer.email(eventEmail,message="Optimization commencing for " + str(poolName) + "!",subject="Optimization commencing for " + str(poolName) + "!")
			print("TIME TO OPTIMIZE!")
			q.enqueue_call(func=doGroupThere,kwargs={'pool_id':pool_id},result_ttl=5000)
			print("Enqueued optimization for pool " + str(poolName))
			for trip in pool.members:
				message="Enqueuing optimization!\n"
				message+="Carpooler name: " + str(trip.member.name) + "\n"
				message+="Carpooler email: " + str(trip.member.email) + "\n"
				message+="Pool name: " + str(trip.pool.poolName) + "\n"

				subject="Enqueued optimization for " + str(trip.pool.poolName)
				emailer.email(trip.member.email,message=message,subject=subject)

		elif (nowish>fireDateTime):
			print("Should have already optimized pool " + str(poolName) + "!")
		else:
			print("We do not yet have to optimize pool " + str(poolName) + "!")
	return("All optimization enqueued.")



