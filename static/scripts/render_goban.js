var goban_div = document.getElementById("goban");

// Render the goban.
for (var row = 0; row < 13; row++) {
    for (var col = 0; col < 13; col++) {
        var loc = document.createElement("div");

        loc.setAttribute("id", "x" + col + "y" + row);
        if (row % 6 == 0 && col % 6 == 0) {
            // The location is a star-point.
            loc.setAttribute("class", "hoshi");
        } else {
            loc.setAttribute("class", "location");
        }

        goban_div.appendChild(loc);
    }
}
