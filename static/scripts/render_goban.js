function renderGoban(cursor) {
    var goban_div = document.getElementById("goban");

    for (var row = cursor[1] - 6; row < cursor[1] + 7; row++) {
        for (var col = cursor[0] - 6; col < cursor[0] + 7; col++) {
            var loc = document.createElement("div");
    
            loc.setAttribute("id", "x" + col + "y" + row);
            if (row % 6 == 0 && col % 6 == 0) {
                // The location is a star-point.
                loc.setAttribute("class", "hoshi");
            } else {
                loc.setAttribute("class", "location");
            }

            loc.setAttribute("onClick", "location = '/?x=" + col + "&y=" + row + "';");
    
            goban_div.appendChild(loc);
        }
    }
}

function renderStones(stones) {
    // Decide a player coloring for the stones.
    var players = [];
    Object.values(stones).forEach((value) => {
        if (!players.includes(value["player"])) {
            players.push(value["player"]);
        }
    });

    // Create a DOM element for each stone.
    Object.keys(stones).forEach((key) => {
        var coords = key.split(" ");
        var id = "x" + coords[0] + "y" + coords[1];
        var loc = document.getElementById(id);
        var stone = document.createElement("div");
        stone.setAttribute("class", "stone");
        stone.setAttribute(
            "style",
            "background-color: " + color_code[players.indexOf(stones[key]["player"])]
        );
        loc.appendChild(stone);
    });
}