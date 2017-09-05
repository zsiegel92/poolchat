from flask import render_template,url_for,jsonify,json,make_response,send_from_directory
from flask_login import current_user, login_user, logout_user,login_required

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime

import googlemaps
from urllib.parse import quote_plus

from GIS_routines import gen_dist_row,gen_dist_col,gen_one_distance
from GT_interactions import doGroupThere_fromDB


import os

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

from encryption import bcrypt

from models import  Carpooler,Pool, Trip,Team,TempTeam,Trip_Distance,Event_Distance,Instruction



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


#TODO:
#build a "reject" that emails user with id user_id
@app.route('/api/approve_team/teamId/<int:team_id>/userId/<int:user_id>',methods=['POST'])
@login_required
def api_approve_team(team_id,user_id):
	print("in api_approve_team")
	team = Team.query.filter_by(id=team_id).first()
	if team is None:
		return "No such team!",401
	if current_user not in team.members:
		return "You are not a member of this team, and as such cannot approve a request to join it!",401
	carpooler = Carpooler.query.filter_by(id=user_id).first()
	if carpooler is None:
		return "No such user!",401

	team.members.append(carpooler)
	db.session.commit()
	subject="(GroupThere) Approved to join team {team_name}".format(team_name=team.name)
	url_base = app.config['URL_BASE']#ends in /
	link = url_base + '?#!/joinTeam'
	message = "Hi {new_name},\nYou have been added to the GroupThere team {team_name} by the member {organizer_name} ({organizer_email})! Congratulations!\nAnyone can join this team using the codeword '{codeword}', so go ahead and invite others to this team by sending them to {link} ! \n\nBest Wishes,\nGroupThere".format(new_name=carpooler.name,organizer_name=current_user.name,team_name=team.name, organizer_email=current_user.email,codeword=team.password,link=link)

	emailer.email(carpooler.email,message=message,subject=subject)

	return_message = "User {user_name} added to team {team_name}. They have been notified via an email to {user_email}, which also lets them know that the team's codeword is {codeword}.".format(user_name=carpooler.name,team_name=team.name,user_email=carpooler.email,codeword=team.password)
	return jsonify({'message':return_message,'email':{'from':emailer.get_email(),'to':carpooler.email,'body':message,'subject':subject}}),200



@app.route('/api/request_team_codeword/teamId/<int:team_id>',methods=['POST'])
@login_required
def api_request_team_codeword(team_id):
	print("User with id " + str(current_user.id) + " requesting access to team with id " + str(team_id))
	team = Team.query.filter_by(id=team_id).first()
	if team is None:
		print("ERROR WITH REQUEST_TEAM_CODEWORD - NO SUCH TEAM")
		return "No such team",401
	else:
		# text_message =5
		toAddress=team.email
		subject = "GroupThere user " + str(current_user.name) + " wants to join your team " + str(team.name) + "!"

		url_base = app.config['URL_BASE']#ends in /
		print("current_user.id: " + str(current_user.id))
		print("team.id: " + str(team.id))
		print("quote_plus(str(team.id)) is: " + str(quote_plus(str(team.id))))
		print("quote_plus(str(current_user.id)) is: " + str(quote_plus(str(current_user.id))))

		link = url_base + '?#!/approveTeamJoin/{new_user_id}/{team_id}'.format(new_user_id=quote_plus(str(current_user.id)),team_id=quote_plus(str(team.id)))
		html_body= render_template('emails/request_join_team.html',team=team,link=link)
		text_message=render_template('emails/request_join_team.txt',team=team,link=link)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(toAddress,html_message=html,subject=subject,text_message=text_message)
		# emailer.send_html_body(toAddress,html_body=html_body,subject=subject,text_message=text_message)
		return "A request has been sent to the owner of team {team_name}! Alternatively, ask anyone you know who is a member of this team to visit {link}".format(team_name=team.name, link=link),200



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
		print("dateTimeText is " + str(request.values.get("dateTimeText")))
		print("eventDateTime set to: " + str(eventDateTime))
		team_ids = json.loads(request.values.get("team_ids"))

		pool=Pool()
		db.session.add(pool)
		db.session.commit()


		pool.poolName=poolName
		pool.eventAddress=eventAddress
		pool.eventEmail=eventEmail
		pool.fireNotice = fireNotice
		pool.latenessWindow = latenessWindow
		pool.eventDateTime = eventDateTime
		pool.eventDate = eventDateTime.strftime("%m/%d/%y")
		pool.eventTime = eventDateTime.strftime("%I:%M %p")

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
				message+="\nTeam affiliations confirmed for team " + str(team.name)
			else:
				message+="User not a member of " + str(team.name)

			db.session.commit()
		print(message)
		return "Pool added to database.", 200
	else:
		return "Pool already in database",409




