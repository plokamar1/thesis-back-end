import MySQLdb
import sys
import hashlib
import uuid
from flask_sqlalchemy import SQLAlchemy
from Classes.User import User

def addUser(db, data):
	if data.get('primary_provider') == 'form':
		return addFormUser(db, data)


def addFormUser(db, data):
	_firstname = data.get('firstname')
	_lastname = data.get('lastname')
	_password = data.get('password')
	_primary_provider = data.get('primary_provider')
	_email = data.get('email')
	_username = data.get('username')
	#initialize user model
	user = User(_firstname,
             _lastname,
             _email,
             _primary_provider,
             _username,
             '')
	#save hashed user password
	user.password_hash(_password)
	#insert user to database
	db.session.add(user)
	data = db.session.commit()

	if not data:
		return True
	else:
		return data


def signInUser(_username, _password):
	#Getting the user object IF there is any with that username
	user = User.query.filter_by(username=_username).first()
	if user:
		json = user.verify_pass(_password)
		return json
	else:
		return False


def isUserRegistered(db, data):
	_username = data.get('username')
	_email = data.get('email')
	#check username availability
	results = User.query.filter_by(username=_username).first()
	if results:
		return 'Username already exists'

	#check email availability
	results = User.query.filter_by(email=_email).first()
	if results:
		return 'Email already exists'
	return False
