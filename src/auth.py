import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_bcrypt import Bcrypt

from src.db import get_db

from src.database_manager import DatabaseManager

from flask_bcrypt import bcrypt

bp = Blueprint('auth', __name__, url_prefix='/auth')
bcrypt = Bcrypt()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    Handle the registration of a new user.
    Shows the registration form on GET and processes the registration on POST.

    :return: The registration template on GET or redirects to the login page on successful registration.
    """
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                DatabaseManager.create_user(name, username, hashed_password, 1, email)
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Handle user login.
    Shows the login form on GET and processes authentication on POST.

    :return: The login template on GET or redirects to the index page on successful login.
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username/password.'
        elif not bcrypt.check_password_hash(user['password'], password):
            error = 'Incorrect username/password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')

@bp.before_app_request
def load_logged_in_user():
    """
    Load the logged-in user's information before each request, if they're logged in.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    """
    Handle user logout, clearing the session.

    :return: Redirects to the index page.
    """
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    """
    View decorator that redirects anonymous users to the login page.

    :param view: The view function to decorate.
    :return: The decorated view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


