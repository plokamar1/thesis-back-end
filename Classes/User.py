#!flask/bin/python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import hashlib
import uuid

db = SQLAlchemy()



class User(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True,
                   nullable = False, autoincrement=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    email = db.Column(db.String(80), unique=True)
    primary_provider = db.Column(db.String(20))
    username = db.Column(db.String(40), unique=True)
    salt = db.Column(db.String(380))
    password = db.Column(db.String(380))
    photo_url = db.Column(db.String(2083))

    def __init__(self, firstname, lastname, email, primary_provider, username, photo_url):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.primary_provider = primary_provider
        self.username = username
        self.photo_url = photo_url

    def password_hash(self, password):
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha512("You;ll never find it:)" + password + self.salt).hexdigest()


