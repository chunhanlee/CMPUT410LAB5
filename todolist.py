from flask import Flask, request, url_for, redirect, render_template, session, redirect, abort, session, g, flash
import sqlite3

conn = None
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'secret key secret'
DEBUG = True
DATABASE ="lab.db"


app = Flask(__name__)
app.config.from_object(__name__)



@app.route('/')
def welcome():
    return '<h1> Welcome to CMPUT410 - Jinja Lab!</h1>'

@app.route('/task', methods = ['GET', 'POST'])
def tasks():
    if request.method == 'POST' :
        if not session.get('logged_in'):
            abort(401)
        category = request.form['category']
        priority = request.form['priority']
        description = request.form['description']
        try:
            if int(priority) >100 or int(priority) < 0:
                raise Exception
        except:
            return "invalid priority"
        try:
            if category == "":
                raise Exception
        except:
            return "No category"
        add_task(category,priority, description)
        flash('New task was successfully added.')
        return redirect(url_for('tasks'))
    tasks = query_db('SELECT * FROM tasks ORDER BY priority DESC')
    return render_template('show_entries.html', tasks=tasks)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username.'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password.'
        else:
            session['logged_in'] = True
            return redirect(url_for('tasks'))
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    flash('You are logged out.')
    return redirect(url_for('tasks'))

@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    removetask(request.form['category'],request.form['priority'],request.form['description'])
    flash('Task deleted successfully')
    return redirect(url_for('tasks'))

def get_conn():
    db=getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def disconn(db):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_conn().cursor()
    cur.execute(query,args)
    r = cur.fetchall()
    cur.close()
    return( r[0] if r else None) if one else r

def add_task(cat, prior, descrip):
    query_db("insert into tasks(category, priority, description) values(?,?,?)", (cat,prior,descrip))
    get_conn().commit();

def removetask(cat, prior, descrip):
    query_db("delete from tasks where category=? and priority=? and description=?", (cat,prior,descrip))
    get_conn().commit();


if __name__ == "__main__":
    app.debug = True
    app.run()

