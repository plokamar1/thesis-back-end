#!flask/bin/python
from flask import Flask, request
import dbfunctions
import sys

app = Flask(__name__)

@app.route("/app/user", methods =["POST","GET"])
def index():
    if request.method == "POST":
        args = request.get_json()
        dbfunctions.addUser(args)
        return "Got Post"
    if request.method == "GET":
        return "Got Get"

if __name__ == "__main__":
    app.run(debug=True)


