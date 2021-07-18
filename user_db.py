from flask import session

import errno
import hashlib
import json
import os
import re
import sqlite3
from time import time

from typing import List, Optional

with open("config.json") as f:
    cfg = json.load(f)

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
        cur.execute("""INSERT INTO users (
            username,
            email,
            registered_time,
            last_login_time,
            password_hash
        ) VALUES (?, ?, ?, ?, ?);""",
        [
            username,
            email,
            registered_time,
            registered_time,
            hash_password(password)
        ])

def get_user_info(user_id: int, *fields: List[str]):
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT {", ".join(fields)} FROM users WHERE id = ?""", [user_id])

        return cur.fetchone()

def get_user_id_from_email(email: str) -> int:
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("SELECT id FROM users WHERE email = ?", [email])
        
        result = cur.fetchone()
        if result is None:
            return None
        
        return result[0]

def get_user_id_from_username(username: str) -> int:
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("SELECT id FROM users WHERE username = ?", [username])
        
        return cur.fetchone()[0]

def hash_password(password: Optional[str]) -> str:
    if password is None: # For SAI.
        return ""

    salted_password = password + cfg["password salt"]
    return hashlib.sha256(bytes(salted_password, "utf-8")).hexdigest()

def update_password(user_id: int, new_password: str):
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("""UPDATE users SET password_hash = ? WHERE id = ?""",
        [
            hash_password(new_password),
            user_id
        ])

def validate_email(email: str) -> bool:
    """
    Returns True if valid, False if invalid.
    """
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)

def validate_password(password: str) -> bool:
    """
    Returns True if valid, False if invalid.
    """
    return re.fullmatch(r"[A-Za-z0-9@#$%^&+=]{8,30}", password) is not None

def validate_username(username: str) -> bool:
    """
    Returns True if valid, False if invalid.
    """
    return re.fullmatch(r"[a-z0-9_]{3,16}", username) is not None

# Create a `data/` directory if it does not exist.
try:
    os.makedirs("data")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

with sqlite3.connect(db_file) as db:
    cur = db.cursor()

    # Check whether the users table exists.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' and name='users'")
    
    # If not, create it and insert the SAI user.
    if cur.fetchall() == []:
        cur.execute("""CREATE TABLE users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT NOT NULL,
            email           TEXT,
            registered_time REAL NOT NULL,
            last_login_time REAL NOT NULL,
            password_hash   TEXT
        )""")

        create_user(username="SAI", email=None, password=None)
