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
	print(form.data)
	if form.validate():
		if Carpooler.query.filter_by(email=form.email.data).first() is None:
			try:
				carpooler = Carpooler(firstname=form.firstName.data, lastname=form.lastName.data,name= str(form.firstName.data) + " " + str(form.lastName.data), email=form.email.data,password=form.password.data)
				db.session.add(carpooler)
				db.session.commit()
				return jsonify({'result':app.config['URL_BASE'] + str(url_for('login'))}),200
			except Exception as exc:
				return jsonify({'result':'Database error! ' + str(exc)}),400
		else:
			return jsonify({'result':'User email already in use!'}),409

	return jsonify({'result':'Form does not validate! Errors: ' + str(form.errors)}),422



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
		carpooler = Carpooler.query.filter_by(email=email).first()
		if carpooler is not None:
			if password==carpooler.password:
				print("logging in user " + str(email) + "!")
				login_user(carpooler,remember=remember_me)
				db.session.commit()
				# return jsonify({'result':app.config['URL_BASE'] + url_for('index')}),200
				return jsonify({'result':True}) #log in
			else:
				# return jsonify({"result":"password doesn't match"}),401
				return jsonify({'result':False})
		else:
			# message = "User not found"
			# return jsonify({"result":"User not found."}),404
			return jsonify({'result':False})
	else:
		# message = "Form doesn't validate. Errors: "  + str(form.errors) +", full data: " + str(form.data)
		return jsonify({'result': False}) #form doesn't validate

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
