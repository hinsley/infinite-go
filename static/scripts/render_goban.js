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

            if (row == cursor[1] && col == cursor[0]) {
                var overlay = document.createElement("div");
                overlay.setAttribute("class", "cursor-overlay");
                loc.appendChild(overlay);
            }

            goban_div.appendChild(loc);
        }
    }
}

function renderStones(stones) {
    // Decide a player coloring for the stones.
    var players = [];
    Object.values(stones).forEach((value) => {
        if (!players.includes(value["player_name"])) {
            players.push(value["player_name"]);
        }
    });
    
    // Sort the players array by user ID.
    players.sort();

    // Create color legend entries.
    for (var i = 0; i < players.length; i++) {
        var legendEntry = document.createElement("div");
        legendEntry.setAttribute("class", "legend-entry")

        var colorIcon = document.createElement("div");
        colorIcon.setAttribute("class", "color-icon");
        colorIcon.setAttribute(
            "style",
            "background-color: " + color_code[i] + ";"
        );

        legendEntry.appendChild(colorIcon);

        // Add the player name to the legend entry.
        legendEntry.append(" " + players[i]);

        document.getElementById("color-legend").appendChild(legendEntry);
    }

    // Create a DOM element for each stone.
    Object.keys(stones).forEach((key) => {
        // Create a DOM element for the stone on the board.
        var coords = key.split(" ");
        var id = "x" + coords[0] + "y" + coords[1];
        var loc = document.getElementById(id);
        var stone = document.createElement("div");
        stone.setAttribute("class", "stone");
        stone.setAttribute(
            "style",
            "background-color: " + color_code[players.indexOf(stones[key]["player_name"])] + ";"
        );
        
        // Create an emblem indicating the locking status of the stone.
        var emblem = document.createElement("div");
        if (stones[key]["status"] == "Locked") {
            emblem.setAttribute("class", "lockedEmblem");
        } else if (stones[key]["status"] == "Self-Locked") {
            emblem.setAttribute("class", "selfLockedEmblem");
        }
        stone.appendChild(emblem);

        loc.appendChild(stone);
    });
}