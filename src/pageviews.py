from page_interactions import view_pool,populate_group_test
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

from interactions import newPool,findRelativeDelta
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone
from groupThere.GroupThere import GroupThere

from app import app,request,abort
from database import db




@app.route('/', methods=['GET', 'POST'])
def index():
	errors = []
	results = {}
	if request.method == "POST":
		# get url that the user has entered
		try:
			url = request.form['url']
			r = requests.get(url)
			print(r.text)
			results = {"hey":"dude","who":"are","you":"?"}
		except:
			errors.append(
				"Unable to get URL. Please make sure it's valid and try again."
			)
	return render_template('index.html', errors=errors, results=results)

@app.route('/view_pool/<int:number>/',methods=['GET'])
def call_view_pool(number):
	poolDict=view_pool(number)
	poolRep = '<br>'.join(['{0}: {1}'.format(key, value) for (key, value) in poolDict.items()])
	return poolRep,200

@app.route('/view_pool/',methods=['POST'])
def post_call_view_pool():
	# pool_id = request.args.get('pool_id',None)
	data = json.loads(request.data.decode())
	pool_id = data.get("pool_id",None)
	print("POOL ID IS " + str(pool_id))
	poolDict=view_pool(pool_id)
	return jsonify(poolDict),200



#TODO: Flip through users in db, message them their table has been dropped :)
@app.route('/dropTabs', methods=["GET"])
def drop_table():
	print("Dropping all tables")
	try:
		db.drop_all()
		db.create_all()
		db.session.commit()
		rando=random.randint(1,10)
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc),500
	else:
		return "Dropped and re-created all tables! Random integer: " + str(rando), 200


@app.route('/triggers/',methods=['GET',"POST"])
def load_triggers():
	# <form action="/populate_generic/" method="post" target="_blank">
 #              Number of Generic Participants: <input type="int" name="n"><br>
	request_vars=request.environ.copy()
	if request.method=="GET":
		n = request.args.get('n',None)
		submit=request.args.get('submit',None)
	else:
		n = request.form.get('n',None)
		submit = request.form.get('submit',None) #Note - can change button "name" tag arbitrarily
	if n is not None:
		n=int(n)
		db.drop_all()
		db.create_all()
		db.session.commit()
		output_list = populate_generic(n)
	elif submit is not None:
		if submit == 'drop_tabs':
			resp = drop_table()
			output_list = ['drop_tab_output: ' + str(resp)]
	else:
		output_list = ["Request_Type = "+ str(request.method),"submit = " + str(submit),"n = " + str(n)]
	return render_template('triggers.html',output_list=output_list,request_vars=request_vars)



@app.route('/q_populate/',methods=['GET',"POST"])
def q_populate():
	# <form action="/populate_generic/" method="post" target="_blank">
 #              Number of Generic Participants: <input type="int" name="n"><br>
	if request.method=="GET":
		print("Getting params from request.args")
		n = request.args.get('n',None)
		randGen=request.args.get('randGen',False)
		numberPools=request.args.get('numberPools',3)
	else:
		print("Getting params from request.form")
		n = request.form.get('n',None)
		randGen = request.form.get("randGen",False)
		numberPools=request.form.get('numberPools',3)
	if n is None:
		print("Getting params from request.data")
		data = json.loads(request.data.decode())
		n = data.get("n",None)
		randGen = data.get("randGen",False)
		numberPools=data.get('numberPools',3)
	n=int(n)
	numberPools=min(n,numberPools)
	if n is not None:
		n=int(n)
		db.drop_all()
		db.create_all()
		db.session.commit()
		job = q.enqueue_call(func=populate_generic,kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools},result_ttl=5000)
		print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
		return job.get_id()
	return "error_occurred_in_q_populate"



