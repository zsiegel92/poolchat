from page_interactions import view_pool,view_pool_formal,populate_group_test
import requests
import copy
import random
from flask import render_template,url_for,jsonify,json,make_response,send_from_directory
from flask_login import current_user, login_user, logout_user,login_required
from sqlalchemy.orm.session import make_transient
from dateutil.parser import parse
from datetime import datetime

from collections import OrderedDict
import numpy as np
import sys
import os
import config

from datetime import datetime
from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)
import pickle

from helpers import findRelativeDelta
from interactions import newPool
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone,Team
from groupThere.GroupThere import GroupThere


from GT_manager import create_generic_parameters


from app import app,request,abort
from database import db

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


	joined_pools =[{'id':trip.pool.id,'name':trip.pool.poolName,'date':trip.pool.eventDate,'time':trip.pool.eventTime,'address':trip.pool.eventAddress,'email':trip.pool.eventEmail,'fireNotice':trip.pool.fireNotice} for trip in current_user.pools]
	unjoined_pools=[{'id':pool.id,'name':pool.poolName,'date':pool.eventDate,'time':pool.eventTime,'address':pool.eventAddress,'email':pool.eventEmail,'fireNotice':pool.fireNotice} for team in current_user.teams for pool in team.pools if pool.id in unjoined_pool_ids]

	seen_ids = []
	unique_unjoined=[]
	for pool in unjoined_pools:
		if pool['id']in seen_ids:
			pass
		else:
			seen_ids.append(pool['id'])
			unique_unjoined.append(pool)

	eligible_pools=unique_unjoined

	return jsonify({'teams':teams,'joined_pools':joined_pools,'eligible_pools':eligible_pools}),200



@app.route('/api/get_teams/',methods=['POST'])
@login_required
def api_get_teams():
	team_names = [team.name for team in current_user.teams]
	team_ids = [team.id for team in current_user.teams]

	if (team_ids is None) or (len(team_ids)==0):
		team_ids = []
		team_names = []
		message= "You have no teams."
	else:
		message = "You are a part of the following teams: " + ", ".join(team_names) + "."

	return jsonify({'team_names':team_names,'team_ids':team_ids,'message':message,}),200


@app.route('/api/get_foreign_teams/',methods=['POST'])
@login_required
def api_get_foreign_teams():
	allTeams = Team.query.all()

	team_names = [team.name for team in current_user.teams]
	team_ids = [team.id for team in current_user.teams]

	foreign_team_names = [team.name for team in allTeams if team.name not in team_names]
	foreign_team_ids = [team.id for team in allTeams if team.name not in team_names]
	print("foreign_team_ids: " + str(foreign_team_ids))
	print("foreign_team_names: " + str(foreign_team_names))
	if (foreign_team_ids is None) or (len(foreign_team_ids)==0):
		foreign_team_ids = []
		foreign_team_names = []
		message= "You are part of EVERY team in the GroupThere database!"
	else:
		message = "You can join the following teams: " + ", ".join(foreign_team_names) + "."

	return jsonify({'foreign_team_names':foreign_team_names,'foreign_team_ids':foreign_team_ids,'message':message,}),200
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
	# return app.send_static_file('index.html')
	return render_template('index.html')

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

@app.route('/api/create_pool/',methods=['POST'])
@login_required
def api_create_pool():
	print("request.values: " + str(request.values))

	poolName = request.values.get("name")

	redundant_pool = Pool.query.filter_by(poolName=poolName).first()
	if redundant_pool is None:

		eventAddress= request.values.get("address")
		eventEmail=request.values.get("email")
		fireNotice= int(request.values.get("fireNotice"))
		latenessWindow= int(request.values.get("latenessWindow"))
		eventDateTime=parse(request.values.get("dateTimeText"))
		team_ids = json.loads(request.values.get("team_ids"))

		pool=Pool()
		trip = Trip()
		trip.pool=pool
		current_user.pools.append(trip)
		current_user.current_pool_id=pool.id
		db.session.add(pool)
		db.session.add(trip)
		db.session.commit()


		pool.poolName=poolName
		pool.eventAddress=eventAddress
		pool.eventEmail=eventEmail
		pool.fireNotice = fireNotice
		pool.latenessWindow = latenessWindow
		pool.eventDateTime = eventDateTime
		pool.eventDate = eventDateTime.strftime("%d/%m/%y")
		pool.eventTime = eventDateTime.strftime("%I:%M %p")

		print("Adding event at " + str(pool.eventDate) + " at " + str(pool.eventTime))
		# >>> d.strftime("%d/%m/%y")
		# '11/03/02'
		# >>> d.strftime("%A %d. %B %Y")
		# 'Monday 11. March 2002'
		# See http://strftime.org/

		db.session.commit()

		message = "Pool added to database"

		# team_names=request.values.get("teams")

		for team_id in team_ids:
			team = Team.query.filter_by(id=team_id).first()
			if current_user in team.members:
				team.pools.append(pool)
				message+="\nTeam affiliations confirmed."
			else:
				message+="User not a member of " + str(team.name)

			db.session.commit()

		return "Pool added to database.", 200
	else:
		return "Pool already in database",409

@app.route('/api/get_email/',methods=['POST'])
@login_required
def api_get_email():
	return getattr(current_user,'email',''),200

@app.route('/api/create_team/',methods=['POST'])
@login_required
def api_create_team():
	print("request.values: " + str(request.values))

	name =request.values.get("name")
	email=request.values.get("email")
	codeword=request.values.get("codeword")
	redundant_team = Team.query.filter_by(name=name).first()
	if redundant_team is None:
		team=Team()
		team.name = name
		team.email=email
		team.password=codeword
		db.session.add(team)
		db.session.add(team)
		db.session.commit()
		team.members.append(current_user)
		db.session.commit()
		return "Team added to database.", 200
	else:
		return "Team already in database.", 409

@app.route('/api/join_team/',methods=['POST'])
@login_required
def api_join_team():
	print("request.values: " + str(request.values))

	teamname =request.values.get("teamname")
	codeword=request.values.get("codeword")
	team = Team.query.filter_by(name=teamname).first()
	if team is not None:
		if team.password==codeword:
			team.members.append(current_user)
			db.session.commit()
			return "Added to team.", 200
		else:
			return "Wrong codeword",401

	else:
		return "Team not found.", 400





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
					# pool_id = pool__id
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

# @app.route('/static/<path:path>')
# def send_js(path):
# 	print("Serving static file")
# 	return send_from_directory('', path)


@app.route('/get_db_metadata')
@login_required
def get_db_metadata():
	metadata1=str(vars(app.extensions['migrate'].db.metadata))
	metadata2 = str(vars(db.metadata))
	metadata=metadata2
	return metadata,200

@app.route('/get_db_metadata2')
@login_required
def get_db_metadata2():
	metadata1=str(vars(app.extensions['migrate'].db.metadata))
	metadata2 = str(vars(db.metadata))
	metadata=metadata1
	return metadata,200


@app.route('/clear_metadata')
@login_required
def clear_data():
	meta = db.metadata
	for table in reversed(meta.sorted_tables):
		print('Clear table %s' % table)
		db.session.execute(table.delete())
	db.session.commit()
	metadata = str(vars(db.metadata))
	return metadata,200


