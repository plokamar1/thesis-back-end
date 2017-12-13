#!flask/bin/python
from flask import Flask, request
import authentication
import sys

app = Flask(__name__)

@app.route("/app/user", methods =["POST","GET"])
def index():
    authentication.createTables()
    if request.method == "POST":
        args = request.get_json()
        authentication.addUser(args)
        return "Got Post"
    if request.method == "GET":
        username = request.args.get('username')
        password = request.args.get('password')
        authentication.signInUser(username,password)
        return "Got Get"

if __name__ == "__main__":
    app.run(debug=True)


