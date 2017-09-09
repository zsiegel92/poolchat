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
from operator import itemgetter

from models import Carpooler,Pool, Trip,Event_Distance,Trip_Distance,Team,Instruction

from emailer import Emailer

from groupThere.GroupThere import GroupThere
from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups

from GT_manager import gt_fromBasicParams,gt_fromDistmattedParams
from GIS_routines import gen_dist_row,gen_dist_col,gen_one_distance

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
		extra.append(1-trip.on_time) #OPPOSITE/INVERTED #trip.on_time is int
		must_drive.append(trip.must_drive) #trip.must_drive is int


	params= SystemParam(email=email,name=name,carpooler_id=carpooler_id,address=address,numberCarSeats=numberCarSeats,minsAvail=minsAvail,extra=extra,must_drive=must_drive,pool_id=pool.id)
	params.numel = len(email)
	return params

# @pre: params.carpooler_id contains all carpooler.id for trip.member in pool.members
# @pre: params.pool_id contains pool.id
# @post: the following are set
# params.d_t, params. R_t, params.dists_to_event['Distances'], params.dists_to_event['Durations']
# RETURN: params
def addDistMatsFromPool(pool,params):
	print("In addDistMatsFromPool")
	assert(pool is not None)
	pool_id=pool.id
	carpooler_ids = params.carpooler_id
	n = params.numel
	d_t = np.zeros((n,n))
	R_t = np.zeros((n,n))
	to_event_durations=np.zeros((1,n))
	to_event_distances=np.zeros((1,n))

	for i in range(n):
		print("Getting distances for carpooler " + str(i) + " out of " + str(n))
		to_event_distance = Event_Distance.query.filter_by(pool_id=pool_id,carpooler_id = carpooler_ids[i]).first()
		if to_event_distance is None:
			print("to_event_distances are None! for " + str(i) + " out of " + str(n))
			get_trip_dists(carpooler_id=carpooler_ids[i],pool_id=pool.id)
			to_event_distance = Event_Distance.query.filter_by(pool_id=pool_id,carpooler_id = carpooler_ids[i]).first()
			if to_event_distance is None:
				print("(GT_interactions.addDistMatsFromPool) TRIED TO FILL MISSING DISTANCES, BUT STILL NO DISTANCES IN DATABASE.")
				print("RETURNING params WITHOUT DIST MATS")
				return params

		to_event_distances[0,i]=to_event_distance.feet
		to_event_durations[0,i]=to_event_distance.seconds

		for j in range(n):
			if (j!=i):
				trip_distance = Trip_Distance.query.filter_by(pool_id=pool_id,from_carpooler_id=carpooler_ids[i],to_carpooler_id=carpooler_ids[j]).first()
				if trip_distance is None:
					get_trip_dists(carpooler_id=carpooler_ids[i],pool_id=pool.id)
					trip_distance = Trip_Distance.query.filter_by(pool_id=pool_id,from_carpooler_id=carpooler_ids[i],to_carpooler_id=carpooler_ids[j]).first()

				d_t[i,j]=trip_distance.feet
				R_t[i,j]=trip_distance.seconds
			else:
				#=0
				pass
	params.dists_to_event['Distances']=to_event_distances
	params.dists_to_event['Durations']=to_event_durations
	params.dist_mats['Distances']=d_t
	params.dist_mats['Durations']=R_t
	print("Successfully created distance matrices from DB")
	return params


def doGroupThere_fromDB(pool_id=None):
	print("In doGroupThere_fromDB")
	if pool_id is not None:
		try:
			with current_app.app_context():
				print("In current_app.app_context()")
				pool = Pool.query.filter_by(id=pool_id).first()
				print("Queried for pool successfully!")
				pool.optimizedYet = True
				pool.optimizationCurrent=True
				pool.noticeWentOut=False
				db.session.commit()
				assert(pool is not None)
				mailParam=mailParamsFromPool(pool)
				params = systemParamFromPool(pool)
				params = addDistMatsFromPool(pool,params)
				if params.dists_to_event['Distances'] is not None:
					print("Got dist mats from pool")
				else:
					print("(GT_interactions.doGroupThere_fromDB) DISTANCE MATRICES NONEXISTANT. TERMINATING.")
					return
				params = gt_fromDistmattedParams(params,mailParam)
				print("did gt from distmatted params")
				#SHOULD DO SOME DATABASE MAINTENENCE HERE, OR AT LEAST ENQUEUE IT
				print("Successfully did groupthere! (doGroupThere_fromDB)")
				# print(params)
				instructions = Instruction()
				instructions.pool_id = pool_id
				# from GTviews.GT_results:
				# output = [[ (tup[0],np.asscalar(tup[1]) if isinstance(tup[1],np.generic) else tup[1]) for tup in piece] for piece in output]

				instruction_helper = {'assignments': params.solution['assignments']}

				instruction_helper['carpooler_ids']=params.carpooler_id
				instruction_helper['addresses']=params.address
				instruction_helper['names'] = params.name
				instruction_helper['number_carseats'] = params.numberCarSeats
				instruction_helper['must_drive']=params.must_drive
				instruction_helper['latenessWindow']=params.latenessWindow
				instruction_helper['canBeLate']=params.extra
				instruction_helper['eventDate']=params.eventDate
				instruction_helper['eventTime']=params.eventTime
				instruction_helper['eventDateTime']=params.eventDateTime
				instruction_helper['minsAvail']=params.minsAvail
				instruction_helper['success']=params.solution['success']
				instruction_helper['totalGroupTime']=params.solution['fun']

				eventDateTime= params.eventDateTime

				minsAvail=params.minsAvail
				#consider that minsAvail can have negative entries!
				for plan in instruction_helper['assignments']:
					order = plan['bestOrder']
					#if only one person (a driver) in a plan:
					if len(order)==1:
						# arrivalTime
						arrivalMins = max(0-params.minsAvail[order[0]] + plan['minTime'],0)
						leaveMins = arrivalMins-plan['minTime']
						plan['addresses'] = [params.address[order[0]]]
					else:
						best = plan['bestTimes']


						driveTimes = [sum(best[i:]) for i in range(len(best))]
						minsAvail = itemgetter(*order)(params.minsAvail)

						minArrivalMins = [driveTimes[i]-minsAvail[i] for i in range(len(driveTimes))]


						arrivalMins = max(max(minArrivalMins),0)
						leaveMins = arrivalMins-plan['minTime']

						plan['addresses']=itemgetter(*order)(params.address)

					plan['arrivalMinutesAfterEventStart'] = arrivalMins
					plan['leaveTimeMinutesAfterEventStart']= leaveMins

					plan['arrivalTime'] = (eventDateTime + relativedelta(minutes=arrivalMins)).isoformat()
					plan['departureTime']=(eventDateTime + relativedelta(minutes=leaveMins)).isoformat()


				instructions.instruction=json.dumps(instruction_helper)
				instructions.success=str(params.solution['success'])
				#params.solution['success'] is a pulp.lpProblem.status, which is an lpStatus object
				instructions.dateTime=datetime.now().isoformat()
				db.session.add(instructions)
				db.session.commit()
				params.instructions_id = instructions.id #FOR QUERYING INSTRUCTIONS FROM DB

				return params

		except Exception as exc:
			print("Error creating GT params.")
			print(exc)
			print("ERROR ERROR ERROR")
			print("INFINITE ERROR")
			return "ERROR ERROR ERROR"





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


