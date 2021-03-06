
import unittest
import random



import json
# from utils import modified_environ
# with modified_environ(APP_SETTINGS='config.TestingConfig'):
# 	from app import app, db,models, ts
if __name__!='__main__':
	from manage import app, db, models, ts
else:
	from utils import modified_environ
	with modified_environ(APP_SETTINGS='config.TestingConfig'):
		from app import app, db,models, ts

numTestUsers=31
baseFirst='Zach'
baseLast='Siegel'
password='masterp123'
emails=['zsiegel92@gmail.com']
original_len_emails = len(emails)


addresses=[
	  "317 S Broadway, Los Angeles, CA 90013",
	  "1441 S Bedford St, LA, CA 90035",
	  "1459 W 54th St, LA, CA",
	  "519 E 7th St, LA, CA",
	  "128 E Avenue 42, LA, CA 90031",
	  "448 S Alexandria Ave, Los Angeles, CA 90020",
	  "448 S Alexandria Ave, Los Angeles, CA 90020",
	  "4437 Radium Drive, Los Angeles, CA",
	  "710 Santiago Ave, Long Beach, CA",
	  "2755 California Ave, Signal Hill, CA 90755",
	  "2723 Alta St, Los Angeles, CA 90031",
	  "3205 Glendale Blvd, Los Angeles, CA 90039",
	  "3205 Glendale Blvd, Los Angeles, CA 90039",
	  "9006 Darby Ave, Northridge, CA 91325",
	  "9723 Eton Ave, Chatsworth, CA 91311",
	  "505 Georgina Ave, Santa Monica, CA 90402",
	  "1250 N June St, Los Angeles, CA 90038",
	  "1850 N College Pl, Long Beach, CA"
	]
if numTestUsers<len(addresses):
	addresses = addresses[:numTestUsers]
else:
	count = 0
	while len(addresses)<numTestUsers:
		addresses.append(addresses[count % len(addresses)])
		count+=1


if numTestUsers<len(emails):
	emails=emails[:numTestUsers]
else:
	count = 0
	while len(emails)<numTestUsers:
		emails.append('bb'+  str(count) + str(emails[count % original_len_emails]))
		count+=1

firsts=[]
lasts=[]
for i in range(len(emails)):
	firsts.append(baseFirst+ "_" + str(i))
	lasts.append(baseLast+ "_" + str(i))

numbers_of_seats=[]
numbers_of_seats= [str(random.randint(2,4)*random.randint(0,1)) for i in range(len(emails))]
must_drives = ['true' if ((random.randint(0,1)*random.randint(0,1)>0) and (int(numbers_of_seats[i])>0)) else 'false' for i in range(len(emails))]
on_times=['true' if random.randint(0,1)*random.randint(0,1)>0 else 'false' for i in range(len(emails))]
preWindows =[str(20 + random.randint(0,1)*10 + random.randint(0,1)*10+random.randint(0,1)*10) for i in range(len(emails))]



