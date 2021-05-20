from typing import Tuple

import stone_db

def perform_captures(stone_pos):
    """
    Checks if any captures (including suicide) have occurred.
    Note that there is an obvious optimization to this implementation
    using per-group liberty cacheing.
    """
    def check_captured(group_origin: Tuple[int, int]):
        """
        Checks if the group to which the stone at `group_origin` belongs
        has any liberties.

        Returns a 2-tuple comprising firstly a dictionary containing the
        stones in the group and secondly a boolean value indicating whether
        that group is captured.

        If the group is not captured, the stone dictionary returned might
        not be a comprehensive collection.
        """
        def new_adjacents(group, location):
            """
            Takes a group and a location within that group,
            returning a set of all locations adjacent to the
            provided location which do not lie within the group.
            """
            adjacents = {
                (location[0] - 1, location[1]), # North
                (location[0], location[1] + 1), # East
                (location[0] + 1, location[1]), # South
                (location[0], location[1] - 1), # West
            }

            return {adjacent for adjacent in adjacents if adjacent not in group}

        # This dict contains all already-checked stones.
        group = {group_origin: stone_db.get_stone(*group_origin)}
        
        player = group[group_origin]["player"]

        # Locations remaining to be checked.
        unchecked = new_adjacents(group, group_origin)

        while unchecked != set():
            # Grab a random element of the unchecked set.
            checking_location = unchecked.pop()
            checking = stone_db.get_stone(*checking_location)
            
            if checking is None: # A liberty has been found!
                return group, False
            
            if checking["player"] == player: # The stone belongs to the group.
                group[checking_location] = checking
                # `|` is the set union operator.
                unchecked = unchecked | new_adjacents(group, checking_location)
        
        # No liberty was found.
        return group, True

    # First stage: Checking captures.
    remaining_to_check = {
        (stone_pos[0], stone_pos[1] - 1), # North
        (stone_pos[0] + 1, stone_pos[1]), # East
        (stone_pos[0], stone_pos[1] + 1), # South
        (stone_pos[0] - 1, stone_pos[1]), # West
    }

    captured_something = False
    while remaining_to_check != set():
        # Grab a random element of the unchecked set.
        checking_location = remaining_to_check.pop()
        checking = stone_db.get_stone(*checking_location)

        if checking is None: # We don't want to check empty locations.
            continue

        group, captured = check_captured(checking_location)

        if captured:
            captured_something = True
            for stone_location in group:
                stone_db.remove_stone(*stone_location)
                try:
                    # Prevent the stone from being checked redundantly.
                    remaining_to_check.remove(stone_location)
                except KeyError: # Stone not in remaining_to_check.
                    pass
    
    # Second stage: Checking suicide.
    if not captured_something:
        group, captured = check_captured(stone_pos)
        
        if captured:
            for stone_location in group:
                stone_db.remove_stone(*stone_location)
