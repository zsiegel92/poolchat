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
	with test_env():
		app.config.from_object(os.environ['APP_SETTINGS'])
		db.init_app(app)
		db.app=app
		bcrypt.init_app(app)
		login_manager.init_app(app)
	manager.app=app
	@wraps(func)
	def wrap(*args, **kwargs):
		with test_env():
			return func(*args, **kwargs)
	return wrap
def use_keeptest_config(func):
	with keep_env():
		app.config.from_object(os.environ['APP_SETTINGS'])
		db.init_app(app)
		db.app=app
		bcrypt.init_app(app)
		login_manager.init_app(app)
	manager.app=app
	@wraps(func)
	def wrap(*args, **kwargs):
		with keep_env():
			return func(*args, **kwargs)
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

import E2E

manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command('db', MigrateCommand)





# source: https://github.com/smurfix/flask-script/blob/master/flask_script/commands.py
@manager.command
@use_test_config
def testserver():
	# with test_keep_env():
	run_a_server(app,port=5001)

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
	import atexit
	atexit.register(testrecreate)
	E2E.run_all_tests()
	# db.session.commit()
	# manager.run()
	# use_reloader=False
	print("RUNING A SERVER")
	run_a_server(app,port=5001,use_reloader=False)
	# testshell()
	# testserver()

@manager.command
@use_keeptest_config
def testkeepshell():
	import atexit
	atexit.register(testrecreate)
	E2E.run_all_tests()
	testshell()


def run_a_server(some_app,port=5000,use_reloader=None,use_debugger=False):
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


if __name__ == '__main__':
	manager.run()