def get_trip_dists(carpooler_id,pool_id):
	print("In get_trip_dists({carpooler_id},{pool_id})".format(carpooler_id=carpooler_id,pool_id=pool_id))
	with current_app.app_context():
		pool = Pool.query.filter_by(id=pool_id).first()
		carpooler= Carpooler.query.filter_by(id=carpooler_id).first()
		trip = Trip.query.filter_by(carpooler_id=carpooler_id,pool_id=pool_id).first()
		if (pool is None) or (carpooler is None) or (trip is None):
			print("carpooler: {}, trip: {}, pool: {}".format(carpooler,trip,pool))
			assert(True==False) #Throw an informative exception ASAP!
			# return "Carpooler, or trip, or pool not found!"
		leaveTime=pool.eventDateTime - relativedelta(hours=1)
		print("pool.eventDateTime is: " + str(pool.eventDateTime))
		print("leaveTime is: " + str(leaveTime))

		new_address = trip.address
		dest = pool.eventAddress
		others =[{'id':other_trip.carpooler_id,'address':other_trip.address} for other_trip in pool.members if (other_trip.carpooler_id !=carpooler.id)]

		print("Generating Distance Objects")
		from_new_address = gen_dist_row(new_address,others,leaveTime)
		print("Got from_new_address!")
		to_new_address=gen_dist_col(new_address,others,leaveTime)
		print("Got to_new_address!")
		to_event = gen_one_distance(new_address,dest,leaveTime)
		if (from_new_address is None) or (to_new_address is None) or (to_event is None):
			print("from_new_address: {}, to_new_address: {}, to_event: {}".format(from_new_address,to_new_address,to_event))
			print("(GT_interactions.get_trip_dists) DISTANCE MATRIX FAILURE! RETURNING WITHOUT GENERATING DISTANCES.")
			return

		for i in range(len(others)):
			from_new_dist = Trip_Distance.query.filter_by(pool_id=pool.id,from_carpooler_id=carpooler.id,to_carpooler_id=from_new_address[i]['id']).first()
			to_new_dist = Trip_Distance.query.filter_by(pool_id=pool.id,to_carpooler_id=carpooler.id,from_carpooler_id=from_new_address[i]['id']).first()
			if from_new_dist is None:
				from_new_dist = Trip_Distance()
				from_new_dist.pool_id = pool.id
				from_new_dist.from_carpooler_id = carpooler.id
				from_new_dist.to_carpooler_id = from_new_address[i]['id']
			if to_new_dist is None:
				to_new_dist = Trip_Distance()
				to_new_dist.pool_id = pool.id
				to_new_dist.from_carpooler_id = to_new_address[i]['id']
				to_new_dist.to_carpooler_id = carpooler.id

			from_new_dist.feet = from_new_address[i]['distance']
			from_new_dist.seconds = from_new_address[i]['duration']

			to_new_dist.feet = to_new_address[i]['distance']
			to_new_dist.seconds = to_new_address[i]['duration']

			db.session.add(from_new_dist)
			db.session.add(to_new_dist)


		print("Processed all 'others'!")
		to_event_dist = Event_Distance.query.filter_by(pool_id=pool.id,carpooler_id=carpooler.id).first()
		if to_event_dist is None:
			to_event_dist = Event_Distance()
			to_event_dist.pool_id = pool.id
			to_event_dist.carpooler_id = carpooler.id
		to_event_dist.feet = to_event['distance']
		to_event_dist.seconds = to_event['duration']
		db.session.add(to_event_dist)
		db.session.commit()

		print("Committed to-event distance!")
		return

