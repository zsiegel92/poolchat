from flask import Flask
from database import db
from login import login_manager
from encryption import bcrypt
import os
from flask import url_for
import base64
import models

def create_app(name=__name__):
	app = Flask(name)
	app.config.from_object(os.environ['APP_SETTINGS'])
	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	# with app.app_context():
	# 	db.create_all()
	return app

