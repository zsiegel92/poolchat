from groupThere.MailParam import MailParam
from groupThere.SystemParam import SystemParam
from groupThere.helpers import sayname, generate_groups_fromParam, generate_model,optimizePulp,gen_assignment,gen_assignment_fromParams, test_groups,test_model,groupsToLists,shortTime#, generate_groups
import os
import pickle
from operator import itemgetter
from datetime import datetime

def say(txt):
	print(txt)
	# os.system('say "' + txt + '"')

@sayname
def GroupThere(inputFilename=None,queryOrLoad='load'):
	latenessWindow=30
	# queryOrLoad='query'
	#queryOrLoad = 'load_distMatOnly'
	mailparam = MailParam(
			# login_filename='login_info.txt',
			eventDate = '8/12/2017',
			eventTime = '7:30 PM',
			eventName = 'Hive Meeting',
			eventLocation = "Jonah's Apartment",
			eventAddress = "3103 Livonia Ave, Culver City",
			eventContact = '(914) 400 - 3675',
			eventEmail = 'ifnotnow-la-swarm@googlegroups.com',
			eventHostOrg = 'IfNotNow LA Hivekeepers',
			signature = 'Which car are you in? Which car are you iinn, my people?',
			latenessWindow='30'
		)

	# eventHour=parse(mailparam.eventTime,fuzzy=True,dayfirst=False).time().hour
	# eventMinute = parse(mailparam.eventTime,fuzzy=True,dayfirst=False).time().minute
	# eventDateTime = parse(mailparam.eventDate,fuzzy=True,dayfirst=False).date()
	if queryOrLoad=='load_distMatOnly':
		print("Generating all parameters except for distance matrix, which will be loaded")
		params = SystemParam(filename=inputFilename,latenessWindow=latenessWindow)
		params.import_google_form(filename=inputFilename)
		params.get_event_info_from_mailparam(mailparam)
		params.coordinate_and_clean()
		params.load_dist_mat()
		with open("params/GTparams_"+str(datetime.now())[0:10]+".txt",'wb') as openfile:
			pickle.dump(params.to_dict(),openfile)
		with open("params/GTparams_prev.txt",'wb') as openfile:
			pickle.dump(params.to_dict(),openfile)
	elif queryOrLoad == 'query':
		print("Generating all parameters (full API usage)")
		params = SystemParam(filename=inputFilename,latenessWindow=latenessWindow)
		params.import_google_form(filename=inputFilename)
		params.get_event_info_from_mailparam(mailparam)
		params.coordinate_and_clean()
		params.gen_dist_mat()
		with open("params/GTparams_"+str(datetime.now())[0:10]+".txt",'wb') as openfile:
			pickle.dump(params.to_dict(),openfile)
		with open("params/GTparams_prev.txt",'wb') as openfile:
			pickle.dump(params.to_dict(),openfile)
	else:
		pickleFile = "params/GTparams_prev.txt"
		print("Loading all parameters from file: " + pickleFile)
		params=SystemParam(**pickle.load(open(pickleFile,'rb')))




	print(params)

	n=params.numel
	mx=max(list(map(int,params.numberCarSeats)))
	say("generating feasible groups")
	(groups,times) = generate_groups_fromParam(params,testing=True)
	params.groups['groups']=groups
	params.groups['times'] = times

	#GROUPS TEST
	doTests=False
	if doTests:
		if not test_groups(groups,times,params,n,mx,verbose=False):
			print("ERROR: GROUPS NOT PASSING TESTS")
		#MODEL TEST
		if not test_model(groups,times,params,n,mx,verbose=False):
			print("ERROR: MODEL NOT PASSING TESTS")

	say("feasible groups enumerated")
	params.model = generate_model(groups,times,n,mx)
	say("model generated")

	say("optimizing")
	(params.solution['fun'],params.solution['x'],params.solution['success']) = optimizePulp(params.model)
	# (params.solution['fun'],params.solution['x'],params.solution['success'])=optimizeCVXPY(params.model)
	say("optimization complete")
	say("Assigning rides")
	params.solution['assignments']=gen_assignment_fromParams(params)

	say("Rides assigned")
	for ass in params.solution['assignments']:
		print(ass['names'])
	os.system('say "GroupThere Complete"')
	return params




	# groups = genGroups(params)

def main():
	params = GroupThere()

	# params = GroupThere(inputFilename='inputs/testInput_extra_plusmustdrive.csv',queryOrLoad='load_distMatOnly')
	# print("\n\n\n\nIN GT MAIN\n\n\n\n")
	# print(params)
	# params = GroupThere(inputFilename='inputs/testInput_extra_plusmustdrive_short.csv',queryOrLoad='query')

	# params = GroupThere(inputFilename='inputs/testInput_extra_plusmustdrive_short.csv',queryOrLoad='load_distMatOnly')
	# params = GroupThere(inputFilename='inputs/testInput_extra.csv')
	# params = GroupThere(inputFilename='inputs/testInput_extra_short.csv',queryOrLoad='query')
	# params = GroupThere(inputFilename='inputs/testInput_extra_short.csv',queryOrLoad='load_distMatOnly')
	# Add to coordinate_and_clean a check that ensures all coordinates are close to eventAddress!
	# print(params)

	# print(params)
	# print(params.model)







if __name__=='__main__':
	main()