@app.route("/results/", methods=['POST'])
def post_get_results():
	try:
		data = json.loads(request.data.decode())
		job_key = data["jobID"]
		print("job_key is " + str(job_key))
	except:
		print("ERROR IN post_get_results")
		return "Error",500
	return get_results(job_key)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
	try:
		job = Job.fetch(job_key, connection=conn)
	except:
		return "No such job!",200
	if job.is_finished:
		result=job.result
		print("Job finished in get_results: " + str(result))
		resultString = str(result)
		print("Number of characters in result as string: " + str(len(resultString)))
		# return resultString[0:-1],200
		output = OrderedDict(("Carpooler_"+str(ind),{'Carpooler':carpooler['Carpooler'],'Pool':carpooler['Pool'],'Trip':carpooler['Trip']}) for ind,carpooler in enumerate(result))
		return jsonify(output),200
	else:
		# print("PROBLEM IS HERE?!")
		return "Still working on it!", 202

#NOTE: All POOL creators are ONLY IN THAT SINGLE POOL
def populate_generic(n,numberPools=2,randGen = False):
	print("in page_interactions.populate_generic(" + str(n) + ")")
	with app.app_context():
		dicts = create_generic_parameters(n=n,numberPools=numberPools,randGen=randGen)
		print("dicts = " + str(dicts))
		for fullDict in dicts:
			print("oneDict = " + str(fullDict))
			fbId=fullDict['fbId']
			carpooler = Carpooler(fbId=fbId)
			db.session.add(carpooler)
			carpooler.externalUpdate(setForMode='fields',**fullDict['Carpooler'])
			db.session.commit()

			if 'joinPools' in fullDict['Pool']:
				for pool_id in fullDict['Pool']['joinPools']:
					# pool_id = pool__id
					pool = Pool.query.filter_by(id=pool_id).first()
					if pool is not None:
						print("pool.to_dict(): " + str(pool.to_dict()))
						print("carpooler.id: " + str(carpooler.id))
						print("pool.id: " + str(pool.id))
						trip = None
						try:
							trip = Trip.query.filter_by(carpooler_id=carpooler.id,pool_id=pool.id).first()
							print("Successfully queried for trip!")
							print("Successful trip queried is: " + str(trip))
						except Exception as exc:
							print("trip is " + str(trip))
							print("Exception:")
							print(str(exc))
							print()
							print()
						if trip is None:
							trip = Trip(carpooler_id = carpooler.id,pool_id = pool.id)
							trip.pool=pool
							carpooler.pools.append(trip)
							carpooler.current_pool_id= trip.pool.id
							db.session.commit()
						else:
							print("Carpooler already part of this carpool!")
						print("Got far enough to use trip.pool.id")
						db.session.commit()
						carpooler.switch_modes('tripfields')
						db.session.commit()
						carpooler.externalUpdate(setForMode='tripfields',**fullDict['Trip'])
						db.session.commit()
					else:
						print("There is no such carpool :(")

			else:
				newPool(fbId,carpooler=carpooler,verbose=False)
				carpooler.externalUpdate(setForMode='poolfields',**fullDict['Pool'])
				db.session.commit()
				carpooler.externalUpdate(setForMode='tripfields',**fullDict['Trip'])
				db.session.commit()
		return dicts


def get_real_generic_addresses(n):
	import csv
	filename='addresses.txt'
	addresses=[]
	with open(filename,'rt',newline='') as csvfile:
		s = csv.reader(csvfile,delimiter = '\n',quotechar='"')
		for row in s:
			for field in row:
				if field!='':
					addresses.append(field)
	return (addresses * int((((n)/len(addresses))+1)))[:n] #repeat until given length

		# f = open(filename, newline='')
		# reader = csv.reader(f)
		# for row in reader:
		# 	for field in row:
		# 		addresses.append(field)



