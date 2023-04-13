import unittest
from app import app
from models import db, User, Pool

class TestPoolModel(unittest.TestCase):

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

    def create_test_user(self):
        user = User.signup("testuser", "test@test.com", "password", "Test City")
        db.session.add(user)
        db.session.commit()
        return user

    def create_test_pool(self, user):
        pool = Pool(owner_username=user.username,
                    rate=100.00,
                    size="Medium",
                    description="A lovely pool",
                    city="Test City",
                    orig_image_url="test_orig_image.jpg",
                    small_image_url="test_small_image.jpg")
        db.session.add(pool)
        db.session.commit()
        return pool

    def test_create_pool(self):
        """Test if a new pool is created."""
        user = self.create_test_user()
        pool = self.create_test_pool(user)

        pools = Pool.query.all()
        self.assertEqual(len(pools), 1)
        self.assertEqual(pools[0].owner_username, "testuser")
        self.assertEqual(pools[0].rate, 100.00)
        self.assertEqual(pools[0].size, "Medium")
        self.assertEqual(pools[0].description, "A lovely pool")
        self.assertEqual(pools[0].city, "Test City")
        self.assertEqual(pools[0].orig_image_url, "test_orig_image.jpg")
        self.assertEqual(pools[0].small_image_url, "test_small_image.jpg")

    def test_serialize(self):
        """Test if the serialize method returns correct data."""
        user = self.create_test_user()
        pool = self.create_test_pool(user)

        serialized_data = pool.serialize()
        expected_data = {
            "id": pool.id,
            "owner_username": "testuser",
            "rate": 100.00,
            "size": "Medium",
            "description": "A lovely pool",
            "city": "Test City",
            "orig_image_url": "test_orig_image.jpg",
            "small_image_url": "test_small_image.jpg"
        }

        self.assertEqual(serialized_data, expected_data)

if __name__ == "__main__":
    unittest.main()
