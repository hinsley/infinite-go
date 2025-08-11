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
    
    for stone in local_stones.values():
        if stone["status"] == "Locked" and player == stone["player"]:
            # Locked stones in the local region must not belong to the player.
            return False
        elif stone["status"] == "Pending" and player != stone["player"]:
            # Any pending stones present in the local region must belong to the player.
            return False

    return True


def evolve_status(stone_pos: Tuple[int, int], stone_row: dict) -> None:
    """
    Performs any necessary updates on the status of a stone
    which has been played nearby.
    
    Note that this does not check if a stone at the supplied
    location exists.
    
    As this feature concerns itself with stone locking status,
    it is considered to be related to move validation.
    """
    if not stone_row:
        return

    current_status = stone_row.get("status")
    next_status = {
        "Locked": "Pending",
        "Pending": "Unlocked",
        "Unlocked": "Unlocked",
    }[current_status]

    # Only write and log an event if the status actually changes
    if next_status != current_status:
        stone_db.update_status(stone_row["id"], next_status)
