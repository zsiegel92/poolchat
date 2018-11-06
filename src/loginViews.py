from flask import url_for,request,redirect,jsonify,json,render_template,abort
import flask

from urllib.parse import urlparse, urljoin

from wtforms_ext import LoginForm, RegistrationForm,ngRegistrationForm,EmailForm,ngPasswordChangeRequestForm, ngForgotPasswordChangeForm, ngPasswordChangeForm, oneClickRegistrationForm,oneClickRegistrationFormPlusTeam,oneClickRegistrationFormPlusTeamAndEvent

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

from models import Carpooler,Pool, Trip,Team,team_affiliation

from app import app, ts
from database import db
from login import login_manager
from flask_login import current_user, login_user, logout_user,login_required
from emailer import Emailer
emailer=Emailer(q)

def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
			ref_url.netloc == test_url.netloc

def get_redirect_target():
	for target in request.values.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return target

def redirect_back(endpoint, **values):
	target = request.form['next']
	if not target or not is_safe_url(target):
		target = url_for(endpoint, **values)
	return redirect(target)


# return 200 for standard registration
# return 201 for one-click validation
# return 202 for one-click validation plus event-join
# request.form can have any keys in ['emtoken','teamusertoken','eventid'], in that precedence
# wtforms_ext has oneClickRegistrationForm, oneClickRegistrationFormPlusTeam, and oneClickRegistrationFormPlusTeamAndEvent
@app.route('/api/register', methods=['POST'])
def api_register():
	print("In /api/register")
	validationLevel=-1
	for formtype in [ngRegistrationForm,oneClickRegistrationForm,oneClickRegistrationFormPlusTeam,oneClickRegistrationFormPlusTeamAndEvent]:
		if formtype(request.form).validate():
			form = formtype(request.form)
			validationLevel += 1

	validationMeanings={-1:"invalid form",0:"valid form",1:"valid form and oneclick auth",2:"valid form, oneclick auth, and team token",3:"valid form, oneclick auth, team token, and event"}
	print("validationLevel is: {}, which means: {}".format(validationLevel,validationMeanings.get(validationLevel,"")))

	if validationLevel >=0:
		email=form.email.data.lower()
		if Carpooler.query.filter_by(email=email).first() is None:
			print("CARPOOLER IS NOT NONE!")
			try:
				carpooler = Carpooler(firstname=str(form.firstName.data), lastname=str(form.lastName.data),name= "{} {}".format(form.firstName.data,form.lastName.data), email=str(email),password=str(form.password.data))
				db.session.add(carpooler)
				db.session.commit()
				print("successfully added new carpooler.")
			except Exception as exc:
				print("database error: '{}'".format(exc))
				return 'Database error! ' + str(exc),400

			#see register.js for status explanation
			if (validationLevel > 0):
				returndict = try_oneclick(carpooler,form,validationLevel)
				oneclickLevel = returndict['oneclickLevel']
				del returndict['oneclickLevel']
				if oneclickLevel >= 1:
					#email token valid, email accepted
					carpooler.authenticated=True
					login_user(carpooler,remember=True)
					db.session.commit()
					status=201
				if oneclickLevel >= 2:
					team = Team.query.filter_by(name=returndict['teamname']).first()
					team.members.append(carpooler)
					db.session.commit()
					#team token valid, team joined
					# returndict['teamname'] defined
					status=202
				if oneclickLevel ==3:
					#event id exists, affiliated with joined team, event navigated
					# returndict['eventname'], returndict['go_to_pool_id'] defined
					status=203
				print("response of /api/register is: \n\n{}\n\n".format(returndict))
				returndict['status']=status
				return jsonify(returndict), 200
			try:
				send_register_email(email)
				print("response of /api/register is: \n\n{}\n\n".format(app.config['URL_BASE'][:-1] + str(url_for('login'))))
				return app.config['URL_BASE'][:-1] + str(url_for('login')),200
			except Exception as exc:
				print("ERROR IN api_register WITH SENDING EMAIL!")
				print(exc)
				return 'Error sending confirmation email - user added.',400

		elif (hasattr(current_user.is_anonymous,'__call__') and (current_user.is_anonymous() is False)) and (email == current_user.email):
			print("current user is anonymous!")
			returndict = try_oneclick(current_user,form,validationLevel)
			oneclickLevel = returndict['oneclickLevel']
			del returndict['oneclickLevel']
			if oneclickLevel >= 2:
				team = Team.query.filter_by(name=returndict['teamname']).first()
				if current_user not in team.members:
					team.members.append(carpooler)
					db.session.commit()
				status=204
			if oneclickLevel ==3:
				status=205
			print("response of /api/register is: \n\n{}\n\n".format(returndict))
			print("RETURNING FROM HERE")
			returndict['status']=status
			return jsonify(returndict), 200
		else:
			print("email already in use!")
			return 'User email already in use!',409

	return 'Form does not validate! Errors: ' + str(form.errors),422


