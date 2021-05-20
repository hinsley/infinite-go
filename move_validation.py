from typing import Tuple

import stone_db

def check_valid_move(player: int, cursor: Tuple[int, int]) -> bool:
    """
    Returns True if valid, False otherwise.
    """
    local_stones = stone_db.retrieve_region(*cursor)

    # Since local_stones is a dict, this is O(1).
    if cursor in local_stones:
        # The position is already occupied by a stone.
        return False

    if len(local_stones) == 0:
        # There must be stones nearby.
        return False
    
    locked_stones_owner = None
    for stone in local_stones.values():
        if stone["status"] == "Locked":
            if player == stone["player"]:
                # Locked stones in the local region must not belong to the player.
                return False
            if locked_stones_owner is None:
                locked_stones_owner = stone["player"]
            elif locked_stones_owner != stone["player"]:
                # Locked stones in the local region may belong to at most one player.
                return False
        elif stone["status"] == "Self-Locked" and player != stone["player"]:
            # Any self-locked stones present in the local region must belong to the player.
            return False

    return True

def evolve_status(stone_pos):
    """
    Performs any necessary updates on the status of a stone
    which has been played nearby.
    
    Note that this does not check if a stone at the supplied
    location exists.
    
    As this feature concerns itself with stone locking status,
    it is considered to be related to move validation.
    """
    stone = stone_db.get_stone(*stone_pos)
    stone_db.update_status(stone["id"], {
        "Locked": "Self-Locked",
        "Self-Locked": "Unlocked",
        "Unlocked": "Unlocked",
    }[stone["status"]])
