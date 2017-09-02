from page_interactions import view_pool_formal
import requests

import random
from flask import render_template,url_for,jsonify,json,make_response,send_from_directory
from flask_login import current_user, login_user, logout_user,login_required



from collections import OrderedDict
import googlemaps


import os
import config

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)


from interactions import newPool
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone,Team,TempTeam,Trip_Distance,Event_Distance,Instruction

from groupThere.GroupThere import GroupThere

from GT_manager import create_generic_parameters
from GT_interactions import doGroupThere_fromDB

from app import app,request,abort
from database import db
from emailer import Emailer
emailer=Emailer(q)
gmaps = googlemaps.Client(key=os.environ['DISTMAT_API_KEY'])
#usage:
# emailer.email(toAddress,message="",subject="")
# emailer.self_email(message=message,subject=subject)

import wtforms_ext
emailForm=wtforms_ext.EmailForm(ng_click='getCarpoolerInfo()')


@app.route('/view_carpooler/',methods=['POST'])
@login_required
def view_carpooler():
	# data = json.loads(request.data.decode())
	# data=request.get_json(force=True)
	data= request.form
	form=wtforms_ext.EmailForm(data)
	if form.validate():
		email=form.emailField.data
		carpooler = Carpooler.query.filter_by(email=email).first()
		if carpooler is not None:
			return jsonify(carpooler.to_dict_formal()),200
		else:
			carpooler = Carpooler()
			db.session.add(carpooler)
			carpooler.externalUpdate(email=email)
			db.session.commit()
			return jsonify(carpooler.to_dict()),201
	else:
		return "Data invalid - errors: " + str(form.errors) +" (FLASK)",500

@app.route('/view_pool/',methods=['POST'])
@login_required
def post_call_view_pool():
	# pool_id = request.args.get('pool_id',None)
	data = json.loads(request.data.decode())
	pool_id = data.get("pool_id",None)
	print("POOL ID IS " + str(pool_id))
	poolDict=view_pool_formal(pool_id)

	pool=Pool.query.filter_by(id=pool_id).first()

	if pool is None:
		poolDict={}
		status=204
	elif current_user not in [trip.member for trip in pool.members]:
		# status=401 #Not Authorized!
		status=206 #partial content
		poolDict={"Affiliated Teams":[team.name for team in pool.teams],"Members":[trip.member.name for trip in pool.members],"Name":pool.poolName,"Date":str(pool.eventDate) +" "+ str(pool.eventTime),"Lateness Window":pool.latenessWindow,"Address":pool.eventAddress,"Contact (phone)":pool.eventContact,"Email":pool.eventEmail,"Host Organization":pool.eventHostOrg,"Signature":pool.signature,"Fire Notice":pool.fireNotice}
	else:
		status=200
		poolDict = {"Affiliated Teams":[team.name for team in pool.teams],"Members":[trip.member.name for trip in pool.members],"Name":pool.poolName,"Date":str(pool.eventDate) +" " + str(pool.eventTime),"Lateness Window":pool.latenessWindow,"Address":pool.eventAddress,"Contact (phone)":pool.eventContact,"Email":pool.eventEmail,"Host Organization":pool.eventHostOrg,"Signature":pool.signature,"Fire Notice":pool.fireNotice}

	return jsonify(poolDict),status

@app.route('/api/re_optimize',methods=['POST'])
@login_required
def api_re_optimize():
	pool_id=request.values.get('pool_id')
	pool = Pool.query.filter_by(id=pool_id).first()
	if current_user not in [trip.member for trip in pool.members]:
		return "Not a member of this pool! Access denied.",401
	else:
		q.enqueue_call(func=doGroupThere_fromDB,kwargs={'pool_id':pool_id},result_ttl=5000)
		return "Enqueued the work to re-process this request.",200


