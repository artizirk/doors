import os
import secrets

from bottle import Bottle, view, TEMPLATE_PATH, static_file, \
    request, redirect, response

application = app = Bottle()

# TODO: Could be replaced with importlib.resources
TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), "views"))
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

COOKIE_KEY = secrets.token_bytes(32)


def check_auth(callback):
    def wrapper(*args, **kwargs):
        user = request.get_cookie("user", key=COOKIE_KEY)
        if user:
            print(f"logged in as {user}")
            return callback(*args, **kwargs)
        else:
            print("not logged in")
            response.set_cookie("error", "Not logged in")
            redirect("/login")
    return wrapper


app.install(check_auth)


@app.route('/static/<path:path>', skip=[check_auth])
def callback(path):
    return static_file(path, root=STATIC_PATH)


@app.route("/", skip=[check_auth])
def index():
    redirect("/login")


@app.route('/login', skip=[check_auth])
@view("login.html")
def login():
    error = request.get_cookie("error")
    if error:
        response.set_cookie("error", "")
    return {"error": error}


@app.post('/login', skip=[check_auth])
def do_login():
    print(dict(request.forms))
    user = request.forms.get("user")
    print(f"user {user}")
    if user:
        response.set_cookie("user", user, key=COOKIE_KEY)
        redirect("/list")
    else:
        response.set_cookie("error", "No user")
        redirect("/login")


@app.route("/logout")
def logout():
    response.set_cookie("user", "", key=COOKIE_KEY)
    redirect("/login")


@app.route("/list")
@view("list.html")
def list():
    return {}


@app.route("/log")
@view("log")
def log():
    return {}
