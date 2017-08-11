import wtforms
def dict_to_tagstring(dic):
	return ' '.join([str(key) + '="' + str(val) + '"' for key,val in dic.items()])

class ngEmailField(wtforms.StringField):
	def __init__(self,label='Your Email Address',validators=[wtforms.validators.input_required(),wtforms.validators.Email()],render_kw={},render_kw2={'placeholder':'Enter a valid email address','type':'email'},_name='email',**kwargs):

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

		rend = f'<input {render_kw} name="{fieldname}" {extraArgs} {required}>'
		rend_help= f'<span class="help-block" ng-show="{form_name}.{fieldname}.$invalid">Valid Email Address Required</span>'

		return f'{self.label()}\n {rend}\n {rend_help}'

	def __call__(self,*args,**kwargs):
		return self.render_ng(*args,**kwargs)

class EmailForm(wtforms.Form):
	emailField=ngEmailField()
	def __init__(self,ng_click="",**kwargs):
		super().__init__()
		self.ng_click=ng_click
