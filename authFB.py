from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json


def getUserInfo(userToken, db):
    users = User.query.all()
    for user in users:
        print(user.email, sys.stderr)
    graph_API_url = 'https://graph.facebook.com/v2.11/me'
    fields_str = 'fields=email,first_name,last_name,short_name,id,link,verified'
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
            response = {'error':'OAuthException'}
    elif not basic_info['verified']:
        response = {'error': 'User not verified'}
    else:
        
        user = User.query.filter_by(email = basic_info['email']).first()
        #print(user.email, sys.stderr)
        if user is None:
            print('GOT IN', sys.stderr)
            response = newFbUser(basic_info, user_pic, db)
        else:
            response = user.user_info_construction()
    # graph = GraphAPI(access_token=userToken, version= "2.11")
    # print(graph, sys.stderr)
    # user =  graph.get_object(id='me', fields='email,first_name,last_name')
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


