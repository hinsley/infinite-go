var rulingSpacing = 50; // Pixels (fixed at 1 in world units).
var rulingWidth = 0.01; // World units.
var rulingsPerHoshi = 6; // World units (natural number).
var hoshiRadius = 0.075; // World units.
var stoneRadius = 0.46; // World units.
var stoneStatusRadius = 0.12; // World units.
var stoneOutlineWidth = 0.01; // World units.
var drawRate = 60; // Hz.
var zoomSpeed = 3; // Pixels per scroll unit.

const canvas = document.getElementById("goban");
const ctx = canvas.getContext("2d");

var _x = -0.5;
var _y = -0.5;
// var _x = Math.round(rulingSpacing / 2);
// var _y = Math.round(rulingSpacing / 2);

// Pixel coordinates.
var _x_offset = 0;
var _y_offset = 0;

// Pixel coordinates.
var cursor_x_initial = null;
var cursor_y_initial = null;

var panning = false;

canvas.addEventListener("mousedown", (e) => {
    // Start cursor tracker.
    cursor_x_initial = mouseX(e);
    cursor_y_initial = mouseY(e);
    panning = true;
});

canvas.addEventListener("mousemove", (e) => {
    if (panning) {
        _x_offset = cursor_x_initial - mouseX(e);
        _y_offset = cursor_y_initial - mouseY(e);
    }
});

["mouseup", "mouseleave"].forEach((event_name) => {
    canvas.addEventListener(event_name, () => {
        _x += _x_offset / rulingSpacing;
        _y += _y_offset / rulingSpacing;
        _x_offset = 0;
        _y_offset = 0;
        panning = false;
    });
});

// Zoom event.
canvas.addEventListener("wheel", (e) => {
    // Zoom around the cursor.
    // Store the current cursor position in world coordinates.
    var cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    rulingSpacing = clamp(rulingSpacing - (e.deltaY / Math.abs(e.deltaY)) * zoomSpeed, 5, 50);
    // Move the viewport to restore the cursor position.
    var new_cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    _x += cursor_world_coords[0] - new_cursor_world_coords[0];
    _y += cursor_world_coords[1] - new_cursor_world_coords[1];
});


function x() {
    // Returns the x coordinate of the viewport in world coordinates.
    return _x + _x_offset / rulingSpacing;
}

function y() {
    // Returns the y coordinate of the viewport in world coordinates.
    return _y + _y_offset / rulingSpacing;
}

function mouseX(e) {
    // Returns the x coordinate of the mouse in canvas coordinates (relative to top left corner).
    return e.clientX - canvas.getBoundingClientRect().left;
}

function mouseY(e) {
    // Returns the y coordinate of the mouse in canvas coordinates (relative to top left corner).
    return e.clientY - canvas.getBoundingClientRect().top;
}

function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
}

function drawGoban() {
    ctx.fillStyle = "#cfa570";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "black";

    current_x = x();
    current_y = y();

    // Draw vertical rulings.
    for (var i = 0; i < canvas.width / rulingSpacing; i++) {
        ctx.fillRect(
            (Math.ceil(current_x) - current_x + i) * rulingSpacing,
            0,
            rulingWidth * rulingSpacing,
            canvas.height
        );
    }
    // Draw horizontal rulings.
    for (var i = 0; i < canvas.height / rulingSpacing; i++) {
        ctx.fillRect(
            0,
            (Math.floor(current_y) - current_y + i + 1) * rulingSpacing,
            canvas.width,
            rulingWidth * rulingSpacing
        );
    }

    // Draw hoshi.
    // Obtain first hoshi position in world coordinates.
    var hoshi_x = Math.floor(x() / rulingsPerHoshi) * rulingsPerHoshi;
    var hoshi_y = Math.floor(y() / rulingsPerHoshi) * rulingsPerHoshi;
    for (var i = 0; i < canvas.width / rulingSpacing / rulingsPerHoshi + 1; i++) {
        for (var j = 0; j < canvas.height / rulingSpacing / rulingsPerHoshi + 1; j++) {
            var hoshi_center = world2Canvas(hoshi_x + i * rulingsPerHoshi, hoshi_y + j * rulingsPerHoshi);
            ctx.beginPath();
            ctx.arc(
                hoshi_center[0],
                hoshi_center[1],
                hoshiRadius * rulingSpacing,
                0,
                2 * Math.PI
            );
            ctx.fill();
        }
    }
}

function drawStones(stones, player) {
    Object.keys(stones).forEach((key) => {
        var coords = key.split(" ");
        var canvas_coords = world2Canvas(coords[0], coords[1]);
        ctx.beginPath();
        ctx.arc(
            canvas_coords[0],
            canvas_coords[1],
            stoneRadius * rulingSpacing,
            0,
            2 * Math.PI
        );
        ctx.fillStyle = player == stones[key]["player_name"] ? "black" : "white";
        ctx.strokeStyle = "black";
        ctx.lineWidth = stoneOutlineWidth * rulingSpacing;
        ctx.fill();
        ctx.stroke();

        if (stones[key]["status"] != "Unlocked") {
            ctx.beginPath();
            ctx.arc(
                canvas_coords[0],
                canvas_coords[1],
                stoneStatusRadius * rulingSpacing,
                0,
                2 * Math.PI
            );
            ctx.fillStyle = stones[key]["status"] == "Locked" ? "black" : "red";
            ctx.strokeStyle = "white";
            ctx.lineWidth = stoneOutlineWidth * rulingSpacing;
            ctx.fill();
        }
    });
}

function world2Canvas(world_x, world_y) {
    world_canvas_coords = canvas2World(0, 0);
    return [
        (world_x - x()) * rulingSpacing,
        (world_y - y()) * rulingSpacing
    ];
}

function canvas2World(canvas_x, canvas_y) {
    return [x() + canvas_x / rulingSpacing, y() + canvas_y / rulingSpacing];
}

function drawLoop(stones, player) {
    // Draw the image on the canvas.
    setInterval(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawGoban();
        drawStones(stones, player);
    }, 1/drawRate);
}
