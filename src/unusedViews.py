from interactions import quick_rules,pester,text_rules,process_referral#Note: have to import webhookviews at bottom of app
from flask_login import current_user, login_user, logout_user,login_required

#IMPORTS FOR TESTING:
from interactions import getStarted#NOTE These are NOT needed for app - only for drop_populate and testing!

from app import app,request,abort
from database import db

from groupThere.GroupThere import GroupThere



#TODO: Flip through users in db, message them their table has been dropped :)
# @app.route('/drop_only', methods=["GET"])
# @login_required
def drop_table_only():
	print("Dropping all tables")
	try:
		if current_user.is_anonymous():
			return "must log in to drop tables.",302
		else:
			logout_user()
			# db.session.expunge(carpooler)  # expunge the object from session
			# make_transient(carpooler)  # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_api.html#sqlalchemy.orm.session.make_transient
			db.session.commit()
			print("committed once")
			db.session.close_all()
			print("closed sessions")
			db.reflect()
			print("reflected")
			db.session.close()
			print("closed session")
			db.drop_all()
			db.session.commit()
			return "Tables dropped!",200
	except Exception as exc:
		return "Exception on table drop:\n" + str(exc),500
	else:
		return "Dropped and re-created all tables!", 200

# @app.route('/drop_ping', methods=["GET"])
# @login_required
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



# @app.route('/pester', methods=["GET"])
# @login_required
def pester_view():
	try:
		sender_id = '1512768535401609'
		pester(sender_id)
	except Exception as exc:
		return "Exception on pester_view:\n" + str(exc)
	else:
		return "Pestered Zach!", 200


# @app.route('/ping_getStarted', methods=["GET"])
# @login_required
def ping_getStarted():
	try:
		fbId = '1512768535401609'
		getStarted(fbId)
	except Exception as exc:
		return "Exception on ping_getStarted:\n" + str(exc)
	else:
		return "Got started!", 200

# @app.route('/ping_text', methods=["GET"])
# @login_required
def ping_text():
	try:
		fbId = '1512768535401609'
		text_rules(fbId,'Hey')#email
	except Exception as exc:
		return "Exception on ping_text:\n" + str(exc)
	else:
		return "ping_text successful!", 200


# @app.route('/drop_populate', methods=["GET"])
# @login_required
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
