import MySQLdb
import sys
import hashlib
import uuid
from flask_sqlalchemy import SQLAlchemy
from Classes.User import User
import authFB

def addUser(db, data):
	if data.get('loginType') == 'FORM':
		return addFormUser(db, data)


def addFormUser(db, data):
	_firstname = data.get('firstname')
	_lastname = data.get('lastname')
	_password = data.get('password')
	_primary_provider = data.get('loginType')
	_email = data.get('email')
	_username = data.get('username')

	print(_email)
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
		return {'success': 'User Created'}
	else:
		return {'error': 'There was a problem'}


def signInUser(_username, _password):
	
	user = User.verify_token(_username)
	if user:
		reponse = user.user_info_construction()
		return response
		# if user.primary_provider == 'facebook':
		# 	authFB.refresh_Token(user)
		# if user.primary_provider == 'google':
		# if user.primary_provider == 'twitter':
		

	#Getting the user object IF there is any with that username
	user = User.query.filter_by(username=_username).first()
	if user:
		response = user.verify_pass(_password)
		if response:
			return response
		else:
			return False
	else:
		return False


def isUserRegistered(db, _username, _email):

	#check username availability
	results = User.query.filter_by(username=_username).first()
	if results:
		return True

	#check email availability
	if _email:
		results = User.query.filter_by(email=_email).first()
		if results:
			return True
	return False
