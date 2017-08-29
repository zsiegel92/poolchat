from flask import url_for,request,redirect,jsonify,json,render_template,abort
import flask

from urllib.parse import urlparse, urljoin

from wtforms_ext import LoginForm, RegistrationForm,ngRegistrationForm,EmailForm

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

from models import Carpooler,Pool, Trip

from app import app
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


#TODO: register.html
#Form fields: username,email,password,confirm,accept_tos
@app.route('/register/', methods=['GET', 'POST'])
def register():
	if 'email'in request.form:
		form = RegistrationForm(request.form)
		# email=request.form.email.data
	else:
		form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		try:
			carpooler = Carpooler(name=form.username.data, email=form.email.data,password=form.password.data)
		except:
			from werkzeug.datastructures import MultiDict
			formb= RegistrationForm(formdata=MultiDict([('email',request.form['email']),('username',request.form['username']),('password',''),('confirm',''),('accept_tos',False)]))
			#non-unique violation
			return render_template('register.html',form=formb)
		db.session.add(carpooler)
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/api/register', methods=['POST'])
def api_register():
	form = ngRegistrationForm(request.form)
	if form.validate():
		if Carpooler.query.filter_by(email=form.email.data).first() is None:
			try:
				carpooler = Carpooler(firstname=form.firstName.data, lastname=form.lastName.data,name= str(form.firstName.data) + " " + str(form.lastName.data), email=form.email.data.lower(),password=form.password.data)
				db.session.add(carpooler)
				db.session.commit()
			except Exception as exc:
				return 'Database error! ' + str(exc),400
			try:
				send_register_email(carpooler.email)
				return app.config['URL_BASE'] + str(url_for('login')),200
			except Exception as exc:
				print("ERROR IN api_register WITH SENDING EMAIL!")
				print(exc)
				return 'Error sending confirmation email - user added.',400
		else:
			return 'User email already in use!',409

	return 'Form does not validate! Errors: ' + str(form.errors),422

@app.route('/api/send_register_email',methods=['POST'])
def send_register_email(email=None):
	print("in send_register_email for user with email " + str(email))
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
		link = url_base + '?#!/register'
		html_body= render_template('emails/invite.html',link=link,email=email)
		text_message=render_template('emails/invite.txt',link=link,email=email)
		html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
		emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
		return "Email not in database", 404
	else:
		print("carpooler is not None!")
		if not carpooler.is_authenticated():
			subject = "GroupThere confirmation for " + str(carpooler.name)
			link = url_base + '?#!/confirmEmail/'+str(email) +'/'+ str(carpooler.id)
			html_body= render_template('emails/confirm_email.html',carpooler=carpooler,link=link)
			text_message=render_template('emails/confirm_email.txt',carpooler=carpooler, link=link)
			html = '<html><head></head><body>{body}</body></html>'.format(body=html_body)
			emailer.send_html(email,html_message=html,subject=subject,text_message=text_message)
			return "Sent registrration email",200
		else:
			return "User already authenticated",200

@app.route('/api/confirm_email',methods=['POST'])
def confirm_email():
	email=request.values.get('email')
	id = request.values.get('id')
	print("Trying to confirm email for user with " + str(email) + " and id " + str(id))
	carpooler=Carpooler.query.filter_by(id=id).first()
	if carpooler is None:
		return "Invalid Request",400
	elif not carpooler.email.lower() == email.lower():
		return "Invalid Email", 400
	else:
		carpooler.authenticated=True
		db.session.commit()
		return "Email Confirmed! Start using GroupThere now!",200

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
		print("attempting to query for carpooler")
		carpooler = Carpooler.query.filter_by(email=email).first()
		print("Successfully queried for carpooler")
		if carpooler is not None:
			if carpooler.is_authenticated():
				if password==carpooler.password:
					print("logging in user " + str(email) + "!")
					login_user(carpooler,remember=remember_me)
					db.session.commit()
					# return jsonify({'result':app.config['URL_BASE'] + url_for('index')}),200
					return "Logged in",200 #log in
				else:
					# return jsonify({"result":"password doesn't match"}),401
					return "Passwords do not match",401
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
			if password==carpooler.password:
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
	if hasattr(current_user.is_anonymous, '__call__'):
		is_anonymous = not current_user.is_anonymous()
	else:
		is_anonymous= not current_user.is_anonymous
	return jsonify({'status':is_anonymous})
