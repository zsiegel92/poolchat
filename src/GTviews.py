from GT_interactions import doGroupThere,post_optimization_update,doGroupThere_fromDB

from flask import jsonify,json,render_template
from flask_login import current_user, login_user, logout_user,login_required

import numpy as np
from dateutil.relativedelta import relativedelta


from datetime import datetime
from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

from models import Carpooler,Pool, Trip,Instruction,Team
from groupThere.GroupThere import GroupThere
from helpers import findRelativeDelta

from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups
from emailer import Emailer

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



# After calling, use
# try:
# 		job = Job.fetch(job_key, connection=conn)
# 	except:
# 		return "No such job",200
# 	if job.is_finished:
# 		try:
# 			params=job.result
#			instructions_id = params.instructions_id
# #			instructions = Instruction.query.filter_by(id=instruction_id).first()
# @app.route('/q_groupthere_fromdb/',methods=['POST'])
# @login_required
def q_doGroupThere_fromDB(pool_id=None):
	print('in q_groupthere')
	if request:
		pool_id = request.args.get('pool_id',None)
		if pool_id is None:
			data= request.get_json()
			if data is not None:
				pool_id = data.get("pool_id",None)
	print("pool_id is " + str(pool_id))
	job = q.enqueue_call(func=doGroupThere_fromDB,kwargs={'pool_id':pool_id},result_ttl=5000)

	return job.get_id()


# @app.route('/q_groupthere/', methods=['GET','POST'])
# @login_required
def q_groupthere(pool_id=None):
	print('in q_groupthere')
	if request:
		pool_id = request.args.get('pool_id',None)
		if pool_id is None:
			data= request.get_json()
			if data is not None:
				pool_id = data.get("pool_id",None)
	print("pool_id is " + str(pool_id))
	job = q.enqueue_call(func=doGroupThere,kwargs={'pool_id':pool_id},result_ttl=5000)
	return job.get_id()




# @app.route('/q_repeat_groupthere/', methods=['GET','POST'])
# @login_required
def q_repeat_groupthere():
	print('in q_repeat_groupthere')
	job = q.enqueue_call(func=GroupThere,result_ttl=5000)
	# kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools}
	print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
	return job.get_id()







@app.route("/GTresults/", methods=['POST'])
@login_required
def post_GT_results():
	try:
		data = json.loads(request.data.decode())
		job_key = data["jobID"]
		print("job_key is " + str(job_key))
	except:
		print("ERROR IN post_get_results")
		return "in post_GT_results",500
	return GT_results(job_key)



@app.route("/GTresults/<job_key>", methods=['GET'])
@login_required
def GT_results(job_key):
	print("in GT_results")
	try:
		job = Job.fetch(job_key, connection=conn)
	except:
		return "No such job",200
	if job.is_finished:
		try:
			params=job.result
			print("Job finished in GT_results: " + str(params))
			print("Solution success: " + str(params.solution['success']))
			assert(hasattr(params,'solution'))
			output = [[('names',ass['names']),('emails',ass['emails']),('isPossible',ass['isPossible']),('notLatePossible',ass['notLatePossible']),('lateOk',ass['lateOk']),('bestTimes',ass['bestTimes'])] for ass in params.solution['assignments']]
			output = [[ (tup[0],np.asscalar(tup[1]) if isinstance(tup[1],np.generic) else tup[1]) for tup in piece] for piece in output] #Convert np.bool_ to bool, eg

			email_assignments = [ass.get('emails',None) for ass in params.solution.get('assignments',{})]
			id_assignments = [ass.get('ids',None) for ass in params.solution.get('assignments',{})]
			email=params.email
			carpooler_id = params.carpooler_id
			pool_id = params.pool_id
			success= params.solution['success']
			dur_mat = params.dist_mats['Durations']
			durs_to_event = params.dists_to_event['Durations']
			# dist_mats = {'Distances':None,'Durations':None}
			# dists_to_event={'Distances':None,'Durations':None}
			q.enqueue_call(func=post_optimization_update,kwargs={'email_assignments':email_assignments,'id_assignments':id_assignments,'email':email,'carpooler_id':carpooler_id,'pool_id':pool_id,'success':success,'dur_mat':dur_mat,'durs_to_event':durs_to_event},result_ttl=5000)
		except Exception as exc:
			return jsonify(["ERROR IN GT_results!",str(exc),"params vars: " + str(vars(params))])
		try:
			a=jsonify({'groups':output,'full':params.to_dict()})
		except Exception as exc:
			a= jsonify({'groups':output,'full':"\nSomething bad happened DURING jsonify " + str(exc) + "\n" + str(params)})
		return a,200

	else:
		# print("PROBLEM IS HERE?!")
		return "Still working on GROUPTHERE!!", 202


