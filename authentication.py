import MySQLdb
import sys
import hashlib
import uuid


def createTables():
	db, cursor = connect()
	createQuery = """CREATE TABLE IF NOT EXISTS profiles(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	firstname VARCHAR(20), 
	lastname VARCHAR(20), 
	password VARCHAR(380), 
	primary_provider VARCHAR(20), 
	email VARCHAR(80) UNIQUE,
	username VARCHAR(40) UNIQUE,
	salt VARCHAR(380),
	photo_url VARCHAR(2083));"""

	cursor.execute(createQuery)
	db.commit()


def connect():
	db = MySQLdb.connect(host='localhost',
                      user='root',
                      passwd='Zangetsou1992',
                      db='backend_thesis')
	cur = db.cursor()
	return db, cur


def addUser(data):

	db, cur = connect()
	if data.get('primary_provider') == 'form':
		return addFormUser(data)


def addFormUser(data):
	firstname = data.get('firstname')
	lastname = data.get('lastname')
	password = data.get('password')
	primary_provider = data.get('primary_provider')
	email = data.get('email')
	username = data.get('username')
	#producing the unique salt for the user
	salt = uuid.uuid4().hex
	#producing the hashed password
	hashed_password = hashlib.sha512(password + salt).hexdigest()

	q = "INSERT INTO profiles(firstname , lastname, password, primary_provider,email,username,salt) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
		firstname, lastname, hashed_password, primary_provider, email, username, salt)

	db, cursor = connect()
	cursor.execute(q)
	db.commit()
	data = cursor.fetchone()
	db.close()

	if not data:
		return True
	else:
		return data


def signInUser(username, password):
	db, cursor = connect()
	query = '''SELECT salt FROM profiles WHERE username='%s';''' % (username)
	cursor.execute(query)
	salt = cursor.fetchone()
	if salt:
		salt = ''.join(salt)
		hashedPass = hashlib.sha512(password + salt).hexdigest()
		query2 = '''SELECT firstname,lastname,email FROM profiles WHERE username='%s' AND password='%s';''' % (
			username, hashedPass)
		cursor.execute(query2)
		result = cursor.fetchone()
		db.commit()
		user = {'firstname': result[0], 'lastname': result[1], 'email': result[2]}
		return user
	else:
		return False


def isUserRegistered(data):
	username = data.get('username')
	email = data.get('email')

	db, cursor = connect()
	#Check if username exists
	queryUsername = """SELECT * FROM profiles WHERE username='%s';""" % (username)
	cursor.execute(queryUsername)
	result1 = cursor.fetchone()
	if result1:
		return 'Username already exists'

	#Check if email exists
	queryEmail = """SELECT * FROM profiles WHERE email='%s';""" % (email)
	cursor.execute(queryEmail)
	result2 = cursor.fetchone()
	if result2:
		return 'Email already exists'
	db.close()
	return False
