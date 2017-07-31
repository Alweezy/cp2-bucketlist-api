import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import db
from app.views import app
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
        self.item = {'name': 'Remember to carry a camera'}

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

            self.client().post('/api/v1/bucketlists/', data=json.dumps(self.bucketlist),
                               content_type="application/json",
                               headers={"Authorization": self.token}, )

    def test_bucketlist_item_creation(self):
        """Test API can create a bucketlist (POST request)"""
        item_res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                      content_type="application/json",
                                      headers={"Authorization": self.token}, )
        self.assertEqual(item_res.status_code, 201)
        self.assertIn('Remember to carry', str(item_res.data))

    def test_api_can_get_bucketlist_item_by_id(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        self.assertIn('Remember to carry', str(res.data))
        result = self.client().get('/api/v1/bucketlists/1/items/1', headers={
            "Authorization": self.token
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn('Remember', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/api/v1/bucketlists/1/items/1',
            data=json.dumps({
                "name": "Remember to carry a camera and batteries!"
            }),
            content_type="application/json",
            headers={"Authorization": self.token})
        self.assertEqual(res.status_code, 201)
        result = self.client().get('/api/v1/bucketlists/1/items/1', headers={
            "Authorization": self.token
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn('and batteries', str(result.data))

    def test_bucketlist_item_deletion(self):
        """Test API can delete an existing bucketlist item. (DELETE request)."""
        res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        result = self.client().delete('/api/v1/bucketlists/1/items/1', headers={
            "Authorization": self.token
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn("has been successfully deleted", str(result.data))
        # Test to see if it exists, should return a 404
        result = self.client().get('/api/v1/bucketlists/1/items/1', headers={
            "Authorization": self.token
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.data)["message"], "Bucketlist item does not exist.")

    def test_submit_request_with_invalid_credentials(self):
        """Test user issuing an invalid token. """
        res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                 content_type="application/json",
                                 headers={"Authorization": "invalid_token"}, )
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid token. Please register or login.", str(res.data))

    def test_unaivailable_bucketlist_item_request(self):
        """Test the request of a nonexistent bucketlist item. """
        res = self.client().post('/api/v1/bucketlists/1/items/', data=json.dumps(self.item),
                                 content_type="application/json",
                                 headers={"Authorization": self.token}, )
        self.assertEqual(res.status_code, 201)
        result = self.client().get('/api/v1/bucketlists/1/items/3', headers={
            "Authorization": self.token
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.data)["message"], "Bucketlist item does not exist.")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
