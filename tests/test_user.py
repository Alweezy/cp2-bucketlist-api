import unittest
import json

from app import create_app, db


class UserTest(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()
            self.user = {"username": "nerd",
                         "password": "nerdy",
                         "email": "nerd@tests.com "
                         }

    def test_registration_successful(self):
        """Test successful user registration."""
        response = self.client.post("auth/register",
                                    data=json.dumps(self.user),
                                    content_type="application/json")
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["message"],
                         'User registration successful.')
        self.assertEqual(result['username'],
                         self.user['username'])

    def test_duplicate_user_registration(self):
        """Test registered user registration."""
        resp = self.client().post('/auth/register/',
                                  data=json.dumps(self.user),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        res = self.client().post('/auth/register/',
                                 data=json.dumps(self.user),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 409)
        result = json.loads(res.data)
        self.assertEqual(result['message'],
                         "User with the username already exists.")

    def test_login_successful(self):
        """Test successful user login."""
        resp = self.client().post('/auth/register/',
                                  data=json.dumps(self.user),
                                  content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        res = self.client().post('/auth/login/',
                                 data=json.dumps(self.user),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 200)
        result = json.loads(res.data)
        self.assertEqual(result['message'],
                         "Login successful.")

    def test_unauthorised_login_attempt(self):
        """Test unauthorised login attempt."""
        res = self.client().post('/auth/login/',
                                 data=json.dumps(self.user),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 401)
        result = json.loads(res.data)
        self.assertEqual(result['message'],
                         "Invalid username/password.")

    def test_incomplete_login_credentials(self):
        """Test partial issue of login credentials"""
        res = self.client().post('/auth/login/',
                                 data=json.dumps({"username": "nerd"}),
                                 content_type="application/json")
        result = json.loads(res.data)
        self.assertEqual(result['error'],
                         "missing data in request.")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
