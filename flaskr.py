# imports
import sqlite3
from flask import Flask, render_template, request, session, flash, redirect, url_for, abort, g

# configuration
DATABASE = 'flaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'bla_bla'

app = Flask(__name__)
app.config.from_object(__name__)

# connecting to the database
def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row 
	return rv

# creating the database
def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

# Opening the database connection
def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

# closing database connection
@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()


@app.route('/')
def index():
	db = get_db()
	cur = db.execute('select title,text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""User login/authentication/session management."""
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	"""User logout/authentication/session management."""
	session.pop('logged_in', None)
	flash('You are logged out')
	return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title,text) values (?,?)', [request.form['title'], request.form['text']])
	db.commit()
	flash('New entry is successfully posted.')
	return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
