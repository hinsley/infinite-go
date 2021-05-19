import errno
import os
import sqlite3
from time import time

db_file = "data/database.db"

def place_stone(player, x, y):
    """
    Places a stone by the specified player at a particular location.
    Note: This does not check if another stone already exists there.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        placement_time = time()
        cur.execute(f"""INSERT INTO stones (
            x,
            y,
            player,
            placement_time,
            last_status_change_time,
            status
        ) VALUES (
            {x},
            {y},
            {repr(player)},
            {placement_time},
            {placement_time},
            'Locked'
        );""")

def remove_stone(x, y):
    """
    Removes any stone at the specified location.
    Note: Does not throw errors when the stone does not exist.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""DELETE FROM stones WHERE x = {x} AND y = {y};""")

def retrieve_region(x, y):
    """
    Retrieves all stones in the 13x13 local region centered at the provided
    coordinates.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT * FROM stones WHERE
            (x BETWEEN {x-6} AND {x+6}) AND
            (y BETWEEN {y-6} AND {y+6});""")
        
        return cur.fetchall()

def update_status(stone_id: int, status: str):
    """
    Modifies the status of the specified stone.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        update_time = time()
        cur.execute(f"""UPDATE stones SET
            status = {repr(status)},
            last_status_change_time = {update_time}
        WHERE
            id = {stone_id};""")

# Create a `data/` directory if it does not exist.
try:
    os.makedirs("data")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

with sqlite3.connect(db_file) as db:
    cur = db.cursor()

    # Check whether the stones table exists.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' and name='stones';")
    
    # If not, create it and place the first (unlocked) stone.
    if cur.fetchall() == []:
        cur.execute("""CREATE TABLE stones (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            x                       INTEGER NOT NULL,
            y                       INTEGER NOT NULL,
            player                  TEXT NOT NULL,
            placement_time          REAL NOT NULL,
            last_status_change_time REAL NOT NULL,
            status                  TEXT NOT NULL
        );""")

        place_stone("GOD", 0, 0)
        update_status(1, "Unlocked")
