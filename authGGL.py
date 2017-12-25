from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string


def getUserInfo(gglSession, db):
    email = gglSession.get(
        'https://www.googleapis.com/gmail/v1/users/me/profile').json()['emailAddress']
    basic_info = gglSession.get(
        'https://www.googleapis.com/userinfo/v2/me').json()

    user = User.query.filter_by(email=email).first()
    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    else:
        if user is None:
            response = newGGLUser(email, basic_info, db, gglSession.token['access_token'])
        elif user.primary_provider != 'google':
            response = {
                'error': 'User has already authenticated with a different medium'}

        else:
            response = user.user_info_construction()

    return response


def newGGLUser(email, basic_info, db, access_token):
    rand_username = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(10))

    user = User(basic_info['given_name'], basic_info['family_name'],
                email, 'google', rand_username, basic_info['picture'])
    db.session.add(user)
    data = db.session.commit()

    connection = Connections(basic_info['given_name'], basic_info['family_name'],
                             email, 'google', basic_info['picture'], basic_info['id'], user.id, access_token)

    db.session.add(connection)
    data = db.session.commit()

    data = db.session.commit()
    if not data:
        json = user.user_info_construction()
        return json


def get_mail(gglSession):
    mail_list = gglSession.get(
        'https://www.googleapis.com/gmail/v1/users/me/messages').json()
    if 'error' in mail_list:
        mail_list = {'error': 'OAuthException'}

    return mail_list
