from functools import wraps
from groupThere.subsets import EnumeratedSubsets,bax
from operator import itemgetter
import numpy as np
from itertools import permutations

import pulp


def sayname(f):
	message ='in '+ f.__name__
	@wraps(f)
	def new_f(*args,**kwargs):
		print(message)
		return f(*args,**kwargs)
	return new_f


@sayname
def generate_groups_fromParam(system_param,testing=False):
	# return generate_groups(*system_param.make_generate_groups_input())
#and must_drive!?
	return generate_groups_bits(*system_param.make_generate_groups_input(),testing=testing)

@sayname
def generate_shortTime_fromParam(system_param):
	(array_duration,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive)=system_param.make_generate_groups_input()
	maxNumberSeats=max(int_numCarSeats)
	array_duration=np.floor(array_duration/60)#convert to minutes
	doubleList_durs_toEvent = np.floor(np.array(doubleList_durs_toEvent)/60)
	st = shortTime(array_duration,maxNumberSeats,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive)
	return st


@sayname
def generate_groups_bits(array_duration,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive,testing=False,verbose=False):
	numFail=0
	en=EnumeratedSubsets()
	maxNumberSeats=max(int_numCarSeats)
	array_duration=np.floor(array_duration/60)#convert to minutes
	doubleList_durs_toEvent = np.floor(np.array(doubleList_durs_toEvent)/60)
	try:
		if len(doubleList_durs_toEvent.shape)>1:
			doubleList_durs_toEvent = doubleList_durs_toEvent[0]
	except:
		print("doubleList_durs_toEvent inexplicably already a list...")
	numPeople = len(int_minsAvailForTransit)
	maxGroupSize = min(numPeople,maxNumberSeats)
	st = shortTime(array_duration,maxNumberSeats,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive)
	print("Created shortTime object")
	groups = {}
	times = {}
	if maxGroupSize ==0:
		print("Max group size is zero, returning " + str((groups,times)) + " from generate_groups_bits. Handle it.")
		return (groups,times)

	drivers = {i:bax((1 if val>=i else 0 for val in int_numCarSeats)) for i in range(1,maxGroupSize+1)}
	manditory_drivers=bax((1 if ((val>=1) and (must_drive[idx])) else 0 for idx,val in enumerate(int_numCarSeats)))
	mandk = {k:manditory_drivers&drivers[k] for k in range(1,maxGroupSize+1)}
	mand_not_k = {k:manditory_drivers&(drivers[k].inverted()) for k in range(1,maxGroupSize+1)}
	#Generate groups of size 1
	groups[1] = bax((1 if drivers[1][j]==1 else 0 for j in range(0,numPeople)),enum=en)

	# doubleList_durs_toEvent: [[ 10.   0.  28.]]
	# groups: {1: bitarray('010')}
	# Error creating GT params. Returning from hardcoded dummy GroupThere params.
	# index 1 is out of bounds for axis 0 with size 1

	times[1]=[doubleList_durs_toEvent[i] for i in range(0,numPeople) if groups[1][i]==1]

	calledForSingleDriver=False
	#Generate groups of size 2 through maxNumSeats
	for k in range(2,maxGroupSize+1):
		numFailk=0
		groups[k]=bax.zeros(en.choose(numPeople,k),enum=en)
		#IF numPeople < k, there is an issue
		times[k] = []
		for ind,group in enumerate(groups[k].bax_gen(numPeople,k)):
			print("k is " + str(k) + "; Examining group " + str(group))
			if (group&drivers[k]).any() and (not (group&mandk[k]).counts_to(2))and (not (group&mand_not_k[k]).counts_to(1)):
				if (group&mandk[k]).counts_to(1):
					driver=(group&mandk[k]).index(1)
					group[driver]=0
					riders = group.toList()
					pair = st.getShortTimeOneDriver(driver,riders,k-1)
					if testing:
						group[driver]=1
						posDrivers=[driver]#for testing
						numPosDrivers=1#for testing
						calledForSingleDriver=True
				else:
					numPosDrivers = (group&drivers[k]).count()
					posDrivers = (group&drivers[k]).toList()
					pair = st.getShortTimeGroup(posDrivers,group.toList(),numPosDrivers,k)
					calledForSingleDriver=False
				#pair =
				#(isPossible,minTime,bestOrder,driver,lateOK,notLatePossible)
				if pair[0]==True:
					if testing:
						(passed,message,formattedResponse)=test_one_group(group,must_drive,int_numCarSeats,st=st,verbose=False)
						if not passed:
							numFail+=1
							numFailk+=1
							print("\n-ERROR " +str(numFail) + " IN GENERATE_GROUPS (printing from generate_groups_bits)-")
							print("Message from test_one_group: " + str(message))
							print("(back in test_one_group)")
							print("Group added to groups, but fails test: " +str(group))
							# print("Formatted response regarding time: ")
							# for key,value in formattedResponse.items():
							# 	print(str(key) + ": " + str(value))
							print("Failure involving " + ('getShortTimeOneDriver' if calledForSingleDriver else 'getShortTimeGroup'))
							print("pair outputted by "+ ('getShortTimeOneDriver' if calledForSingleDriver else 'getShortTimeGroup') +": " + str(pair))
							print("-END OF ERROR " + str(numFail) + "-")

					times[k].append(pair[1])
					groups[k][ind]=1

		print("Number of feasible groups of size " + str(k)+ ": " + str(groups[k].count()))
		if testing:
			print("Number of failures among groups of size " + str(k)+ ": " + str(numFailk))



	if testing:
		print("Number of failures = " +str(numFail))
		print("drivers: " + str(drivers))
		print('intnumcarseats: ' + str(int_numCarSeats))
		print()
		print("manditory drivers: " + str(manditory_drivers))
		print("mandk: " + str(mandk))
		print("mand_not_k: " + str(mand_not_k))
		print("must_drive: " + str(must_drive))



	return (groups,times)






