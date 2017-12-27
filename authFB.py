from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from time import time

def getUserInfo(facebook, db):

    basic_info = facebook.get(
        'https://graph.facebook.com/v2.11/me?fields=email,first_name,last_name,id,link,verified').json()

    user_pic = facebook.get(
        'https://graph.facebook.com/v2.11/me/picture?redirect=false').json()

    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    elif not basic_info['verified']:
        response = {'error': 'User not verified'}
    else:

        user = User.query.filter_by(email=basic_info['email']).first()
        #If there isn't such email already saved in the db make a new user
        if user is None:
            response = newFbUser(basic_info, user_pic, db,
                                 facebook.token)
        #if there is already that email and the primary provider isn't facebook then he should connect with the medium he has authenticated the first time
        elif user.primary_provider != 'facebook':
            response = {
                'error': 'User has already authenticated with a different medium'}
        #if there is that user correct just send back the user info he needs
        else:
            newUser = updatedFbUser(basic_info, user_pic, db, facebook.token, user)

            response = newUser.user_info_construction()
    return response


def newFbUser(basic_info, user_pic, db, access_token):
    import json

    rand_username = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(10))
    user = User(basic_info['first_name'], basic_info['last_name'],
                basic_info['email'], 'facebook', rand_username, user_pic['data']['url'])
    db.session.add(user)
    data = db.session.commit()
    connection = Connections(basic_info['first_name'], basic_info['last_name'],
                             basic_info['email'], 'facebook', user_pic['data']['url'], basic_info['id'], user.id, json.dumps(access_token))

    db.session.add(connection)
    data = db.session.commit()
    if not data:
        json = user.user_info_construction()

        return json

def updatedFbUser(basic_info, user_pic, db, access_token, user):
    user.firstname= basic_info['first_name']
    user.lastname = basic_info['last_name']
    user.email = basic_info['email']
    user.photo_url = user_pic['data']['url']

    db.session.commit()

    user_account = Connections.query.filter_by(user_id = user.id).first()
    user_account.firstname= basic_info['first_name']
    user_account.lastname = basic_info['last_name']
    user_account.email = basic_info['email']
    user_account.photo_url = user_pic['data']['url']
    user_account.access_token = json.dumps(access_token)

    db.session.commit()
    return user

def refresh_Token(user):
    fbCreds = json.load(open('FBclient_secret.json'))
    user_account = Connections.query.filter_by(user_id= user.id).first()
    old_token = json.loads(user_account.access_token)
    old_token['expires_at'] = time() - 10
    print(json.dumps(old_token), sys.stderr)
    extras = {
    'client_id': fbCreds['client_id'],
    'client_secret': fbCreds['client_secret']
    }
    facebook = OAuth2Session(fbCreds['client_id'] , auto_refresh_kwargs= extras, auto_refresh_url= fbCreds['token_uri'] )
    facebook.token = old_token


    facebook = facebook_compliance_fix(facebook)
    data = facebook.get('https://graph.facebook.com/v2.11/me').json()
    token = data.token
    print(token, sys.stderr)


