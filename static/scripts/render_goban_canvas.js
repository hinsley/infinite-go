var rulingSpacing = 50; // Pixels (fixed at 1 in world units).
var rulingWidth = 0.01; // World units.
var rulingsPerHoshi = 6; // World units (natural number).
var hoshiRadius = 0.075; // World units.
var stoneRadius = 0.46; // World units.
var stoneOutlineWidth = 0.02; // World units.
var stoneStatusRadius = 0.125; // World units.
var stoneStatusOutlineWidth = 0.05; // World units.
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

// Tooltip and hover state
var tooltipEl = document.getElementById("stone-tooltip");
var visibleStones = []; // [{key, cx, cy, rPx, player_name, player_score}]
var playerColorMap = null; // {player_name: color}
var currentPlayerName = null;

// Selected cell highlight
var selectedCell = { x: null, y: null };
window.setSelectedCell = function(x, y) {
    selectedCell.x = Number(x);
    selectedCell.y = Number(y);
};
// Center viewport on a given world coordinate
window.centerOnWorldCoord = function(x, y) {
    // reset any transient offsets
    _x_offset = 0;
    _y_offset = 0;
    // compute top-left world position so that (x,y) is centered
    const halfCellsX = canvas.width / (2 * rulingSpacing);
    const halfCellsY = canvas.height / (2 * rulingSpacing);
    _x = Number(x) - halfCellsX;
    _y = Number(y) - halfCellsY;
};

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
        hideTooltip();
        return;
    }

    // Hover detection using last rendered visible stones
    const mx = mouseX(e);
    const my = mouseY(e);
    const hovered = findHoveredStone(mx, my);
    if (hovered) {
        // Use viewport coordinates for the fixed-position tooltip
        showTooltip(`${hovered.player_name} — ${Number(hovered.player_score).toLocaleString()} stones`, e.clientX + 12, e.clientY + 12);
    } else {
        hideTooltip();
    }
});

["mouseup", "mouseleave"].forEach((event_name) => {
    canvas.addEventListener(event_name, () => {
        _x += _x_offset / rulingSpacing;
        _y += _y_offset / rulingSpacing;
        _x_offset = 0;
        _y_offset = 0;
        panning = false;
        hideTooltip();
    });
});

// Zoom event.
canvas.addEventListener("wheel", (e) => {
    // Prevent page scrolling while zooming inside the board view
    e.preventDefault();

    // Zoom around the cursor.
    // Store the current cursor position in world coordinates.
    var cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    rulingSpacing = clamp(rulingSpacing - (e.deltaY / Math.abs(e.deltaY)) * zoomSpeed, 5, 50);
    // Move the viewport to restore the cursor position.
    var new_cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    _x += cursor_world_coords[0] - new_cursor_world_coords[0];
    _y += cursor_world_coords[1] - new_cursor_world_coords[1];
}, { passive: false });

function hideTooltip() {
    if (tooltipEl) tooltipEl.style.display = "none";
}

function showTooltip(text, xPx, yPx) {
    if (!tooltipEl) return;
    tooltipEl.textContent = text;
    tooltipEl.style.left = `${xPx}px`;
    tooltipEl.style.top = `${yPx}px`;
    tooltipEl.style.display = "block";
}

function findHoveredStone(mx, my) {
    let winner = null;
    let bestDist2 = Infinity;
    for (let i = 0; i < visibleStones.length; i++) {
        const s = visibleStones[i];
        const dx = mx - s.cx;
        const dy = my - s.cy;
        const dist2 = dx * dx + dy * dy;
        if (dist2 <= s.rPx * s.rPx && dist2 < bestDist2) {
            bestDist2 = dist2;
            winner = s;
        }
    }
    return winner;
}

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

