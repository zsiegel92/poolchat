import flask_login
# import base64

from models import Carpooler
from database import db

login_manager = flask_login.LoginManager()

@login_manager.user_loader
def load_user(session_id):
	# carpooler= db.session.query(Carpooler).filter(Carpooler.session_id==session_id).first()
	# if carpooler is None:
	# 	print("NOT LOGGED IN!")
	# else:
	# 	print("YOU ARE LOGGED IN!")
	# return carpooler
	return db.session.query(Carpooler).filter(Carpooler.session_id==session_id).first()

login_manager.login_message = u"Please log in before proceeding."
login_manager.login_view ='login'

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
	u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

# @login_manager.request_loader
# def load_user_from_request(request):

# 	# first, try to login using the api_key url arg
# 	api_key = request.args.get('api_key')
# 	if api_key:
# 		user = Carpooler.query.filter_by(session_id=api_key).first()
# 		if user:
# 			return user

# 	# next, try to login using Basic Auth
# 	api_key = request.headers.get('Authorization')
# 	if api_key:
# 		api_key = api_key.replace('Basic ', '', 1)
# 		try:
# 			api_key = base64.b64decode(api_key)
# 		except TypeError:
# 			pass
# 		user = Carpooler.query.filter_by(session_id=api_key).first()
# 		if user:
# 			return user

# 	# finally, return None if both methods did not login the user
# 	return None
