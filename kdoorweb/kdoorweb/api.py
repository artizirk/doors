from bottle import Bottle, request, response, HTTPError
from .utils import check_api_key


api = Bottle()


def check_api_auth(callback):
    def wrapper(*args, **kwargs):
        print("check api auth")
        user, api_key = request.auth or (None, None)
        if "db" not in kwargs:
            return "Auth not possible, db not available"
        user = kwargs["db"].get_door_by_name_and_api_key(user) or {}
        hash_line = dict(user).get("api_key", ":")
        if user and check_api_key(api_key, hash_line):
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