@app.route('/api/create_trip/',methods=['POST'])
@login_required
def api_create_trip():
	tripform = wtforms_ext.tripForm(request.form)

	if tripform.validate():
		pool_id=tripform.pool_id.data


		pool=Pool.query.filter_by(id=pool_id).first()
		if pool is None:
			return "No such event!",400

		if current_user in [trip.member for trip in pool.members]:
			if (tripform.resubmit.data == True):
				trip = Trip.query.filter_by(pool_id=pool_id,carpooler_id = current_user.id).first()
			else:
				return "You are already part of this event!",409
		else:

			trip = Trip()
			trip.pool=pool
			trip.member=current_user

			db.session.add(trip)
			db.session.commit()

		print("STARTING TO ADD FIELDS")

		tripform.populate_obj(trip) #has additional "resubmit" property
		pool.noticeWentOut=False
		pool.optimizationCurrent=False
		db.session.commit()

		q.enqueue_call(func=get_trip_dists,kwargs = {'carpooler_id':current_user.id,'pool_id':pool.id},result_ttl=5000)
		q.enqueue_call(func=doGroupThere_fromDB,kwargs={'pool_id':pool_id},result_ttl=5000)
		# job.get_id()

		if (tripform.resubmit.data == True):
			q.enqueue_call(func=send_pool_trip_update,kwargs={'pool_id':pool.id,'carpooler_id':current_user.id},result_ttl=5000)
			return "Updated trip in database!",200
		else:
			q.enqueue_call(func=send_pool_join_notice,kwargs={'pool_id':pool.id,'carpooler_id':current_user.id},result_ttl=5000)
			return "Added trip to database!",200

	else:
		return "Input invalid - errors: " + str(tripform.errors) +" (FLASK)",500

# def get_instruction_history(pool_id):
# 	instructions = Instruction.query.filter_by(pool_id=pool_id).order_by(Instruction.dateTime.desc()).all()
# 	return jsonify([instruction.to_dict() for instruction in instructions]),200


@app.route('/api/create_team/',methods=['POST'])
@login_required
def api_create_team():
	print("request.values: " + str(request.values))

	name =request.values.get("name")
	email=request.values.get("email")
	codeword=request.values.get("codeword")
	redundant_team = Team.query.filter_by(name=name).first()
	redundant_temp = TempTeam.query.filter_by(name=name).first()
	if (redundant_team is not None) or (redundant_temp is not None):
		return "Team already in database.", 409

	team=TempTeam()
	team.name=name
	team.email=email
	team.password=codeword
	team.carpooler_id=current_user.id
	db.session.add(team)
	db.session.commit()

	if current_user.email.lower()==email.lower():
		team.confirmed_email=True
		db.session.commit()
		#Maybe send "Your team is awaiting approval from an admin" email?
		send_team_admin_approval_email(team)
		return "Team awaiting admin approval.", 202
	else:
		send_team_email_confirmation(team)
		send_team_admin_approval_email(team)
		return "Team status pending admin approval and email confirmation.", 202



def send_pool_join_notice(pool_id,carpooler_id):
	with app.app_context():
		pool=Pool.query.filter_by(id=pool_id).first()
		carpooler = Carpooler.query.filter_by(id=carpooler_id).first()
		trip = Trip.query.filter_by(carpooler_id=carpooler_id,pool_id=pool_id).first()
		instruction = Instruction.query.filter_by(pool_id = pool_id).order_by(Instruction.dateTime.desc()).first()
		if carpooler is None or pool is None or trip is None:
			assert(True==False)
		email = pool.eventEmail
		url_base = app.config['URL_BASE']#ends in /
		subject = "(GroupThere) - " + str(pool.poolName) +" has a new member!"
		link = '{base}?#!/viewPool'.format(base=url_base)
		html_body = render_template('emails/tripJoin.html',link=link,carpooler=carpooler,pool=pool,trip=trip,instruction=instruction)
		text_message = render_template('emails/tripJoin.txt',link=link,carpooler=carpooler,pool=pool,trip=trip,instruction=instruction)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "email sent!"

