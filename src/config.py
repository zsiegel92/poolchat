import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Note: The following was removed from app.py, after app.confi.from_object(...)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	SECRET_KEY = 'this-really-needs-to-be-changed'
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
	APP_NAME="ZachAndFriends"
	DEBUG = False
	MESSENGER_PLATFORM_ACCESS_TOKEN='EAAbL0Ffr9PkBADy64t821NSnuMRQx8U1Tm0FAXgS5840g7bm2ryZAHVo4YP74O5mOuZCERJ5mXxaDi7aaFC8RjHM9B4a1YGaba3do6ZAkxX5ci9ncGIH8KuHx2UJoBzUdAuuCWamNJXSbbxGdxqJoUpPoCyGEBYjTx4RdczFwZDZD' #ZachNFriends

#NOTE: I can change this to:

#    MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN')

#As long as I run in a shell:

#heroku config:set MESSENGER_PLATFORM_ACCESS_TOKEN=TOKEN_FROM_ABOVE --remote pro

#The question is: would I rather edit these tokens in .env (for local) and on heroku (for remote), or in my  .env (for local) and in this file config.py (for remote).

class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class DevelopmentConfig(Config):
	APP_NAME = "GroupThere"
	DEVELOPMENT = True
	DEBUG = True
	MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN') #Zach and Friends
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
	TESTING = True
