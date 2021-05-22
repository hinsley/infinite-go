from flask import Flask, render_template, request, session
import json

import user_db
import stone_db

import move_validation
import captures

with open("config.json") as f:
    cfg = json.load(f)

app = Flask(__name__)
app.secret_key = cfg["secret key"]

@app.route("/", methods=["GET"])
def index():
    """
    The page where the game is actually played. We need to send 3 items to
    the client in an JSON object:
    - Cursor coordinates (obtained from GET data),
    - All data associated with any nearby stones, and
    - The logged-in username.
    """
    try:
        cursor = [int(request.args["x"]), int(request.args["y"])]
    except KeyError:
        cursor = [0, 0]

    selected_stones = stone_db.retrieve_region(*cursor)
    # We need to pass the player names and scores for each stone to the client as well.
    # CODESMELL
    player_names = {}
    player_scores = {}
    for coords in selected_stones:
        # Perform cacheing so we don't have to access the database multiple times per player.
        if selected_stones[coords]["player"] not in player_names:
            player_names[selected_stones[coords]["player"]] = user_db.get_user_info(selected_stones[coords]["player"], "username")[0]
            player_scores[selected_stones[coords]["player"]] = stone_db.player_score(selected_stones[coords]["player"])
        selected_stones[coords]["player_name"] = player_names[selected_stones[coords]["player"]]
        selected_stones[coords]["player_score"] = player_scores[selected_stones[coords]["player"]]
    
    # Make the indices comprehensible to Javascript (it can't accept tuples for keys).
    stones = {" ".join(map(str, stone)): selected_stones[stone] for stone in selected_stones}

    return render_template("index.html",
                           username=(user_db.get_user_info(session["user"], "username")[0] if "user" in session else None),
                           score=f"{stone_db.player_score(session['user']):,}" if "user" in session else None,
                           cursor=cursor,
                           stones=stones)

@app.route("/go", methods=["GET"])
def go():
    """
    This is where stone placement requests are submitted.
    Full validation and board updating is done here.
    """
    x = int(request.args.get("x"))
    y = int(request.args.get("y"))

    if move_validation.check_valid_move(session["user"], (x, y)):
        local_stones = stone_db.retrieve_region(x, y)
        for stone_pos in local_stones:
            move_validation.evolve_status(stone_pos)
        stone_db.place_stone(session["user"], x, y)
        captures.perform_captures((x, y))
    else:
        pass # TODO: Add error messages.

    # TODO: Replace with `redirect` once that works.
    return render_template("redirect.html", to=f"/?x={x}&y={y}")

@app.route("/login")
def login():
    """
    Login form page.
    """
    return render_template("login.html")

@app.route("/process-login", methods=["POST"])
def process_login():
    """
    Processes the results of the login form.
    """
    
    # Validate credentials.
    if not user_db.validate_username(request.form["username"].lower()):
        # Invalid username.
        # TODO: Add error message.
        return render_template("redirect.html", to="/login")

    if not user_db.validate_password(request.form["password"]):
        # Invalid password.
        # TODO: Add error message.
        return render_template("redirect.html", to="/login")

    # TODO: Check if the username even exists.
    user_id = user_db.get_user_id_from_username(request.form["username"].lower())
    stored_password_hash = user_db.get_user_info(user_id, "password_hash")[0]

    # Check that the password is correct.
    if user_db.hash_password(request.form["password"]) == stored_password_hash:
        user_db.login(user_id)
        # TODO: Replace with `redirect` once that works.
        return render_template("redirect.html", to="/")
    else:
        # TODO: Add an invalid password error message.
        # TODO: Replace with `redirect` once that works.
        return render_template("redirect.html", to="/login")

@app.route("/logout")
def logout():
    """
    Logs the user out.
    """
    user_db.logout()

    # TODO: Replace with `redirect` once that works.
    return render_template("redirect.html", to="/")

@app.route("/register")
def register():
    """
    Registration form page.
    """
    return render_template("register.html")

@app.route("/process-registration", methods=["POST"])
def process_registration():
    """
    Processes the results of the registration form, creating a new
    user in the database.
    """
    # Perform validation.
    if not user_db.validate_username(request.form["username"].lower()):
        # Invalid username.
        # TODO: Add error message.
        return render_template("redirect.html", to="/register")
    
    if not user_db.validate_email(request.form["email"]):
        # Invalid email address.
        # TODO: Add error message.
        return render_template("redirect.html", to="/register")

    if not user_db.validate_password(request.form["password"]):
        # Invalid password.
        # TODO: Add error message.
        return render_template("redirect.html", to="/register")
    
    # TODO: Check whether the user already exists.

    user_db.create_user(request.form["username"].lower(), request.form["email"], request.form["password"])

    # Log in as the newly-registered user.
    user_db.login(user_db.get_user_id_from_username(request.form["username"].lower()))

    return render_template("redirect.html", to="/")
