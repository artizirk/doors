from bottle import Bottle, request, response


api = Bottle()


# FIXME: Fix door api auth
def check_api_auth(callback):
    def wrapper(*args, **kwargs):
        print("check api auth")
        if "db" not in kwargs:
            request.current_user = None
            return callback(*args, **kwargs)
        user = None
        request.current_user = user
        if user:
            print(f"logged in as {user['user']}")
            print(request.current_user)
            return callback(*args, **kwargs)
        else:
            print("not logged in")
            return "Invalid authentication"
    return wrapper

# FIXME: db plugin not available yet
api.install(check_api_auth)

@api.route("/")
def index():
    return "api v1"

@api.route("/cards")
def api_list_cards(db):
    return {"keycards":[dict(card) for card in db.list_all_keycards()]}
