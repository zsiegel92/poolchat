from interactions import quick_rules,text_rules,process_referral#Note: have to import webhookviews at bottom of app

#IMPORTS FOR TESTING:
from interactions import getStarted#NOTE These are NOT needed for app - only for drop_populate and testing!

from app import app,db,request,abort


@app.route("/", methods=["GET"])
def root():
#    assert app.debug == False
	try:
#        messenger.say('1512768535401609','booting now')
		return 'WUTWUTWUT10', 200
	except Exception as exc:
		return str(exc)

#TODO: Flip through users in db, message them their table has been dropped :)
@app.route('/dropTabs', methods=["GET"])
def drop_table():
	try:
		db.drop_all()
		db.create_all()
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc)
	else:
		return "Dropped and re-created all tables!", 200


@app.route('/drop_ping', methods=["GET"])
def drop_and_ping():
	try:
		db.drop_all()
		db.create_all()
		fbId = '1512768535401609'
		getStarted(fbId)
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc)
	else:
		return "Dropped and re-created all tables!", 200

@app.route('/testing', methods=["GET"])
def testing():
	try:
		db.drop_all()
		db.create_all()
		fbId = '1512768535401609'
		getStarted(fbId)
		text_rules(fbId,'zsiegel92@gm')#email
		quick_rules(fbId,'mode') #CHANGE TO MODE FOR POOL
		quick_rules(fbId,'CREATE_NEW_POOL')# calls NEW POOL (triggers postback response)
		text_rules(fbId,"IfNotNow HM at David's")#email
		text_rules(fbId,'153 N New Hampshire Ave, LA, CA')#email
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc)
	else:
		return "Dropped and re-created all tables!", 200



@app.route('/ping_getStarted', methods=["GET"])
def ping_getStarted():
	try:
		fbId = '1512768535401609'
		getStarted(fbId)
	except Exception as exc:
		return "Exception on ping_getStarted:\n" + str(exc)
	else:
		return "Got started!", 200

@app.route('/ping_text', methods=["GET"])
def ping_text():
	try:
		fbId = '1512768535401609'
		text_rules(fbId,'Hey')#email
	except Exception as exc:
		return "Exception on ping_text:\n" + str(exc)
	else:
		return "ping_text successful!", 200

@app.route('/drop_ping_text', methods=["GET"])
def drop_ping_text():
	drop_table()
	ping_text()

@app.route('/drop_populate', methods=["GET"])
def drop_populate():
	try:
		db.drop_all()
		db.create_all()
		fbId = '1512768535401609'
		getStarted(fbId)
		text_rules(fbId,'zsiegel92@gm')#email
		quick_rules(fbId,'RESPONSE/Carpooler/mode') #CHANGE TO MODE FOR POOL
		quick_rules(fbId,'CREATE_NEW_POOL')# calls NEW POOL (triggers postback response)
		text_rules(fbId,'DTLA 6TH ST')#go to address
		text_rules(fbId,'7:30pm')#Time
		quick_rules(fbId,'RESPONSE/Pool/mode')#GO TO MODE FOR TRIP
		quick_rules(fbId,'RESPONSE/Pool/tripfields')#CHANGE TO TRIP
		text_rules(fbId,'153 NORTH NEW HAMPSHIRE')#COMING FROM ADDRESS
		quick_rules(fbId,'RESPONSE/Trip/4')#SEATS AVAILABLE
		quick_rules(fbId,'RESPONSE/Trip/25')#MINUTES AVAILABLE FOR TRANSIT
		quick_rules(fbId,'RESPONSE/Trip/1') #Arrive on time
		quick_rules(fbId,'RESPONSE/Trip/1') #Drive own car
		quick_rules(fbId,'RESPONSE/Trip/mode') #All good!

		quick_rules(fbId,'CREATE_NEW_POOL')# calls NEW POOL (triggers postback response)
		text_rules(fbId,"David's House")#GOING TO ADDRESS
		text_rules(fbId,"7:30")#Time
		quick_rules(fbId,'RESPONSE/Pool/mode')#GO TO MODE FOR TRIP
		quick_rules(fbId,'RESPONSE/Pool/tripfields')#CHANGE TO TRIP
		text_rules(fbId,'153 NORTH NEW HAMPSHIRE')#COMING FROM ADDRESS
		quick_rules(fbId,'RESPONSE/Trip/4')#SEATS AVAILABLE
		quick_rules(fbId,'RESPONSE/Trip/45')#MINUTES AVAILABLE FOR TRANSIT
		quick_rules(fbId,'RESPONSE/Trip/0') #Arrive on Time
		quick_rules(fbId,'RESPONSE/Trip/0') #Drive own car
		quick_rules(fbId,'RESPONSE/Trip/mode') #All good!
		quick_rules(fbId,'CREATE_NEW_POOL')# calls NEW POOL (triggers postback response)
		text_rules(fbId,"Jonah's House")#GOING TO ADDRESS
		text_rules(fbId,"7:30")#GOING TO ADDRESS
		quick_rules(fbId,'RESPONSE/Pool/mode')#GO TO MODE FOR TRIP
		quick_rules(fbId,'RESPONSE/Pool/tripfields')#CHANGE TO TRIP
		text_rules(fbId,'153 NORTH NEW HAMPSHIRE')#COMING FROM ADDRESS
		quick_rules(fbId,'RESPONSE/Trip/4')#SEATS AVAILABLE
		quick_rules(fbId,'RESPONSE/Trip/45')#MINUTES AVAILABLE FOR TRANSIT
		quick_rules(fbId,'RESPONSE/Trip/0') #Arrive on Time
		quick_rules(fbId,'RESPONSE/Trip/1') #Arrive on Time
	except Exception as exc:
		return "Exception in drop_populate:\n" + str(exc)
	else:
		return "Dropped and re-created all tables!", 200
