from flask import Flask
from database import db
from login import login_manager
from encryption import bcrypt
import os
from flask import url_for
import base64
import models


# import logging



# gunicorn_error_logger = logging.getLogger('gunicorn.error')


# def create_testing_app(name=__name__):
# 	testapp=Flask(name)
# 	testapp.config.from_object("config.TestingConfig")
# 	# testdb=gen_db()
# 	testdb=db
# 	#in config.TestingConfig,
# 	# SQLALCHEMY_DATABASE_URI = "postgresql://localhost/testing"
# 	testdb.init_app(testapp)
# 	bcrypt.init_app(testapp)
# 	login_manager.init_app(testapp)
# 	with testapp.app_context():
# 		testdb.create_all()
# 	return testapp

# import logging
def create_app(name=__name__):
	app = Flask(name)
	app.config.from_object(os.environ['APP_SETTINGS'])

	app.logger.log("STARTING APP!")
	# gunicorn_logger = logging.getLogger('gunicorn.error')
	# app.logger.handlers = gunicorn_logger.handlers
	# app.logger.setLevel(gunicorn_logger.level)

	# app.logger.handlers.extend(gunicorn_error_logger.handlers)
	# app.logger.setLevel(logging.DEBUG)
	# app.logger.info('this will show in the log')
	# app.logger=logging.getLogger()

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	# with app.app_context():
	# 	db.create_all()
	return app

