import datetime
import sqlite3

SCHEMA_VERSION = 1


class DB:

    def __init__(self, dbfile=":memory:"):
        self.dbfile = dbfile
        self.db = sqlite3.connect(self.dbfile)

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
                real_name text,
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

    def list_users(*, page=0, count=20, query=None):
        pass

    def add_user(self, user, real_name=None, email=None, disabled=False, admin=False):
        self.add_users([(
            user, real_name, email, disabled, admin
        )])

    def add_users(self, users):
        self.db.executemany("""
        insert into users(user, real_name, email, disabled, admin)
        values(?, ?, ?, ?, ?)
        """, users)
        self.db.commit()




if __name__ == "__main__":
    #DB.create_db("kdoorweb.sqlite")
    db = DB("kdoorweb.sqlite")
    db.add_user("juku")
