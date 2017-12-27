#!flask/bin/python
from flask import Flask, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from requests_oauthlib import OAuth2Session, OAuth1Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import sys
import json
from flask_cors import CORS

import authFB
import authGGL
import authTTR
from Classes.User import db
import authentication

##INITIALIZING GOOGLE
gglCreds = json.load(open('Gclient_secret.json'))
scope=['https://www.googleapis.com/auth/drive.metadata.readonly','https://mail.google.com/','profile','https://www.googleapis.com/auth/gmail.readonly ']
google = OAuth2Session(gglCreds['client_id'], scope = scope, redirect_uri = 'http://localhost:4200/auth/sign-in?prov=ggl')

##INITIALIZING FACEBOOK
fbCreds = json.load(open('FBclient_secret.json'))
facebook = OAuth2Session(fbCreds['client_id'] , redirect_uri= 'http://localhost:4200/auth/sign-in?prov=fb')
facebook = facebook_compliance_fix(facebook)

ttrCreds = json.load(open('TTRclient_secret.json'))
twitter = OAuth1Session(ttrCreds['client_id'],client_secret=ttrCreds['client_secret'] ,callback_uri = 'http://localhost:4200/auth/sign-in?prov=ttr')
twitter.fetch_request_token(ttrCreds['token_uri'] )


app = Flask(__name__)
app.config['SECRET_KEY'] = 'BIMOJI OTO FLAT KNER Punk IPA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Zangetsou1992@localhost/backend_thesis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(app, resources={r"/.*": {"origins": "*"}})



db.init_app(app)
with app.app_context():

    db.create_all()
    
@app.route("/api/user", methods=["POST", "GET"])
def index():
    ###SIGN UP
    if request.method == "POST":
        args = request.get_json()
        #Check if user exists already
        userExists = authentication.isUserRegistered(db ,args.get('username'), args.get('email'))
        #Return Error
        if userExists:
            print(json.dumps({'error': 'User already exists'}), sys.stderr)
            return json.dumps({'error': 'User already exists'}), 403
        else:
            #Make new user
            resp = authentication.addUser(db, args)
            if 'error' in resp:
                #if something went wrong return error
                return json.dumps(resp), 403
            else:
                return json.dumps(resp), 200

    ###LOGIN
    if request.method == "GET":
        username = request.args.get('username')
        password = request.args.get('password')
        exists = authentication.isUserRegistered(db, username, None)
        # if not exists:
        #     #if there isnt any user with that username then return an error
        #     return json.dumps({'message': 'No such user'}), 403
        user = authentication.signInUser(username, password)
        if user:
            #return user data
            print(json.dumps(user), sys.stderr)
            return json.dumps(user), 200
        else:
            return json.dumps({'message': 'Wrong Credentials'}),403


@app.route("/api/socialAuth", methods=["POST", "GET"])
def socialAuth():
    if request.method== "GET":
        #Getting FB redirect uri
        redirect_FB, state = facebook.authorization_url(fbCreds['auth_uri'] )
        #Getting Google redirect uri
        redirect_GGL, state = google.authorization_url(gglCreds['auth_uri'], access_type="offline", prompt="select_account")

        #Getting Twitter redirect uri
        redirect_TTR = twitter.authorization_url(ttrCreds['auth_uri'])

        return json.dumps({'fb_uri': redirect_FB, 'ggl_uri': redirect_GGL, 'ttr_uri': redirect_TTR} ), 200

    if request.method == "POST":
        prov = request.get_json()
        prov = prov.get('prov')
        if prov == 'ggl':
            code = request.get_json().get('code')
            google.fetch_token(gglCreds['token_uri'] , client_secret=gglCreds['client_secret'],code=code)
            token = google.token
            resp = authGGL.getUserInfo(google,db)
            if 'error' in resp:
                return json.dumps(resp), 400
            else:
                return json.dumps(resp), 200

        if prov == 'fb':
            code = request.get_json().get('code')
            facebook.fetch_token(fbCreds['token_uri'], client_secret=fbCreds['client_secret'],code = code)
            resp = authFB.getUserInfo(facebook, db)
            if 'error' in resp:
                return json.dumps(resp), 400
            else:
                return json.dumps(resp), 200

        if prov == 'ttr':
            code = request.get_json().get('code')
            twitter.parse_authorization_response(code)
            tokens = twitter.fetch_access_token(ttrCreds['access_token_uri'])
            resp = authTTR.getUserInfo(twitter, db, tokens)
            if 'error' in resp:
                return json.dumps(resp), 400
            else:
                return json.dumps(resp), 200
            


@app.route('/api/getmails', methods=['GET'])
def get_mails():

    mails_list = authGGL.get_mail(google)
    return json.dumps(mails_list), 200


if __name__ == "__main__":
    app.run(debug=True)
