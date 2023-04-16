import unittest
import json
from app import app
from models import db, User, Pool
from flask_jwt_extended import create_access_token



class PoolViewsTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb_test'
        app.config['TESTING'] = True
        self.client = app.test_client()

        db.drop_all()
        db.create_all()

        # Add a test user and a test pool here
        user = User.signup("testuser", "test@example.com", "testpassword", "Test City")
        db.session.add(user)
        db.session.commit()

        pool = Pool(owner_username="testuser", rate=100, size="1000 sqft", description="Test pool", city="Test City",
                    orig_image_url="https://example.com/orig_image.jpg", small_image_url="https://example.com/small_image.jpg")
        db.session.add(pool)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_list_pools(self):
        response = self.client.get("/api/pools")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("pools" in data)

    def test_show_pool_by_id(self):
        # Replace 1 with the test pool ID if needed
        response = self.client.get("/api/pools/1")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("pool" in data)

    def test_show_pool_by_city(self):
        response = self.client.get("/api/pools/Test%20City")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("pools" in data)

    def login(self, username, password):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({"username": username, "password": password}),
            content_type="application/json",
        )
        return response

    # def get_jwt_token(self, username):
    #     access_token = create_access_token(identity=username)
    #     return access_token

    def test_create_pool(self):
        user2 = User.signup("testuser2", "test2@test.com", "password", "Test City2")
        db.session.add(user2)
        db.session.commit()

        with self.client as client:
            access_token2 = create_access_token(identity="testuser2")
            headers = {"Authorization": f"Bearer {access_token2}"}
            response = client.post(
                "/api/pools",
                data={
                    "rate": 200,
                    "size": "2000 sqft",
                    "description": "Test pool 2",
                    "city": "Test City 2"
                },
                headers=headers,
            )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue("pool" in data)


        
    def test_update_pool(self):
        access_token = create_access_token(identity="testuser")
        headers = {"Authorization": f"Bearer {access_token}"}

        response = self.client.patch(
            "/api/pools/1",
            data=json.dumps({
                "rate": 150,
                "size": "1500 sqft",
                "description": "Updated test pool",
                "address": "Updated test address"
            }),
            content_type="application/json",
            headers=headers,
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("pool" in data)

    def test_delete_pool(self):
        access_token = create_access_token(identity="testuser")
        headers = {"Authorization": f"Bearer {access_token}"}

        response = self.client.delete(
            "/api/pools/1",
            headers=headers,
        )

        self.assertEqual(response.status_code, 200)
if __name__ == "__main__":
    unittest.main()
