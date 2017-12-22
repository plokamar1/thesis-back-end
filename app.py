#!flask/bin/python
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
import authFB
from Classes.User import db
import authentication
import sys
import json
from flask_cors import CORS

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
        if not exists:
            #if there isnt any user with that username then return an error
            return json.dumps({'message': 'No such user'}), 403
        user = authentication.signInUser(username, password)
        if user:
            #return user data
            print(user, sys.stderr)
            return json.dumps(user), 200
        else:
            return json.dumps({'message': 'Wrong Credentials'}),403


@app.route("/api/fbAuth", methods=["POST", "GET"])
def get_user_data():
    if request.method== "GET":
        userToken = request.args.get('token')
        resp = authFB.getUserInfo(userToken,db)
        return json.dumps(resp)
        

if __name__ == "__main__":
    app.run(debug=True)
