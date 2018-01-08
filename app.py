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
from Classes.User import *
import authentication
#################
##INITIALIZING GOOGLE
gglCreds = json.load(open('Gclient_secret.json'))
scope=['https://www.googleapis.com/auth/drive.metadata.readonly','https://mail.google.com/','profile','https://www.googleapis.com/auth/gmail.readonly ']
google = OAuth2Session(gglCreds['client_id'], scope = scope, redirect_uri = 'http://localhost:4200/load?prov=ggl')

##INITIALIZING FACEBOOK
fbCreds = json.load(open('FBclient_secret.json'))
facebook = OAuth2Session(fbCreds['client_id'] , redirect_uri= 'http://localhost:4200/load?prov=fb')
facebook = facebook_compliance_fix(facebook)
##INITIALIZING TWITTER
ttrCreds = json.load(open('TTRclient_secret.json'))
def twitterSess():
    twitter = OAuth1Session(ttrCreds['client_id'],client_secret=ttrCreds['client_secret'] ,callback_uri = 'http://localhost:4200/load?prov=ttr')
    twitter.fetch_request_token(ttrCreds['token_uri'] )
    return twitter



app = Flask(__name__)
app.config['SECRET_KEY'] = 'BIMOJI OTO FLAT KNER Punk IPA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Zangetsou1992@localhost/backend_thesis?charset=utf8'
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
        username = request.args.get('username', '')
        password = request.args.get('password', '')
        exists = authentication.isUserRegistered(db, username, None)
        # if not exists:
        #     #if there isnt any user with that username then return an error
        #     return json.dumps({'message': 'No such user'}), 403
        user = authentication.signInUser(username, password)
        if user:
            #return user data

            return json.dumps(user.token_construction()), 200
        else:
            return json.dumps({'message': 'Wrong Credentials'}),403


@app.route("/api/socialAuth", methods=["POST", "GET"])
def socialAuth():
    if request.method== "GET":
        #Getting FB redirect uri
        redirect_FB, state = facebook.authorization_url(fbCreds['auth_uri'] )
        #Getting Google redirect uri
        redirect_GGL, state = google.authorization_url(gglCreds['auth_uri'], access_type="offline", prompt="consent")

        #Getting Twitter redirect uri
        twitter = twitterSess()
        redirect_TTR = twitter.authorization_url(ttrCreds['auth_uri'])

        return json.dumps({'fb_uri': redirect_FB, 'ggl_uri': redirect_GGL, 'ttr_uri': redirect_TTR} ), 200

    if request.method == "POST":
        prov = request.get_json()
        token = prov.get('token')
        prov = prov.get('prov')
        #In case we receive a token then we update a user's profile with an extra connection
        if token :
            user = authentication.signInUser(token, '')
            if user and prov=='ggl':
                code = request.get_json().get('code')
                google.fetch_token(gglCreds['token_uri'] , client_secret=gglCreds['client_secret'],code=code)
                resp = authGGL.getUserInfo(google, db, user)
                if 'error' in resp:
                    return json.dumps(resp), 400
                else:
                    return json.dumps(resp), 200
            if user and prov=='ttr':
                code = request.get_json().get('code')
                twitter = twitterSess()
                twitter.parse_authorization_response(code)
                tokens = twitter.fetch_access_token(ttrCreds['access_token_uri'])
                resp = authTTR.getUserInfo(twitter, db, tokens, user)

        if prov == 'ggl':
            code = request.get_json().get('code')
            new_token = google.fetch_token(gglCreds['token_uri'] , client_secret=gglCreds['client_secret'],code=code)
            token = google.token
            resp = authGGL.getUserInfo(google,db,None)
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
            twitter = twitterSess()
            twitter.parse_authorization_response(code)
            tokens = twitter.fetch_access_token(ttrCreds['access_token_uri'])
            resp = authTTR.getUserInfo(twitter, db, tokens, None)
            if 'error' in resp:
                return json.dumps(resp), 400
            else:
                return json.dumps(resp), 200

@app.route('/api/get-user', methods=['GET'])
def get_user():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        user_data = user.user_info_construction()
        return json.dumps(user.user_info_construction())
    else:
        abort(400)

@app.route('/api/rss', methods=['GET'])
def modify_rss():
    token = request.args.get('token', '')
    rss_url = request.args.get('rss', '')
    user = authentication.signInUser(token, '')
    if not user:
        abort(400)
    
    action = request.args.get('action', '')
    if action == 'add':
        exists = Rss.query.filter_by(user_id = user.id, url=rss_url).scalar() is not None
        if exists:
            rss_list = user.rss_construction()
            return json.dumps({"rss_feeds": rss_list}), 200
        rss = Rss(user.id, rss_url)
        db.session.add(rss)
        db.session.commit()
        rss_list = user.rss_construction()
        return json.dumps({"rss_feeds": rss_list}), 200

    if action == 'remove':
        rss = Rss.query.filter_by(user_id = user.id, url = rss_url).first()
        if rss:
            db.session.delete(rss)
            db.session.commit()
        rss_list = user.rss_construction()
        return json.dumps({"rss_feeds": rss_list}), 200

    abort(400)

@app.route('/api/getmails', methods=['GET'])
def get_mails():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        nextPageToken = request.args.get('nextPageToken', '')
        mails_list = authGGL.get_mail(user, db, nextPageToken)
        if 'error' in mails_list:
            return json.dumps(mails_list) , 400
        return json.dumps(mails_list), 200
    else:
        abort(400)

@app.route('/api/modifymails', methods=['GET'])
def modify_mails():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        label = request.args.get('label', '')
        action = request.args.get('action', '')
        mess_id = request.args.get('id', '')
        response = authGGL.modify_mail(label, action, mess_id, user, db)
        if response:
            return json.dumps({'message':'Label modified'}), 200
        else:
            return json.dumps({'error':'There was a problem'}), 400
    else:
        abort(400)
@app.route('/api/trash', methods=['POST'])
def trash():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        req = request.data
        deleted = authGGL.toTrash(req, user, db)
        if deleted:
            return json.dumps({'success': str(deleted)+' mails succesfully moved to trash!'}), 200
        else:
            return json.dumps({'error':'There was a problem'}), 400

    else:
        abort(400)

@app.route('/api/sendmail', methods=['POST'])
def send_mail():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        req = request.data
        if authGGL.send_mail(req, db, user):
            return json.dumps({'success': 'Mail succesfully sent'}), 200
        else:
            return json.dumps({'error':'There was a problem'}), 400

    else:
        abort(400)

@app.route('/api/gettwits', methods=['GET'])
def get_twits():
    token = request.args.get('token', '')
    user = authentication.signInUser(token, '')
    if user:
        max_id = request.args.get('max_id', '')
        response = authTTR.get_Timeline(user, max_id)
        if 'error' in response:
            return json.dumps(response), 400
        return json.dumps(response), 200
    abort(400)

if __name__ == "__main__":
    app.run(debug=True,threaded=True)
