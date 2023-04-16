import unittest
import json
from app import app
from models import db, User
from sqlalchemy.exc import IntegrityError

class TestAuthViews(unittest.TestCase):

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

    def test_create_user(self):
        """Test if the signup endpoint creates a new user and returns a token."""

        response = self.client.post(
            "/api/auth/signup",
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password": "password",
                "location": "Test City"
            }
        )

        json_response = json.loads(response.data)
        self.assertIn("token", json_response)

        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, "testuser")
        self.assertEqual(users[0].email, "test@test.com")
        self.assertEqual(users[0].location, "Test City")

    def test_create_user_existing_username(self):
        """Test if the signup endpoint returns an error when the username already exists."""

        existing_user = User.signup("testuser", "existing@test.com", "password", "Test City")
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post(
            "/api/auth/signup",
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password": "password",
                "location": "Test City"
            }
        )

        json_response = json.loads(response.data)
        self.assertEqual(response.status_code, 424)
        self.assertIn("error", json_response)
        db.session.rollback()  

def test_login_successful(self):
    """Test if the login endpoint authenticates a user and returns a token."""

    # Create a test user
    user = User.signup("testuser", "test@test.com", "password", "Test City")
    db.session.add(user)
    db.session.commit()

    response = self.client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "password"
        }
    )

    json_response = json.loads(response.data)
    self.assertEqual(response.status_code, 200)
    self.assertIn("token", json_response)

def test_login_failed(self):
    """Test if the login endpoint returns an error for incorrect credentials."""

    # Create a test user
    user = User.signup("testuser", "test@test.com", "password", "Test City")
    db.session.add(user)
    db.session.commit()

    response = self.client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrong_password"
        }
    )

    json_response = json.loads(response.data)
    self.assertEqual(response.status_code, 401)
    self.assertIn("error", json_response)
    self.assertEqual(json_response["error"], "Invalid credentials")


    

if __name__ == "__main__":
    unittest.main()
