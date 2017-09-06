from utils import modified_environ
import unittest
import json

with modified_environ(APP_SETTINGS='config.TestingConfig'):
	from app import app, db,models, ts


class AppTestCase(unittest.TestCase):
	def setUp(self):
		self.app=app.test_client()
		with app.app_context():
			db.create_all()


	def tearDown(self):
		with app.app_context():
			db.drop_all()
		# pass

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

	def login(self,username,password,remember_me=False):
		pass

	def register(self,firstName,lastName,email,password):
		args = {'firstName':firstName,'lastName': lastName,'email':email,'confirm':password,'password':password,'accept_tos':'true'}
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

	def test_register(self):
		firstName='Zach'
		email='zsiegel92@gmail.com'
		lastName='Siegel'
		password='masterp123'
		rv = self.register(firstName,lastName,email,password)
		assert('200' in rv.status)
		cp=self.getUser(email)
		assert(cp.authenticated==False)
		self.authenticate(email)
		cp=self.getUser(email)
		assert(cp.authenticated==True)



	def test_login_logout(self):
		pass

if __name__=='__main__':
	unittest.main()

