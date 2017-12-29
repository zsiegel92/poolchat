import wtforms
from wtforms import Form, BooleanField, StringField, PasswordField, IntegerField, validators


def dict_to_tagstring(dic):
	return ' '.join([str(key) + '="' + str(val) + '"' for key,val in dic.items()])


# validators=[wtforms.validators.DataRequired(),wtforms.validators.Email()]
class ngEmailField(wtforms.StringField):
	def __init__(self,label='Your Email Address',validators=[wtforms.validators.DataRequired(),wtforms.validators.Email()],render_kw={},render_kw2={'placeholder':'Valid email','type':'email'},_name='email',**kwargs):

		render_kw2.update(render_kw) #render_kw keys take precedence
		render_kw.update(render_kw2)
		if 'ng-model' not in render_kw:
			if 'ng_model' in kwargs:
				render_kw['ng-model']=kwargs.pop('ng_model')
			elif 'ng-model' in kwargs:
				render_kw['ng-model']=kwargs.pop('ng-model')
			else:
				render_kw['ng-model']= _name
		super().__init__(label=label,validators=validators,render_kw=render_kw,_name=_name,**kwargs)

	def render_ng(self,form_name='',**kwargs):
		fieldname= self.type
		# ng_model= f'{self.render_kw.pop("ng-model")}'
		required = "required" if vars(self.flags).get("required",False) else ""
		extraArgs= dict_to_tagstring(kwargs)
		render_kw=dict_to_tagstring(self.render_kw)

		rend = '<input {render_kw} name="{fieldname}" {extraArgs} {required}>'.format(render_kw=render_kw,fieldname=fieldname,extraArgs=extraArgs,required=required)
		rend_help= '<span class="help-block" ng-show="{form_name}.{fieldname}.$invalid">Valid Email Address Required</span>'.format(form_name=form_name,fieldname=fieldname)
		return '{self.label()}\n {rend}\n {rend_help}'.format(rend=rend,rend_help=rend_help)

	def __call__(self,*args,**kwargs):
		return self.render_ng(*args,**kwargs)

class EmailForm(wtforms.Form):
	emailField=ngEmailField()
	def __init__(self,*args,ng_click="",**kwargs):
		super().__init__(*args,**kwargs)
		self.ng_click=ng_click


class LoginForm(wtforms.Form):
	email= StringField("Email",  [validators.DataRequired("Please enter your email address."), validators.Email("Please enter a valid email address.")])
	password = PasswordField('Password', [validators.Length(min=4, max=25),
		validators.DataRequired()
	])
	remember_me=BooleanField(
		label='Remember Me',
		validators=[],
		default=False,
		description="Would you like to be remembered?"
	)

class RegistrationForm(wtforms.Form):
	username = StringField('Name', [validators.Length(min=2, max=25)])
	email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('New Password', [validators.Length(min=4, max=25),
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class ngRegistrationForm(wtforms.Form):
	firstName = StringField('First Name', [validators.Length(min=1, max=25)])
	lastName = StringField('Last Name', [validators.Length(min=1, max=25)])
	email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('New Password', [validators.Length(min=4, max=25),
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


# emtoken?/:teamusertoken?/:eventid?/:name?
class oneClickRegistrationForm(ngRegistrationForm):
	emtoken = StringField("Email Token",[validators.Length(min=1)])


class oneClickRegistrationFormPlusTeam(oneClickRegistrationForm):
	teamusertoken = StringField("Team User Token",[validators.Length(min=1)])

class oneClickRegistrationFormPlusTeamAndEvent(oneClickRegistrationFormPlusTeam):
	eventid = StringField("Event ID",[validators.Length(min=1)])

class ngPasswordChangeRequestForm(wtforms.Form):
	email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])

class ngForgotPasswordChangeForm(wtforms.Form):
	password = PasswordField('New Password', [validators.Length(min=4, max=25),
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')

class ngPasswordChangeForm(wtforms.Form):
	current_password = PasswordField('New Password', [validators.Length(min=4, max=25),
		validators.DataRequired()
	])
	password = PasswordField('New Password', [validators.Length(min=4, max=25),
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')


def test_EmailForm():
	from werkzeug.datastructures import MultiDict
	a= EmailForm(formdata=MultiDict([('emailField','zsiegel@gmail.com')]),ng_click="makeResponse()")
	print(a.data)
	print(a.validate())
	print(a.errors)

# Documentation at:
# (form): https://github.com/wtforms/wtforms/blob/60abf4fbb9fc5231f6525a2062e40fd88be240dc/wtforms/form.py
# (field): https://github.com/wtforms/wtforms/blob/086d0bf7d6d73ab9a05e30b861adee627916a71c/wtforms/fields/core.py
class nonpopulating_IntegerField(IntegerField):
	def populate_obj(self,obj,name):
		pass
class castAsInteger_BooleanField(BooleanField):
	def populate_obj(self,obj,name):
		setattr(obj,name,int(self.data))

class tripForm(wtforms.Form):
	address= StringField('Address',[validators.InputRequired("Please enter address")])
	num_seats = IntegerField('Number of Seats', validators=[validators.InputRequired("Please select how many seats you have (0 if no car)"), validators.number_range(min=0,max=5, message='Must input between 0 and 5 seats.')])
	preWindow = IntegerField('Number of minutes before the event that you are available', validators=[validators.InputRequired(), wtforms.validators.number_range(min=0, message='Must be positive.')])
	on_time = castAsInteger_BooleanField('Do you have to arrive on time?', [validators.InputRequired()])
	must_drive = castAsInteger_BooleanField("Do you have to drive (is it not possible to catch a ride)?",[validators.InputRequired()])
	pool_id = nonpopulating_IntegerField('Pool ID',validators=[validators.InputRequired()])
	resubmit = BooleanField('Resubmission',validators=[validators.InputRequired("Please specify whether or not this is a resubmission")])











