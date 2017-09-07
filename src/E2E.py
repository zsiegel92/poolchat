
import unittest



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



class AppTestCase(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		with app.test_request_context():
			db.drop_all()
			db.create_all()

	def drop(self):
		with app.test_request_context():
			db.session.commit()
			db.drop_all()
			db.create_all()

	def tearDown(self):
		# self.drop()
		pass

	def getUser(self,email):
		with app.app_context():
			return models.Carpooler.query.filter_by(email=email).first()


	def test_empty_db(self):
		rv = self.app.get('/')
		# assert b'No entries here so far' in rv.data
		# print(rv.data)
		# for thing in vars(rv.data):
		# 	print(thing)
		print("rv.status: " + str(rv.status))
		assert '200' in rv.status


	def assert_not_logged_in(self):
		rv=self.app.post('/api/status')
		data= json.loads(rv.data)
		assert(data['status']==False)

	def login(self,email,password):
		args={'email':email,'password':password,'remember_me':True}
		print("/api/login call")
		rv= self.app.post('/api/login',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		print("/api/login return")
		return rv

	def logout(self,session_id=None):
		print("/api/logout/ call")
		rv = self.app.post('/api/logout/',follow_redirects=True)
		print("/api/logout/ return")
		return rv


	def register(self,firstName,lastName,email,password):
		args = {'firstName':firstName,'lastName': lastName,'email':email,'confirm':password,'password':password,'accept_tos':True}
		print("/api/register call")
		rv= self.app.post('/api/register',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		print("/api/register return")
		return rv

	def authenticate(self,email):
		cp = self.getUser(email)
		email = cp.email.lower()
		token=ts.dumps(email,salt='email-confirm-key')
		print("/api/confirm_email call")
		rv = self.app.post('/api/confirm_email',data={'email':email,'token':token},follow_redirects=True)
		print("/api/confirm_email return")
		return rv

	def test_register_and_login(self):
		numTestUsers=2
		baseFirst='Zach'
		baseLast='Siegel'
		password='masterp123'
		emails=['zsiegel92@gmail.com','thesouroaf@gmail.com','grouptherela@gmail.com','grouptherenow@gmail.com','ifnotnowcarpooling@gmail.com','grouptherecarpool@gmail.com','grouptheretest@gmail.com']
		emails=emails[:numTestUsers]
		for i,email in enumerate(emails):
			firstName=baseFirst + "_"+ str(i)
			lastName=baseLast+ "_"+ str(i)
			rv = self.register(firstName,lastName,email,password)
			assert('200' in rv.status)
			cp=self.getUser(email)
			assert(cp.authenticated==False)
			self.authenticate(email)
			cp=self.getUser(email)
			assert(cp.authenticated==True)
			rv= self.login(email,password)
			assert('200' in rv.status)
			rv= json.loads(self.app.post('/api/status').data)
			assert(rv['status'] is True)
			rv= self.logout()
			assert('200' in rv.status)
			rv = self.login(email + 'x', password)
			assert('200' not in rv.status)
			rv = self.login(email , str(password) + 'x')
			assert('200' not in rv.status)
			rv= self.logout()
			assert('200' in rv.status)
		all_users = models.Carpooler.query.all()
		assert(len(all_users) == len(emails))

		firstName=baseFirst + "_"+ str(0)
		lastName=baseLast+ "_"+ str(0)
		email = emails[0]
		rv = self.login(email,password)
		rvdata= json.loads(self.app.post('/api/status').data)
		assert(rvdata['status'] is True)





suite = unittest.defaultTestLoader.loadTestsFromTestCase(AppTestCase)
def run_all_tests():
	unittest.TextTestRunner(verbosity=2).run(suite)
	print("RAN ALL TESTS!")

def main():
	# unittest.main()
	run_all_tests()

if __name__=='__main__':
	main()

