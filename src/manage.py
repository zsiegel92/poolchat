import os
import sys
from flask_script import Manager,Shell,Server,prompt_bool
from flask_migrate import Migrate, MigrateCommand
from functools import wraps

from utils import modified_environ

from database import db
from login import login_manager
from encryption import bcrypt

import models
from models import Carpooler, Pool, Trip, Team,team_membership,team_affiliation

testing_env_dict={"APP_SETTINGS":"config.TestingConfig","EMAIL":''}#{"APP_SETTINGS":"config.TestingConfig","EMAIL":''}
testing_runserver_env_dict ={"APP_SETTINGS":"config.TestingConfig","EMAIL":'','FLASKDEBUG':'False'}

def test_env():
	return modified_environ(**testing_env_dict)
def keep_env():
	return modified_environ(**testing_runserver_env_dict)

def use_test_config(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		with test_env():
			app.config.from_object(os.environ['APP_SETTINGS'])
			# db.init_app(app)
			# db.app=app
			# bcrypt.init_app(app)
			# login_manager.init_app(app)
			# manager.app=app
			return func(*args, **kwargs)
	with test_env():
		return wrap
def use_keeptest_config(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		with keep_env():
			app.config.from_object(os.environ['APP_SETTINGS'])
			db.init_app(app)
			db.app=app
			bcrypt.init_app(app)
			login_manager.init_app(app)
			manager.app=app
			return func(*args, **kwargs)
	with keep_env():
		return wrap

testing=False
for arg in sys.argv:
	if 'test' in arg:
		testing = True


if testing:
	print("Flask Manager in Testing Mode")
	with test_env():
		from app import app, ts
else:
	print("Flask Manager in Regular Mode")
	from app import app,ts




manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command('db', MigrateCommand)




# source: https://github.com/smurfix/flask-script/blob/master/flask_script/commands.py
@manager.command
@use_test_config
def testserver():
	# with test_keep_env():
	run_a_server(app)

@manager.command
@use_test_config
def test():
	import E2E
	E2E.run_all_tests()
	db.session.commit()
	testrecreate() #added this when added testkeep, so that teardown can be pass
	db.session.commit()




@manager.command
@use_keeptest_config
def testkeepserver():
	import E2E
	# import atexit
	# atexit.register(testrecreate)
	E2E.run_all_tests()
	print("RUNNING A SERVER")
	with keep_env():
		run_a_server(app,use_reloader=False)


@manager.command
@use_keeptest_config
def testkeepshell():
	import E2E
	# import atexit
	# atexit.register(testrecreate)
	E2E.run_all_tests()
	testshell()


def run_a_server(some_app,port=None,use_reloader=None,use_debugger=None):
	if port is None:
		port = app.config.get('SERVERPORT',5000)
	server=  Server(port=port,host='127.0.0.1',use_reloader=use_reloader,use_debugger=use_debugger)
	server(app=some_app,host=server.host,port=server.port,use_debugger=server.use_debugger,use_reloader=server.use_reloader,threaded=server.threaded,processes=server.processes,passthrough_errors=server.passthrough_errors)



@manager.command
@use_test_config
def testdrop(internal=False):
	if (internal is True) or prompt_bool("Are you sure you want to lose all your data"):
		with app.app_context():
			db.session.commit()
			db.drop_all()


@manager.command
@use_test_config
def testcreate(default_data=True, sample_data=False):
	with app.app_context():
		db.create_all()


@manager.command
@use_test_config
def testrecreate(internal=True):
	with app.app_context():
		testdrop(internal)
		testcreate()
		print("Dropped and recreated all tables.")



# manager.add_command("runserver", Server(port=8383, host='127.0.0.1'))#not default
# manager.add_command("runserver", Server(port=5000, host='127.0.0.1'))#Default
#manager.add_command('debug', Server(use_debugger=True, use_reloader=True, port=8383, host='127.0.0.1'))
@manager.shell
def make_shell_context():
	return dict(app=app, db=db, models=models,Carpooler=Carpooler,Pool=Pool,Trip=Trip,Team=Team)


@manager.command
@use_test_config
def testshell():
	shell = Shell(make_context=make_shell_context)
	shell.run(False,False)


# :email?/:emtoken?/:teamusertoken?/:eventid?/:firstname?/:lastname?'
# take team_name or team_id
@manager.command
def generate_oneclick(email,team_name=None,team_id=None,event_id = None,first_name=None,last_name=None):
	with app.app_context():

		REGISTRATION_TOKEN_KEY = app.config['REGISTRATION_TOKEN_KEY']
		URL_BASE = app.config['URL_BASE']

		emtoken=ts.dumps(email,salt=REGISTRATION_TOKEN_KEY+"emailtoken")

		link = '{}?#!/register/{}/{}/'.format(URL_BASE, email,emtoken)

		if team_name is not None:
			team = Team.query.filter_by(name=team_name).first()
		if team_id is not None:
			team = Team.query.filter_by(id=team_id).first()
		if team is not None:
			teamUserToken=ts.dumps("++++".join([email, team.id, team.password]),salt=REGISTRATION_TOKEN_KEY+"teamUserToken")
		else:
			teamUserToken = None
		link += teamUserToken + '/'
		if event_id is not None and teamUserToken is not None:
			link += event_id + '/'

		if (first_name is not None) and (teamUserToken is not None) and (event_id is not None):
			link += first_name + '/'
		if (last_name is not None) and (first_name is not None) and (teamUserToken is not None) and (event_id is not None):
			link += last_name + '/'

		print(link)
		return link
if __name__ == '__main__':
	manager.run()
