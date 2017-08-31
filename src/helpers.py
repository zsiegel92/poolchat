from dateutil.relativedelta import relativedelta
from operator import itemgetter

def findRelativeDelta(dt,inputted_delta,mode='minutes',delta_after=-1):
	print("in interactions.findRelativeDelta")
	if mode not in ['minutes','hours','days']:
		return "ERROR"
	difDt = dt + relativedelta(**{mode:delta_after*int(inputted_delta)})
	date = str(difDt.date().strftime("%B") + " " + difDt.date().strftime("%d") + ", " + difDt.date().strftime("%Y"))
	time = str(difDt.time().strftime("%I:%M %p"))
	return [date,time,difDt]

#constructor args should be itemgetter args
class itemget_force_tuple:
	def __init__(self,*args):
		self.itemget= itemgetter(*args)
		if len(args)<2:
			self.singleton=True
			print("Creating a singleton-force-tuple itemgetter!")
		else:
			self.singleton=False
			print("Creating a regular itemgetter!")

	def __call__(self,*args,**kwargs):
		if self.singleton:
			return (self.itemget(*args,**kwargs),)
		else:
			self.itemget(*args)
	def __repr__(self):
		return self.itemget.__repr__()
