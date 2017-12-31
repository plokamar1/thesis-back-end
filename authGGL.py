from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string


def getUserInfo(gglSession, db, old_user):
    email = gglSession.get(
        'https://www.googleapis.com/gmail/v1/users/me/profile').json()['emailAddress']
    basic_info = gglSession.get(
        'https://www.googleapis.com/userinfo/v2/me').json()

    #print(basic_info.json()['family_name'], sys.stderr)
    user = User.query.filter_by(email=email).first()
    if old_user:
        exists = Connections.query.filter_by(email=email, provider = 'google').first()
        if not exists:
            newConnection(email, basic_info, db, gglSession.token, old_user)
            response = old_user.token_construction()
            return response
        else:
            response = {'error': 'Already connected account!'}
            return response
        
    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    else:
        if user is None:
            response = newGGLUser(email, basic_info, db, gglSession.token)
        elif user.primary_provider != 'google':
            response = {
                'error': 'User has already authenticated with a different medium'}

        else:
            newUser = updatedGGLUser(email, basic_info, db, gglSession.token , user)
            response = newUser.token_construction()

    return response

def newConnection(email, basic_info, db, access_token, user):

    connection = Connections(basic_info['given_name'], basic_info['family_name'],
                             email, 'google', basic_info['picture'], basic_info['id'], user.id, json.dumps(access_token))

    db.session.add(connection)
    data = db.session.commit()
    if data:
        return False
    else:
        return True

def newGGLUser(email, basic_info, db, access_token):
    import json

    rand_username = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(10))

    user = User(basic_info['given_name'], basic_info['family_name'],
                email, 'google', rand_username, basic_info['picture'])
    db.session.add(user)
    data = db.session.commit()

    newConnection(email, basic_info, db, access_token, user)


    json = user.token_construction()
    return json

def updatedGGLUser(email, basic_info, db, access_token, user):
    user.firstname= basic_info['given_name']
    user.lastname = basic_info['family_name']
    user.email = email
    user.photo_url = basic_info['picture']

    db.session.commit()

    user_account = Connections.query.filter_by(user_id = user.id).first()
    user_account.firstname= basic_info['given_name']
    user_account.lastname = basic_info['family_name']
    user_account.email = email
    user_account.photo_url = basic_info['picture']
    user_account.access_token = json.dumps(access_token)

    db.session.commit()
    return user

def get_mail(gglSession):
    mail_list = gglSession.get(
        'https://www.googleapis.com/gmail/v1/users/me/messages').json()
    if 'error' in mail_list:
        mail_list = {'error': 'OAuthException'}

    return mail_list
