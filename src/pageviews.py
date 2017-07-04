from interactions import quick_rules,pester,text_rules,process_referral#Note: have to import webhookviews at bottom of app
from collections import OrderedDict
from flask import render_template

#IMPORTS FOR TESTING:
from interactions import getStarted#NOTE These are NOT needed for app - only for drop_populate and testing!


from app import app,request,abort
from database import db

@app.route("/", methods=["GET"])
def root():
#    assert app.debug == False
	try:
#        messenger.say('1512768535401609','booting now')
		return render_template('index.html'), 200
	except Exception as exc:
		return str(exc)
