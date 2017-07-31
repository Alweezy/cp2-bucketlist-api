import unittest
import json

from app import db
from app.app import app
from instance.config import app_config


class BucketListTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        app.config.from_object(app_config["testing"])
        app.config.from_pyfile('config.py')
        self.app = app
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go Skiing in the Himalayas'}
        self.bucketlist2 = {'name': 'Attend a BBQ at the Dojo'}
        self.item = {'name': 'Remember to cary a camera'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

            self.user_info = {
                "username": "nerd",
                "password": "nerdy",
                "email": "nerd@tests.com"
            }
            self.client().post("/auth/register/", data=json.dumps(self.user_info),
                               content_type="application/json")
            self.login_info = {
                "username": "nerd",
                "password": "nerdy",
            }
            self.login_result = self.client().post("/auth/login/",
                                                   data=json.dumps(self.login_info),
                                                   content_type="application/json")
            self.token = json.loads(self.login_result.data.decode())['token']

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist (POST request)"""
        res = self.client().post('/api/v1/bucketlists/', data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go Skiing', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/', headers={
            "Authorization": self.token
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go Skiing', str(res.data))

    def test_api_no_bucketlists(self):
        """Test output for user with no bucketlists."""
        res = self.client().get('/api/v1/bucketlists/', headers={
            "Authorization": self.token
        })
        # results = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        res = self.client().get(
            '/api/v1/bucketlists/{}'.format(res_in_json['id']),
            content_type="application/json",
            headers={"Authorization": self.token}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go Skiing', str(res.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist2),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/api/v1/bucketlists/1',
            data=json.dumps({
                "name": "Attend a BBQ at the Dojo and have some booze!"
            }),
            content_type="application/json",
            headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/1',
                                content_type="application/json",
                                headers={"Authorization": self.token})
        self.assertIn('and have some booze!', str(res.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        res = self.client().post('/api/v1/bucketlists/', data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        # res = self.client().delete('/api/v1/bucketlists/1')
        res = self.client().delete('/api/v1/bucketlists/1',
                                   content_type="application/json",
                                   headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 200)
        # # Test to see if it exists, should return a 404
        res = self.client().get('/api/v1/bucketlists/1',
                                content_type="application/json",
                                headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)["message"], "Bucketlist does not exist.")

    def test_submit_request_with_invalid_credentials(self):
        """Test user issuing an invalid token. """
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": "invalid_token"
                                 })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid token. Please register or login.", str(res.data))

    def test_unaivailable_bucketlist_request(self):
        """Test the request of a nonexistent bucketlist. """
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json", headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/3',
                                content_type="application/json",
                                headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)

    def test_pagination_successful(self):
        """Test the API pagination works fine"""
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json", headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        result = self.client().get('/api/v1/bucketlists/?limit=20',
                                   headers={"Authorization": self.token})
        json_results = json.loads(result.data.decode("utf-8").
                                  replace("'", "\""))
        self.assertEqual(result.status_code, 200)
        self.assertIn("next_page", str(result.data))
        self.assertIn("previous_page", str(result.data))
        self.assertIn("Go Skiing", str(result.data))
        self.assertTrue(json_results["bucketlists"])

    def test_pagination_invalid_credentials(self):
        """Test API pagination fails with invalid credentials."""
        result = self.client().get('/api/v1/bucketlists/?limit=20')
        self.assertEqual(result.status_code, 401)
        self.assertIn("Register or log in to access this resource",
                      str(result.data))

    def test_bucketlist_search_successful(self):
        """Test API search executes successfully."""
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json", headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/?q=Go',
                                content_type="application/json",
                                headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go Skiing', str(res.data))

    def test_bucketlist_search_invalid_credentials(self):
        res = self.client().post('/api/v1/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json", headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/bucketlists/?q=Go',
                                content_type="application/json",
                                headers={"Authorization": "invalid_token"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid token. Please register or login.",
                      str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
