# main.py

LOCAL_REGION_SIZE = 13

cursor = (0, 0)

board = {
    (0, 0): {
        "player": "GOD",
        "status": "unlocked",
    }
}

def draw(board, cursor_coords):
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
            
            coords = cursor_coords[0] + col, cursor_coords[1] + row
            # Draw stone-place position.
            if coords not in board:
                drawing += "+"
            elif board[coords]["status"] == "unlocked":
                drawing += "o"
            elif board[coords]["status"] == "locked":
                drawing += "x"
            elif board[coords]["status"] == "self-locked" and board[coords]["status"] != "YOU (CHANGE THIS TO ACTUALLY CHECK WHETHER IT'S YOURS)":
                drawing += "X"
            else:
                drawing += "!"
        drawing += "-\n"
    print(drawing)

def handle_command(cursor, command):
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
    elif words[0] == "place":
        stone_pos = cursor if len(words) == 1 else (int(words[1]), int(words[2]))
        if stone_pos in board:
            print(f"You cannot place a stone at {stone_pos}, as there is another already present.")
        else:
            board[stone_pos] = {
                "player": "You",
                "status": "locked",
            }

    return cursor

if __name__ == "__main__":
    while True:
        draw(board, cursor)
        print(cursor)
        try:
            print(board[cursor])
        except KeyError:
            pass
        cursor = handle_command(cursor, input("> ").strip())