# in: form.email.data, form.emtoken.data, form.team.data, form.teamusertoken.data, form.eventid.data
# validationLevel = 1 if only emtoken
# validationLevel = 2 if team
# validationLevel = 3 if team and event
# returns 0 if no oneclick succeeds
# returns 1 if oneclick email succeeds
# returns 2 if oneclick email and team succeed
# returns 3 if oneclick email, team, and event succeed
# emtoken=ts.dumps(email,salt=app.config['REGISTRATION_TOKEN_KEY']+"emailtoken")
# teamUserToken=ts.dumps("++++".join([email, team.id, team.password]),salt=app.config['REGISTRATION_TOKEN_KEY']+"teamUserToken")
def try_oneclick(carpooler, form, validationLevel):
	d={}
	d['oneclickLevel']=0
	try:
		email_encrypted = ts.loads(form.emtoken.data, salt=app.config['REGISTRATION_TOKEN_KEY']+"emailtoken", max_age=190000)
		if email_encrypted.lower() == form.email.data.lower():
			d['oneclickLevel']=1
		else:
			return d
	except:
		return d

	if (validationLevel >= 2):
		try:
			teamUserToken = ts.loads(form.teamusertoken.data, salt=app.config['REGISTRATION_TOKEN_KEY']+"teamUserToken", max_age=190000)
			teamUserArgs = teamUserToken.split('++++') #[email,team.id,team.password]
			team = Team.query.filter_by(id=teamUserArgs[1]).first()
			if (teamUserArgs[0]==carpooler.email) and (team is not None) and (team.password==teamUserArgs[2]):
				d['oneclickLevel']=2
				d['teamname']=team.name
			else:
				return d
		except:
			return d

	if (validationLevel >=3):
		try:
			event = Pool.query.filter_by(id=form.eventid.data).first()
			if (event is not None) and (event in team.pools):
				d['oneclickLevel'] = 3
				d['eventname']=event.poolName
				d['go_to_pool_id']=event.id
			else:
				return d
		except:
			return d
	return d

@app.route('/api/send_register_email',methods=['POST'])
def send_register_email(email=None):
	print("in send_register_email for user with email " + str(email))
	email=email.lower()
	if email is None:
		if request:
			if request.values:
				email=request.values.get('email')
		else:
			return "incorrectly calling function send_register_email"
	if email is None:
		return "No data arriving at server!",400
	url_base = app.config['URL_BASE']#ends in /
	carpooler=Carpooler.query.filter_by(email=email).first()
	if carpooler is None:
		#send a link to ?#!/register to whatever the email is
		subject = "Register for GroupThere"
		link = url_base + '?#!/register/' +str(email)
		html_body= render_template('emails/invite.html',link=link,email=email)
		text_message=render_template('emails/invite.txt',link=link,email=email)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "Email not in database, invitation sent!", 404
	else:
		print("carpooler is not None!")
		if not carpooler.is_authenticated():
			print("carpooler not authenticated")
			subject = "GroupThere confirmation for " + str(carpooler.name)

			token=ts.dumps(email,salt='email-confirm-key')
			# link = url_base + '?#!/confirmEmail/'+str(email) +'/'+ str(carpooler.id)
			link = url_base + '?#!/confirmEmail/'+str(email) +'/'+ str(token)
			html_body= render_template('emails/confirm_email.html',carpooler=carpooler,link=link)
			text_message=render_template('emails/confirm_email.txt',carpooler=carpooler, link=link)
			html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
			emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
			return "Sent registration email",200
		else:
			print("carpooler already authenticated")
			return "User already authenticated",200

#post with form {email:}
@app.route('/api/forgot_password',methods=['POST'])
def forgot_password():
	form = ngPasswordChangeRequestForm(request.form)
	if form.validate():
		email=form.email.data.lower()
		carpooler=Carpooler.query.filter_by(email=email).first()
		if carpooler is None:
			return "No such user in database",404
		url_base = app.config['URL_BASE']
		token = ts.dumps(email,salt='recover-key')
		link = url_base+ '?#!/forgotPasswordChange/'+ str(email.lower()) + "/" + str(token)

		subject = "Change your GroupThere password"

		html_body= render_template('emails/recovery_email.html',carpooler=carpooler,link=link)
		text_message=render_template('emails/recovery_email.txt',carpooler=carpooler, link=link)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)

		print("SENDING EMAIL TO " + email.lower())
		return "Sent registrration email",200
	else:
		return "Invalid entry",400

#post with form {password:,confirm:}
@app.route('/api/reset_password/<token>', methods=["POST"])
def reset_with_token(token):
	try:
		email = ts.loads(token, salt="recover-key", max_age=86400)
	except:
		return "Please re-request password change email",400

	form = ngForgotPasswordChangeForm(request.form)

	if form.validate():
		carpooler = Carpooler.query.filter_by(email=email).first()
		if carpooler is None:
			return "Invalid token",404
		carpooler.password = form.password.data
		carpooler.authenticated=True #changing password => email valid!
		db.session.add(carpooler)
		db.session.commit()
		return "Password Changed",200
	else:
		return "Please try again! Password invalid.",400





