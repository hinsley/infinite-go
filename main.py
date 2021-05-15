# main.py

LOCAL_REGION_SIZE = 13

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

if __name__ == "__main__":
    draw(board, (0, 0))