import MySQLdb
import sys
import hashlib, uuid


def connect():
	db = MySQLdb.connect(host = 'localhost',
					user = 'root',
					passwd = 'Zangetsou1992',
					db= 'backend_thesis')
	cur = db.cursor()
	ret = cur.execute('SELECT VERSION()')
	data = cur.fetchone()
	print(data, sys.stderr)
	return db,cur


def addUser(data):
	db, cur = connect()
	if data.get('primary_provider') == 'form':
		query = addFormUser(data)

		ret = cur.execute(query)
		db.commit()
		data = cur.fetchone()


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

	q = "INSERT INTO profiles(firstname , lastname, password, primary_provider,email,username,photo_url) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (firstname, lastname, hashed_password, primary_provider, email, username, photo_url)
	return q