def send_pool_trip_update(pool_id,carpooler_id):
	with app.app_context():
		pool=Pool.query.filter_by(id=pool_id).first()
		carpooler = Carpooler.query.filter_by(id=carpooler_id).first()
		trip = Trip.query.filter_by(carpooler_id=carpooler_id,pool_id=pool_id).first()
		instruction = Instruction.query.filter_by(pool_id = pool_id).order_by(Instruction.dateTime.desc()).first()
		if carpooler is None or pool is None or trip is None:
			assert(True==False)
		email = pool.eventEmail
		url_base = app.config['URL_BASE']#ends in /
		subject = "(GroupThere) - " + str(pool.poolName) +" member " + str(carpooler.name) + " has edited their trip details."
		link = '{base}?#!/viewPool'.format(base=url_base)
		html_body = render_template('emails/tripUpdate.html',link=link,carpooler=carpooler,pool=pool,trip=trip,instruction=instruction)
		text_message = render_template('emails/tripUpdate.txt',link=link,carpooler=carpooler,pool=pool,trip=trip,instruction=instruction)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "email sent!"





def send_team_email_confirmation(temp_team,second=False):
	#utilize current_user
	#temp teams have an id that is not guessable.
	with app.app_context():
		print("in send_team_email_confirmation")
		email=temp_team.email.lower()
		url_base = app.config['URL_BASE']#ends in /
		#send a link to ?#!/register to whatever the email is
		subject = "Confirm Email for New GroupThere Team " + str(temp_team.name) +"!"
		link = '{base}?#!/confirmTeamEmail/{email}/{id}'.format(base=url_base,email=quote_plus(temp_team.email.lower()),id=quote_plus(str(temp_team.id)))
		if temp_team.carpooler_id != current_user.id:
			carpooler = Carpooler.query.filter_by(id=temp_team.carpooler_id).first()
		else:
			carpooler = current_user

		if second is False:
			print("Sending second confirmation email for team! Team approved yet still no email confirmation!")
			html_body= render_template('emails/confirmTeamEmail.html',link=link,team=temp_team,carpooler=carpooler)
			text_message=render_template('emails/confirmTeamEmail.txt',link=link,team=temp_team,carpooler=carpooler)
		else:
			print("Sending first confirmation email for team!")
			subject = "Your team has been approved! Confirm Email to start using GroupThere with Team " + str(temp_team.name) +"!"
			html_body= render_template('emails/second_confirmTeamEmail.html',link=link,team=temp_team,carpooler=carpooler)
			text_message=render_template('emails/second_confirmTeamEmail.txt',link=link,team=temp_team,carpooler=carpooler)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "email sent!"

#TODO: write second_confirmTeamEmail.html and .txt email
#TODO: make {url_base}?#!/approveTeam/:team_id/:team_key ping {url_base}api/approve_team with params {team_id:,team_key:}
# TODO: write admin_approve_team.html and .txt emails!
def send_team_admin_approval_email(temp_team):
	with app.app_context():
		team_key = bcrypt.generate_password_hash(temp_team.name).decode('utf-8')
		team_id = temp_team.id

		url_base = app.config['URL_BASE']#ends in /
		link = '{base}?#!/adminApproveTeam/{team_id}/{team_key}'.format(base=url_base,team_id=quote_plus(team_id),team_key=quote_plus(team_key))
		carpooler=Carpooler.query.filter_by(id=temp_team.carpooler_id).first()
		subject = "Approve team " + str(temp_team.name)
		html_body= render_template('emails/admin_approve_team.html',link=link,team=temp_team,carpooler=carpooler)
		text_message=render_template('emails/admin_approve_team.txt',link=link,team=temp_team,carpooler=carpooler)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.self_send_html_body(html_body=html,subject=subject,text_message=text_message)

def send_team_created_email(temp_team):
	with app.app_context():
		print("in send_team_email_confirmation")
		email=temp_team.email.lower()
		url_base = app.config['URL_BASE']#ends in /
		subject = "(GroupThere) Your team is ready to roll!"
		link = '{base}?#!/makePool'.format(base=url_base)
		carpooler = Carpooler.query.filter_by(id=temp_team.carpooler_id).first()

		html_body= render_template('emails/team_created.html',link=link,team=temp_team,carpooler=carpooler)
		text_message=render_template('emails/team_created.txt',link=link,team=temp_team,carpooler=carpooler)

		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "email sent!"

