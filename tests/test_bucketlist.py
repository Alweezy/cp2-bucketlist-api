import os
import unittest
import json

from app import create_app, db
from app.models import User


class BucketListTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go Skiing in the Himalayas'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

            self.user = {
                "username": "nerd",
                "password": "nerdy",
                "email": "nerd@tests.com"
            }
            self.dummy_user = User(self.user["username"],
                                   self.user["password"],
                                   self.user["email"]
                                   )
            self.token = self.dummy_user.generate_auth_token(self.dummy_user.id)

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist (POST request)"""
        res = self.client().post('/bucketlists/', data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go Skiing', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().post('/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/bucketlists/', headers={
            "Authorization": self.token
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go Skiing', str(res.data))

    def test_api_no_bucketlists(self):
        """Test output for user with no bucketlists."""
        res = self.client().get('/bucketlists/', headers={
            "Authorization": self.token
        })
        # results = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_api_can_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        res = self.client().post('/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": self.token
                                 })
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/bucketlists/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go Skiing', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        res = self.client().post(
            '/bucketlists/',
            data={'name': 'Attend BBQ at the Dojo'})
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/bucketlists/1',
            data={
                "name": "Attend a BBQ at the Dojo and have some booze!"
            })
        self.assertEqual(res.status_code, 200)
        results = self.client().get('/bucketlists/1')
        self.assertIn('and have some booze', str(results.data))

    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. (DELETE request)."""
        res = self.client().post(
            '/bucketlists/',
            data={'name': 'Attend BBQ at the Dojo'})
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/bucketlists/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        res = self.client().get('/bucketlists/1')
        self.assertEqual(res.status_code, 404)

    def test_submit_request_with_invalid_credentials(self):
        """Test user issuing an invalid token. """
        res = self.client().post('/bucketlists/',
                                 data=json.dumps(self.bucketlist),
                                 content_type="application/json",
                                 headers={
                                    "Authorization": "invalid_token"
                                 })
        self.assertEqual(res.status_code, 201)
        self.assertIn("Invalid token issued, register or log in ", str(res.data))

    def test_unaivailable_bucketlist_request(self):
        """Test the request of a nonexistent bucketlist. """
        res = self.client().post('/bucketlists/',
                               data=json.dumps(self.bucketlist),
                               content_type="application/json", headers={
                                    "Authorization": self.token
                                })
        self.assertEqual(res.status_code, 201)
        response = self.client().get(
            "/bucketlists/3", headers={
                "Authorization": self.token})
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual(result["message"],
                         "No bucketlist with such an id.")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
