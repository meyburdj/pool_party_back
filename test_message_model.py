import unittest
from app import app, db
from models import User, Message
from sqlalchemy.orm import Session

class TestMessageModel(unittest.TestCase):

    def setUp(self):
        """Set up test client."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb_test'
        app.config['TESTING'] = True
        self.client = app.test_client()

        db.drop_all()
        db.create_all()

        # Create some test users
        self.user1 = User.signup("testuser1", "test1@test.com", "password", "Test City")
        self.user2 = User.signup("testuser2", "test2@test.com", "password", "Test City")

        # Commit the users to the database
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_create_message(self):
        """Test creating a new message"""

        # Create a new message
        message = Message(
            sender_username=self.user1.username,
            recipient_username=self.user2.username,
            title="Test message",
            body="This is a test message",
            listing=1
        )

        # Commit the message to the database
        db.session.add(message)
        db.session.commit()

        # Check that the message was created correctly
        self.assertEqual(message.sender_username, self.user1.username)
        self.assertEqual(message.recipient_username, self.user2.username)
        self.assertEqual(message.title, "Test message")
        self.assertEqual(message.body, "This is a test message")
        self.assertEqual(message.listing, 1)

    def test_serialize_message(self):
        """Test serializing a message"""

        # Create a new message
        message = Message(
            sender_username=self.user1.username,
            recipient_username=self.user2.username,
            title="Test message",
            body="This is a test message",
            listing=1
        )

        # Serialize the message
        data = message.serialize()

        # Check that the serialized data is correct
        self.assertEqual(data['sender_username'], self.user1.username)
        self.assertEqual(data['recipient_username'], self.user2.username)
        self.assertEqual(data['title'], "Test message")
        self.assertEqual(data['body'], "This is a test message")
        self.assertEqual(data['listing'], 1)

    def test_create_message_no_sender(self):
        """Test creating a new message without a sender"""
        
        # Create a new message without a sender
        message = Message(
            recipient_username=self.user2.username,
            title="Test message",
            body="This is a test message",
            listing=1
        )
        
        # Ensure that a Exception is raised
        with self.assertRaises(Exception):
            db.session.add(message)
            db.session.commit()

    def test_create_message_no_recipient(self):
        """Test creating a new message without a recipient"""
        
        # Create a new message without a recipient
        message = Message(
            sender_username=self.user1.username,
            title="Test message",
            body="This is a test message",
            listing=1
        )
        
        # Ensure that a Exception is raised
        with self.assertRaises(Exception):
            db.session.add(message)
            db.session.commit()

    def test_create_message_invalid_listing(self):
        """Test creating a new message with an invalid listing"""
        
        # Create a new message with an invalid listing
        message = Message(
            sender_username=self.user1.username,
            recipient_username=self.user2.username,
            title="Test message",
            body="This is a test message",
            listing="invalid"
        )
        
        # Ensure that a Exception is raised
        with self.assertRaises(Exception):
            db.session.add(message)
            db.session.commit()

    def test_delete_message(self):
        """Test deleting a message"""
        
        # Create a new message
        message = Message(
            sender_username=self.user1.username,
            recipient_username=self.user2.username,
            title="Test message",
            body="This is a test message",
            listing=1
        )
        
        # Add the message to the database
        db.session.add(message)
        db.session.commit()
        
        # Delete the message
        db.session.delete(message)
        db.session.commit()
        
        # Ensure that the message was deleted successfully
        self.assertIsNone(db.session.get(Message, message.id))

if __name__ == "__main__":
    unittest.main()
