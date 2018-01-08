from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string
from requests_oauthlib import OAuth1Session, OAuth1

ttrCreds = json.load(open('TTRclient_secret.json'))
def twitterSess():
    twitter = OAuth1Session(ttrCreds['client_id'],client_secret=ttrCreds['client_secret'] ,callback_uri = 'http://localhost:4200/load?prov=ttr')
    twitter.fetch_request_token(ttrCreds['token_uri'] )
    return twitter

def authTwitterSess(connection):
    twitToken = json.loads(connection.access_token)
    headeroauth = OAuth1(ttrCreds['client_id'], ttrCreds['client_secret'],
                      twitToken['oauth_token'], twitToken['oauth_token_secret'],
                     signature_type='auth_header')
    return headeroauth

def getUserInfo(twitter, db, tokens, old_user):

    basic_info = twitter.get(
        'https://api.twitter.com/1.1/account/verify_credentials.json').json()
    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    

    exists = Connections.query.filter_by(email = basic_info['id_str'] + '@twit.com', provider = 'twitter').first()
    user = User.query.filter_by(username=basic_info['id_str']).first()

    if old_user:
        if not exists:
            newConn = newConnection(basic_info, db, tokens, old_user)
            if newConn:
                response = old_user.token_construction()
                return response
            else:
                response = {'error': 'There was a problem registering that account'}
                return response
        else:
            response = {'error': 'Already connected account!'}
            return response


    else:
        if user:
            if user.primary_provider != 'twitter':
                response = {
                'error': 'User has already authenticated with a different medium'}
            else:
                newUser = updatedTwitterUser(basic_info, db, tokens, user)
                response = newUser.token_construction()
        else:
            if exists:
                response = {'error': 'User has already authenticated with a different medium'}
            else:
                response = newTwitterUser(basic_info, db,
                                      tokens)
    return response

def newConnection(basic_info, db, tokens, user):
    import json
    name_lst = basic_info['name'].split(' ')
    first_name = name_lst[0]
    last_name = name_lst[1]

    connection = Connections(first_name, last_name,
                             basic_info['id_str'] + '@twit.com', 'twitter',  basic_info['profile_image_url_https'], basic_info['id_str'], user.id, json.dumps(tokens))

    db.session.add(connection)
    data = db.session.commit()
    if data:
        return False
    else:
        return True



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

def get_Timeline(user, max_id):
    if max_id:
        max_str = '&max_id='+max_id
    else:
        max_str = ''
    connection = Connections.query.filter_by(provider='twitter', user_id=user.id ).first()
    try:
        data = requests.get('https://api.twitter.com/1.1/statuses/home_timeline.json?count=200'+max_str,auth=authTwitterSess(connection)).json()

        return data
    except requests.exceptions.RequestException as e:
        print(e)
        return {"error": "error", "status":400}
