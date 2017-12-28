from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string


def getUserInfo(twitter, db, tokens):

    basic_info = twitter.get(
        'https://api.twitter.com/1.1/account/verify_credentials.json').json()

    print(json.dumps(basic_info), sys.stderr)

    # user_pic = twitter.get(
    #     'https://graph.facebook.com/v2.11/me/picture?redirect=false').json()

    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    else:

        user = User.query.filter_by(username=basic_info['id_str']).first()
        #Because i dont have access to the email of the user i search for the username WHERE i will store the twitter user id
        if user is None:
            response = newTwitterUser(basic_info, db,
                                      tokens)
        #if there is already that email and the primary provider isn't facebook then he should connect with the medium he has authenticated the first time
        elif user.primary_provider != 'twitter':
            response = {
                'error': 'User has already authenticated with a different medium'}
        #if there is that user correct just send back the user info he needs
        else:
            newUser = updatedTwitterUser(basic_info, db, tokens, user)
            response = newUser.token_construction()
    return response


def newTwitterUser(basic_info, db, tokens):
    import json
    name_lst = basic_info['name'].split(' ')
    first_name = name_lst[0]
    last_name = name_lst[1]

    user = User(first_name, last_name,
                basic_info['id_str'] + '@twit.com', 'twitter', basic_info['id_str'], basic_info['profile_image_url_https'])
    db.session.add(user)
    data = db.session.commit()

    connection = Connections(first_name, last_name,
                             basic_info['id_str'] + '@twit.com', 'twitter',  basic_info['profile_image_url_https'], basic_info['id_str'], user.id, json.dumps(tokens))

    db.session.add(connection)
    data = db.session.commit()
    if not data:
        json = user.token_construction()

        return json

def updatedTwitterUser(basic_info, db, token, user):
    name_lst = basic_info['name'].split(' ')
    first_name = name_lst[0]
    last_name = name_lst[1]

    user.firstname= first_name
    user.lastname = last_name
    user.photo_url = basic_info['profile_image_url_https']

    db.session.commit()

    user_account = Connections.query.filter_by(user_id = user.id).first()
    user_account.firstname=  first_name
    user_account.lastname = last_name
    user_account.photo_url = basic_info['profile_image_url_https']
    user_account.access_token = json.dumps(token)

    db.session.commit()
    return user