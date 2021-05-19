# cli_demo.py

LOCAL_REGION_SIZE = 13

cursor = (0, 0)
player = "Alice"

board = {
    (0, 0): {
        "player": "GOD",
        "status": "unlocked",
    }
}

def check_captures(board, stone_pos):
    """
    Checks if any captures have occurred (including suicide) and
    returns the new board state.
    The current implementation is rather slow as it does not
    perform any liberty cacheing. There is an obvious significant
    optimization available.
    """
    
    def check_captured(board, stone_in_group):
        """
        Checks if a group associated with a particular stone has
        run out of liberties. Returns the set of stones in that
        group as well as a boolean indicating whether the group
        has been captured. If the group has not been captured, that
        means that a liberty has been found, and the returned group
        set may not actually contain all stones within the group, as
        short-circuiting is performed.
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

        player = board[stone_in_group]["player"]
        # Checked stones.
        group = {stone_in_group}
        # Locations remaining to be checked.
        unchecked = new_adjacents(group, stone_in_group)

        while unchecked != set():
            # Grab a random element of the unchecked set.
            to_check = unchecked.pop()
            if to_check not in board: # A liberty has been found!
                return group, False
            else: # The location contains a stone.
                if board[to_check]["player"] == player: # The stone belongs to the group being checked.
                    group.add(to_check)
                    # `|` is the set union operator.
                    unchecked = unchecked | new_adjacents(group, to_check)
        
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
        print(remaining_to_check)
        to_check = remaining_to_check.pop()
        if to_check not in board: # We don't want to check empty locations.
            continue
        group, captured = check_captured(board, to_check)
        if captured:
            captured_something = True
            for stone in group:
                del board[stone]
                try:
                    # Remove the stone from those which remain to be checked,
                    # so that it is not redundantly checked.
                    remaining_to_check.remove(stone)
                except KeyError: # Stone not in remaining_to_check.
                    pass
    # Second stage: Checking suicide.
    if not captured_something:
        group, captured = check_captured(board, stone_pos)
        if captured:
            for stone in group:
                del board[stone]

    return board

def draw(board, player, cursor_coords):
    """
    Draw the local region.
    """
    
    drawing = ""
    for row in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
        for col in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
            # Draw cursor brackets.
            if row == 0:
                if col == 0:
                    drawing += "["
                elif col == 1:
                    drawing += "]"
                else:
                    drawing += "-"
            # Draw divider lines.
            else:
                drawing += "-"
            
            coords = (cursor_coords[0] + col, cursor_coords[1] + row)
            # Draw stone-place position.
            if coords not in board:
                drawing += "+"
            elif board[coords]["status"] == "unlocked":
                drawing += board[coords]["player"][0].lower()
            elif board[coords]["status"] == "locked":
                drawing += board[coords]["player"][0]
            elif board[coords]["status"] == "self-locked" and board[coords]["player"] != player:
                drawing += "?"
            else:
                drawing += "!"
        drawing += "-\n"
    print(drawing)

def handle_command(board, player, cursor, command):
    # TODO: Yes, I know that this control flow is unbecoming. I
    # will make a separate module for this later.
    words = command.split()
    if words[0] == "up":
        units = 1 if len(words) == 1 else int(words[1])
        cursor = (cursor[0], cursor[1] - units)
    elif words[0] == "right":
        units = 1 if len(words) == 1 else int(words[1])
        cursor = (cursor[0] + units, cursor[1])
    elif words[0] == "down":
        units = 1 if len(words) == 1 else int(words[1])
        cursor = (cursor[0], cursor[1] + units)
    elif words[0] == "left":
        units = 1 if len(words) == 1 else int(words[1])
        cursor = (cursor[0] - units, cursor[1])
    elif words[0] == "move":
        cursor = (int(words[1]), int(words[2]))
    elif words[0] == "player":
        player = words[1].capitalize()
    elif words[0] == "place":
        stone_pos = cursor if len(words) == 1 else (int(words[1]), int(words[2]))
        
        # Check placement criteria.
        valid_move = True

        # Check that the stone is being placed in an empty location.
        if stone_pos in board:
            valid_move = False
            print(f"You cannot place a stone at {stone_pos}, as there is another already present.")

        # Iterate over the local region, checking the relevant locking and existence criteria.
        stone_in_region = False
        nearby_locked_stone = None
        nearby_self_locked_stones = []
        for row in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
            for col in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
                coords = (stone_pos[0] + row, stone_pos[1] + col)
                if coords in board:
                    stone_in_region = True
                    # Check if the stone is locked.
                    if board[coords]["status"] == "locked":
                        # Check if the locked stone belongs to the player.
                        if board[coords]["player"] == player:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as you have a locked stone at {coords}.")
                        # Store the coordinates of the locked stone.
                        elif nearby_locked_stone is None:
                            nearby_locked_stone = coords
                        # Check that the locked stone threshold has not been met.
                        elif board[nearby_locked_stone]["player"] != board[coords]["player"]:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as there are locked stones belonging to more than one player in the local region.")
                    # Check if the stone is self-locked.
                    elif board[coords]["status"] == "self-locked":
                        # Check if the self-locked stone belongs to the player.
                        if board[coords]["player"] == player:
                            nearby_self_locked_stones.append(coords)
                        else:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as there is a self-locked stone at {coords} belonging to {board[coords]['player']}.")

        # Check whether there is another stone in the local region.
        if not stone_in_region:
            valid_move = False
            print(f"You cannot place a stone at {stone_pos}, as there is no other stone present in the local region.")

        # If valid, place stone.
        if valid_move:
            if nearby_locked_stone is not None:
                board[nearby_locked_stone]["status"] = "self-locked"
            for coords in nearby_self_locked_stones:
                board[coords]["status"] = "unlocked"
            board[stone_pos] = {
                "player": player,
                "status": "locked",
            }
            board = check_captures(board, stone_pos)

    return board, player, cursor

if __name__ == "__main__":
    while True:
        draw(board, player, cursor)
        print(cursor)
        try:
            print(f"Stone at cursor: {str(board[cursor])}")
        except KeyError:
            pass
        try:
            board, player, cursor = handle_command(board, player, cursor, input(f"<{player}> ").strip())
        except IndexError:
            print("Your command elicited an IndexError.")
        except ValueError:
            print("Your command elicited a ValueError.")