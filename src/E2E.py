from utils import modified_environ
import unittest
import json

with modified_environ(APP_SETTINGS='config.TestingConfig'):
	from app import app, db,models


class AppTestCase(unittest.TestCase):
	def setUp(self):
		self.app=app.test_client()
		with app.app_context():
			db.create_all()


	def tearDown(self):
		with app.app_context():
			db.drop_all()
		# pass

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
		print("api/register called")
		rv= self.app.post('/api/register',data=args,follow_redirects=True,content_type='application/x-www-form-urlencoded')
		print("/api/register returned")
		return rv

	def test_register(self):
		rv = self.register('Zach','Siegel','zsiegel92@gmail.com','masterp123')
		assert('200' in rv.status)


	def test_login_logout(self):
		pass

if __name__=='__main__':
	unittest.main()