#times = {1:[...],2:[...],...,maxSeats:[...]}
#groups = {1:bax('...'),2:bax('...'),...,maxSeats:bax('...')}
#len(times[k])==groups[k].count() for all k
@sayname
def generate_model(groups,times,n,maxSeats):
	model={'A':None,'Aeq':None,'b':None,'beq':None,'f':None}
	totNumGroups = sum([(groups[k]).count() for k in range(1,maxSeats+1)])
	Aeq=np.zeros((n,totNumGroups))
	ff=np.zeros((1,totNumGroups))
	beq=np.ones((n,1))
	cur_column=0
	for k in range(1,maxSeats+1):
		for numseen,subsetInd in enumerate(groups[k].list_ones()):
			Aeq[:,cur_column]=np.array(groups[k].generateSubsetBax(n,k,subsetInd))
			ff[0,cur_column]= times[k][numseen]
			cur_column+=1

	model['Aeq']=Aeq
	model['beq']=beq
	model['f']=ff
	return model


def groupsToLists(groups,n):
	return {k:groups[k].toListOfLists(n,k) for k in groups}




#@pre:
#	group is bax
#	must_drive is boolean list
#	numberCarSeats is int list
def test_one_group(group,must_drive,numberCarSeats,st=None,verbose=True):
	gpList = group.toList()
	k=group.count()
	message='\n'
	formatted=None
	apass=True
	if k==1:
		if numberCarSeats[gpList[0]]<1:
			message+= "ERROR - NO DRIVER (group length 1)\n"
			apass=False
		#Ensure time constraint by calling short_time
	else:
		if max(list(itemgetter(*gpList)(numberCarSeats)))<len(gpList):
			message+="ERROR - NO DRIVER\n"
			apass=False
		nMand = sum(list(itemgetter(*gpList)(must_drive)))
		if nMand>1:
			message+="ERROR - MULTIPLE MANDITORY DRIVERS\n"
			apass=False
		elif nMand==1:
			if itemgetter(gpList[list(itemgetter(*gpList)(must_drive)).index(True)])(numberCarSeats)< len(gpList):
				message+="ERROR - (SOLE) MANDATORY DRIVER CANNOT ACCOMODATE GROUP CAPACITY\n"
				apass=False
		elif nMand==0:
			pass


	if st is not None:
		formatted=st.returnFormattedGroup(gpList)
		message+= "\nOUTPUT OF returnFormattedGroup:"
		for key,val in formatted.items():
			message += "\n" + str(key) + ": " + str(val)
		message += "\n(end of returnFormattedGroup output)"

	if (not apass) and verbose:
		print("Failures for group (test_one_group) " + str(gpList) +":")
		print(message)
		print("formatted message regarding time: ")
		for key,val in formatted.items():
			print()
			print(str(key) + ": " + str(val))
		print()

			#ensure only one must_drive
			#ensure some driver has enough seats, and if there is a must_driver, they must
			#ensure time constraint by calling short_time
	return (apass,message,formatted)

