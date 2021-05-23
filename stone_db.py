import errno
import os
import sqlite3
from time import time

from typing import Optional, Tuple

db_file = "data/database.db"

pending_timeout = 3600 # Seconds.

def get_stone(x: int, y: int):
    """
    Retrieves the stone at the specified location. If one does not exist,
    returns None.
    """
    unlock_stale_pending()

    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        try:
            cur.execute(f"""SELECT * FROM stones WHERE x={x} AND y={y};""")
        except:
            return None
        
        entry = cur.fetchone()

        if entry is None:
            return None
        
        return {
            "id":                      entry[0],
            "player":                  entry[3],
            "placement_time":          entry[4],
            "last_status_change_time": entry[5],
            "status":                  entry[6],
        }

def new_pending(user_id: int, since: float) -> bool:
    """
    Determines if there are any new pending stones belonging to the player.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("""SELECT
            *
        FROM
            stones
        WHERE
            player = ? AND
            status = 'Pending' AND
            last_status_change_time > ?;""",
        [user_id, since])

        if cur.fetchone() is None:
            return False # No new pending stone was found.
        
        return True # A pending stone was found.

def next_pending_location(user_id: int, current_coords: Optional[Tuple[int, int]] = None) -> Optional[Tuple[int, int]]:
    """
    Retrieves the next pending stone's coordinates. If current_coords is not specified (or is not pending),
    retrieves the longest-pending stone's coordinates. The order for determining which stone is "next" is
    defined by how long stones have been pending -- successive applications of this function will retrieve
    successively younger pending stones. If there is no younger pending stone, the coordinates of the
    oldest pending stone are returned. If there are no pending stones at all, None is returned.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        current_stone_pending_since = 0 # Will always be older than any stone.
        if current_coords is not None:
            current_stone = get_stone(*current_coords)
            if current_stone is not None and current_stone["player"] == user_id and current_stone["status"] == "Pending":
                # The current stone belongs to the player and is pending.
                current_stone_pending_since = current_stone["last_status_change_time"]
        
        query = """SELECT
            x, y
        FROM
            stones
        WHERE
            player = ? AND
            status = 'Pending' AND
            last_status_change_time > ?
        ORDER BY
            last_status_change_time ASC;"""
        
        cur.execute(query, [user_id, current_stone_pending_since])

        next_pending_coords = cur.fetchone()

        # A younger pending stone exists.
        if next_pending_coords is not None:
            return next_pending_coords
        
        # Otherwise, a younger pending stone does not exist.
        
        # Retrieve the oldest stone.
        cur.execute(query, [user_id, 0])

        next_pending_coords = cur.fetchone()

        # Return either the coords of the oldest pending stone, or None if no such stone exists.
        return next_pending_coords

def place_stone(player: int, x: int, y: int):
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
            {player},
            {placement_time},
            {placement_time},
            'Locked'
        );""")

def player_score(user_id: int) -> Optional[int]:
    """
    Counts how many stones belong to the specified player.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("SELECT COUNT(id) FROM stones WHERE player = ?;", [user_id])

        return cur.fetchone()[0]

def remove_stone(x, y):
    """
    Removes any stone at the specified location.
    Note: Does not throw errors when the stone does not exist.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute("DELETE FROM stones WHERE x = ? AND y = ?;", [x, y])

def retrieve_region(x, y):
    """
    Retrieves all stones in the 13x13 local region centered at the provided
    coordinates.
    """
    unlock_stale_pending()

    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        cur.execute(f"""SELECT * FROM stones WHERE
            (x BETWEEN {x-6} AND {x+6}) AND
            (y BETWEEN {y-6} AND {y+6});""")
        
        stone_entries = cur.fetchall()

        stones = {}

        for entry in stone_entries:
            stones[(entry[1], entry[2])] = {
                "player":                  entry[3],
                "placement_time":          entry[4],
                "last_status_change_time": entry[5],
                "status":                  entry[6],
            }

        return stones

def unlock_stale_pending():
    """
    Unlocks every pending stone which has timed out.
    This function should be called beforehand any time
    information about any stone is retrieved.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        unlock_time = time()
        cur.execute("""UPDATE stones SET
            status = 'Unlocked',
            last_status_change_time = ?
        WHERE
            status = 'Pending' AND
            last_status_change_time <= ? - ?;""",
        [unlock_time, unlock_time, pending_timeout])

def update_status(stone_id: int, status: str):
    """
    Modifies the status of the specified stone.
    """
    with sqlite3.connect(db_file) as db:
        cur = db.cursor()

        update_time = time()
        cur.execute("""UPDATE stones SET
            status = ?,
            last_status_change_time = ?
        WHERE
            id = ?;""",
        [status, update_time, stone_id])

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
            player                  INTEGER NOT NULL,
            placement_time          REAL NOT NULL,
            last_status_change_time REAL NOT NULL,
            status                  TEXT NOT NULL
        );""")

        place_stone(1, 0, 0)
        update_status(1, "Unlocked")
