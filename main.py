# main.py

LOCAL_REGION_SIZE = 13

cursor = (0, 0)
player = "Alice"

board = {
    (0, 0): {
        "player": "GOD",
        "status": "locked",
    }
}

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
                drawing += "o"
            elif board[coords]["status"] == "locked":
                drawing += "x"
            elif board[coords]["status"] == "self-locked" and board[coords]["player"] != player:
                drawing += "X"
            else:
                drawing += "!"
        drawing += "-\n"
    print(drawing)

def handle_command(player, cursor, command):
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
        locked_stones = 0
        for row in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
            for col in range(-LOCAL_REGION_SIZE // 2 + 1, LOCAL_REGION_SIZE // 2 + 1):
                coords = (stone_pos[0] + row, stone_pos[1] + col)
                if coords in board:
                    stone_in_region = True
                    # Check if the stone is locked.
                    if board[coords]["status"] == "locked":
                        locked_stones += 1
                        # Check if the locked stone belongs to the player.
                        if board[coords]["player"] == player:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as you have a locked stone at {coords}.")
                        # Check that the locked stone threshold has not been met.
                        if locked_stones > 1:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as there are multiple locked stones in the local region.")
                    # Check if the stone is self-locked.
                    elif board[coords]["status"] == "self-locked":
                        # Check if the self-locked stone belongs to the player.
                        if board[coords]["player"] != player:
                            valid_move = False
                            print(f"You cannot place a stone at {stone_pos}, as there is a self-locked stone at {coords} belonging to {board[coords]['player']}.")

        # Check whether there is another stone in the local region.
        if not stone_in_region:
            valid_move = False
            print(f"You cannot place a stone at {stone_pos}, as there is no other stone present in the local region.")

        # If valid, place stone.
        if valid_move:
            board[stone_pos] = {
                "player": player,
                "status": "locked",
            }

    return player, cursor

if __name__ == "__main__":
    while True:
        draw(board, player, cursor)
        print(cursor)
        try:
            print(f"Stone at cursor: {str(board[cursor])}")
        except KeyError:
            pass
        player, cursor = handle_command(player, cursor, input(f"<{player}> ").strip())