def test_groups(groups,times,params,n,maxSeats,verbose=False):
	st = generate_shortTime_fromParam(params)
	allPass=True
	must_drive = params.must_drive
	numberCarSeats = list(map(int,params.numberCarSeats))
	listOfGroups = {k:groups[k].toListOfLists(k) for k in groups}
	if verbose:
		print("NumberCarSeats: " + str([(i,val) for i,val in enumerate(numberCarSeats)]))
		print("Drivers: " + str([(i,val) for i,val in enumerate(numberCarSeats) if val>0]))
		print("Mandatory Drivers: " + str([i for i,val in enumerate(must_drive) if must_drive[i]]))
	numFails=0
	for k in listOfGroups:
		numFailsK=0
		for gp in listOfGroups[k]:
			message='\n'
			aPass=True
			if k==1:
				if numberCarSeats[gp[0]]<1:
					allPass=False
					aPass=False
					message+= "ERROR - NO DRIVER (group length 1)\n"
					#Ensure time constraint by calling short_time
			else:
				if max(list(itemgetter(*gp)(numberCarSeats)))<len(gp):
					message+="ERROR - NO DRIVER\n"
					allPass=False
					aPass=False
				nMand = sum(list(itemgetter(*gp)(must_drive)))
				if nMand>1:
					message+="ERROR - MULTIPLE MANDITORY DRIVERS\n"
					allPass=False
					aPass=False
				elif nMand==1:
					if itemgetter(gp[list(itemgetter(*gp)(must_drive)).index(True)])(numberCarSeats)< len(gp):
						message+="ERROR - (SOLE) MANDATORY DRIVER CANNOT ACCOMODATE GROUP CAPACITY\n"
						allPass=False
						aPass=False
				elif nMand==0:
					pass
			if not aPass:
				if verbose:
					print("Failures for group " + str(gp) +":")
					print(message)
					print()
				numFails+=1
				numFailsK+=1

			#ensure only one must_drive
			#ensure some driver has enough seats, and if there is a must_driver, they must
			#ensure time constraint by calling short_time
		if verbose:
			print("Number of total possible groups of size " + str(k)+": " + str(groups[k].length()))
			print("Number of supposedly feasible groups of size " + str(k)+": " + str(groups[k].count()))
			print("Number of failures among groups of size " + str(k) + ": " + str(numFailsK))
			print()

	print("Number of total possible groups: " + str(sum([groups[k].length() for k in groups])))
	print("Number of total supposedly feasible groups : " + str(sum([groups[k].count() for k in groups])))
	print("Number of failures: " + str(numFails))

	return allPass

