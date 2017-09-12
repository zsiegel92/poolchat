import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Note: The following was removed from app.py, after app.confi.from_object(...)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	SECRET_KEY = 'masterfulCarpooling'
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	print("Setting SQLALCHEMY_DATABASE_URI TO " + str(SQLALCHEMY_DATABASE_URI))
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BCRYPT_LOG_ROUNDS = 12



class ProductionConfig(Config):
	APP_NAME="ZachAndFriends"
	DEBUG = False
	SECRET_KEY = 'masterfulCarpoolingPro'
	SQLALCHEMY_TRACK_MODIFICATIONS = False #might cause problems
	MESSENGER_PLATFORM_ACCESS_TOKEN='EAAbL0Ffr9PkBADy64t821NSnuMRQx8U1Tm0FAXgS5840g7bm2ryZAHVo4YP74O5mOuZCERJ5mXxaDi7aaFC8RjHM9B4a1YGaba3do6ZAkxX5ci9ncGIH8KuHx2UJoBzUdAuuCWamNJXSbbxGdxqJoUpPoCyGEBYjTx4RdczFwZDZD' #ZachNFriends
	GMAPS_STATIC_API_TOKEN = 'AIzaSyDpWUPSNr1RW4MsWWEcXMJiX1ZN3ZTqpU0'
	GMAPS_GEOCODE_API_TOKEN = 'AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
	#GroupThere
	DISTMAT_API_KEY='AIzaSyDn-zSmuif-Mf8z16Pm1MLYp41zYcFoaX0'
	GEOCODE_API_KEY='AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
	EMAIL = os.environ['EMAIL']
	EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
	SEND_FILE_MAX_AGE_DEFAULT = 1200#seconds
	URL_BASE='https://groupthere.herokuapp.com/'
	# URL_BASE='www.grouptherenow.com/' #NO SSL!

#NOTE: I can change this to:

#    MESSENGER_PLATFORM_ACCESS_TOKEN=os.environ.get('MESSENGER_PLATFORM_ACCESS_TOKEN')

#As long as I run in a shell:

#heroku config:set MESSENGER_PLATFORM_ACCESS_TOKEN=TOKEN_FROM_ABOVE --remote pro

class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG = False

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
	GMAPS_STATIC_API_TOKEN = 'AIzaSyDpWUPSNr1RW4MsWWEcXMJiX1ZN3ZTqpU0'
	GMAPS_GEOCODE_API_TOKEN='AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
	#GroupThere
	DISTMAT_API_KEY='AIzaSyDn-zSmuif-Mf8z16Pm1MLYp41zYcFoaX0'
	GEOCODE_API_KEY='AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
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
	GMAPS_STATIC_API_TOKEN = 'AIzaSyDpWUPSNr1RW4MsWWEcXMJiX1ZN3ZTqpU0'
	GMAPS_GEOCODE_API_TOKEN='AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
	#GroupThere
	DISTMAT_API_KEY='AIzaSyDn-zSmuif-Mf8z16Pm1MLYp41zYcFoaX0'
	GEOCODE_API_KEY='AIzaSyBZOMnco4p7dC-OLv1f1xI-txujDoSCrms'
	EMAIL = str(os.environ.get('EMAIL'))
	EMAIL_PASSWORD = str(os.environ.get('EMAIL_PASSWORD'))
	SEND_FILE_MAX_AGE_DEFAULT = 0#seconds
	URL_BASE='https://groupthere.ngrok.io/'
	print("setting URL_BASE to " + str(URL_BASE))
