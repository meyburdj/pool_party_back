import os
from unittest import TestCase
from app import app
from models import db, User, Message, connect_db

os.environ['TEST_DATABASE_URL'] = "postgresql:///pool_party_test"

connect_db(app)

class UserViewTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        # Add some sample data
        # ...

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_login(self):
        # Your test code here

    def test_signup(self):
        # Your test code here