def test_model(groups,times,params,n,maxSeats,verbose=False):
	totNumGroups = sum([(groups[k]).count() for k in range(1,maxSeats+1)])
	Aeq=np.zeros((n,totNumGroups))
	ff=np.zeros((1,totNumGroups))
	cur_column=0
	for k in range(1,maxSeats+1):
		for numseen,subsetInd in enumerate(groups[k].list_ones()):
			Aeq[:,cur_column]=np.array(groups[k].generateSubsetBax(n,k,subsetInd),dtype='uint8')
			ff[0,cur_column]= times[k][numseen]
			cur_column+=1
	colsets = [set(Aeq[:,col].nonzero()[0]) for col in range(Aeq.shape[1])]
	cols=[]
	found = True
	for gpsize in range(1,maxSeats+1):
		for gpindex in range(groups[gpsize].length()):
			if (not found) and (groups[gpsize][gpindex-1]):
				print("ERROR!")
				print("Feasible group not found - size: " + str(gpsize) + ", index: " + str(gpindex-1))
			found = False
			oneset = set(np.array(groups[gpsize].generateSubsetBax(n,gpsize,gpindex),dtype='uint8').nonzero()[0])
			for col,colset in enumerate(colsets):
				if colset==oneset:
					cols.append(col)
					found=True
					if verbose:
						print("Group found - size: " + str(gpsize) + ", index: " + str(gpindex-1) + ", in column: " + str(col))

	if Aeq.shape[1]!=len(cols):
		print("ERROR ERROR ERROR: NOT ALL GROUPS ARE FOUND AS COLUMNS")
		print('len(cols): ' + str(len(cols)))
		print('Aeq.shape: ' + str(Aeq.shape))
		return False
	else:
		print("All groups found in model matrix")
		return True


@sayname
def optimizePulp(model):

	Aeq=np.matrix(model['Aeq'])
	f=np.matrix(model['f'])
	m=Aeq.shape[0]
	n=Aeq.shape[1]
	x=pulp.LpVariable.dicts('assignments',range(0,n),lowBound=0,upBound=1,cat=pulp.LpBinary) #pulp.LpInteger
	assignment_model=pulp.LpProblem('assignment model',pulp.LpMinimize)
	assignment_model += pulp.lpSum([f[0,ind]*x[ind] for ind in range(0,n)])
	for l in range(0,m):
		assignment_model += pulp.lpSum([x[ind]*Aeq[l,ind] for ind in range(0,n) if Aeq[l,ind]!=0])==1
	assignment_model.solve()
	TOL=.00001
	x_thresholded = np.matrix([1 if x[i].varValue > TOL else 0 for i in range(0,n)])
	return (assignment_model.objective.value(),x_thresholded,assignment_model.status)

@sayname
def gen_assignment_fromParams(params):
	return gen_assignment(params.model['Aeq'],params.solution['x'],params.name,params.email,*params.make_generate_groups_input(),ids=params.carpooler_id)


#This function outputs a list of tuples consisting of participants in each carload. The tuples are ordered with driver at index 0 in pickup-order.
@sayname
def gen_assignment(Aeq,x,name,email,array_duration,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive,ids=None):
	maxNumberSeats=max(int_numCarSeats)
	array_duration=np.floor(array_duration/60)#convert to minutes
	doubleList_durs_toEvent = np.floor(np.array(doubleList_durs_toEvent)/60)
	try:
		if len(doubleList_durs_toEvent.shape)>1:
			doubleList_durs_toEvent = doubleList_durs_toEvent[0]
	except:
		print("doubleList_durs_toEvent inexplicably already a list...")

	st = shortTime(array_duration,maxNumberSeats,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive)

	cols = Aeq[:,x.nonzero()[1]]#EDITED FOR FLASK
	cols=np.array(list(map(np.ndarray.flatten,cols)))

	gps = [list((i for i in range(cols.shape[0]) if cols[i,j]==1)) for j in range(cols.shape[1])]
	assignments=list(map(st.returnFormattedGroup,gps))

	named_assignments=[]
	email_assignments=[]
	id_assignments=[]
	for ass in assignments:
		print(itemgetter(*ass['bestOrder'])(name))
		named_assignments.append(itemgetter(*ass['bestOrder'])(name))
		ass['names']=itemgetter(*ass['bestOrder'])(name)

		email_assignments.append(itemgetter(*ass['bestOrder'])(email))
		ass['emails']=itemgetter(*ass['bestOrder'])(email)

		ass['ids']=[]
		try:
			ass['ids']=itemgetter(*ass['bestOrder'])(ids)
			id_assignments.append(itemgetter(*ass['bestOrder'])(ids))
		except:
			print("Groupthere pool does not have carpooler_id")

	return assignments



