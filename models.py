"""SQLAlchemy models for ShareBNB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO: USER DEFAULT IMAGE URL
DEFAULT_USER_IMAGE_URL = ""
# TODO: POOL DEFAULT IMAGE URL
DEFAULT_POOL_IMAGE_URL = ""

# USERS
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default=DEFAULT_USER_IMAGE_URL,
    )


    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    reserved_pools = db.relationship(
        'Pools',
        secondary='owner',
        backref='booker'
    )

    owned_pools = db.relationship(
        'Pools',
        secondary='booker',
        backref='owner'
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "email" : self.email,
            "username" : self.username,
            "image_url" : self.image_url,
            "location" : self.location,
            "password" : self.password,
            "reserved_pools" : self.reserved_pools,
            "owned_pools" : self.owned_pools
        }


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url=DEFAULT_USER_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


# Messages
class Message(db.Model):
    "Messages between users in the system"

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # userid to
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # userid from
    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    # text
    text = db.Column(
        db.Text,
        nullable=False,
    )

    # timestamp
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "user_id_to" : self.user_id_to,
            "user_id_from" : self.user_id_from,
            "text" : self.text,
            "timestamp" : self.timestamp
        }


# POOLS

class Pool(db.Model):
    """ Pool in the system """

    __tablename__ = 'pools'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    rate = db.Column(
        db.Number,
        nullable=False
    )

    size = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default=DEFAULT_POOL_IMAGE_URL,
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "user_id" : self.user_id,
            "rate" : self.rate,
            "size" : self.size,
            "description" : self.description,
            "address" : self.address,
            "image_url" : self.image_url,
        }


class Availability(db.Model):
    """ Connection of a pool to its available dates """

    id = db.Column(
        db.Integer,
        nullable=False,
        primary_key=True
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
    )

    pool_id = db.Column(
        db.Integer,
        db.ForeignKey("pools.id", ondelete="CASCADE"),
    )


class Reservation(db.Model):
    """ Connection of a User and Pool that they reserve """

    __tablename__ = "reservations"


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    pool_id = db.Column(
        db.Integer,
        db.ForeignKey("pools.id", ondelete="CASCADE"),
        primary_key=True
    )
    date = db.Column(
        db.DateTime,
        nullable=False,
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "user_id" : self.user_id,
            "pool_id" : self.pool_id,
            "date" : self.date,
        }



# db
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)