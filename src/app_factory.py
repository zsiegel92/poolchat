from flask import Flask
from database import db
import os

def create_app(name=__name__):
	app = Flask(name)
	app.config.from_object(os.environ['APP_SETTINGS'])
	db.init_app(app)
	with app.app_context():
		db.create_all()
	return app

