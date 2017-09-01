from numpy import  ceil
import googlemaps
import time

import os

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)


from operator import itemgetter

from emailer import Emailer
emailer=Emailer(q)
gmaps = googlemaps.Client(key=os.environ['DISTMAT_API_KEY'])
#usage:
# emailer.email(toAddress,message="",subject="")
# emailer.self_email(message=message,subject=subject)

import wtforms_ext
emailForm=wtforms_ext.EmailForm(ng_click='getCarpoolerInfo()')




# docs for gmaps https://developers.google.com/maps/documentation/distance-matrix/intro#traffic-model
#origin is a string, leaveTime is datetime, others is list as [{id:,address:},...]
def gen_dist_row(origin,others,leaveTime):
	print("In gen_dist_row")
	n = len(others)
	numAtATime=10
	distances=[]
	durations=[]
	durations_in_traffic=[]
	for k in range(0,int(ceil(n/numAtATime))):
		first= numAtATime*k
		last = min(numAtATime*(k+1),n)
		getter = itemgetter(*range(first,last))
		dests = [others[i]['address'] for i in range(first,last)]
		# best_guess
		# optimistic
		# pessimistic

		matrix = gmaps.distance_matrix([origin],dests,mode='driving',language='en',avoid='tolls',units='imperial',departure_time=leaveTime,traffic_model='best_guess')

		# if ((matrix.get('rows') is not None) and (len(matrix.get('rows'))>0)):
		if (last-first)>1:
			distances.extend([ element['distance']['value'] for element in getter(matrix['rows'][0]['elements']) ])

			durations.extend([element['duration']['value'] for element in getter(matrix['rows'][0]['elements']) ])
			durations_in_traffic.extend([element['duration_in_traffic']['value'] for element in getter(matrix['rows'][0]['elements']) ])
		else:
			distances.append(matrix['rows'][0]['elements'][0]['distance']['value'])
			durations.append(matrix['rows'][0]['elements'][0]['duration']['value'])
			durations_in_traffic.append(matrix['rows'][0]['elements'][0]['duration_in_traffic']['value'])


		if (int(ceil(n/numAtATime)) > 1):
			time.sleep(1) #To prevent API from overloading
	labeled = [{'id':others[ind]['id'], 'distance':distances[ind],'duration':durations_in_traffic[ind]} for ind in range(len(others))]
	return labeled

#dest is a string, leaveTime is datetime, others is list as [{id:,address:},...]
def gen_dist_col(dest,others,leaveTime):
	print("In gen_dist_col")
	n = len(others)
	numAtATime=10
	distances=[]
	durations=[]
	durations_in_traffic=[]
	for k in range(0,int(ceil(n/numAtATime))):
		first= numAtATime*k
		last = min(numAtATime*(k+1),n)
		getter = itemgetter(*range(first,last))
		origins = [others[i]['address'] for i in range(first,last)]
		# best_guess
		# optimistic
		# pessimistic
		matrix = gmaps.distance_matrix(origins,[dest],mode='driving',language='en',avoid='tolls',units='imperial',departure_time=leaveTime,traffic_model='best_guess')
		# if ((matrix.get('rows') is not None) and (len(matrix.get('rows'))>0)):



		if (last-first)>1:
			distances.extend([ row['elements'][0]['distance']['value'] for row in getter(matrix['rows']) ])
			durations.extend([ row['elements'][0]['duration']['value'] for row in getter(matrix['rows']) ])
			durations_in_traffic.extend([ row['elements'][0]['duration_in_traffic']['value'] for row in getter(matrix['rows']) ])
		else:
			distances.append(matrix['rows'][0]['elements'][0]['distance']['value'])
			durations.append(matrix['rows'][0]['elements'][0]['duration']['value'])
			durations_in_traffic.append(matrix['rows'][0]['elements'][0]['duration_in_traffic']['value'])

		if (int(ceil(n/numAtATime)) > 1):
			time.sleep(1) #To prevent API from overloading
	labeled = [{'id':others[ind]['id'], 'distance':distances[ind],'duration':durations_in_traffic[ind]} for ind in range(len(others))]
	return labeled


#origin and dest are strings, leaveTime is datetime
def gen_one_distance(origin,dest,leaveTime):
	print("In gen_one_distance")
	# best_guess
	# optimistic
	# pessimistic
	matrix = gmaps.distance_matrix([origin],[dest],mode='driving',language='en',avoid='tolls',units='imperial',departure_time=leaveTime,traffic_model='best_guess')
	distance = matrix['rows'][0]['elements'][0]['distance']['value']
	duration = matrix['rows'][0]['elements'][0]['duration']['value']
	duration_in_traffic=matrix['rows'][0]['elements'][0]['duration_in_traffic']['value']
	time.sleep(1) #To prevent API from overloading
	return {'duration':duration_in_traffic,'distance':distance}