@app.route('/api/confirm_email',methods=['POST'])
def confirm_email():
	email=request.values.get('email')
	token = request.values.get('token')
	try:
		email2 = ts.loads(token, salt="email-confirm-key", max_age=86400)
	except:
		return "Invalid request!",400
	if email2.lower() != email.lower():
		return "Invalid request!",400

	print("Trying to confirm email for user with " + str(email))
	carpooler=Carpooler.query.filter_by(email=email.lower()).first()
	if carpooler is None:
		return "Invalid Request",400
	else:
		if carpooler.authenticated==False:
			carpooler.authenticated=True
			login_user(carpooler,remember=True)
			db.session.commit()
			return "Email Confirmed! Start using GroupThere now!",200
		else:
			logout_user()
			return "Email already confirmed. Logged into GroupThere.",201

##TODO: login.html should have a form that displays all errors. No angular.
#Form fields: email,password,remember_me
@app.route('/api/login', methods=['POST'])
def api_login():
	form=LoginForm(request.form)
	password=form.password.data

	form.password.data='xxxx'
	form.password.raw_data=None
	remember_me=form.remember_me.data

	if 'remember_me' in request.form:
		remember_me = True
	if form.validate():
		email=form.email.data
		email=email.lower()
		carpooler = Carpooler.query.filter_by(email=email).first()
		if carpooler is not None:
			if carpooler.is_authenticated():
				if carpooler.is_correct_password(password):
					print("logging in user " + str(email) + "!")
					login_user(carpooler,remember=remember_me)
					db.session.commit()
					# return jsonify({'result':app.config['URL_BASE'] + url_for('index')}),200
					return "Logged in",200 #log in
				else:
					# return jsonify({"result":"password doesn't match"}),401
					return "Username or Password Incorrect",401
			else:
				# not authenticated
				#re-sending email
				print("sending registration email")
				try:
					db.session.close()
					send_register_email(carpooler.email)
				except Exception as exc:
					print("Exception sending email (in loginViews.login")
					print(exc)
					return "User not authenticated. Just attempted to send authentication email to {}, but email failed. Please stand by.".format(carpooler.email),401
				else:
					print("sent registration email (in api_login)")
					return "User not authenticated. Just sent authentication email to {}.".format(carpooler.email),401
		else:
			return "User not found", 404
	else:
		# message = "Form doesn't validate. Errors: "  + str(form.errors) +", full data: " + str(form.data)
		return "Please enter a valid email and password",400 #form doesn't validate

##TODO: login.html should have a form that displays all errors. No angular.
#Form fields: email,password,remember_me
@app.route('/login/', methods=['GET','POST'])
def login():
	# Here we use a class of some kind to represent and validate our
	# client-side form data. For example, WTForms is a library that will
	# handle this for us, and we use a custom LoginForm to validate.
	data= request.form
	form=LoginForm(data)
	password=form.password.data
	form.password.data='xxxx'
	form.password.raw_data=None
	remember_me=form.remember_me.data

	if 'remember_me' in request.form:
		remember_me = True
	if form.validate():
		email=form.email.data
		carpooler = Carpooler.query.filter_by(email=email).first()
		if carpooler is not None:
			if carpooler.is_correct_password(password):
				login_user(carpooler,remember=remember_me)
				db.session.commit()
				flask.flash('Logged in successfully.')
				next=request.args.get('next')
				if not is_safe_url(next):
					return abort(400)
				else:
					return redirect(next or url_for('index'))#'next' is unsafe
			else:
				message = "password doesn't match"
				return render_template('login.html',form=form,message=message)#wrong password
		else:
			message = "User not found"
			return render_template('login.html',form=form,message=message)#wrong password
			# return redirect(url_for('register')) #carpooler is None
	else:
		message = "Form doesn't validate. Errors: "  + str(form.errors) +", full data: " + str(form.data)
		return render_template('login.html',form=form,message=message) #form doesn't validate


@app.route('/api/logout/',methods=['POST','GET'])
@login_required
def api_logout():
	logout_user()
	return jsonify({'result': 'success'})

@app.route('/logout/',methods=['POST','GET'])
@login_required
def logout():
	logout_user()
	flask.flash('You have been logged out.')
	return redirect(url_for('login'))

@app.route('/api/status',methods=['POST','GET'])
def api_status():
	print("api/status called!")
	if hasattr(current_user.is_anonymous, '__call__'):
		is_anonymous = not current_user.is_anonymous()
	else:
		is_anonymous= not current_user.is_anonymous
	return jsonify({'status':is_anonymous})







