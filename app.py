import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Message, Pool, Availability, Reservation
from sqlalchemy.exc import IntegrityError
import boto3


load_dotenv()

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['aws_access_key_id'] = os.environ['aws_access_key_id']
app.config['aws_secret_access_key'] = os.environ['aws_secret_access_key']
app.config['aws_session_token'] = os.environ['aws_session_token']


s3 = boto3.client('s3',
                    aws_access_key_id,
                    aws_secret_access_key,
                    aws_session_token
                     )
BUCKET_NAME='sharebnb-gmm'

connect_db(app)
db.create_all()

#######################  USERS ENDPOINTS START  ################################

@app.get("/api/users")
def list_users():
    """Return all users in system.

    Returns JSON like:
        {users: [{id, email, username, image_url, location, reserved_pools, owned_pools}, ...]}
    """
    users = User.query.all()

    serialized = [user.serialize() for user in users]

    return jsonify(users=serialized)

@app.post("/api/users")
def create_user():
    """Add cupcake, and return data about new cupcake.

    Returns JSON like:
        {cupcake: [{id, flavor, rating, size, image}]}
    """

    data = request.json
    print("data", data)
    user = User(
        email=data['email'],
        username=data['username'],
        password=data['password'],
        location=data['location'],
        image_url=data['image_url'] or None)

    db.session.add(user)
    db.session.commit()

    # POST requests should return HTTP status of 201 CREATED
    return (jsonify(user=user.serialize()), 201)


########################  USERS ENDPOINTS END  #################################
