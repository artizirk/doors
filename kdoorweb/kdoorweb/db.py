import datetime
import sqlite3
import inspect
import json
from bottle import HTTPError

SCHEMA_VERSION = 1


class SQLitePlugin:

    name = "sqlite"
    api = 2

    def __init__(self, dbfile):
        self.dbfile = dbfile

    def apply(self, callback, context):
        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.signature(context.callback).parameters
        if "db" not in args:
            return callback

        def wrapper(*args, **kwargs):
            db = DB(self.dbfile)
            # Add the connection handle as a keyword argument.
            kwargs["db"] = db
            try:
                rv = callback(*args, **kwargs)
            except sqlite3.IntegrityError as e:
                db.db.rollback()
                raise HTTPError(500, "Database Error", e)
            finally:
                db.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper


class DB:

    def __init__(self, dbfile=":memory:"):
        self.dbfile = dbfile
        self.db = sqlite3.connect(self.dbfile)
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()

    @staticmethod
    def create_db(dbfile):
        db = sqlite3.connect(dbfile)
        db.executescript("""
            create table versions (
                version integer,
                upgraded text
            );
            create table users (
                id integer primary key,
                user text,
                full_name text,
                email text,
                disabled integer,
                admin integer
            );
            create table keycards (
                id integer primary key,
                user_id integer,
                card_uid blob,
                name text,
                created text,
                disabled integer,

                foreign key (user_id)
                    references users (id)
                    on delete cascade
            );
            create table doors (
                id integer primary key,
                name text,
                note text,
                api_key text,
                created text,
                disabled integer
            );
            create table door_log (
                id integer primary key,
                timestamp integer,
                door_id integer,
                keycard_id integer,
                user_id integer,

                foreign key (door_id)
                    references doors (id)
                    on delete set null,
                foreign key (user_id)
                    references users (id)
                    on delete set null,
                foreign key (keycard_id)
                    references keycards (id)
                    on delete set null
            )
        """)
        db.execute(
            "insert into versions (version, upgraded) values (?, ?)",
            (SCHEMA_VERSION, str(datetime.datetime.now()))
        )
        db.commit()

    def add_user(self, user, full_name=None, email=None, disabled=False, admin=False):
        self.add_users([(
            user, full_name, email, int(disabled), int(admin)
        )])

    def add_users(self, users):
        self.db.executemany("""
        insert into users(user, full_name, email, disabled, admin)
        values(?, ?, ?, ?, ?)
        """, users)
        self.db.commit()

    def list_users(self):
        cur = self.db.execute(
            "select id, user, full_name, email from users"
        )
        return cur.fetchall()

    def get_user(self, user_id):
        cur = self.db.execute(
            "select * from users where id = ?",
            (user_id, )
        )
        return cur.fetchone()

    def get_user_by_name(self, user_name):
        cur = self.db.execute(
            "select * from users where user = ?",
            (user_name, )
        )
        return cur.fetchone()

    @staticmethod
    def import_ad(json_file):
        with open(json_file) as fp:
            json_data = json.load(fp)
        for user, fields in json_data.items():
            if fields.get("considered_active", False) and \
                    fields.get("groups", {}).get("floor_access", False):
                yield (
                    user,
                    fields.get("full_name"),
                    fields.get("personal_mail"),
                    0,
                    int(fields.get("groups",{}).get("onboarding", False))
                )






if __name__ == "__main__":
    dbfile = "../kdoorweb.sqlite"
    import os, sys
    from pprint import pprint
    try:
        os.unlink(dbfile)
    except FileNotFoundError:
        pass
    DB.create_db(dbfile)
    db = DB(dbfile)
    db.add_users(db.import_ad("../ad.json"))
    users = db.list_users()
    for user in users:
        print(dict(user))
