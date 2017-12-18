#!flask/bin/python
from flask import Flask, request
import authentication
import sys
import json

authentication.createTables()

app = Flask(__name__)

@app.route("/app/user", methods =["POST","GET"])
def index():
    ###SIGN UP
    if request.method == "POST":
        args = request.get_json()
        userExists = authentication.isUserRegistered(args)
        if userExists:
            return userExists
        if authentication.addUser(args):
            return 'User successfuly registered'
        else:
            return 'There was a problem'

    ###LOGIN
    if request.method == "GET":
        username = request.args.get('username')
        password = request.args.get('password')
        user = authentication.signInUser(username,password)
        if user:
            return json.dumps(user)
        else:
            return "Wrong credentials"

if __name__ == "__main__":
    app.run(debug=True)


