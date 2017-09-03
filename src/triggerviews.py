from interactions import quick_rules,pester,text_rules,process_referral#Note: have to import webhookviews at bottom of app
from page_interactions import populate_group_test
from collections import OrderedDict
from flask_login import current_user, login_user, logout_user,login_required

#IMPORTS FOR TESTING:
from interactions import getStarted#NOTE These are NOT needed for app - only for drop_populate and testing!
import sys
from flask import render_template
from app import app,request
from database import db

from groupThere.GroupThere import GroupThere

# myapp/util.py




# @app.route('/populate_group/',methods=['GET'])
# @login_required
def populate_group():
	populate_group_test()
	return 200




# <form role="form" method="GET" action="/populate_generic/" target="_self">
#             <div class="form-group">
#               <input type="text" name="n" class="form-control" id="n-box" placeholder="Enter number of generic populators." style="max-width: 300px;">
#             </div>
#             <button type="submit" class="btn btn-default">Submit</button>
#           </form>

# @app.route('/populate_generic/',methods=['POST'])
# def post_populate_generic_test():
# 	print("in post_populate_generic_test")
# 	print("request is : " + str(request))
# 	n = int(request.form['n'])
# 	db.drop_all()
# 	db.create_all()
# 	dicts =populate_generic(n)
# 	return 'Populated database with ' + str(n) + " people.\r\n\r\n" + str("\r\n".join(map(str,dicts))),200



# @app.route('/populate_generic/<int:n>',methods=['GET'])
# def get_populate_generic_test(n):
# 	print("in get_populate_generic_test")
# 	db.drop_all()
# 	db.create_all()
# 	dicts =populate_generic(n)
# 	return 'Populated database with ' + str(n) + " people.\r\n\r\n" + str("\r\n".join(map(str,dicts))),200




# @app.route('/do_groupthere/', methods=['GET'])
# @login_required
def do_groupthere():
	params = GroupThere()
	for ass in params.solution['assignments']:
		names = ass['names']
		print(names)
		#check if names is iterable
		#print each name
	return  str(params.solution['assignments'])




# @app.route('/testing/', methods=["POST"])
# def post_testing(fbId):
# 	fbId = int(request.form['fbId'])

# @app.route('/testing/<int:fbId>', methods=["GET"])
# @login_required
def testing(fbId):
	fbId = str(fbId)
	# db.drop_all()
	# db.create_all()
	# db.session.commit()

	# fbId = '1512768535401609' #GroupThere page-scoped ID for Zach
	# fbId = '1585931554790785' #Zach and Friends page-scoped ID for Zach
	actions = [
		('start','None'),
		('text','zsiegel92@gmail.com'),#user email
		('quick','mode'),
		('quick','CREATE_NEW_POOL'),
		('text',"IfNotNow HM at David's"),#eventName
		('text',"8/30 at 4:30"),#eventDateTime
		('quick','eventAddress'),
		('text','100 W 1st St LA CA'),#going TO
		('quick','eventContact'),
		('text','9144003675'),#eventContact
		('text','If Not Now LA'),#host org
		('text',"Which car are you in? Which car are you in, my people?"),#signature
		('quick','30'),#latenessWindow
		('quick','12'),#fireNotice
		('quick','EMAIL_INPUT/Pool/OWN_EMAIL'),
		# ('text','zsiegel92@gmail.com'),#eventEmail
		('quick','mode'),
		('quick','SWITCH_MODE/tripfields'),
		('text',"153 N New Hampshire Ave, LA CA"),#FROM
		('quick','num_seats'),
		('quick','4'),#num_seats
		('quick','30'),#preWindow
		('quick','1'),#on_time
		('quick','1'),#must_drive
		('quick','mode')
		]

	functions = {'quick':(lambda input: quick_rules(fbId,input)),'text':(lambda input: text_rules(fbId,input)),'start':(lambda input: getStarted(fbId))}

	for tuple in actions:
		print("DOING AN ACTION IN pageviews.testing()",file=sys.stderr)
		print('tuple[0]: ' + str(tuple[0]) + ", tuple[1]: " + str(tuple[1]) + ", functions[tuple[0]]: " + str(functions[tuple[0]]),file=sys.stderr)
		functions[tuple[0]](tuple[1])

	return "Ran test!", 200
