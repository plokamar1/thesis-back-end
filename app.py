#!flask/bin/python
from flask import Flask, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from requests_oauthlib import OAuth2Session
import sys
import json
from flask_cors import CORS

import authFB
from Classes.User import db
import authentication

gglCreds = json.load(open('client_secret.json'))
scope=['https://www.googleapis.com/auth/drive.metadata.readonly','https://mail.google.com/','profile','https://www.googleapis.com/auth/gmail.readonly ']
google = OAuth2Session(gglCreds['web']['client_id'], scope = scope, redirect_uri = 'https://localhost:4200/auth/sign-in')


# authentication.createTables()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BIMOJI OTO FLAT KNER Punk IPA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Zangetsou1992@localhost/backend_thesis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})



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
        prov = request.args.get('prov')
        if prov == 'fb':
            userToken = request.args.get('token')
            resp = authFB.getUserInfo(userToken,db)
            return json.dumps(resp)
        if prov == 'ggl':
            redirect_uri, state = google.authorization_url(gglCreds['web']['auth_uri'], access_type="offline", prompt="select_account")
            return redirect_uri, 200
    if request.method == "POST":
        code = request.get_json().get('code')


@app.route('/api/googleuser', methods=['GET'])
def user_create():
    code = request.args.get('code')
    google.fetch_token(gglCreds['web']['token_uri'] , client_secret=gglCreds['web']['client_secret'],code=code)
    data = google.get('https://www.googleapis.com/gmail/v1/users/me/profile').json()
    # flow.fetch_token(code = code)

    # session = flow.authorized_session()
    # g._gsession = session
    # data = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    # print(data, sys.stderr)

    # data = session.get('https://www.googleapis.com/gmail/v1/users/me/profile').json()

    return json.dumps(data)

if __name__ == "__main__":
    app.run(debug=True)
