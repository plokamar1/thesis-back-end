import MySQLdb
import sys
import hashlib
import uuid
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from Classes.User import User



# def createTables():
# 	profiles = Table('profiles', metadata, autoload=True)
# 	if not profiles.exists():
# 		profiles = Table('profiles', metadata,
#                   Column('id', Integer, primary_key=True,
#                          nullable=False, autoincrement=True),
#                   Column('firstname', VARCHAR(20)),
#                   Column('lastname', VARCHAR(20)),
#                   Column('password', VARCHAR(380)),
#                   Column('primary_provider', VARCHAR(20)),
#                   Column('email', VARCHAR(80), unique=True),
#                   Column('username', VARCHAR(40)),
#                   Column('salt', VARCHAR(380)),
#                   Column('photo_url', VARCHAR(2083))
#                   )
# 		profiles.create()
# db, cursor = connect()
# createQuery = """CREATE TABLE IF NOT EXISTS profiles(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
# firstname VARCHAR(20),
# lastname VARCHAR(20),
# password VARCHAR(380),
# primary_provider VARCHAR(20),
# email VARCHAR(80) UNIQUE,
# username VARCHAR(40) UNIQUE,
# salt VARCHAR(380),
# photo_url VARCHAR(2083));"""

# cursor.execute(createQuery)
# db.commit()


def connect():
	db = MySQLdb.connect(host='localhost',
                      user='root',
                      passwd='Zangetsou1992',
                      db='backend_thesis')
	cur = db.cursor()
	return db, cur


def addUser(db, data):
	if data.get('primary_provider') == 'form':
		return addFormUser(db ,data)


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
	user = User.query.filter_by(username = _username).first()
	if user:
		email = user.verify_pass(_password)
		user = {'email': email}
		return user
	else:
		return False


def isUserRegistered(db,data):
	_username = data.get('username')
	_email = data.get('email')
	#check username availability
	results = User.query.filter_by(username=_username).first()
	print(results , sys.stderr)

	if results:
		return 'Username already exists'

	#check email availability
	results = User.query.filter_by(email = _email).first()
	if results:
		return 'Email already exists'
	return False