# @app.route("/email_all/", methods=['GET','POST'])
# @login_required
def email_all_carpoolers(pool_id=None):
	with app.app_context():
		# emailer = Emailer(queue=q)
		if request:
			if request.method=="POST":
				data = json.loads(request.data.decode())
				pool_id = data["pool_id"]
		pool_ids = get_all_pool_ids(pool_id)
		for pool_id in pool_ids:
			q.enqueue_call(func=email_aPool,kwargs={'pool_id':pool_id},result_ttl=5000)
		return "Emails Enqueued.",200


def get_all_pool_ids(pool_id=None):
	pool_ids=[]
	if pool_id is not None:
		pools = Pool.query.filter_by(id=pool_id)
	else:
		pools = Pool.query.all()
	for pool in pools:
		pool_ids.append(pool.id)
	return pool_ids

def email_aPool(pool_id,scheduler_frequency=60):
	emailer=Emailer(q)
	nowish = datetime.now() - relativedelta(minutes=int(scheduler_frequency/2))
	pool=Pool.query.filter_by(id=pool_id).first()
	instruction = Instruction.query.filter_by(pool_id=pool_id).order_by(Instruction.dateTime.desc()).first()
	fireNotice = int(pool.fireNotice)
	eventDateTime= pool.eventDateTime
	eventEmail=pool.eventEmail
	[date,time,fireDateTime] = findRelativeDelta(eventDateTime,fireNotice,mode='hours',delta_after=-1)

	url_base = app.config['URL_BASE']#ends in /
	link = url_base + '?#!/viewPool'
	print("EXAMINING POOL: " + str(pool.poolName))

	if (nowish> fireDateTime) and (not pool.noticeWentOut):
		if not (pool.optimizedYet and pool.optimizationCurrent):
			print("Instructions should be sent in the next hour!")
			pass
		else:
			print("Emailing all members of pool " + str(pool.poolName))
			pool.noticeWentOut = True
			db.session.commit()
			subject= "(GroupThere) Optimal solution for " + str(pool.poolName) + "!"
			poolHTML = "<html><head></head><body>Hi, thanks for making {poolName},<br><br>Please visit <a href='{link}'>GroupThere</a> for a full solution!</body></html>".format(link=link,poolName=pool.poolName)
			poolTXT = 'Thanks for making {poolName}.\n\nFor a full solution, please visit {link}'.format(link=link,poolName=pool.poolName)
			emailer.send_html(eventEmail,html_message=poolHTML,subject=subject,text_message=poolTXT)
			for trip in pool.members:
				carpooler = trip.member
				toAddress=carpooler.email

				html_body= render_template('emails/solution.html',carpooler=carpooler,pool=pool,trip=trip,instruction=instruction,link=link)
				text_message=render_template('emails/solution.txt',carpooler=carpooler,pool=pool,trip=trip,instruction=instruction,link=link)
				html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
				emailer.send_html(toAddress,html_message=html,subject=subject,text_message=text_message)

	elif (nowish>fireDateTime):
		print("Should have already fired a notice for pool " + str(pool.poolName) + "!")
	else:
		print("We do not yet have to fire a notice for pool " + str(pool.poolName) + "!")



def do_all_gt(scheduler_frequency=60):
	nowish = datetime.now() - relativedelta(minutes=int(scheduler_frequency/2))
	pools = Pool.query.all()
	for pool in pools:
		pool_id=pool.id
		poolName = pool.poolName
		fireNotice = int(pool.fireNotice)
		eventDateTime= pool.eventDateTime
		[date,time,fireDateTime] = findRelativeDelta(eventDateTime,fireNotice,mode='hours',delta_after=-1)
		print("EXAMINING POOL: " + str(poolName))

		if (nowish> fireDateTime) and (not (pool.optimizedYet and pool.optimizationCurrent)):
			print("TIME TO OPTIMIZE!")
			q.enqueue_call(func=doGroupThere_fromDB,kwargs={'pool_id':pool_id},result_ttl=5000)
			print("Enqueued optimization for pool " + str(poolName))

		elif (nowish>fireDateTime):
			print("Should have already optimized pool " + str(poolName) + "!")
		else:
			print("We do not yet have to optimize pool " + str(poolName) + "!")
	return("All optimization enqueued.")


