class AppTestCase(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		with app.test_request_context():
			db.session.commit()
			db.drop_all()
			db.create_all()
			db.session.commit()

	def drop(self):
		with app.test_request_context():
			db.session.commit()
			db.drop_all()
			db.create_all()
			db.session.commit()

	def tearDown(self):
		# self.drop()
		pass

	def getUser(self,email):
		# with app.app_context():
		cp = models.Carpooler.query.filter_by(email=email).first()
		if cp not in db.session:
			cp = db.session.query(models.Carpooler).get(cp.id)
		# return db.session.query(models.Carpooler).filter(Carpooler.id==)
		return cp
		# return models.Carpooler.query.filter_by(email=email).first()

	def assert_not_logged_in(self):
		rv=self.app.post('/api/status')
		data= json.loads(rv.data)
		assert(data['status']==False)

	def login(self,email,password):
		args={'email':email,'password':password,'remember_me':True}
		print("/api/login call")
		rv= self.app.post('/api/login',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv

	def logout(self,session_id=None):
		print("/api/logout/ call")
		rv = self.app.post('/api/logout/',follow_redirects=True)
		return rv


	def register(self,firstName,lastName,email,password):
		args = {'firstName':firstName,'lastName': lastName,'email':email,'confirm':password,'password':password,'accept_tos':True}
		print("/api/register call")
		rv= self.app.post('/api/register',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv

	def join_team(self,teamname,codeword):
		args={'teamname':teamname,'codeword':codeword}
		print("/api/join_team call")
		rv= self.app.post('/api/join_team/',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv

	def authenticate(self,email):
		cp = self.getUser(email)
		email = cp.email.lower()
		token=ts.dumps(email,salt='email-confirm-key')
		print("/api/confirm_email call")
		rv = self.app.post('/api/confirm_email',data={'email':email,'token':token},follow_redirects=True)
		return rv

	def make_team(self,name,email,codeword):
		print("/api/create_team/ call")
		rv=self.app.post('/api/create_team/',data={'email':email,'name':name,'codeword':codeword},follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv


	def make_pool(self,name,address,dateTimeText,email,fireNotice,latenessWindow,team_ids):
		print("/api/create_pool/ call")
		rv=self.app.post('/api/create_pool/',data={'name':name,'address':address,'dateTimeText':dateTimeText,'email':email,'fireNotice':fireNotice,'latenessWindow':latenessWindow,'team_ids':team_ids},follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv

	def create_trip(self,address,must_drive,num_seats,on_time,pool_id,preWindow,resubmit=False):
		print("/api/create_trip/ call")
		args={'address':address,'must_drive':must_drive,'num_seats':num_seats,'on_time':on_time,'pool_id':pool_id,'preWindow':preWindow,'resubmit':resubmit}
		rv = self.app.post("/api/create_trip/",data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		return rv



	def approve_team(self,temp_team_id,team_key):
		print("/api/admin_approve_team call")
		rv = self.app.post('/api/admin_approve_team',data={'team_id':temp_team_id,'team_key':team_key})
		return rv


	def test_0_empty_db(self):
		rv = self.app.get('/')
		# assert b'No entries here so far' in rv.data
		# print(rv.data)
		# for thing in vars(rv.data):
		# 	print(thing)
		assert '200' in rv.status

	def test_1_register_and_login(self):
		for i,email in enumerate(emails):
			firstName=firsts[i]
			lastName=lasts[i]
			rv = self.register(firstName,lastName,email,password)
			print("rv: " + str(rv))
			assert('20' in rv.status)
			cp=self.getUser(email)
			assert(cp.authenticated==False)
			self.authenticate(email)
			cp=self.getUser(email)
			assert(cp is not None)
			assert(cp.authenticated==True)
			rv= self.login(email,password)
			assert('20' in rv.status)
			rv= json.loads(self.app.post('/api/status').data)
			assert(rv['status'] is True)
			rv= self.logout()
			assert('20' in rv.status)
			rv = self.login(email + 'x', password)
			assert('20' not in rv.status)
			rv = self.login(email , str(password) + 'x')
			assert('20' not in rv.status)
			rv= self.logout()
			assert('20' in rv.status)
		with app.app_context():
			all_users = models.Carpooler.query.all()
		assert(len(all_users) == len(emails))
		db.session.commit()
		print("There are " + str(len(all_users)) + " users, created from " + str(len(emails)) + " emails")

		#login first user
		email = emails[0]
		rv = self.login(email,password)
		assert('20' in rv.status)
		rv= json.loads(self.app.post('/api/status').data)
		assert(rv['status'] is True)
		#create team
		teamName='testing1'
		rv=self.make_team(name=teamName,email=email,codeword='testing1')
		assert('20' in rv.status)
		#approve team
		temp_team = models.TempTeam.query.filter_by(name=teamName).first()
		assert(temp_team is not None)
		team_key = ts.dumps(temp_team.name,salt='team-confirm-key')
		rv = self.approve_team(temp_team.id,team_key)
		assert('20' in rv.status)

		team = models.Team.query.filter_by(email=email).first()
		assert(team is not None)
		self.logout()

		#TODO: test confirmation of team id
		#TODO: test team join request approval

		#login as each user, join team

		team= models.Team.query.filter_by(email=emails[0]).first()
		for i,email in enumerate(emails):
			self.login(email,password)
			rv= json.loads(self.app.post('/api/status').data)
			assert(rv['status'] is True)
			rv= self.join_team(team.name,team.password)
			assert('20' in rv.status)
			with app.test_request_context():
				cp=self.getUser(emails[0])
				db.session.add(cp)
				assert(team in cp.teams)

		team_id = team.id

		#create pool
		name = 'CARNIVAL'
		address='1502 S Robertson Blvd, Los Angeles, CA 90035, USA'
		dateTimeText='10-10-2017 19:30 -0700'
		email=emails[0]
		fireNotice=6
		latenessWindow=30
		team_ids=str([team_id])
		rv= self.make_pool(name,address,dateTimeText,email,fireNotice,latenessWindow,team_ids)
		assert('20' in rv.status)

		with app.test_request_context():
			db.session.add(cp)
			team=cp.teams[0]
			pool = team.pools[0]
			assert(pool is not None)
		pool_id = pool.id

		self.logout()

		#login as each user, create trip
		pool = models.Pool.query.filter_by(id=pool_id).first()
		for i,email in enumerate(emails):
			address=addresses[i]
			must_drive=must_drives[i]#'false'
			num_seats=numbers_of_seats[i]
			on_time= on_times[i]#'false'
			preWindow=preWindows[i]#'30'
			resubmit='false'

			self.login(email,password)
			rv= json.loads(self.app.post('/api/status').data)

			assert(rv['status'] is True)
			rv= self.create_trip(address,must_drive,num_seats,on_time,pool_id,preWindow,resubmit)
			print(rv.status)
			print(rv.data)
			assert('20' in rv.status)
			with app.test_request_context():
				cp=self.getUser(emails[0])
				db.session.add(cp)
				trip=cp.pools[0]
				assert(trip.carpooler_id == cp.id)
				assert(trip.pool_id == pool.id)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(AppTestCase)
def run_all_tests():
	unittest.TextTestRunner(verbosity=2).run(suite)
	carpoolers=models.Carpooler.query.all()
	pools=models.Pool.query.all()
	teams = models.Team.query.all()
	trips = models.Trip.query.all()
	print("RAN ALL TESTS!")
	print("Users: " + ", ".join([str((carpooler.id,carpooler.email)) for carpooler in carpoolers]))
	print("Pools: " + ", ".join([str((pool.id,pool.poolName,pool.eventAddress)) for pool in pools]))
	print("Teams: " + ", ".join([str((team.id, team.name, team.email,team.password)) for team in teams]))
	print("TRIPS:")
	for trip in trips:
		print("--- pool{}, {}, {}, {}, {}, {}, {}".format(trip.pool_id, trip.carpooler_id,trip.address,trip.preWindow,trip.num_seats,str(trip.on_time),str(trip.must_drive)))


def main():
	# unittest.main()
	run_all_tests()

if __name__=='__main__':
	main()

