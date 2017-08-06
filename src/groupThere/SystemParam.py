import csv
from numpy import zeros, ceil,savetxt,loadtxt
from groupThere.helpers import sayname
import requests
import googlemaps
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os
import time


class SystemParam:
	def __init__(self,email=[],name=[],address=[],numberCarSeats =[],canLeaveAt=[],minsAvail=None,extra=[],latenessWindow=0,must_drive=[],timestamps=[],headers_colNames = [],eventAddress=None,eventDate=None,eventTime=None,eventDateTime=None,eventCoords=None,dist_mats = {'Distances':None,'Durations':None},dists_to_event={'Distances':None,'Durations':None},coords =[],numel=None,model={'A':None,'Aeq':None,'b':None,'beq':None,'f':None},solution={'x':None,'fun':None,'success':None,'assignments':None},filename=None,groups={'groups':None,'times':None}, **kwargs):
		self.email = email
		self.name = name
		self.address= address
		self.numberCarSeats=numberCarSeats
		self.canLeaveAt=canLeaveAt
		self.extra=extra
		self.latenessWindow=latenessWindow
		self.must_drive=must_drive
		self.timestamps = timestamps
		self.headers_colNames = headers_colNames

		self.minsAvail=minsAvail

		self.must_drive=[True if ((int(val)>0) and (self.must_drive[idx]!='No')) else False for idx,val in enumerate(self.numberCarSeats)]

		self.eventAddress=eventAddress
		self.eventDate=eventDate
		self.eventTime=eventTime
		self.eventDateTime=eventDateTime
		self.eventCoords = eventCoords
		self.numel=len(email)

		self.dist_mats = dist_mats#GENERATE DIST MATS (call f'n)
		self.dists_to_event = dists_to_event
		self.coords= coords#GENERATE COORDS (call f'n)
		self.model = model#Generate model!
		self.solution=solution

		self.groups=groups

		self.filename=filename
		# if filename:
		# 	self.import_google_form(filename)

		if (numel):
			self.numel=numel
		else:
			self.numel=len(self.email)



	def __str__(self):
		d = self.to_dict()
		msg=""
		for key, val in d.items():
			msg = msg+ "\n\n" + str(key) + ":\n" + str(val)
		return msg

	def __repr__(self):
		return str(self.to_dict())


	def to_dict(self):
		# stuff = ['email','name','address','numberCarSeats','canLeaveAt','extra','latenessWindow','timestamps','headers_colNames','eventAddress','eventDate','eventTime','eventDateTime','eventCoords','dist_mats','dists_to_event','coords','model','filename','numel']
		# selfdict = {key:getattr(self,key,None) for key in stuff}
		# return selfdict
		return (vars(self))

	@sayname
	def get_event_info_from_mailparam(self,mailparam):
		self.eventAddress=mailparam.eventAddress
		self.eventDate=mailparam.eventDate
		self.eventTime=mailparam.eventTime
		self.eventDateTime = parse(str(self.eventDate) + " at " + str(self.eventTime))#datetime object
		self.latenessWindow = int(mailparam.latenessWindow)

	#datetime, email, name, address (quoted), can leave (time), on_time (yes/no), number seats
	@sayname
	def import_google_form(self,filename=None):
		if (filename is None) and (self.filename is None):
			print("Please enter a filename for import_google_form.")
			return
		elif filename is None:
			filename = self.filename
		else:
			self.filename=filename
		columnNames=['timestamps','email','name','address','canLeaveAt','extra','numberCarSeats','must_drive']#must_drive

		appender = (lambda x,y: x.append(y))

		with open(filename,'rt') as csvfile:
			s = csv.reader(csvfile,delimiter=',',quotechar='"')
			self.headers_colNames = list(zip(columnNames,next(s,None)))
			for row in s:
				columns = list(map((lambda name: getattr(self,name)),columnNames))
				#map(f,x,y) is equivalent to map((lambda tuple: f(*tuple)),zip(x,y))
				# print("list(s): " + str(list(s)))
				columns[:] = map(appender,columns,row)
		self.numel = len(self.email)


	@sayname
	def coordinate_and_clean(self):
		GMAPS_GEOCODE_API_TOKEN=os.environ['GEOCODE_API_KEY']
		geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
		for index, address in enumerate(self.address):
			print("Geocoding address " + str(index) + ": " + str(address))
			response = requests.request("GET", geocode_url, params={"address":address,"key":GMAPS_GEOCODE_API_TOKEN}).json()

			self.address[index]=response['results'][0]['formatted_address']
			lat = response['results'][0]['geometry']['location']['lat']
			lon = response['results'][0]['geometry']['location']['lng']

			self.coords.append((lat,lon))
			print("		formatted_address: " + str(self.address[index]))
			print("		coordinates: " + str(self.coords[index]))
		if self.eventAddress:
			address =self.eventAddress
			print("Geocoding event address " + str(address))
			response = requests.request("GET", geocode_url, params={"address":address,"key":GMAPS_GEOCODE_API_TOKEN}).json()

			self.eventAddress=response['results'][0]['formatted_address']
			lat = response['results'][0]['geometry']['location']['lat']
			lon = response['results'][0]['geometry']['location']['lng']
			self.eventCoords=(lat,lon)
			print("		formatted_address: " + str(self.eventAddress))
			print("		coordinates: " + str(self.eventCoords))

	# @pre: self.address is a list of address strings
	# @post: self.dist_mats is a distance matrix
	# @post : self.coords is a 2xn list of coordinates
	@sayname
	def gen_dist_mat(self):
		n = self.numel
		d_t = zeros((n,n))
		R_t = zeros((n,n))
		self.dists_to_event['Distances']=zeros((1,n))
		self.dists_to_event['Durations']=zeros((1,n))

		addresses=self.address
		leavetime = self.eventDateTime - relativedelta(hours=1)

		APIkey= os.environ['DISTMAT_API_KEY']
		# pre_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
		gmaps = googlemaps.Client(key=APIkey)
		issue = False
		count=0
		try:
			numAtATime=10
			for k in range(0,int(ceil(n/numAtATime))):
				mink = numAtATime*k
				maxk = min(numAtATime*(k+1),n)#one greater than the max index
				origins = addresses[mink:maxk]
				print("\n\n\nOrigins "+ str(mink) + " to " + str(maxk) + ": " + str(origins))
				for L in range(0,int(ceil(n/numAtATime))):
					minL = numAtATime*L
					maxL = min(numAtATime*(L+1),n)#one greater than the max index
					count = count + (maxL-minL)*(maxk-mink)
					print("Querying distance " + str(count))
					dests = addresses[minL:maxL]
					print("Destinations: " + str(dests))


					matrix = gmaps.distance_matrix(origins,dests,mode='driving',language='en',avoid='tolls',units='imperial',departure_time=leavetime,traffic_model='optimistic')


					print("Output matrix['rows']:\n\n\n" + str(matrix.get('rows')) +"\n\n")
					if ((matrix.get('rows') is not None) and (len(matrix.get('rows'))>0)):
						for i in range(0,maxk-mink):
							print("\n\nd_t row:\n\n")
							print(str(list(map((lambda ind: matrix['rows'][i]['elements'][ind]['distance']['value']),range(0,maxL-minL)))))
							print("\n\nR_t row:\n\n")
							print(str(list(map((lambda ind: matrix['rows'][i]['elements'][ind]['duration']['value']),range(0,maxL-minL)))))

							d_t[mink+i,minL:maxL]=list(map((lambda ind: matrix['rows'][i]['elements'][ind]['distance']['value']),range(0,maxL-minL))) #in "feet"
							R_t[mink+i,minL:maxL]=list(map((lambda ind: matrix['rows'][i]['elements'][ind]['duration']['value']),range(0,maxL-minL)))
					else:
						issue = True
						print("Error accessing Google Maps API! Returning.")
						break

					if (int(ceil(n/numAtATime)) > 1):
						time.sleep(1) #To prevent API from overloading
				if issue:
					break
				try:
					#FILL OUT DISTANCES TO EVENT
					dests = [self.eventAddress]
					matrix = gmaps.distance_matrix(dests,origins,mode='driving',language='en',avoid='tolls',units='imperial',departure_time=leavetime,traffic_model='optimistic')

					print("\n\ndists_to_event['Durations'][" + str(mink) +":" + str(maxk) + "]:\n\n")
					print(str(list(map((lambda ind: matrix['rows'][0]['elements'][ind]['duration']['value']),range(0,maxk-mink)))))

					self.dists_to_event['Distances'][0,mink:maxk]=list(map((lambda ind: matrix['rows'][0]['elements'][ind]['distance']['value']),range(0,maxk-mink)))
					self.dists_to_event['Durations'][0,mink:maxk]=list(map((lambda ind: matrix['rows'][0]['elements'][ind]['duration']['value']),range(0,maxk-mink)))
				except Exception as exc:
					print("Error finding distances to event!")
					print(exc)
			else:
				print("Finished filling distance matrix!")
		except Exception as exc:
			print("Exception while filling distance matrix:\n\n" + str(exc)+"\n\n")
		self.dist_mats['Distances']=d_t
		self.dist_mats['Durations']=R_t
		print("\n\nself.d_t:\n\n" + str(self.dist_mats['Distances']) + "\n\n")
		print("\n\nself.R_t:\n\n" + str(self.dist_mats['Durations']) + "\n\n")
				# origins="|".join(self.address[mink:maxk]).replace(" ","+")
				# dests="|".join(self.address[minL:maxL]).replace(" ","+")

		print("\n\nself.dists_to_event['Durations']" + str(self.dists_to_event['Durations'])+"\n\n")
		print("\n\nself.dists_to_event['Distances']" + str(self.dists_to_event['Distances'])+"\n\n")

		savetxt('params/distances'+ str(datetime.now())[0:10]+ '.txt',self.dist_mats['Distances'])
		savetxt('params/durations'+ str(datetime.now())[0:10]+ '.txt',self.dist_mats['Durations'])

		savetxt('params/toEventDurations'+ str(datetime.now())[0:10]+ '.txt',self.dists_to_event['Durations'])
		savetxt('params/toEventDistances'+ str(datetime.now())[0:10]+ '.txt',self.dists_to_event['Distances'])

		savetxt('params/distances_prev.txt',self.dist_mats['Distances'])
		savetxt('params/durations_prev.txt',self.dist_mats['Durations'])

		savetxt('params/toEventDurations_prev.txt',self.dists_to_event['Durations'])
		savetxt('params/toEventDistances_prev.txt',self.dists_to_event['Distances'])


	@sayname
	def load_dist_mat(self,filename_dist=None,filename_dur=None,filename_eventdist=None,filename_eventdur=None):
		try:
			os.chdir("params")
			# if (not filename_dist) or (not filename_dur):
			# 	filelist=[x for x in os.listdir() if x.endswith('.txt')]
			# 	# filelistDist = os.listdir()
			# 	filelistDur = [afilename for afilename in filelist if  re.match(r"durations2017-([0-9]{2})-([0-9]{2})\.txt",afilename)]
			# 	filelistDist = [afilename for afilename in filelist if  re.match(r"distances2017-([0-9]{2})-([0-9]{2})\.txt",afilename)]
			# 	if len(filelistDist)==1:
			# 		print("Suitable file found in directory")
			# 		filename_dist = filelistDist[0]
			# 		filename_dur= filelistDur[0]
			# 	elif len(filelistDist)==0:
			# 		print("No suitable file found in directory")
			# 	else:
			# 		months = list(map((lambda nam: int(nam[14:16])),filelistDist))
			# 		maxmonthstr=filelistDist[argmax(months)][14:16]
			# 		filelistDist = [afilename for afilename in filelistDist if afilename[14:16]==filelistDist[argmax(months)][14:16]]

			# 		months = list(map((lambda nam: int(nam[14:16])),filelistDur))
			# 		filelistDur = [afilename for afilename in filelistDur if afilename[14:16]==filelistDur[argmax(months)][14:16]]

			# 		days = list(map((lambda nam: int(nam[17:19])),filelistDist))
			# 		maxdaystr=filelistDist[argmax(days)][17:19]
			# 		filelistDist = [afilename for afilename in filelistDist if afilename[17:19]==filelistDist[argmax(days)][17:19]]

			# 		days = list(map((lambda nam: int(nam[17:19])),filelistDur))
			# 		filelistDur = [afilename for afilename in filelistDur if afilename[17:19]==filelistDur[argmax(days)][17:19]]
			# 		if (len(filelistDist)>1):
			# 			filename_dist=filelistDist[0]
			# 			filename_dur=filelistDur[0]
			# 			print("Duplicate files in directory. Arbitrariliy selecting file " + str(filename_dist))
			# 		else:
			# 			filename_dist=filelistDist[0]
			# # 			filename_dur=filelistDur[0]
			# 			print("Most recent saved dist matrix is " + str(filename_dist) + " from " + str(filename_dist[14:19]))
			# 			print("Most recent saved duration matrix is " + str(filename_dur) + " from " + str(filename_dur[14:19]))
			# if ((not filename_eventdur) or (not filename_eventdist)):
			# 	filename_eventdist = "toEventDistances2017-" + str(maxmonthstr) + "-"+str(maxdaystr) +".txt"
			# 	filename_eventdur = "toEventDurations2017-" + str(maxmonthstr) + "-"+str(maxdaystr) +".txt"

			filename_dist='distances_prev.txt'
			filename_dur='durations_prev.txt'
			filename_eventdist='toEventDistances_prev.txt'
			filename_eventdur='toEventDurations_prev.txt'

			self.dist_mats['Distances']=loadtxt(filename_dist)
			self.dist_mats['Durations']=loadtxt(filename_dur)

			self.dists_to_event['Durations'] = loadtxt(filename_eventdur)
			self.dists_to_event['Distances'] = loadtxt(filename_eventdist)

			if ((len(self.dist_mats['Distances'])!=self.numel) or (len(self.dist_mats['Durations'])!=self.numel)):
				for i in range(0,10):
					print("ERROR! MATRICES LOADED FOR INCORRECT NUMBER OF PARTICIPANTS!")
		except Exception as exc:
			print("Error loading distance matrices from file.")
			print(exc)

		if os.path.basename(os.getcwd())=='params':
			os.chdir('..')

	@sayname
	def canLeaveToMinsAvailable(self,canLeaveAt=None,lateWindow=None):
		if canLeaveAt is None:
			canLeaveAt=self.canLeaveAt
		if lateWindow is None:
			lateWindow = self.latenessWindow

		self.eventDateTime = parse(str(self.eventDate) + " at " + str(self.eventTime))#datetime object
		dateTimes=list(map((lambda t: parse(str(self.eventDate)+" at " + str(t)) ),self.canLeaveAt))

		timeAvail= list(map((lambda t: relativedelta(self.eventDateTime,t)),dateTimes))
		minsAvail = list(map((lambda rd: 60*rd.hours + rd.minutes),timeAvail))
		return minsAvail


	@sayname
	def make_generate_groups_input(self):
		boolList_canBeLate = list(map((lambda s: s!='No'),self.extra))
		if (self.minsAvail is not None):
			int_minsAvailForTransit=self.minsAvail
		elif (self.canLeaveAt is not None):
			int_minsAvailForTransit = self.canLeaveToMinsAvailable(self.canLeaveAt,self.latenessWindow)

		int_numCarSeats = list(map(int,self.numberCarSeats))
		must_drive = list(map((lambda s: s!='No'),self.must_drive))

		#irrelevant if number seats is zero
		for idx, val in enumerate(must_drive):
			if int_numCarSeats[idx]==0:
				must_drive[idx]=False

		array_duration = self.dist_mats['Durations']
		doubleList_durs_toEvent = self.dists_to_event['Durations']
		int_latenessWindow=int(self.latenessWindow)



		params=[array_duration,boolList_canBeLate,int_minsAvailForTransit,int_numCarSeats,doubleList_durs_toEvent,int_latenessWindow,must_drive]

		return params

