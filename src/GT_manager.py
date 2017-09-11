import csv
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
import random
from helpers import findRelativeDelta
import pickle

from groupThere.GroupThere import GroupThere
from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups


# @pre: params.d_t, params. R_t, and params.dists_to_event['Distances'] and params.dists_to_event['Durations'] are all corrent
def gt_fromDistmattedParams(params,mailParam):
	print("in GT_manager.gt_fromDistmattedParams")
	# params.get_event_info_from_mailparam(mailParam)
	# params.coordinate_and_clean()
	with open("params/GTparams_"+str(datetime.now())[0:10]+".txt",'wb') as openfile:
		pickle.dump(params.to_dict(),openfile)
	with open("params/GTparams_prev.txt",'wb') as openfile:
		pickle.dump(params.to_dict(),openfile)
	# pickleFile = "params/GTparams_prev.txt"
	# print("Loading all parameters from file: " + pickleFile)
	# params=SystemParam(**pickle.load(open(pickleFile,'rb')))
	print("wrote pickles!")
	# print(params)


	(groups,times) = generate_groups_fromParam(params,testing=False)
	print("(gt_fromDistmattedParams) Generated groups!")
	# print("groups is: " + str(groups))
	# print("times is: " + str(times))
	params.groups['groups']=groups
	params.groups['times'] = times

	n=params.numel
	mx=max(list(map(int,params.numberCarSeats)))
	mx=min(mx,n)
	params.model = generate_model(groups,times,n,mx)
	(params.solution['fun'],params.solution['x'],params.solution['success'],params.solution['all_got_rides'],params.solution['got_rides']) = optimizePulp(params.model)


	print("Solution success: " + str(params.solution['success']))
	print("All got rides: " + str(params.solution['all_got_rides']))

	params.solution['assignments']=gen_assignment_fromParams(params)
	# for ass in params.solution['assignments']:
	# 	print(ass['names'])
	# 	print(ass['emails'])
	print("assignments successful: " + str(params.solution['assignments']))
	print("returning params from GT_manager.gt_fromDistmattedParams")
	return params



def gt_fromBasicParams(params,mailParam):
	params.get_event_info_from_mailparam(mailParam)
	params.coordinate_and_clean()
	params.gen_dist_mat()
	with open("params/GTparams_"+str(datetime.now())[0:10]+".txt",'wb') as openfile:
		pickle.dump(params.to_dict(),openfile)
	with open("params/GTparams_prev.txt",'wb') as openfile:
		pickle.dump(params.to_dict(),openfile)
	# pickleFile = "params/GTparams_prev.txt"
	# print("Loading all parameters from file: " + pickleFile)
	# params=SystemParam(**pickle.load(open(pickleFile,'rb')))
	print("wrote pickles!")
	print(params)

	n=params.numel
	mx=max(list(map(int,params.numberCarSeats)))
	(groups,times) = generate_groups_fromParam(params,testing=False)
	params.groups['groups']=groups
	params.groups['times'] = times
	params.model = generate_model(groups,times,n,mx)

	(params.solution['fun'],params.solution['x'],params.solution['success'],params.solution['all_got_rides'],params.solution['got_rides']) = optimizePulp(params.model)


	print("Solution success: " + str(params.solution['success']))
	params.solution['assignments']=gen_assignment_fromParams(params)
	# for ass in params.solution['assignments']:
	# 	print(ass['names'])
	# 	print(ass['emails'])
	return params

def get_real_generic_addresses(n):
	filename='addresses.txt'
	addresses=[]
	with open(filename,'rt',newline='') as csvfile:
		s = csv.reader(csvfile,delimiter = '\n',quotechar='"')
		for row in s:
			for field in row:
				if field!='':
					addresses.append(field)
	return (addresses * int((((n)/len(addresses))+1)))[:n] #repeat until given length

		# f = open(filename, newline='')
		# reader = csv.reader(f)
		# for row in reader:
		# 	for field in row:
		# 		addresses.append(field)



def create_generic_parameters(n=1,numberPools=None,randGen=False):
	print("In create_generic_parameters. n = " + str(n) + ", numberPools = " + str(numberPools) + ", randGen = " + str(randGen) + ".")
	real_addresses = get_real_generic_addresses(n+1)
	real_event_addresses = list(reversed(real_addresses))

	dicts=[]
	today = datetime.now()
	if (not numberPools) or (int(numberPools) > n):
		if randGen:
			numberPools = random.randint(1,n)
		else:
			numberPools = 1

	for k in range(1,n+1):
		##Carpooler
		fbId = str(k)
		first = "first" + str(k)
		last = "last_"+str(k)
		name = first + " " + last
		email= "email_" + str(k ) + "@notARealThing.com"

		##Pool
		poolName = "poolName_" + str(k)
		numberDaysInFuture= (random.randint(-10,10) if randGen else 10)
		[eventDate,eventTime,eventDateTime] = findRelativeDelta(today,numberDaysInFuture,mode='days',delta_after=1)
		latenessWindow= (10*random.randint(2,3) if randGen else 30)
		eventAddress = real_event_addresses[k]
		eventContact = "555-555-5555_" + str(k)
		eventEmail = "eventEmail_"+str(k)+"@notARealThing.com" #"groupThereLA@gmail.com"
		eventHostOrg = "eventHostOrg_"+str(k)
		signature = "signature_"+str(k)
		fireNotice = (6*random.randint(1,3) if randGen else 12)

		##Trip
		tripAddress=real_addresses[k]
		a=random.randint(0,1)
		num_seats = (a*4 + (1-a)*2*random.randint(0,1) if randGen else 4)
		preWindow = (10*random.randint(2,5) if randGen else 30)
		on_time = (random.randint(0,1)*random.randint(0,1) if randGen else 0)
		must_drive = (random.randint(0,1)*random.randint(0,1) if (randGen and num_seats>0) else 0)

		#formalrep? created and maintained by externalUpdate.
		carpoolDict = {'first':first,'last':last,'name':name,'email':email}
		if k<=numberPools:
			poolDict = {'poolName':poolName,'latenessWindow':latenessWindow,'eventAddress':eventAddress,'eventContact':eventContact,'eventEmail':eventEmail,'eventHostOrg':eventHostOrg,'signature':signature,'fireNotice':fireNotice,'eventDate':eventDate,'eventTime':eventTime,'eventDateTime':eventDateTime}
		else:
			numPoolsToJoin=min((random.randint(1,numberPools) if randGen else numberPools),k)#All have been created thus far, but if code is changed, it will definitely be true that at most k have been created at this point.
			poolDict={'joinPools':list(range(1,numPoolsToJoin+1))}

		tripDict = {'address':tripAddress,'num_seats':num_seats,'preWindow':preWindow,'on_time':on_time,'must_drive':must_drive}

		fullDict= {'fbId':fbId,'Carpooler':carpoolDict,'Pool':poolDict,'Trip':tripDict}

		dicts.append(fullDict)
	return dicts