def create_generic_parameters(n=1,numberPools=None,randGen=False):
	print("In create_generic_parameters. n = " + str(n) + ", numberPools = " + str(numberPools) + ", randGen = " + str(randGen) + ".")
	real_addresses = get_real_generic_addresses(n+1)
	real_event_addresses = list(reversed(real_addresses))

	dicts=[]
	today = datetime.now()
	if (not numberPools) or (int(numberPools) > n):
		if randGen:
			numberPools = random.randint(1,n)
		else:
			numberPools = 1

	for k in range(1,n+1):
		##Carpooler
		fbId = str(k)
		first = "first" + str(k)
		last = "last_"+str(k)
		name = first + " " + last
		email= "email_" + str(k ) + "@notARealThing.com"

		##Pool
		poolName = "poolName_" + str(k)
		numberDaysInFuture= (random.randint(1,35) if randGen else 10)
		[eventDate,eventTime,eventDateTime] = findRelativeDelta(today,numberDaysInFuture,mode='days',delta_after=1)
		latenessWindow= (10*random.randint(0,3) if randGen else 30)
		eventAddress = real_event_addresses[k]
		eventContact = "555-555-5555_" + str(k)
		eventEmail = "eventEmail_"+str(k)+"@notARealThing.com"
		eventHostOrg = "eventHostOrg_"+str(k)
		signature = "signature_"+str(k)
		fireNotice = (6*random.randint(1,5) if randGen else 12)

		##Trip
		tripAddress=real_addresses[k]
		num_seats = (random.randint(0,1)*random.randint(1,4) if randGen else 4)
		preWindow = (5*random.randint(1,9) if randGen else 30)
		on_time = (random.randint(0,1) if randGen else 0)
		must_drive = (random.randint(0,1) if (randGen and num_seats>0) else 0)

		#formalrep? created and maintained by externalUpdate.
		carpoolDict = {'first':first,'last':last,'name':name,'email':email}
		if k<=numberPools:
			poolDict = {'poolName':poolName,'latenessWindow':latenessWindow,'eventAddress':eventAddress,'eventContact':eventContact,'eventEmail':eventEmail,'eventHostOrg':eventHostOrg,'signature':signature,'fireNotice':fireNotice}
		else:
			numPoolsToJoin=min((random.randint(1,numberPools) if randGen else numberPools),k)#All have been created thus far, but if code is changed, it will definitely be true that at most k have been created at this point.
			poolDict={'joinPools':list(range(1,numPoolsToJoin+1))}

		tripDict = {'address':tripAddress,'num_seats':num_seats,'preWindow':preWindow,'on_time':on_time,'must_drive':must_drive}

		fullDict= {'fbId':fbId,'Carpooler':carpoolDict,'Pool':poolDict,'Trip':tripDict}

		dicts.append(fullDict)
	return dicts

@app.route('/q_groupthere/', methods=['GET','POST'])
def q_groupthere():

	job = q.enqueue_call(func=GroupThere,result_ttl=5000)
	print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
	return job.get_id()

	params = GroupThere()
	for ass in params.solution['assignments']:
		names = ass['names']
		print(names)
		#check if names is iterable
		#print each name
	return  str(params.solution['assignments'])


@app.route("/GTresults/", methods=['POST'])
def post_GT_results():
	try:
		data = json.loads(request.data.decode())
		job_key = data["jobID"]
		print("job_key is " + str(job_key))
		print("job_key is " + str(job_key),file=sys.stderr)
	except:
		print("ERROR IN post_get_results",file=sys.stderr)
		return "in post_GT_results",500
	return GT_results(job_key)

@app.route("/GTresults/<job_key>", methods=['GET'])
def GT_results(job_key):
	try:
		job = Job.fetch(job_key, connection=conn)
	except:
		return "No such job",200
	if job.is_finished:
		params=job.result
		print("Job finished in GT_results: " + str(params),file=sys.stderr)
		output = [[('names',ass['names']),('isPossible',ass['isPossible']),('notLatePossible',ass['notLatePossible']),('lateOk',ass['lateOk']),('bestTimes',ass['bestTimes'])] for ass in params.solution['assignments']]
		output = [[ (tup[0],np.asscalar(tup[1]) if isinstance(tup[1],np.generic) else tup[1]) for tup in piece] for piece in output] #Convert np.bool_ to bool, eg
		# output = [{'names':ass['names'],'bestTimes':ass['bestTimes']} for ass in params.solution['assignments']]
		print("output before jsonify: " + str(output),file=sys.stderr)
		a=jsonify(output)
		print("successfully jsonified output!",file=sys.stderr)
		return a,200
	else:
		# print("PROBLEM IS HERE?!")
		return "Still working on GROUPTHERE!!", 202


