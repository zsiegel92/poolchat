import os
import config
import smtplib
import json
from rq import Queue #INTERACTIONS MOVEMENT!
from rq.job import Job  #FOR Redis jobs #INTERACTIONS MOVEMENT!
from worker import conn #INTERACTIONS MOVEMENT!
from flask_sqlalchemy import SQLAlchemy
q = Queue(connection=conn) #INTERACTIONS MOVEMENT!
from models import  Carpooler,Pool, Trip,ensure_carpooler_notNone
from app import app,db,request
from interactions import findRelativeDelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
from messengerbot import messenger

from emailer import Emailer

scheduler_frequency=60

@app.route("/email_all/", methods=['GET','POST'])
def email_carpoolers(pool_id=None,localTesting=False):
	# emailer = Emailer(queue=q)
	emailer=Emailer(q)
	nowish = datetime.now() - relativedelta(minutes=int(scheduler_frequency/2))
	with app.app_context():
		if request:
			if request.method=="POST":
				data = json.loads(request.data.decode())
				pool_id = data["pool_id"]

		if pool_id is not None:
			pools = Pool.query.filter_by(id=pool_id)
		else:
			pools = Pool.query.all()
		for pool in pools:
			poolName = pool.poolName
			fireNotice = int(pool.fireNotice)
			eventDateTime= pool.eventDateTime
			eventEmail=pool.eventEmail
			[date,time,fireDateTime] = findRelativeDelta(eventDateTime,fireNotice,mode='hours',delta_after=-1)
			print("EXAMINING POOL: " + str(poolName))

			if (nowish> fireDateTime) and (not pool.noticeWentOut):
				emailer.email(eventEmail,message="Carpooling instructions going out for " + str(poolName) + "!",subject="GroupThere instructions en route for " + str(poolName) + "!")
				print("BETTER FIRE A NOTICE!")
				try:
					assert (pool.optimizedYet and pool.optimizationCurrent)
				except:
					message = "Pool with id " + str(pool.id) + " trying to send instructions, but not yet optimized! Ensure optimization is called by scheduler before emailing."
					subject = "ERROR with pool " + str(pool.id)
					print(message)
					emailer.self_email(message=message,subject=subject)#sent to self
					##FOR TESTING ONLY!
					for trip in pool.members:
						print("	trip")
						print("		trip.member.name: " + str(trip.member.name))
						print("		trip.pool.poolName: " + str(trip.pool.poolName))
						print("		trip.member.email: " + str(trip.member.email))
						print()
						message2 = message +"\n"
						message2+="Carpooler name: " + str(trip.member.name) + "\n"
						message2+="Carpooler email: " + str(trip.member.email) + "\n"
						message2+="Pool name: " + str(trip.pool.poolName) + "\n"

						subject2=subject + " --- CARPOOLNG instructions for " + str(trip.pool.poolName) + " on " + str(date) + " at " + str(time)
						emailer.email(trip.member.email,message=message2,subject=subject2)
					# FOR TESTING ONLY!

				else:
					print("Emailing all members of pool " + str(poolName))
					pool.noticeWentOut = True
					db.session.commit()
					for trip in pool.members:
						print("	trip")
						print("		trip.member.name: " + str(trip.member.name))
						print("		trip.pool.poolName: " + str(trip.pool.poolName))
						print("		trip.member.email: " + str(trip.member.email))
						print()
						message=""
						message+="Carpooler name: " + str(trip.member.name) + "\n"
						message+="Carpooler email: " + str(trip.member.email) + "\n"
						message+="Pool name: " + str(trip.pool.poolName) + "\n"

						subject="CARPOOLNG instructions for " + str(trip.pool.poolName) + " on " + str(date) + " at " + str(time)
						emailer.email(trip.member.email,message=message,subject=subject)

			elif (nowish>fireDateTime):
				print("Should have already fired a notice for pool " + str(poolName) + "!")
			else:
				print("We do not yet have to fire a notice for pool " + str(poolName) + "!")
				print("	Current time is " + datetime.now().strftime('%m/%d/%Y'))
				print("	Instructions to be sent on " + str(date) + " at " + str(time))
				print("	Event datetime: " + str(eventDateTime))
	return("All emails enqueued."),200



