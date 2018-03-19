import sys
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, get_raw_jwt
)
from app import app, db
from app.models import Candidate, AuthToken
import uuid


def authenticate(email, password):
    user = Candidate.query.filter_by(email=email)
    if user is not None and user.check_password(password):
        return user


def identity(payload):
  print(payload)
  user_id = payload['identity']
  return Candidate.query.filter_by(user_id, None)


@app.route('/')
@app.route('/index')
def index():
    return 'Hello, world!'


@app.route('/register', methods=['POST'])
def register():
    print("Posted to /register")
    data = request.get_json()
    #Check if email is already in use
    check_candidate = Candidate.query.filter_by(email=data['email'])
    if(check_candidate is not None):
      return jsonify({'status': 'Failure', 'error': 'Email is already in use. Please use another'})
    candidate = Candidate(candidate_id=uuid.uuid4().hex,
                          username=data['username'],
                          email=data['email'],
                          first_name=data['first_name'],
                          middle_name=data['middle_name'],
                          last_name=data['last_name'])
    candidate.set_password(data['password'])
    try:
      db.session.add(candidate)
      db.session.commit()
      return jsonify({'status': 'Success'})
    except:
      print('Unexpected error:', sys.exc_info()[0])
      return jsonify({'status': 'Failure', 'error': 'Unknown error - please try again later'})


jwt = JWTManager(app)


# By default, the CRSF cookies will be called csrf_access_token and
# csrf_refresh_token, and in protected endpoints we will look for the
# CSRF token in the 'X-CSRF-TOKEN' header. You can modify all of these
# with various app.config options. Check the options page for details.


# With JWT_COOKIE_CSRF_PROTECT set to True, set_access_cookies() and
# set_refresh_cookies() will now also set the non-httponly CSRF cookies
# as well
@app.route('/token/auth', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    Candidate.query.filter_by(email=email)

    check_candidate = Candidate.query.filter_by(email=email).first()
    if check_candidate is None or not check_candidate.check_password(password):
        return jsonify({'login': False}), 401

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    auth_token = AuthToken(jti=access_token.get_jti(), revoked=False)
    refresh_auth_token = AuthToken(jti=refresh_token.get_jti(), revoked=False)
    db.session.add(auth_token)
    db.session.add(refresh_auth_token)
    db.session.commit()

    # Set the JWTs and the CSRF double submit protection cookies
    # in this response
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the access JWT and CSRF double submit protection cookies
    # in this response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@jwt.token_in_blacklist_loader
def check_token_against_blacklist(decrypted_token):
  jti = decrypted_token['jti']
  token = AuthToken.query.filter_by(jti=jti)
  if(token is None or token.revoked == True):
    return True
  else:
    return False

# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@app.route('/token/remove', methods=['POST'])
@jwt_required
def logout():
  jti = get_raw_jwt()['jti']



  resp = jsonify({'logout': True})
  unset_jwt_cookies(resp)
  return resp, 200


@app.route('/api/example', methods=['GET'])
@jwt_required
def protected():
    email = get_jwt_identity()
    return jsonify({'hello': 'from {}'.format(email)}), 200