def self_monitor_results(func):
	def wrapper(*func_args, **func_kwargs):
		print('function call ' + func.__name__ + '() with args ' + str(func_args[1:]) + ", and kwargs " + str(func_kwargs))
		retval = func(*func_args,**func_kwargs)
		print('function ' + func.__name__ + '() returns ' + repr(retval))
		return retval
	wrapper.__name__ = func.__name__
	return wrapper
def monitor_results(func):
	def wrapper(*func_args, **func_kwargs):
		print('function call ' + func.__name__ + '() with args ' + str(func_args) + ", and kwargs " + str(func_kwargs))
		retval = func(*func_args,**func_kwargs)
		print('function ' + func.__name__ + '() returns ' + repr(retval))
		return retval
	wrapper.__name__ = func.__name__
	return wrapper

class shortTime:
	def __init__(self,durs,maxNumSeats,canBeLate,minsAvail,numCarSeats,durs_toEvent,latenessWindow,must_drive):
		self.maxNumSeats=maxNumSeats
		self.durs = durs
		self.canBeLate=canBeLate
		self.minsAvail=minsAvail
		self.numCarSeats=numCarSeats
		self.durs_toEvent=durs_toEvent
		self.latenessWindow=latenessWindow
		self.must_drive=must_drive
		self.routeAdders = self.getRouteAdders(maxNumSeats)

	@sayname
	def getRouteAdders(self,maxNumSeats):
		# assert(maxNumSeats >0)
		ra=[]
		ra.append([[]])
		ra.append([[1]])
		for k in range(2,maxNumSeats+1):
			ra.append([[1]+ra[-1][0]] +[[0]+chunk for chunk in ra[-1]])
		print("routeAdders: " + str(list(map(np.array,ra))))
		return list(map(np.array,ra))

	@self_monitor_results
	def returnFormattedGroup(self,group,verbose=True):
		message =''
		message+= "Formatting group " + str(group)

		if len(group)==1:
			i = group[0]
			return {'isPossible':True,'minTime':self.durs_toEvent[i],'bestOrder':[i],'driver':i,'lateOk':bool(self.canBeLate[i]),'notLatePossible':bool(self.durs_toEvent[i]<=self.minsAvail[i]),'bestTimes':[self.durs_toEvent[i]]}

		drs = [i for i in group if self.numCarSeats[i] >= len(group)]

		message+=" && drivers are " + str(drs)

		mds = 0
		for i in group:
			if self.must_drive[i]:
				message += " && " + str(i) + " is manditory"
				drs=[i]
				mds +=1
		if mds > 1:
			message += " && ERROR: MULTIPLE MANDITORY DRIVERS IN GROUP"



		output= self.getShortTimeGroup(drs,group,len(drs),len(group),returnAll=True)

		message += " && Output of self.getShortTime is " + str(output)


		if output[0]==False:
			message+= " && Assigned group infeasible!"
			return {'isPossible':output[0],'minTime':output[1],'bestOrder':group,'driver':output[3],'lateOk':output[4],'notLatePossible':output[5],'message':message,'bestTimes':output[6]}

		return {'isPossible':output[0],'minTime':output[1],'bestOrder':tuple([output[3]]+list(output[2])),'driver':output[3],'lateOk':output[4],'notLatePossible':output[5],'message':message,'bestTimes':output[6]}
	# minimize_mode='human_hours'
	# @self_monitor_results
	def getShortTimeGroup(self,drivers,participants,numPosDrivers,numParticipants,minimize_mode='car_hours',returnAll=False):
		#drivers is a list of indices (but is it a list of indices wrt participants? Or base indices?)
		#participants includes drivers
		isPossible = False
		minTime = -1
		bestOrder=None
		bestDriver=None
		lateOK=None
		notLatePossible=None
		bestTimes=None
		for driver in drivers:
			participants.remove(driver)
			solution = self.getShortTimeOneDriver(driver,participants,numParticipants-1,minimize_mode=minimize_mode,returnAll=returnAll)
			participants.append(driver)
			if solution[0]:
				if (solution[1]<minTime) or (isPossible==False):
					isPossible=True
					minTime=solution[1]
					if returnAll:
						bestOrder = solution[2]
						bestDriver = solution[3]
						lateOK = bool(solution[4])
						notLatePossible= bool(solution[5])
						bestTimes = solution[6]
		#Note: bestOrder does not include driver.
		return (isPossible,minTime,bestOrder,bestDriver,lateOK,notLatePossible,bestTimes)




	# minimize_mode='human_hours'
	# @self_monitor_results
	def getShortTimeOneDriver(self,driver,participants,numParticipantsNotDriver,minimize_mode='car_hours',returnAll=False):
		# minimize_mode='car_hours'
		#drivers is an int
		#participants & drivers=={}
		if len(participants)==1:
			lastLeg=self.durs_toEvent[participants[0]]
			firstLeg = self.durs[driver,participants[0]]
			timeForDriver = self.minsAvail[driver]
			timeForRider=self.minsAvail[participants[0]]
			if all(x==1 for x in itemgetter(driver,*participants)(self.canBeLate)):
				lateOK = True
				timeForDriver +=self.latenessWindow
				timeForRider+= self.latenessWindow
			else:
				lateOK = False

			if (lastLeg<= timeForRider) and (firstLeg+lastLeg <=timeForDriver):
				if lateOK:
					if (lastLeg<= timeForRider-self.latenessWindow) and (firstLeg+lastLeg <=timeForDriver-self.latenessWindow):
						notLatePossible=True
					else:
						notLatePossible=False
				else:
					notLatePossible=True
				return (True,firstLeg+lastLeg,tuple(participants),driver,lateOK,notLatePossible,[firstLeg,lastLeg])
			else:
				return (False,-1,[],-1,False,False,False)
		driverConstraint = self.minsAvail[driver]
		constraints = itemgetter(*participants)(self.minsAvail)
		durmat=self.durs[np.ix_(participants,participants)]
		durs_from_driver = self.durs[np.ix_([driver],participants)].flatten()
		durs_to_event = [self.durs_toEvent[i] for i in participants]

		if all(x==1 for x in itemgetter(driver,*participants)(self.canBeLate)):
			lateOK=True
			constraints = [x+self.latenessWindow for x in constraints]
			driverConstraint = driverConstraint + self.latenessWindow
		else:
			lateOK=False


		minTime=-1
		isPossible = False
		bestOrder=[]
		bestTimes=[]
		times = [-1 for i in range(numParticipantsNotDriver+1)]
		for perm in permutations(range(numParticipantsNotDriver)):
			times[0]=durs_from_driver[perm[0]]
			times[1:numParticipantsNotDriver]=[durmat[perm[i],perm[i+1]] for i in range(numParticipantsNotDriver-1)]
			times[-1]= durs_to_event[perm[-1]]
			if (sum(times)<minTime) or (isPossible==False):
				if all((self.routeAdders[numParticipantsNotDriver+1]).dot(np.array(times)) < np.array([driverConstraint]+list(itemgetter(*perm)(constraints)))):
					if minimize_mode=='human_hours':
						minTime=sum((self.routeAdders[numParticipantsNotDriver+1]).dot(np.array(times)))
					elif minimize_mode == "car_hours":
						minTime=sum(times)
					else:
						minTime=sum(times)

					isPossible = True
					if returnAll:
						bestOrder = perm[:]
						bestTimes = times[:]


		if returnAll:

			notLatePossible=True
			if lateOK:
				if len(bestTimes)>0:
					if not all((self.routeAdders[numParticipantsNotDriver+1]).dot(np.array(bestTimes)) < np.array([driverConstraint-self.latenessWindow]+list(itemgetter(*bestOrder)([constraint - self.latenessWindow for constraint in constraints])))):
						notLatePossible = False

			bestOrder=itemgetter(*bestOrder)(participants)

			return (isPossible,minTime,bestOrder,driver,lateOK,notLatePossible,bestTimes)
		else:
			return (isPossible,minTime)

