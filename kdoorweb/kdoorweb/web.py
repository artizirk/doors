import os
import secrets

from bottle import Bottle, view, TEMPLATE_PATH, static_file, \
    request, redirect, response, HTTPError

from .db import SQLitePlugin

application = app = Bottle()

# TODO: Could be replaced with importlib.resources
TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), "views"))
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "kdoorweb.sqlite")

COOKIE_KEY = b"1234"#secrets.token_bytes(32)


def current_user(db):
    user_id = request.get_cookie("uid", secret=COOKIE_KEY)
    if not user_id:
        return
    return db.get_user(user_id)


def login_user(uid):
    response.set_cookie("uid", uid, secret=COOKIE_KEY)


def logout_user():
    response.set_cookie("uid", "", secret=COOKIE_KEY)


def check_auth(callback):
    def wrapper(*args, **kwargs):
        if "db" not in kwargs:
            request.current_user = None
            return callback(*args, **kwargs)
        user = current_user(kwargs["db"])
        request.current_user = user
        if user:
            print(f"logged in as {user['user']}")
            print(request.current_user)
            return callback(*args, **kwargs)
        else:
            print("not logged in")
            response.set_cookie("error", "Not logged in")
            redirect("/login")
    return wrapper


app.install(SQLitePlugin(SQLITE_PATH))
app.install(check_auth)


@app.route('/static/<path:path>', skip=[check_auth])
def callback(path):
    return static_file(path, root=STATIC_PATH)


@app.route("/", skip=[check_auth])
def index(db):
    user = current_user(db)
    if user:
        if user["admin"]:
            redirect("/list")
        else:
            redirect(f"/info/{user['id']}")

    redirect("/login")


@app.route('/login', skip=[check_auth])
@view("login.html")
def login():
    error = request.get_cookie("error")
    if error:
        response.set_cookie("error", "")
    return {"error": error}


@app.post('/login', skip=[check_auth])
def do_login(db):
    user_name = request.forms.get("user")
    user = db.get_user_by_name(user_name)
    if user:
        print(f"user {dict(user)}")
        login_user(user["id"])
        redirect("/")
    else:
        response.set_cookie("error", "Login Failed")
        redirect("/login")


@app.route("/logout")
def logout():
    logout_user()
    redirect("/login")


@app.route("/list")
@view("list.html")
def user_list(db):
    user = request.current_user
    if user and not user["admin"]:
        users = [user]
    else:
        users = db.list_users()
    return {"users": users}


@app.route("/info")
def user_info(db):
    user = request.current_user
    redirect(f"/info/{user['id']}")


@app.route("/info/<user_id>")
@view("info.html")
def info(db, user_id):
    user_id = int(user_id)
    c_user = request.current_user
    if not c_user["admin"] and c_user["id"] != user_id:
        raise HTTPError(403, "Logged in user is not admin")
    user = db.get_user(user_id)
    if not user:
        raise HTTPError(404, "User does not exist")
    return {**user, "keycards": []}


@app.route("/log")
@view("log.html")
def log(db):
    return {
        "events":
                [
                    {
                        "timestamp": 0,
                        "door": "Back Door",
                        "user_id":1,
                        "user_name": "Arti Zirk"
                    }
                ]
            }


@app.route("/doors")
@view("doors.html")
def doors(db):
    return {"doors":[]}
