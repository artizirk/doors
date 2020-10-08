import hashlib
from functools import partial

from bottle import Bottle, request, response, HTTPError


api = Bottle()

scrypt = partial(hashlib.scrypt, n=16384, r=8, p=1)


def check_api_auth(callback):
    def wrapper(*args, **kwargs):
        print("check api auth")
        user, api_key = request.auth or (None, None)
        if "db" not in kwargs:
            return "Auth not possible, db not available"
        user = kwargs["db"].get_door_by_name_and_api_key(user) or {}
        stored_hash, salt = dict(user).get("api_key", ":").split(":")
        api_hash = scrypt(api_key, salt=salt)
        if user and api_hash  == api_key:
            request.current_door = user
            print(f"logged in as {user['name']}")
            print(user)
            return callback(*args, **kwargs)
        else:
            print("not logged in")
            return "Invalid authentication"
    return wrapper


@api.route("/")
def index():
    return "api v1"

@api.route("/cards")
def api_list_cards(db):
    return {"keycards":[dict(card) for card in db.list_all_keycards()]}
