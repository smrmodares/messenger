import requests
import urllib.parse
import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps


def init_db():
    # create database
    messenger = sqlite3.connect('messenger.db', check_same_thread=False)
    db = messenger.cursor()

    #create tables
    db.execute("CREATE TABLE users ('user_id' INTEGER PRIMARY KEY AUTOINCREMENT, 'username' TEXT UNIQUE NOT NULL, 'password' TEXT NOT NULL, 'email' TEXT NOT NULL)")
    db.execute("CREATE TABLE messages ('message_id' INTEGER PRIMARY KEY AUTOINCREMENT,'user_id' INTEGER, 'message' TEXT,FOREIGN KEY ('user_id') REFERENCES users('user_id')  FOREIGN KEY ('user_id') REFERENCES users('user_id'))")

    # Save (commit) the changes
    messenger.commit()


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
