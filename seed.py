# noinspection PyUnresolvedReferences
from app import db
from models import User

db.drop_all()
db.create_all()

user1 = User(
    email="test1@email.com",
    username="test1",
    password="pasword",
    location="testlocation1",
)

user2 = User(
    email="test2@email.com",
    username="test2",
    password="password2",
    location="testlocation2",
)


db.session.add_all([user1, user2])
db.session.commit()

