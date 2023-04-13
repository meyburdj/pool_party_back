import unittest
from app import app
from models import db, User, DEFAULT_USER_IMAGE_URL

class TestUserModel(unittest.TestCase):

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

    def test_signup(self):
        """Test if the signup method creates a new user."""

        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.commit()

        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, "testuser")
        self.assertEqual(users[0].email, "test@test.com")
        self.assertEqual(users[0].location, "Test City")

    def test_authenticate(self):
        """Test if the authenticate method returns the user when given correct credentials."""

        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.commit()

        auth_user = User.authenticate("testuser", "password")
        self.assertEqual(auth_user, user)

        auth_user_wrong_password = User.authenticate("testuser", "wrong_password")
        self.assertFalse(auth_user_wrong_password)

        auth_user_wrong_username = User.authenticate("wronguser", "password")
        self.assertFalse(auth_user_wrong_username)

    def test_serialize(self):
        """Test if the serialize method returns correct data."""

        user = User.signup("testuser", "test@test.com", "password", "Test City", "testimage.jpg")
        db.session.commit()

        serialized_data = user.serialize()
        expected_data = {
            "username": "testuser",
            "email": "test@test.com",
            "location": "Test City",
            "image_url": "testimage.jpg",
        }

        self.assertEqual(serialized_data, expected_data)

    def test_signup_default_image_url(self):
        """Test if the signup method assigns the default image URL when no image URL is provided."""

        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.commit()

        self.assertEqual(user.image_url, DEFAULT_USER_IMAGE_URL)

    def test_authenticate_nonexistent_user(self):
        """Test if the authenticate method returns False when the user does not exist."""

        auth_user = User.authenticate("nonexistentuser", "password")
        self.assertFalse(auth_user)



if __name__ == "__main__":
    unittest.main()
