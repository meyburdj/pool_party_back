import unittest
import json
from app import app
from models import db, User, Pool
from flask_jwt_extended import create_access_token

class TestUsersViews(unittest.TestCase):

    def setUp(self):
        """Set up test client."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb_test'
        app.config['TESTING'] = True
        self.client = app.test_client()

        db.drop_all()
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_list_users(self):
        """Test the list_users route."""
        # Create test users
        user1 = User.signup("testuser1", "test1@test.com", "password", "Test City")
        user2 = User.signup("testuser2", "test2@test.com", "password", "Test City")

        db.session.add_all([user1, user2])
        db.session.commit()

        response = self.client.get("/api/users")
        json_response = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("users", json_response)
        self.assertEqual(len(json_response["users"]), 2)

    def test_show_user(self):
            """Test the show_user route."""
            user = User.signup("testuser", "test@test.com", "password", "Test City")
            db.session.add(user)
            db.session.commit()

            response = self.client.get("/api/users/testuser")
            json_response = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertIn("user", json_response)
            self.assertEqual(json_response["user"]["username"], "testuser")

    def test_update_user(self):
        """Test the update_user route."""
        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.add(user)
        db.session.commit()

        with self.client as client:
            access_token = create_access_token(identity="testuser")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.patch(
                "/api/users/testuser",
                json={"email": "updated@test.com", "location": "Updated City"},
                headers=headers,
            )

        json_response = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("user", json_response)
        self.assertEqual(json_response["user"]["email"], "updated@test.com")

    def test_delete_user(self):
        """Test the delete_user route."""
        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.add(user)
        db.session.commit()

        with self.client as client:
            access_token = create_access_token(identity="testuser")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.delete("/api/users/delete/testuser", headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_list_pools_of_user(self):
        """Test the list_pools_of_user route."""
        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.add(user)
        db.session.commit()
        pool = Pool(owner_username='testuser',
                    rate=100.00,
                    size="Medium",
                    description="A lovely pool",
                    city="Test City",
                    orig_image_url="test_orig_image.jpg",
                    small_image_url="test_small_image.jpg")
              
        db.session.add(pool)
        db.session.commit()

        response = self.client.get("/api/users/testuser/pools")
        json_response = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("pools", json_response)
        self.assertEqual(len(json_response["pools"]), 1)
        self.assertEqual(json_response["pools"][0]["owner_username"], "testuser")
if __name__ == "__main__":
    unittest.main()

