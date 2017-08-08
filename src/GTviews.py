from page_interactions import view_pool,view_pool_formal,populate_group_test
import requests
import copy
import random
from flask import render_template,url_for,jsonify,json,make_response

from collections import OrderedDict
import numpy as np
import sys

from datetime import datetime
from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)
import pickle

from interactions import newPool,findRelativeDelta
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone
from groupThere.GroupThere import GroupThere

from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups



from app import app,request,abort
from database import db

def flatten(L):
	def flattener(L):
		for item in L:
			try:
				yield from flattener(item)
			except TypeError:
				yield item
	return list(flattener(L))



@app.route('/q_groupthere/', methods=['GET','POST'])
def q_groupthere():
	print('in q_groupthere')
	pool_id = request.args.get('pool_id',None)
	if pool_id is None:
		data= request.get_json()
		if data is not None:
			pool_id = data.get("pool_id",None)
	print("pool_id is " + str(pool_id))

	job = q.enqueue_call(func=doGroupThere,kwargs={'pool_id':pool_id},result_ttl=5000)
	# kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools}
	print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
	return job.get_id()


@app.route('/q_repeat_groupthere/', methods=['GET','POST'])
def q_repeat_groupthere():
	print('in q_repeat_groupthere')
	job = q.enqueue_call(func=GroupThere,result_ttl=5000)
	# kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools}
	print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
	return job.get_id()



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


def doGroupThere(pool_id=None):
	if pool_id is not None:
		try:
			with app.app_context():
				pool = Pool.query.filter_by(id=pool_id).first()
				assert(pool is not None)
				mailParam=mailParamsFromPool(pool)
				params = systemParamFromPool(pool)
				params.get_event_info_from_mailparam(mailParam)
				params.coordinate_and_clean()
				params.gen_dist_mat()
				with open("params/GTparams_"+str(datetime.now())[0:10]+".txt",'wb') as openfile:
					pickle.dump(params.to_dict(),openfile)
				with open("params/GTparams_prev.txt",'wb') as openfile:
					pickle.dump(params.to_dict(),openfile)
				# pickleFile = "params/GTparams_prev.txt"
				# print("Loading all parameters from file: " + pickleFile)
				# params=SystemParam(**pickle.load(open(pickleFile,'rb')))
				print("wrote pickles!")
				print(params)

				n=params.numel
				mx=max(list(map(int,params.numberCarSeats)))
				(groups,times) = generate_groups_fromParam(params,testing=False)
				params.groups['groups']=groups
				params.groups['times'] = times
				params.model = generate_model(groups,times,n,mx)
				(params.solution['fun'],params.solution['x'],params.solution['success']) = optimizePulp(params.model)
				print("Solution success: " + str(params.solution['success']))
				params.solution['assignments']=gen_assignment_fromParams(params)
				# for ass in params.solution['assignments']:
				# 	print(ass['names'])
				# 	print(ass['emails'])
				return params
				#make mailparam
				#make systemparam
				#etc
		except Exception as exc:
			print("Error creating GT params. Returning from hardcoded dummy GroupThere params.")
			print(exc)
	return GroupThere()

@app.route("/GTresults/", methods=['POST'])
def post_GT_results():
	try:
		data = json.loads(request.data.decode())
		job_key = data["jobID"]
		print("job_key is " + str(job_key))
		print("job_key is " + str(job_key))
	except:
		print("ERROR IN post_get_results")
		return "in post_GT_results",500
	return GT_results(job_key)


#use carpooler_id (or email, which is also a unique key) to store distances in relational database
#update Pool.noticeWentOut, Pool.optimizedYet, Pool.optimizationCurrent
#Store pooling information in text in trip.
def post_optimization_update(pool_id,email_assignments,id_assignments,email,carpooler_id,success,dur_mat,durs_to_event):
	pass


@app.route("/GTresults/<job_key>", methods=['GET'])
def GT_results(job_key):
	print("in GT_results")
	try:
		job = Job.fetch(job_key, connection=conn)
	except:
		return "No such job",200
	if job.is_finished:
		params=job.result
		print("Job finished in GT_results: " + str(params))
		print("Solution success: " + str(params.solution['success']))

		output = [[('names',ass['names']),('emails',ass['emails']),('isPossible',ass['isPossible']),('notLatePossible',ass['notLatePossible']),('lateOk',ass['lateOk']),('bestTimes',ass['bestTimes'])] for ass in params.solution['assignments']]
		output = [[ (tup[0],np.asscalar(tup[1]) if isinstance(tup[1],np.generic) else tup[1]) for tup in piece] for piece in output] #Convert np.bool_ to bool, eg

		email_assignments = flatten([ass['emails'] for ass in params.solution['assignments']])
		id_assignments = flatten([ass.get('ids',None) for ass in params.solution['assignments']])
		email=params.email
		carpooler_id = params.carpooler_id
		pool_id = params.pool_id
		success= params.solution['success']
		dur_mat = params.dist_mats['Durations']
		durs_to_event = params.dists_to_event['Durations']
		# dist_mats = {'Distances':None,'Durations':None}
		# dists_to_event={'Distances':None,'Durations':None}
		q.enqueue_call(func=post_optimization_update,kwargs={'email_assignments':email_assignments,'id_assignments':id_assignments,'email':email,'carpooler_id':carpooler_id,'pool_id':pool_id,'success':success,'dur_mat':dur_mat,'durs_to_event':durs_to_event},result_ttl=5000)

		a=str(output)
		try:
			a=jsonify(output)
		except Exception as exc:
			a += "\nSomething bad happened DURING jsonify " + str(exc)

		if isinstance(a,str):
			return a ,200
		else:
			return a,200

	else:
		# print("PROBLEM IS HERE?!")
		return "Still working on GROUPTHERE!!", 202



