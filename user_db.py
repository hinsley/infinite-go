from flask import session

import errno
import hashlib
import os
import sqlite3
from time import time

from typing import List, Optional

db_file = "data/database.db"

def login(user_id: int):
    """
    Forces a login as the specified user.
    Does not check whether that user actually exists.
    """
    session["user"] = user_id

def logout():
    """
    Clears the session variable corresponding to logged-in username.
    """
    session.pop("user")

def create_user(username: str, email: str, password: Optional[str]) -> None:
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        registered_time = time()
        cur.execute(f"""INSERT INTO users (
            username,
            email,
            registered_time,
            last_login_time,
            password_hash
        ) VALUES (
            {repr(username)},
            {"NULL" if email is None else repr(email)},
            {registered_time},
            {registered_time},
            {"NULL" if password is None else repr(hash_password(password))}
        );""")

def get_user_info(user_id: int, *fields: List[str]):
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT {", ".join(fields)} FROM users WHERE id = {user_id};""")

        return cur.fetchone()

def get_user_id_from_email(email: str) -> int:
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT id FROM users WHERE email = {repr(email)};""")
        
        return cur.fetchone()[0]

def get_user_id_from_username(username: str) -> int:
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT id FROM users WHERE username = {repr(username)};""")
        
        return cur.fetchone()[0]

def hash_password(password: str) -> str:
    return hashlib.sha256(bytes(password, "utf-8")).hexdigest()

# Create a `data/` directory if it does not exist.
try:
    os.makedirs("data")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

with sqlite3.connect(db_file) as db:
    cur = db.cursor()

    # Check whether the users table exists.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' and name='users';")
    
    # If not, create it and insert the SAI user.
    if cur.fetchall() == []:
        cur.execute("""CREATE TABLE users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT NOT NULL,
            email           TEXT,
            registered_time REAL NOT NULL,
            last_login_time REAL NOT NULL,
            password_hash   TEXT
        );""")

        create_user(username="SAI", email=None, password=None)
