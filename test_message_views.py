import unittest
import json
from app import app
from models import db, User, Message
from flask_jwt_extended import create_access_token

class MessagesViewsTestCase(unittest.TestCase):
    """Main class for message views testing"""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///sharebnb_test"
        self.client = app.test_client()

        db.create_all()

        # Add users
        user1 = User(username="user1", email="user1@example.com", password="password")
        user2 = User(username="user2", email="user2@example.com", password="password")
        user3 = User(username="user3", email="user3@example.com", password="password")
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        # Add messages
        message1 = Message(sender_username="user1", recipient_username="user2", title="Test Message", body="This is a test message.", listing=1)
        db.session.add(message1)

        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        response = self.client.post(
            "/api/auth/login",
            data=json.dumps({"username": username, "password": password}),
            content_type="application/json",
        )
        return response

    def test_list_messages(self):
        access_token1 = create_access_token(identity="user1")
        headers = {"Authorization": f"Bearer {access_token1}"}

        response = self.client.get("/api/messages", headers=headers)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("messages" in data)
        self.assertTrue("inbox" in data["messages"])
        self.assertTrue("outbox" in data["messages"])

    def test_create_message(self):
        access_token1 = create_access_token(identity="user1")
        headers = {"Authorization": f"Bearer {access_token1}"}

        message_data = {
            "recipient_username": "user2",
            "title": "New Message",
            "body": "This is a new message.",
            "listing": 2
        }

        response = self.client.post(
            "/api/messages",
            data=json.dumps(message_data),
            content_type="application/json",
            headers=headers,
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue("message" in data)

    def test_show_message(self):
        access_token1 = create_access_token(identity="user1")
        headers = {"Authorization": f"Bearer {access_token1}"}

        response = self.client.get("/api/messages/1", headers=headers)
        print("response", response, response.data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("message" in data)

    def test_show_message_unauthorized(self):
        access_token3 = create_access_token(identity="user3")
        headers = {"Authorization": f"Bearer {access_token3}"}

        response = self.client.get("/api/messages/1", headers=headers)
        data = json.loads(response.data)

        print("response.data =", response.data)
        self.assertEqual(response.status_code, 401)
        self.assertTrue("error" in data)

if __name__ == "__main__":
    unittest.main()
