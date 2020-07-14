import os
import sqlite3

from flask import Flask, flash, session, render_template, request, redirect, jsonify, escape
from flask_session import Session
from flask_socketio import SocketIO, emit
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# from functools import wraps
from helpers import apology, login_required
from functools import wraps



# Configure application
app = Flask(__name__)
messages = []
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("sqlite:///messenger.db",
                    connect_args={'check_same_thread':False})
db = scoped_session(sessionmaker(bind=engine))

# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """register user"""

    if request.method == "POST":

        # Forget any user_id
        session.clear()

        # Check inputs
        if not request.form.get("username"):
            return render_template("error.html", message="Username missing!")

        elif not request.form.get("password"):
            return render_template("error.html", message="Password missing!")

        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Password confirmation missing!")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="Password and confirmation don't match!")

        elif not request.form.get("email"):
            return render_template("error.html", message="Email missing!")

        # Hash the password
        hash =  generate_password_hash(request.form.get("password"))


        username = request.form.get("username")
        # Check if this username exist
        exist = db.execute("SELECT user_id FROM users WHERE username = :username", {"username": username}).fetchone()

        if not exist:
            # Insert user to the database
            db.execute("INSERT INTO users (username, password, email) VALUES (:username, :hash, :email)",
                                {"username": username, "hash": hash, "email": request.form.get("email")})
            db.commit()

            # Remember which user has logged in
            uid = db.execute("SELECT user_id FROM users WHERE username = :username",
                             {"username": username}).fetchone()

            session["user_id"] = uid[0]
            flash("Registerd!")
            return redirect("/")

        else:
            return render_template("error.html", message="Username is taken.")

    # If method is GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    if request.method == "POST":

        # Forget any user_id
        session.clear()

        if not request.form.get("username"):
            return render_template("error.html", message="Username missing!")

        elif not request.form.get("password"):
            return render_template("error.html", message="Password missing!")

        result = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username")}).fetchone()

        if not result or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="Username or password is incorect.")

        else:
            session["user_id"] = result[0]
            flash("Logged in!")
            return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/contact", methods=["GET", "POST"])
@login_required
def messaging():
    """recieve and send messages"""

    result = db.execute("SELECT message_id, username, message FROM messages JOIN users ON users.user_id = messages.user_id").fetchall()

    # print(result)
    return render_template("contact.html", messages=result)

@app.route("/get_id", methods=["POST"])
def get_id():
    return jsonify({"user_id": session['user_id']})

@socketio.on("send message")
@login_required
def vote(data):
    message = data["message"]
    # messages.append(message)
    db.execute("INSERT INTO messages (user_id, message) VALUES (:user_id, :message)",
                        {"user_id": session["user_id"], "message": escape(message)})
    db.commit()

    result = db.execute("SELECT * FROM messages WHERE user_id = :user_id AND message = :message",
                        {"user_id": session["user_id"], "message": escape(message)}).fetchone()
    username = db.execute("SELECT username FROM users WHERE user_id = :user_id ",
                        {"user_id": session["user_id"]}).fetchone()[0]
    print(username)
    emit("new message", {"message_id":result[0], "username": username, "message": result[2]}, broadcast=True)

@socketio.on("delete message")
@login_required
def vote(data):
    message_id = data["id"]

    db.execute("DELETE FROM messages WHERE message_id = :message_id", {"message_id": message_id})
    db.commit()

    emit("update message", {"id": message_id, "action": 'delete'}, broadcast=True)
