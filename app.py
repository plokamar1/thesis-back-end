#!flask/bin/python
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
import authFB
from Classes.User import db
import authentication
import sys
import json

# authentication.createTables()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BIMOJI OTO FLAT KNER Punk IPA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Zangetsou1992@localhost/backend_thesis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():

    db.create_all()
    
@app.route("/app/user", methods=["POST", "GET"])
def index():
    ###SIGN UP
    if request.method == "POST":
        args = request.get_json()
        userExists = authentication.isUserRegistered(db ,args)
        if userExists:
            return userExists
        if authentication.addUser(db,args):
            return 'User successfuly registered'
        else:
            return 'There was a problem'

    ###LOGIN
    if request.method == "GET":
        username = request.args.get('username')
        password = request.args.get('password')
        user = authentication.signInUser(username, password)
        if user:
            return json.dumps(user)
        else:
            abort(400)

@app.route("/fbdata", methods=["POST", "GET"])
def get_user_data():
    if request.method== "GET":
        userToken = request.args.get('token')
        resp = authFB.getUserInfo(userToken,db)
        return json.dumps(resp)
        

if __name__ == "__main__":
    app.run(debug=True)
