#!flask/bin/python
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
import hashlib
import uuid
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import sys
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    email = db.Column(db.String(80), unique=True)
    primary_provider = db.Column(db.String(20))
    username = db.Column(db.String(40), unique=True)
    salt = db.Column(db.String(380))
    password = db.Column(db.String(380))
    photo_url = db.Column(db.String(2083))
    connections = db.relationship('Connections', backref='profiles', lazy=True)

    def __init__(self, firstname, lastname, email, primary_provider, username, photo_url):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.primary_provider = primary_provider
        self.username = username
        self.photo_url = photo_url

    def password_hash(self, password):
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha512(
            "You;ll never find it:)" + password + self.salt).hexdigest()

    def verify_pass(self, _password):
        password = hashlib.sha512(
            "You;ll never find it:)" + _password + self.salt).hexdigest()
        if self.password == password:
            json = self.user_info_construction()
            return json

    def generate_token(self, duration=3000):
        #the token encrypts the user's id. Upon verification we use that id
        #to return the user's info
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=duration)
        return s.dumps({'id': self.id})

    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = User.query.get(data['id'])
        return user

    def user_info_construction(self):
        connections = Connections.query.filter_by(user_id = self.id).all()
        connections_list = []
        if isinstance(connections, list):
            for connection in connections:
                data = {
                    'firstname': connection.firstname,
                    'lastname': connection.lastname,
                    'provider': connection.provider,
                    'email': connection.email,
                    'provider_id': connection.provider_id,
                }
                connections_list.append(data)
        else:
            data = {
                'firstname': connections.firstname,
                'lastname': connections.lastname,
                'provider': connections.provider,
                'email': connections.email,
                'provider_id': connections.provider_id,
            }
            connections_list.append(data)

        json = {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'photo_url': self.photo_url,
            'token': self.generate_token(),
            'id': self.id,
            'connections': connections_list
        }
        return json


class Connections(db.Model):
    __tablename__ = 'connections'
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    provider = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id'), nullable=False)
    email = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    photo_url = db.Column(db.String(2083))
    provider_id = db.Column(db.String(80))

    def __init__(self, firstname, lastname, email, provider, photo_url, provider_id, user_id):
            self.firstname = firstname
            self.lastname = lastname
            self.email = email
            self.provider = provider
            self.photo_url = photo_url
            self.provider_id = provider_id
            self.user_id = user_id
