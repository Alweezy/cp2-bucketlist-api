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
        result = self.client().post("/auth/register/", data=json.dumps(self.user),
                                    content_type="application/json")
        results = json.loads(result.data.decode())

        self.assertEqual(results["message"],
                         'User registration successful.')
        self.assertEqual(result.status_code, 201)

    def test_duplicate_user_registration(self):
        """Test registered user registration."""
        res = self.client().post("/auth/register/", data=json.dumps(self.user),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 201)

        # Test double registration
        res_2 = self.client().post("/auth/register/",
                                   data=json.dumps(self.user),
                                   content_type="application/json")
        self.assertEqual(res_2.status_code, 409)
        final_result = json.loads(res_2.data.decode())
        self.assertEqual(final_result["message"],
                         "User already exists. Please login")

    def test_login_successful(self):
        """Test successful user login."""
        res = self.client().post("/auth/register/", data=json.dumps(self.user),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 201)

        login_res = self.client().post("/auth/login/", data=json.dumps(self.user),
                                       content_type="application/json")
        results = json.loads(login_res.data.decode())
        self.assertEqual(results["message"], "You logged in successfully.")
        # Confirm the status code and access token
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(results["token"])

    def test_unauthorised_login_attempt(self):
        """Test unauthorised login attempt."""
        res = self.client().post('/auth/login/',
                                 data=json.dumps(self.user),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 401)
        result = json.loads(res.data)
        self.assertEqual(result['message'],
                         'Invalid email or password. Please try again.')

    def test_incomplete_login_credentials(self):
        """Test partial issue of login credentials"""
        new_user = {"username": "",
                    "password": "new_password"
                    }

        res = self.client().post("/auth/register/", data=json.dumps(new_user),
                                 content_type="application/json")
        final_result = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 400)
        self.assertEqual(final_result["message"],
                         "Error. The username or password cannot be empty")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