@app.route('/api/confirm_team_email',methods=['POST'])
def confirm_team_email():
	email=request.values.get('email')
	my_id = request.values.get('id')
	temp_team=TempTeam.query.filter_by(id=my_id).first()
	if temp_team is None:
		return "No such team!",404
	if str(temp_team.email) != str(email):
		return "Invalid confirmation link!",400
	else:
		if temp_team.approved is True:
			send_team_created_email(temp_team)
			return legitimize_team(temp_team)
		else:
			temp_team.confirmed_email = True
			db.session.commit()
			return jsonify({'message': str(temp_team.name) + "'s email (" + str(temp_team.email) + ") is confirmed, but team's status is awaiting confirmation from the GroupThere administrators.","team_name":temp_team.name}),200



@app.route('/api/admin_approve_team',methods=['POST'])
@login_required
def api_admin_approve_team():
	print("in api_admin_approve_team. request.values is " + str(request.values))
	team_id=request.values.get('team_id')
	team_key=request.values.get('team_key')

	temp_team = TempTeam.query.filter_by(id=str(team_id)).first()
	if temp_team is None:
		msg= "No such team! team_id is " + str(team_id)
		return jsonify({'message':msg,"team_name":"undefined"}),404

	if not bcrypt.check_password_hash(team_key,temp_team.name):
		return jsonify({'message':"Incorrect link!","team_name":"undefined"}),404
	else:
		temp_team.approved=True
		db.session.commit()

	if temp_team.confirmed_email==True:
		legitimize_team(temp_team)
		# TODO: send "team created" email notification
		send_team_created_email(temp_team)
		return jsonify({'message':"Team " + temp_team.name + " approved. User email is confirmed, so team created."}),200
	else:
		# TODO: send "team approved, but awaiting email confirmation" confirmation email.
		send_team_email_confirmation(temp_team,second=True)
		return jsonify({'message':"Team " + temp_team.name + " approved, but awaiting email confirmation. Additional confirmation email sent."}),200

# a= jsonify({'message':"Team " + team.name + " approved."}),200

def legitimize_team(temp_team):
	permTeam=Team()
	permTeam.name = temp_team.name
	permTeam.email=temp_team.email
	permTeam.password=temp_team.password
	db.session.add(permTeam)
	db.session.commit()
	db.session.delete(temp_team)
	db.session.commit()
	carpooler=Carpooler.query.filter_by(id=temp_team.carpooler_id).first()
	if carpooler is not None:
		permTeam.members.append(carpooler)
		db.session.commit()
		return jsonify({'message':"User " + str(carpooler.name) + " added to " + str(permTeam.name) + ". This team can now be used.","team_name":permTeam.name}),200
	else:
		return jsonify({'message':"Team created, but the user who created the team could not be added to " + str(permTeam.name) + ". They can join the team like everyone else, though.","team_name":permTeam.name}),200

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




def get_trip_dists(carpooler_id,pool_id):
	print("In get_trip_dists({carpooler_id},{pool_id})".format(carpooler_id=carpooler_id,pool_id=pool_id))
	with app.app_context():
		pool = Pool.query.filter_by(id=pool_id).first()
		carpooler= Carpooler.query.filter_by(id=carpooler_id).first()
		trip = Trip.query.filter_by(carpooler_id=carpooler_id,pool_id=pool_id).first()
		if (pool is None) or (carpooler is None) or (trip is None):
			print("Carpooler, or trip, or pool not found!")
			assert(True==False) #Throw an informative exception ASAP!
			# return "Carpooler, or trip, or pool not found!"
		leaveTime=pool.eventDateTime - relativedelta(hours=1)
		new_address = trip.address
		dest = pool.eventAddress
		others =[{'id':other_trip.carpooler_id,'address':other_trip.address} for other_trip in pool.members if (other_trip.carpooler_id !=carpooler.id)]

		print("Generating Distance Objects")
		from_new_address = gen_dist_row(new_address,others,leaveTime)
		print("Got from_new_address!")
		to_new_address=gen_dist_col(new_address,others,leaveTime)
		print("Got to_new_address!")
		to_event = gen_one_distance(new_address,dest,leaveTime)


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
