import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Message, Pool, Availability, Reservation
from sqlalchemy.exc import IntegrityError
import boto3
from werkzeug.utils import secure_filename
from slugify import slugify

load_dotenv()

app = Flask(__name__)
bucket_base_url = "https://sharebnb-gmm.s3.us-west-1.amazonaws.com/"

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']
# app.config['aws_session_token'] = os.environ['aws_session_token']


s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
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
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {id, email, username, image_url, location, reserved_pools, owned_pools}}
    """

    data = request.json
    print("data", data)

    img = data['image_url']
    if data['image_url']:
        filename = secure_filename(img.filename)
        print("filename", filename)
        img.save(filename)
        res = s3.upload_file(
            Bucket = BUCKET_NAME,
            Filename=filename,
            Key = filename
        )
        


    # user = User(
    #     email=data['email'],
    #     username=data['username'],
    #     password=data['password'],
    #     location=data['location'],
    #     image_url=data['image_url'] or None)



    # db.session.add(user)
    # db.session.commit()

    # POST requests should return HTTP status of 201 CREATED
    return (res)


########################  USERS ENDPOINTS END  #################################




#######################  POOLS ENDPOINTS START  ################################

@app.get("/api/pools")
def list_pools():
    """Return all pools in system.

    Returns JSON like:
        {pools: {id, owner_id, rate, size, description, address, image_url}, ...}
    """
    pools = Pool.query.all()

    serialized = [pool.serialize() for pool in pools]

    return jsonify(pools=serialized)

@app.post("/api/pools")
def create_pool():
    """Add pool, and return data about new pool.

    Returns JSON like:
        {pool: {id, owner_id, rate, size, description, address, image_url}}
    """

    data = request.json
    print("data", data)
    pool = Pool(
        owner_id=data['owner_id'],
        rate=data['rate'],
        size=data['size'],
        description=data['description'],
        address=data['address'],
        image_url=data['image_url'],
        )

    db.session.add(pool)
    db.session.commit()

    # POST requests should return HTTP status of 201 CREATED
    return (jsonify(pool=pool.serialize()), 201)


########################  USERS ENDPOINTS END  #################################

@app.post("/api/pools/images")
def add_pool_image():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {id, email, username, image_url, location, reserved_pools, owned_pools}}
    """

    file = request.files['file']
    print("file.filename", file.filename)
    if file:
        filename = secure_filename(file.filename)
        file.save(filename)
        s3.upload_file(
            Bucket = BUCKET_NAME,
            Filename=filename,
            ExtraArgs={"ContentType": "mimetype"},
            Key = filename
        )
        url = f"{bucket_base_url}{filename}"

        return url


    # user = User(
    #     email=data['email'],
    #     username=data['username'],
    #     password=data['password'],
    #     location=data['location'],
    #     image_url=data['image_url'] or None)



    # db.session.add(user)
    # db.session.commit()

    # # POST requests should return HTTP status of 201 CREATED
    # return (jsonify(user=user.serialize()), 201)