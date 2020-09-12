import sys
from . import application

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    application.run(host='127.0.0.1', port=port)
