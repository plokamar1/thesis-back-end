from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json
import random
import string
from requests_oauthlib import OAuth2Session
import re

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

def get_mail(user, db):
    google = token_refresh(user , db)
    payload = {
            'labelIds': ['INBOX'],
            'maxResults':25,
            'q': 'category:primary'    
            }

    mail_list = google.get(
        'https://www.googleapis.com/gmail/v1/users/me/messages', params = payload).json()

    fetched_messages = messages_construction(mail_list, google)

    if 'error' in mail_list:
        mail_list = {'error': 'OAuthException'}

    return {'messages': fetched_messages}

def messages_construction(mail_list, google):

    fetched_messages = []
    headers = {'Authorization': 'Bearer '+google.token['access_token'],
                'Content-Type': 'multipart/mixed;boundary="foo_bar"'}
    whole_request = '--foo_bar\n'

    for message in mail_list['messages']:
        req_string = '''Content-Type: application/http

GET   /gmail/v1/users/me/messages/'''+message['id']+'''

--foo_bar
'''
        whole_request = whole_request + req_string

    batch_req = google.post('https://www.googleapis.com/batch',headers=headers,data = whole_request)
    index = batch_req.headers['Content-Type'].find('boundary')
    batch_code = batch_req.headers['Content-Type'][index:].replace('boundary=', '')
    messages = batch_req.text.split('--'+batch_code)
    messages = splitter(messages)
        
    for new_message in messages:
        new_message = json.loads(new_message)
        # new_message = google.get('https://www.googleapis.com/gmail/v1/users/me/messages/'+message['id'], params= {'format':'full'}).json()
        mess_id = new_message['id']
        mess_timestamp = new_message['internalDate']
        if 'UNREAD' in new_message['labelIds']:
            mess_unread = True
        else:
            mess_unread = False
        for header in new_message['payload']['headers']:
            if header['name'] == 'Subject':
                mess_subject =header['value']
            if header['name'] == 'Date':
                mess_date = header['value']
            if header['name'] == 'From':
                mess_from = header['value']
        if new_message['payload']['body']['size'] == 0:
            if 'parts' in new_message['payload']['parts'][0]:
                mess_body = new_message['payload']['parts'][0]['parts'][0]['body']['data']
            else:
                mess_body = new_message['payload']['parts'][0]['body']['data']
        else:
            mess_body = new_message['payload']['body']['data']


        mess_json = {
        'From': mess_from,
        'Id': mess_id,
        'Timestamp': mess_timestamp,
        'Subject': mess_subject,
        'Date': mess_date,
        'Body': mess_body,
        'Unread': mess_unread
        }


        fetched_messages.append(mess_json)
    # batch_req = google.post('https://www.googleapis.com/batch',headers=headers,data = whole_request)
    # index = batch_req.headers['Content-Type'].find('boundary')
    # batch_code = batch_req.headers['Content-Type'][index:].replace('boundary=', '')
    # messages = batch_req.text.split('--'+batch_code)
    # messages = splitter(messages)
    # print(len(messages))

    # response = json.dumps(re.findall(r'\{[^}]*\}', batch_req.text))
    # #str1 = ''.join(response)
    # response = json.loads(response)
    # print(response)

    return fetched_messages
   

def splitter(str_lst):
    new_lst = []
    for data in str_lst:
        index = data.find('{')
        if index != 0 and index != -1:
            new_lst.append(data[index:])
    return new_lst

def token_refresh(user, db):
    account = Connections.query.filter_by(user_id = user.id, provider = 'google').first()
    token = account.access_token
    gglCreds = json.load(open('Gclient_secret.json'))

    extra = {
    'client_id': gglCreds['client_id'],
    'client_secret': gglCreds['client_secret']
    }

    google = OAuth2Session(gglCreds['client_id'], token = json.loads(token), auto_refresh_kwargs=extra,
                           auto_refresh_url=gglCreds['token_uri'])

    basic_info = google.get('https://www.googleapis.com/userinfo/v2/me').json()
    
    new_token = google.token

    account.access_token = json.dumps(new_token)
    db.session.commit()
    return google