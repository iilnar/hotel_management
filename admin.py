from flask import Flask, g
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import _app_ctx_stack

import db

SECRET_KEY = 'MR'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db() -> db.DB:
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = db.DB()
    return top.db


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('info'))
    error = None
    if request.method == 'POST':
        user = get_db().get_manager(request.form['username'])
        if user is None:
            error = 'No such user'
        elif user.password != request.form['password']:  # TODO change to hash
            error = 'Wrong password'
        else:
            flash('You\'re now logged in')
            session['user_id'] = user.id
            return redirect(url_for('info'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id')
    return redirect(url_for('login'))


@app.route('/info', methods=['GET', 'POST'])
def info():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('info.html', error=None)


@app.route('/')
def empty():
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = get_db().get_manager(id=session['user_id'])


if __name__ == '__main__':
    app.run()