function buildPlayerColorMap(stones, player) {
    // Build unique players and scores, excluding the current player
    const nameToScore = new Map();
    Object.keys(stones).forEach((key) => {
        const s = stones[key];
        if (s["player_name"] === player) return; // reserve black for current player
        if (!nameToScore.has(s["player_name"])) {
            nameToScore.set(s["player_name"], s["player_score"] ?? 0);
        }
    });

    // Sort players by score descending
    const entries = Array.from(nameToScore.entries()).sort((a, b) => (b[1] - a[1]));

    const map = {};
    const safePalette = Array.isArray(color_code) ? color_code.filter((_, idx) => idx > 1) : ["#008941", "#006FA6", "#A30059"];
    for (let i = 0; i < entries.length; i++) {
        map[entries[i][0]] = safePalette[i % safePalette.length];
    }
    return map;
}

function drawStones(stones, player) {
    if (playerColorMap === null) {
        currentPlayerName = player;
        try {
            playerColorMap = buildPlayerColorMap(stones, player);
        } catch (e) {
            // If color_code is not available for some reason, fallback to simple white
            playerColorMap = {};
        }
    }

    visibleStones = [];

    Object.keys(stones).forEach((key) => {
        var coords = key.split(" ");
        var canvas_coords = world2Canvas(coords[0], coords[1]);
        const cx = canvas_coords[0];
        const cy = canvas_coords[1];
        const rPx = stoneRadius * rulingSpacing;

        // Cull stones far outside the viewport for hover testing list
        if (cx < -rPx || cy < -rPx || cx > canvas.width + rPx || cy > canvas.height + rPx) {
            // Still skip drawing? We can also skip rendering to save draw time
            return;
        }

        ctx.beginPath();
        ctx.arc(
            cx,
            cy,
            rPx,
            0,
            2 * Math.PI
        );
        // Color logic: your stones black; others from palette mapping
        let fill = "white";
        if (player && player === stones[key]["player_name"]) {
            fill = "black";
        } else {
            const pname = stones[key]["player_name"];
            fill = (playerColorMap && playerColorMap[pname]) ? playerColorMap[pname] : "white";
        }
        ctx.fillStyle = fill;
        ctx.strokeStyle = "black";
        ctx.lineWidth = stoneOutlineWidth * rulingSpacing;
        ctx.fill();
        ctx.stroke();

        // Save for hover detection
        visibleStones.push({
            key: key,
            cx: cx,
            cy: cy,
            rPx: rPx,
            player_name: String(stones[key]["player_name"]),
            player_score: stones[key]["player_score"] ?? 0
        });

        if (stones[key]["status"] != "Unlocked") {
            ctx.beginPath();
            ctx.arc(
                cx,
                cy,
                stoneStatusRadius * rulingSpacing,
                0,
                2 * Math.PI
            );
            ctx.fillStyle = stones[key]["status"] == "Locked" ? "black" : "crimson";
            ctx.strokeStyle = "white";
            ctx.lineWidth = stoneStatusOutlineWidth * rulingSpacing;
            ctx.fill();
            ctx.stroke();
        }
    });
}

function drawSelection() {
    if (selectedCell.x === null || selectedCell.y === null) return;
    // Center the 1x1 overlay square on the stone at (x, y)
    const topLeft = world2Canvas(selectedCell.x - 0.5, selectedCell.y + 0.5);
    ctx.fillStyle = "rgba(0,0,0,0.25)";
    ctx.fillRect(topLeft[0], topLeft[1], rulingSpacing, -rulingSpacing);
}

function drawActiveAreaBoundary() {
    if (selectedCell.x === null || selectedCell.y === null) return;
    // 13x13 positions centered at selected cell means 12 cells wide/high.
    // Top-left corner lies 6 cells left and 6 cells up in world coords.
    const topLeft = world2Canvas(selectedCell.x - 6, selectedCell.y + 6);
    const widthPx = 12 * rulingSpacing;
    const heightPx = -12 * rulingSpacing;

    ctx.save();
    ctx.strokeStyle = "red";
    ctx.lineWidth = rulingWidth * rulingSpacing; // match grid line thickness
    ctx.setLineDash([]);
    ctx.strokeRect(topLeft[0], topLeft[1], widthPx, heightPx);
    ctx.restore();
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
        // Boundary must appear above the rulings but behind stones
        drawActiveAreaBoundary();
        drawStones(stones, player);
        drawSelection();
    }, 1000 / drawRate);
}
