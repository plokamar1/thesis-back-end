from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json


def getUserInfo(userToken, db):
    graph_API_url = 'https://graph.facebook.com/v2.11/me'
    fields_str = 'fields=email,first_name,last_name,id,link,verified'
    access_token = 'access_token=%s' % (userToken)
    user_info_str = graph_API_url + '?' + fields_str + '&' + access_token
    r = requests.get(user_info_str)
    basic_info = r.json()

    user_pic_str = graph_API_url + '/picture' + \
        '?' + access_token + '&' + 'redirect=false'
    pic_r = requests.get(user_pic_str)
    user_pic = pic_r.json()
    if 'error' in basic_info:
        if basic_info['error']['type'] == 'OAuthException':
            response = {'error': 'OAuthException'}
    elif not basic_info['verified']:
        response = {'error': 'User not verified'}
    else:

        user = User.query.filter_by(email=basic_info['email']).first()
        #If there isn't such email already saved in the db make a new user
        if user is None:
            response = newFbUser(basic_info, user_pic, db)
        #if there is already that email and the primary provider isn't facebook then he should connect with the medium he has authenticated the first time
        elif user.primary_provider != 'facebook':
            response = {
                'error': 'User has already authenticated with a different medium'}
        #if there is that user correct just send back the user info he needs
        else:
            response = user.user_info_construction()
    return response


def newFbUser(basic_info, user_pic, db):
    user = User(basic_info['first_name'], basic_info['last_name'],
                basic_info['email'], 'facebook', '', user_pic['data']['url'])
    db.session.add(user)
    data = db.session.commit()

    connection = Connections(basic_info['first_name'], basic_info['last_name'],
                             basic_info['email'], 'facebook', user_pic['data']['url'], basic_info['id'], user.id)

    db.session.add(connection)
    data = db.session.commit()
    if not data:
        json = user.user_info_construction()

        return json
