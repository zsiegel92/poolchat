from dateutil.relativedelta import relativedelta
def findRelativeDelta(dt,inputted_delta,mode='minutes',delta_after=-1):
	print("in interactions.findRelativeDelta")
	if mode not in ['minutes','hours','days']:
		return "ERROR"
	difDt = dt + relativedelta(**{mode:delta_after*int(inputted_delta)})
	date = str(difDt.date().strftime("%B") + " " + difDt.date().strftime("%d") + ", " + difDt.date().strftime("%Y"))
	time = str(difDt.time().strftime("%I:%M %p"))
	return [date,time,difDt]
