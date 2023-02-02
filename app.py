import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Message, Pool, Availability, Reservation
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from api_helpers import upload_to_aws


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

#Setting up jwt
app.config["JWT_SECRET_KEY"] = os.environ['SECRET_KEY']
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_IDENTITY_CLAIM"] = "username"



connect_db(app)
db.create_all()

#######################  AUTH ENDPOINTS START  ################################

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.json
    username = data['username']
    password = data['password']

    user = User.authenticate(username, password)

    # username = request.json.get("username", None)
    # password = request.json.get("password", None)
    # if username != "test" or password != "test":
    #     return jsonify({"msg": "Bad username or password"}), 401

    print("user", user)
    print("username", user.username)
    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token)

@app.post("/api/auth/signup")
def create_user():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {id, email, username, image_url, location, reserved_pools, owned_pools}}
    """

    form = request.form

    file = request.files['file']

    if (file):
        url = upload_to_aws(file)

        user = User.signup(
            username=form['username'],
            password=form['password'],
            email=form['email'],
            location=form['location'],
            image_url=url
        )

        db.session.commit()

        return (jsonify(user=user.serialize()), 201)

    return (jsonify({"error": "Failed to signup"}), 424)


#######################  AUTH ENDPOINTS END  ################################


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


# // TODO: read specific user
@app.get('/api/users/<username>')
def show_user(username):
    """Show user profile.

    Returns JSON like:
        {user: id, email, username, image_url, location, reserved_pools, owned_pools}
    """
    user = User.query.get_or_404(username)
    user = user.serialize()

    return jsonify(user=user)


# // TODO: update user
@app.patch('/api/users/<username>')
@jwt_required()
def update_user(username):
    """ update user information

    Returns JSON like:
        {user: id, email, username, image_url, location, reserved_pools, owned_pools}
    """

    current_user = get_jwt_identity()
    if current_user == username:
        user = User.query.get_or_404(username)
        data = request.json

        # user.username = data['username'],
        # TODO: ADD "CHANGE PASSWORD FEATURE LATER"
        user.email = data['email'],
        user.location = data['location'],

        db.session.add(user)
        db.session.commit()

        return (jsonify(user=user.serialize()), 200)

    return (jsonify({"error": "not authorized"}), 401)



# // TODO: delete user
@app.delete('/api/users/delete/<username>')
@jwt_required()
def delete_user(username):
    """Delete user. """

    current_user = get_jwt_identity()
    if current_user == username:
        user = User.query.get_or_404(username)

        db.session.delete(user)
        db.session.commit()

        return jsonify("User successfully deleted", 200)
    return (jsonify({"error": "not authorized"}), 401)


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


# TODO: read specific pool


# create pool
@app.post("/api/pools")
@jwt_required()
def create_pool():
    """Add pool, and return data about new pool.

    Returns JSON like:
        {pool: {id, owner_id, rate, size, description, address, image_url}}
    """
    current_user = get_jwt_identity()
    if current_user:
        data = request.json
        print("data", data)
        pool = Pool(
            owner_username=current_user,
            rate=data['rate'],
            size=data['size'],
            description=data['description'],
            address=data['address']
            )

        db.session.add(pool)
        db.session.commit()

        # POST requests should return HTTP status of 201 CREATED
        return (jsonify(pool=pool.serialize()), 201)

    return (jsonify({"error": "not authorized"}), 401)


# TODO: update pool
@app.patch('/api/pools/<int:pool_id>')
@jwt_required()
def update_pool(pool_id):
    """ update pool information

    Returns JSON like:
    {pool: owner_username, rate, size, description, address}

    Authorization: must be owner of pool
    """

    current_user = get_jwt_identity()
    pool = Pool.query.get_or_404(pool_id)
    print("pool owner", pool.owner_username)
    if current_user == pool.owner_username:
        data = request.json

        pool.rate=data['rate'],
        pool.size=data['size'],
        pool.description=data['description'],
        pool.address=data['address']

        db.session.add(pool)
        db.session.commit()

        return (jsonify(pool=pool.serialize()), 200)

    return (jsonify({"error": "not authorized"}), 401)



# TODO: delete pool

@app.delete('/api/pools/<int:pool_id>')
@jwt_required()
def delete_pool(pool_id):
    """ update pool information

    Returns JSON like:
    {pool: owner_username, rate, size, description, address}

    Authorization: must be owner of pool
    """

    current_user = get_jwt_identity()
    pool = Pool.query.get_or_404(pool_id)
    if current_user == pool.owner_username:

        db.session.delete(pool)
        db.session.commit()

        return (jsonify("Pool successfully deleted"), 200)

    return (jsonify({"error": "not authorized"}), 401)


########################  POOLS ENDPOINTS END  #################################

@app.post("/api/pools/images")
def add_pool_image():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {id, email, username, image_url, location, reserved_pools, owned_pools}}
    """

    file = request.files['file']

    if file:
        url = upload_to_aws(file)

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


    ########################  POOLS ENDPOINTS END  #################################


    #######################  RESERVATIONS ENDPOINTS START  ################################

    # TODO: CREATE RESERVATION

    # TODO: READ RESERVATION

    # TODO: GET ALL RESERVATIONS

    # TODO: update reservation

    # TODO: delete reservation