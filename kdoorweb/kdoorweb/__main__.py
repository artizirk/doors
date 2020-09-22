import sys
from . import application


def print_help():
    print("K-Door webserver")
    print(f"Usage: {sys.argv[0]} [PORT|initdb|import_ookean]")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd in {"-h", "--help"}:
            print_help()
        elif cmd == "initdb":
            from .db import initdb
            initdb()
            sys.exit(0)
        elif cmd == "import_ookean":
            from .db import import_ookean
            import_ookean()
            sys.exit(1)
        else:
            try:
                port = int(sys.argv[1])
            except ValueError:
                print_help()
    else:
        port = 8080
    application.run(host='127.0.0.1', port=port)