@app.route('/api/get_most_recent_instructions',methods=['POST'])
@login_required
def api_get_recent_instructions():
	pool_id=request.values.get('pool_id')
	pool = Pool.query.filter_by(id=pool_id).first()
	if current_user not in [trip.member for trip in pool.members]:
		return "Not a member of this pool! Access denied.",401
	else:
		instruction = Instruction.query.filter_by(pool_id=pool_id).order_by(Instruction.dateTime.desc()).first()
		if instruction is not None:
			instruct = json.loads(instruction.instruction)
			instruct['my_id']=current_user.id
			try:
				instruct['my_index'] = instruct['carpooler_ids'].index(current_user.id)
			except:
				instruct['my_index'] =-1
			instruct['numel'] = len(instruct['carpooler_ids'])
			my_ass = -1
			for i in range(len(instruct['assignments'])):
				if hasattr(instruct['assignments'][i]['ids'],'__iter__'):
					if current_user.id in instruct['assignments'][i]['ids']:
						my_ass=i
				else:
					if current_user.id == instruct['assignments'][i]['ids']:
						my_ass=i

			instruct['my_ass_index']=my_ass

			return jsonify(instruct),200
		else:
			return "No instructions generated yet!",404



@app.route('/view_pool/<int:number>/',methods=['GET'])
@login_required
def call_view_pool(number):
	poolDict=view_pool_formal(number)
	poolRep = '<br>'.join(['{0}: {1}'.format(key, value) for (key, value) in poolDict.items()])
	return poolRep,200

@app.route('/api/get_pool_info_for_user',methods=['POST'])
@login_required
def api_get_pool_info_for_user():
	# team.to_dict(self) returns {'id':self.id,'email':self.email,'name':self.name}
	teams = [team.to_dict() for team in current_user.teams]

	joined_pool_ids = [trip.pool.id for trip in current_user.pools]

	team_pool_ids = list(set([pool.id for team in current_user.teams for pool in team.pools])) #uniquified

	unjoined_pool_ids = list(set(team_pool_ids).difference(joined_pool_ids))


	joined_pools =[{'id':trip.pool.id,'name':trip.pool.poolName,'date':trip.pool.eventDate,'time':trip.pool.eventTime,'address':trip.pool.eventAddress,'email':trip.pool.eventEmail,'fireNotice':trip.pool.fireNotice,'latenessWindow':trip.pool.latenessWindow,'dateTime':trip.pool.eventDateTime.isoformat(),'trip':{'address':trip.address,'num_seats':trip.num_seats,'preWindow':trip.preWindow,'on_time':trip.on_time,'must_drive':trip.must_drive},'teams':[team.to_dict() for team in trip.pool.teams]} for trip in current_user.pools]
	unjoined_pools=[{'id':pool.id,'name':pool.poolName,'date':pool.eventDate,'time':pool.eventTime,'address':pool.eventAddress,'email':pool.eventEmail,'fireNotice':pool.fireNotice,'latenessWindow':pool.latenessWindow,'dateTime':pool.eventDateTime.isoformat(),'teams':[poolTeam.to_dict() for poolTeam in pool.teams],'team_names':[poolTeam.name for poolTeam in pool.teams]} for team in current_user.teams for pool in team.pools if pool.id in unjoined_pool_ids]
	carpooler={'name':current_user.name,'first':current_user.firstname,'last':current_user.lastname,'email':current_user.email}

	seen_ids = []
	unique_unjoined=[]
	for pool in unjoined_pools:
		if pool['id']in seen_ids:
			pass
		else:
			seen_ids.append(pool['id'])
			unique_unjoined.append(pool)

	eligible_pools=unique_unjoined
	for pool in eligible_pools:
		print("Can join a pool with dateTime " + str(pool['dateTime']))
		# print("timezone is " + str(pool['dateTime'].utcoffset().total_seconds()))
	return jsonify({'teams':teams,'joined_pools':joined_pools,'eligible_pools':eligible_pools,'carpooler':carpooler}),200



