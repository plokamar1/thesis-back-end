import MySQLdb
import sys
import hashlib, uuid

def createTables():
	db, cursor = connect()
	createQuery = """CREATE TABLE IF NOT EXISTS profiles(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	firstname VARCHAR(20), 
	lastname VARCHAR(20), 
	password VARCHAR(380), 
	primary_provider VARCHAR(20), 
	email VARCHAR(80),
	username VARCHAR(40),
	photo_url VARCHAR(2083));"""

	cursor.execute(createQuery)
	db.commit()



def connect():
	db = MySQLdb.connect(host = 'localhost',
					user = 'root',
					passwd = 'Zangetsou1992',
					db= 'backend_thesis')
	cur = db.cursor()
	return db,cur


def addUser(data):

	db, cur = connect()
	if data.get('primary_provider') == 'form':
		query = addFormUser(data)

		ret = cur.execute(query)
		db.commit()
		data = cur.fetchone()
		db.close()


def addFormUser(data):
	firstname = data.get('firstname')
	lastname = data.get('lastname')
	password = data.get('password')
	primary_provider = data.get('primary_provider')
	email = data.get('email')
	username = data.get('username')
	photo_url = data.get('photo_url')

	salt = uuid.uuid4().hex
	hashed_password = hashlib.sha512(password + salt).hexdigest()

	q = "INSERT INTO profiles(firstname , lastname, password, primary_provider,email,username,photo_url,salt) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (firstname, lastname, hashed_password, primary_provider, email, username, photo_url, salt)
	return q


def signInUser(username, password):
	db,cursor = connect()
	query = '''SELECT salt FROM profiles WHERE username='%s';'''%(username)
	ret = cursor.execute(query)
	salt = cursor.fetchone()
	salt = ''.join(salt)
	hashedPass = hashlib.sha512(password + salt).hexdigest()
	query2 = '''SELECT firstname,lastname,email FROM profiles WHERE username='%s' AND password='%s';'''%(username,hashedPass)
	cursor.execute(query2)
	result = cursor.fetchone()
	db.commit()
	print(result, sys.stderr)
	print(salt)
