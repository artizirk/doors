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
        if type(dbfile) is DB:
            db = dbfile.db
        else:
            db = sqlite3.connect(dbfile)
        db.executescript("""
            create table versions (
                version integer,
                upgraded text
            );
            create table users (
                id integer primary key,
                distinguished_name text unique,
                user text unique,
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
                name text unique,
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
                log_msg text,

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
            insert into users(distinguished_name, user, full_name, email, disabled, admin)
            values(?, ?, ?, ?, ?, ?)
        """, users)
        self.db.commit()

    def list_users(self):
        cur = self.db.execute("""
            select users.id, users.user , users.full_name, users.email, users.disabled, count(k.id) as cards from users
            left join keycards k on users.id = k.user_id group by users.id order by users.disabled
        """
        )
        return cur.fetchall()

    def get_user(self, user_id):
        cur = self.db.execute(
            "select id, distinguished_name, user, full_name, email, admin, disabled from users where id = ?",
            (user_id, )
        )
        return cur.fetchone()

    def get_user_by_name(self, user_name):
        cur = self.db.execute(
            "select id, distinguished_name, user, full_name, email, admin, disabled from users where user = ?",
            (user_name, )
        )
        return cur.fetchone()

    def add_keycard(self, user_id, card_uid, name):
        self.add_keycards([(user_id, card_uid, name)])

    def add_keycards(self, keycards):
        self.db.executemany("""
                    insert into keycards(user_id, card_uid, name)
                    values(?, ?, ?)
                """, keycards)
        self.db.commit()

    def get_user_keycards(self, user_id):
        cur = self.db.execute("select id, name, created, disabled from keycards where user_id = ?", (user_id,))
        return cur.fetchall()

    def list_all_keycards(self):
        cur = self.db.execute("""
            select
                users.id as user_id,
                users.user as user,
                users.full_name as full_name,
                k.id as card_id,
                k.card_uid as card_uid
            from users
            join
                keycards k on users.id = k.user_id
            where
                (users.disabled = 0 or users.disabled is null)
            and
                (k.disabled is 0 or k.disabled is null)
        """)
        return cur.fetchall()

    def add_door(self, name, note, api_key):
        self.add_doors([name, note, api_key, ])

    def add_doors(self, doors):
        self.db.executemany("""
                    insert into doors(name, note, api_key, created, disabled)
                    values(?, ?, ?, ?, ?)
                """, doors)
        self.db.commit()

    def get_door(self, door_id):
        cur = self.db.execute("select id, name, note, api_key, created, disabled from doors where id = ?", (door_id,))
        return cur.fetchone()

    def get_door_by_name(self, name):
        cur = self.db.execute("select id, name, note, api_key, created, disabled from doors where name = ?", (name,))
        return cur.fetchone()

    @staticmethod
    def import_ad(json_file):
        with open(json_file) as fp:
            json_data = json.load(fp)
        for user, fields in json_data.items():
            yield (
                fields.get("distinguished_name"),
                fields.get("username"),
                fields.get("full_name"),
                fields.get("personal_mail"),
                0 if fields.get("considered_active") is True and
                     fields.get("groups", {}).get("floor_access") is not False else 1,
                0 if fields.get("groups",{}).get("onboarding") is False else 1
            )

    def import_ookean(self, json_file):
        unmatched = {}
        with open(json_file) as fp:
            json_data = json.load(fp)
        for user, tokens in json_data.items():
            self.db.execute("PRAGMA case_sensitive_like = true")
            cur = self.db.execute(
                "select id, user, distinguished_name from users where full_name like ?",
                (f"%{user}%",)
            )
            user_row = cur.fetchone()
            if user_row:
                print(f"User {user:20} matched with {user_row['user']:20} ({user_row['distinguished_name']})")

                self.add_keycards(((user_row["id"], card["uid"], card["descr"]) for card in tokens))
            else:
                unmatched[user] = tokens

        print(f"Cound not match {len(unmatched)} users")
        for user in unmatched:
            print(f"User {user}")

    def export_db(self):
        users = {}
        cur = self.db.execute("select id, distinguished_name, user, full_name, email, disabled, admin from users")
        for user in cur.fetchall():
            users[user["full_name"]] = dict(user)
            del users[user["full_name"]]["id"]
            cards_cur = self.db.execute(
                "select card_uid, name, created, disabled from keycards where user_id = ?",
                (user["id"],)
            )
            users[user["full_name"]]["keycards"] = [dict(keycard) for keycard in cards_cur.fetchall()]
        return users


def initdb():
    dbfile = "kdoorweb.sqlite"
    import os, sys
    from pprint import pprint
    try:
        os.unlink(dbfile)
    except FileNotFoundError:
        pass
    DB.create_db(dbfile)
    db = DB(dbfile)
    db.add_users(db.import_ad("ad.json"))
    users = db.list_users()
    for user in users:
        print(dict(user))


def import_ookean():
    dbfile = "kdoorweb.sqlite"
    db = DB(dbfile)
    db.import_ookean("../contrib/ookean_cards.json")


def export_db():
    dbfile = "kdoorweb.sqlite"
    db = DB(dbfile)
    import sys
    exports = db.export_db()
    json.dump(exports, sys.stdout, indent=2)
    sys.stdout.write("\n")



if __name__ == "__main__":
    initdb()