# @app.route('/api/get_teams/',methods=['POST'])
# @login_required
# def api_get_teams():
# 	team_names = [team.name for team in current_user.teams]
# 	team_ids = [team.id for team in current_user.teams]

# 	if (team_ids is None) or (len(team_ids)==0):
# 		team_ids = []
# 		team_names = []
# 		message= "You have no teams."
# 	else:
# 		message = "You are a part of the following teams: " + ", ".join(team_names) + "."

# 	return jsonify({'team_names':team_names,'team_ids':team_ids,'message':message,}),200




# @app.route('/api/get_teams/',methods=['POST'])
# @login_required
# def api_get_teams():
@app.route('/api/get_teams/',methods=['POST'])
@login_required
def api_get_teams():
	allTeams = Team.query.all()

	team_ids = [team.id for team in current_user.teams]

	foreign_team_names = [team.name for team in allTeams if team.id not in team_ids]
	foreign_team_ids = [team.id for team in allTeams if team.id not in team_ids]

	team_ids = [team.id for team in current_user.teams]
	team_objects = [{'name':team.name,'id':team.id,'email':team.email} for team in current_user.teams]
	foreign_team_ids = [team.id for team in allTeams if team.id not in team_ids]
	foreign_team_objects=[{'name':team.name,'id':team.id} for team in allTeams if team.id not in team_ids]

	print("foreign_team_ids: " + str(foreign_team_ids))
	if (foreign_team_ids is None) or (len(foreign_team_ids)==0):
		foreign_team_ids = []
		foreign_team_names = []
		message= "You are part of EVERY team in the GroupThere database!"
	else:
		message = "You can join the following teams: " + ", ".join(foreign_team_names) + "."
	makePoolMessage = "You are a member of the following teams: " + ", ".join([team['name'] for team in team_objects]) + "."

	selfDict={'id':current_user.id,'name':current_user.name,'email':current_user.email}
	return jsonify({'teams':team_objects,'foreign_teams':foreign_team_objects,'self':selfDict,'message':message,'makePoolMessage':makePoolMessage}),200



# @app.route('/', methods=['GET', 'POST'])
# @login_required
# def index():
# 	errors = []
# 	results = {}
# 	if request.method == "POST":
# 		# get url that the user has entered
# 		try:
# 			# url = request.form['url']
# 			pass
# 		except:
# 			errors.append(
# 				"Unable to get URL. Please make sure it's valid and try again."
# 			)
# 	return render_template('index.html', emailForm=emailForm,errors=errors, results=results)
@app.route('/', methods=['GET', 'POST'])
def index():
	print("Sending index.html")
	return app.send_static_file('index.html')
	# return render_template('index.html')

@app.route('/form_views/',methods=['POST'])
@login_required
def render_forms_1():
	return render_template('form_sequence.html')



#TODO: Flip through users in db, message them their table has been dropped :)
@app.route('/dropTabs', methods=["GET","POST"])
@login_required
def drop_table():
	print("Dropping all tables")
	rando=random.randint(1,10)
	try:
		if current_user.is_anonymous():

			id = "anonymousId"
			return "must log in to drop tables.",302
		else:

			carpooler = Carpooler.query.filter_by(id=current_user.id).first()
			copy_dict=carpooler.to_copy_dict()
			logout_user()
			# db.session.expunge(carpooler)  # expunge the object from session
			# make_transient(carpooler)  # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_api.html#sqlalchemy.orm.session.make_transient
			db.session.commit()
			print("committed once")
			db.session.close_all()
			print("closed sessions")
			db.reflect()
			print("reflected")
			db.session.close()
			print("closed session")
			db.drop_all()
			db.create_all()
			db.session.commit()
			carpooler = Carpooler(**copy_dict)
			login_user(carpooler)
			db.session.add(carpooler)
			db.session.commit()
			return "Tables dropped (except for you)!",200
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc),500
	else:
		return "Dropped and re-created all tables! Random integer: " + str(rando)+ " (your id is " + str(id) + ")", 200


