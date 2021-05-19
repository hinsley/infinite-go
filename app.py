from flask import Flask, render_template, request

import stone_db

app = Flask(__name__)

@app.route("/play", methods=["GET"])
def play():
    """
    The page where the game is actually played. We need to send 3 items to
    the client in an JSON object:
    - Cursor coordinates (obtained from GET data),
    - All data associated with any nearby stones, and
    - The logged-in username.
    """
    try:
        cursor = [int(request.args.get("x")), int(request.args.get("y"))]
    except ValueError:
        cursor = [0, 0]

    selected_stones = stone_db.retrieve_region(*cursor)
    stones = {}
    for stone in selected_stones:
        stones[" ".join([str(stone[1]), str(stone[2])])] = {
            "player":  stone[3],
            "placed":  stone[4],
            "updated": stone[5],
            "status":  stone[6],
        }

    return render_template("play.html", cursor=cursor, stones=stones)

@app.route("/go", methods=["GET"])
def go():
    """
    This is where stone placement requests are submitted.
    Full validation and board updating is done here.
    """
    x = int(request.args.get("x"))
    y = int(request.args.get("y"))
    stone_db.place_stone("Alice", x, y)

    # Yeah, I know. This sucks. Bite me. I hate this bit of Flask.
    return render_template("redirect.html", to=f"play?x={x}&y={y}")
