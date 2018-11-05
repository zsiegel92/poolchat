import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Note: The following was removed from app.py, after app.confi.from_object(...)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	SECRET_KEY = os.environ['CONFIG_SECRET_KEY']
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	print("Setting SQLALCHEMY_DATABASE_URI TO " + str(SQLALCHEMY_DATABASE_URI))
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BCRYPT_LOG_ROUNDS = 12
	REGISTRATION_TOKEN_KEY = os.environ['REGISTRATION_TOKEN_KEY']



class ProductionConfig(Config):
	APP_NAME="ZachAndFriends"
	DEBUG = False
	SECRET_KEY = os.environ['PROD_SECRET_KEY']
	SQLALCHEMY_TRACK_MODIFICATIONS = False #might cause problems
	MESSENGER_PLATFORM_ACCESS_TOKEN= os.environ['PROD_MESSENGER_PLATFORM_ACCESS_TOKEN']#ZachNFriends
	GMAPS_STATIC_API_TOKEN = os.environ['PROD_GEOCODE_API_KEY']#os.environ['PROD_GMAPS_STATIC_API_TOKEN']
	GMAPS_GEOCODE_API_TOKEN = os.environ['PROD_GEOCODE_API_KEY']#os.environ['PROD_GMAPS_GEOCODE_API_TOKEN']
	#GroupThere
	DISTMAT_API_KEY=os.environ['PROD_GEOCODE_API_KEY']#os.environ['PROD_DISTMAT_API_KEY']
	GEOCODE_API_KEY=os.environ['PROD_GEOCODE_API_KEY']
	EMAIL = os.environ['EMAIL']
	EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
	SEND_FILE_MAX_AGE_DEFAULT = 1200#seconds
	URL_BASE='https://groupthere.herokuapp.com/'
	# URL_BASE='www.grouptherenow.com/' #NO SSL!

##NOTE: I can change this to:

#    MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN')

#As long as I run in a shell:

#heroku config:set MESSENGER_PLATFORM_ACCESS_TOKEN=TOKEN_FROM_ABOVE --remote pro

class StagingConfig(ProductionConfig):
	DEVELOPMENT = True
	DEBUG = False
	URL_BASE='https://groupthere-stage.herokuapp.com/'

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = "postgresql://localhost/testing"
	print("Setting SQLALCHEMY_DATABASE_URI TO " + str(SQLALCHEMY_DATABASE_URI))
	APP_NAME = "GroupThere"
	DEVELOPMENT = True
	debugging = os.environ.get('FLASKDEBUG')
	if debugging=='True':
		DEBUG = True
	else:
		DEBUG= False
	SERVERPORT=5001
	SECRET_KEY = 'masterfulCarpoolingDev'
	MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN') #Zach and Friends
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	GMAPS_STATIC_API_TOKEN = os.environ['PROD_GMAPS_STATIC_API_TOKEN']
	GMAPS_GEOCODE_API_TOKEN=os.environ['PROD_GMAPS_GEOCODE_API_TOKEN']
	#GroupThere
	DISTMAT_API_KEY=os.environ['PROD_DISTMAT_API_KEY']
	GEOCODE_API_KEY=os.environ['PROD_GEOCODE_API_KEY']
	EMAIL = str(os.environ.get('EMAIL'))
	EMAIL_PASSWORD = str(os.environ.get('EMAIL_PASSWORD'))
	SEND_FILE_MAX_AGE_DEFAULT = 0#seconds
	# URL_BASE='https://poolchat.ngrok.io/'
	URL_BASE='http://localhost:' + str(SERVERPORT) + '/'
	print("setting URL_BASE to " + str(URL_BASE))

class DevelopmentConfig(Config):
	APP_NAME = "GroupThere"
	SERVERPORT=5000
	DEVELOPMENT = True
	DEBUG = True
	SECRET_KEY = 'masterfulCarpoolingDev'
	MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN') #Zach and Friends
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	GMAPS_STATIC_API_TOKEN = os.environ['PROD_GMAPS_STATIC_API_TOKEN']
	GMAPS_GEOCODE_API_TOKEN=os.environ['PROD_GMAPS_GEOCODE_API_TOKEN']
	#GroupThere
	DISTMAT_API_KEY=os.environ['PROD_GEOCODE_API_KEY']#os.environ['PROD_DISTMAT_API_KEY']
	GEOCODE_API_KEY=os.environ['PROD_GEOCODE_API_KEY']#os.environ['PROD_GEOCODE_API_KEY']
	EMAIL = str(os.environ.get('EMAIL'))
	EMAIL_PASSWORD = str(os.environ.get('EMAIL_PASSWORD'))
	SEND_FILE_MAX_AGE_DEFAULT = 0#seconds
	URL_BASE='https://groupthere.ngrok.io/'
	print("setting URL_BASE to " + str(URL_BASE))