@app.route('/triggers/',methods=['GET',"POST"])
@login_required
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
	return render_template('trigger_base.html',output_list=output_list,request_vars=request_vars)


@app.route('/api/get_email/',methods=['POST'])
@login_required
def api_get_email():
	return getattr(current_user,'email',''),200





@app.route('/q_populate/',methods=['GET',"POST"])
@login_required
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
		drop_table()

		job = q.enqueue_call(func=populate_generic,kwargs = {'n':n,'randGen': randGen,'numberPools':numberPools},result_ttl=5000)
		print("job.get_id() = " + str(job.get_id())) #job.result will store output of populate_generic(n), which is "output_list" in the non-enqueued version above
		return job.get_id()
	return "error_occurred_in_q_populate"



@app.route("/results/", methods=['POST'])
@login_required
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
@login_required
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
	elif job.is_queued:
		# print("PROBLEM IS HERE?!")
		return "Job queued!", 202
	elif job.is_started:
		return "Job being processed AT THIS MOMENT!", 202
	elif job.is_failed:
		return "Job failed!",500

#NOTE: All POOL creators are ONLY IN THAT SINGLE POOL
def populate_generic(n,numberPools=2,randGen = False):
	print("in page_interactions.populate_generic(" + str(n) + ")")
	with app.app_context():
		dicts = create_generic_parameters(n=n,numberPools=numberPools,randGen=randGen)
		print("dicts = " + str(dicts))
		for fullDict in dicts:
			print("oneDict = " + str(fullDict))
			fbId=fullDict['fbId']
			carpooler = Carpooler()
			db.session.add(carpooler)
			db.session.commit()
			carpooler.fbId=fbId
			carpooler.externalUpdate(setForMode='fields',**fullDict['Carpooler'])
			db.session.commit()

			if 'joinPools' in fullDict['Pool']:
				for pool_id in fullDict['Pool']['joinPools']:
					pool = Pool.query.filter_by(id=pool_id).first()
					if pool is not None:
						trip = None
						try:
							trip = Trip.query.filter_by(carpooler_id=carpooler.id,pool_id=pool.id).first()
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

@app.route('/api/confirm_address/',methods=['POST'])
@login_required
def api_confirm_address():
	try:
		address=request.values.get('address')
		GMAPS_GEOCODE_API_TOKEN =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).GEOCODE_API_KEY #INTERACTIONS MOVEMENT
		# GMAPS_GEOCODE_API_TOKEN = app.config['GMAPS_GEOCODE_API_TOKEN']

		geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
		querystring = {"address":address,"key":GMAPS_GEOCODE_API_TOKEN}
		response = requests.request("GET", geocode_url, params=querystring)
		response=response.json()

		formatted_address =response['results'][0]['formatted_address']
		lat = response['results'][0]['geometry']['location']['lat']
		lon = response['results'][0]['geometry']['location']['lng']


		# GMAPS_STATIC_API_TOKEN = app.config['GMAPS_STATIC_API_TOKEN']
		GMAPS_STATIC_API_TOKEN =getattr(config,os.environ['APP_SETTINGS'].split('.')[1]).GMAPS_STATIC_API_TOKEN #INTERACTIONS MOVEMENT
		marker_attributes="color:red|{lat},{lon}".format(lat=lat,lon=lon)
		static_maps_base_url = "https://maps.googleapis.com/maps/api/staticmap"
		querystring = {"center":str(lat)+","+str(lon),"zoom":"14","size":"400x400","markers":marker_attributes,"key":GMAPS_STATIC_API_TOKEN}
		response = requests.request("GET", static_maps_base_url, params=querystring,stream=True)
		full_url= response.url
		del response
		# img = response.content
		return jsonify({'formatted_address':formatted_address,'image_url':full_url}),200
		# messenger.send_image(sender_id,full_url)
	except Exception as exc:
		print(exc)
		return "Error",400


