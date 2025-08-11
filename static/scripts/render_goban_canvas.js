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
var initialRulingSpacing = rulingSpacing; // Remember the initial zoom level for forced pans

const canvas = document.getElementById("goban");
const ctx = canvas.getContext("2d");

// High-DPI resolution scaling (controlled via window.VIEWPORT_RESOLUTION_SCALE from viewer.html)
const RESOLUTION_SCALE = Number(window.VIEWPORT_RESOLUTION_SCALE || 1);
function getResolutionScale() { return RESOLUTION_SCALE; }
function displayWidth() { return canvas.width / getResolutionScale(); }
function displayHeight() { return canvas.height / getResolutionScale(); }

// Ensure the canvas fits the viewport on mobile to avoid horizontal scrolling
function resizeCanvasToFit() {
    const maxSize = 650;
    const viewportWidth = Math.min(window.innerWidth || maxSize, document.documentElement.clientWidth || maxSize);
    const targetSize = Math.max(200, Math.min(maxSize, Math.floor(viewportWidth))); // guard a minimum size
    // CSS size stays logical; backing store is scaled for sharper rendering
    canvas.style.width = `${targetSize}px`;
    canvas.style.height = `${targetSize}px`;
    const scale = getResolutionScale();
    canvas.width = Math.floor(targetSize * scale);
    canvas.height = Math.floor(targetSize * scale);
    // Map logical CSS pixels to device pixels
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    // Clamp current zoom to dynamic limits after resize
    const limits = getDynamicZoomLimits();
    rulingSpacing = clamp(rulingSpacing, limits[0], limits[1]);
}
resizeCanvasToFit();
window.addEventListener('resize', resizeCanvasToFit);

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
// Flag to suppress click selection immediately after a drag-based pan
window.suppressNextClickSelection = false;

// Touch pan thresholding to avoid accidental pans on tiny drags
const TOUCH_PAN_START_THRESHOLD = 8; // pixels
let panPointerId = null;
let activePointers = new Map();
let initialPinchDistance = null;
let initialPinchCenterCanvas = null; // [x, y] in canvas pixels
let initialPinchWorld = null; // [x, y] in world coords under pinch center at pinch start
let pinchBaseRulingSpacing = null;
let pinchZooming = false;

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
    const halfCellsX = displayWidth() / (2 * rulingSpacing);
    const halfCellsY = displayHeight() / (2 * rulingSpacing);
    _x = Number(x) - halfCellsX;
    _y = Number(y) - halfCellsY;
};

// Center viewport and reset zoom to the initial level
window.centerAndResetZoom = function(x, y) {
    // Reset to initial but clamp to dynamic range for current canvas size
    const limits = getDynamicZoomLimits();
    rulingSpacing = clamp(initialRulingSpacing, limits[0], limits[1]);
    window.centerOnWorldCoord(x, y);
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
        const scoreStr = Number(hovered.player_score).toLocaleString();
        const tooltipText = `${hovered.player_name} (${scoreStr})\n${formatTimestamp(hovered.placement_time)}`;
        showTooltip(tooltipText, e.clientX, e.clientY, hovered.rPx);
    } else {
        hideTooltip();
    }
});

["mouseup", "mouseleave"].forEach((event_name) => {
    canvas.addEventListener(event_name, () => {
        // If releasing after a drag, mark to suppress the following click selection
        if (event_name === "mouseup") {
            const dragDistance = Math.hypot(_x_offset, _y_offset);
            // Use a small threshold to avoid accidental suppression on micro-movements
            if (dragDistance > 3) {
                window.suppressNextClickSelection = true;
            }
        }
        _x += _x_offset / rulingSpacing;
        _y += _y_offset / rulingSpacing;
        _x_offset = 0;
        _y_offset = 0;
        panning = false;
        hideTooltip();
    });
});

// Compute dynamic zoom limits proportional to current canvas size relative to base 650
function getDynamicZoomLimits() {
    const BASE_CANVAS_SIZE = 650;
    const scale = displayWidth() / BASE_CANVAS_SIZE;
    const minSpacing = 5 * scale;
    const maxSpacing = 50 * scale;
    return [minSpacing, maxSpacing];
}

// Zoom event.
canvas.addEventListener("wheel", (e) => {
    // Prevent page scrolling while zooming inside the board view
    e.preventDefault();

    // Zoom around the cursor.
    // Store the current cursor position in world coordinates.
    var cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    const limits = getDynamicZoomLimits();
    rulingSpacing = clamp(rulingSpacing - (e.deltaY / Math.abs(e.deltaY)) * zoomSpeed, limits[0], limits[1]);
    // Move the viewport to restore the cursor position.
    var new_cursor_world_coords = canvas2World(mouseX(e), mouseY(e));
    _x += cursor_world_coords[0] - new_cursor_world_coords[0];
    _y += cursor_world_coords[1] - new_cursor_world_coords[1];
}, { passive: false });

// Pointer events for touch drag and pinch zoom on mobile devices
function getCanvasXYFromClient(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    return [clientX - rect.left, clientY - rect.top];
}

canvas.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse') return; // keep mouse path separate
    e.preventDefault();
    try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
    activePointers.set(e.pointerId, { clientX: e.clientX, clientY: e.clientY });

    if (activePointers.size === 1) {
        // Prepare single-finger interaction; do not start panning until movement exceeds threshold
        panPointerId = e.pointerId;
        const [cx, cy] = getCanvasXYFromClient(e.clientX, e.clientY);
        cursor_x_initial = cx;
        cursor_y_initial = cy;
        panning = false; // will activate if movement passes threshold
        updateTouchTooltip(e);
    } else if (activePointers.size === 2) {
        // Begin pinch
        panning = false;
        _x_offset = 0;
        _y_offset = 0;
        const pts = Array.from(activePointers.values());
        const [c1x, c1y] = getCanvasXYFromClient(pts[0].clientX, pts[0].clientY);
        const [c2x, c2y] = getCanvasXYFromClient(pts[1].clientX, pts[1].clientY);
        initialPinchDistance = Math.hypot(c2x - c1x, c2y - c1y);
        initialPinchCenterCanvas = [(c1x + c2x) / 2, (c1y + c2y) / 2];
        pinchBaseRulingSpacing = rulingSpacing;
        initialPinchWorld = [
            x() + initialPinchCenterCanvas[0] / rulingSpacing,
            y() + initialPinchCenterCanvas[1] / rulingSpacing
        ];
        pinchZooming = true;
        hideTooltip();
    }
}, { passive: false });

canvas.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'mouse') return;
    if (!activePointers.has(e.pointerId)) return;
    e.preventDefault();
    activePointers.set(e.pointerId, { clientX: e.clientX, clientY: e.clientY });

    if (activePointers.size >= 2 && initialPinchDistance != null) {
        // Handle pinch-zoom with two active pointers
        const pts = Array.from(activePointers.values());
        const [c1x, c1y] = getCanvasXYFromClient(pts[0].clientX, pts[0].clientY);
        const [c2x, c2y] = getCanvasXYFromClient(pts[1].clientX, pts[1].clientY);
        const dist = Math.hypot(c2x - c1x, c2y - c1y);
        const center = [(c1x + c2x) / 2, (c1y + c2y) / 2];
        const scale = dist / (initialPinchDistance || 1);
        const limits = getDynamicZoomLimits();
        const newSpacing = clamp(pinchBaseRulingSpacing * scale, limits[0], limits[1]);

        // Update zoom and adjust viewport to keep the world under the pinch center stable
        rulingSpacing = newSpacing;
        _x_offset = 0;
        _y_offset = 0;
        _x = initialPinchWorld[0] - center[0] / rulingSpacing;
        _y = initialPinchWorld[1] - center[1] / rulingSpacing;
        hideTooltip();
        return;
    }

    // Single-finger interaction
    if (e.pointerId === panPointerId) {
        const [cx, cy] = getCanvasXYFromClient(e.clientX, e.clientY);
        const dx = cx - cursor_x_initial;
        const dy = cy - cursor_y_initial;
        const dist = Math.hypot(dx, dy);
        if (!panning && dist >= TOUCH_PAN_START_THRESHOLD) {
            panning = true;
        }
        if (panning) {
            _x_offset = cursor_x_initial - cx;
            _y_offset = cursor_y_initial - cy;
        }
        updateTouchTooltip(e);
    }
}, { passive: false });

function endPointer(e) {
    if (e.pointerType === 'mouse') return;
    if (!activePointers.has(e.pointerId)) return;
    e.preventDefault();

    // Track whether we were panning before resetting state
    const wasPanning = panning && e.pointerId === panPointerId;

    // If releasing after a drag, mark to suppress the following click selection
    if (wasPanning) {
        const dragDistance = Math.hypot(_x_offset, _y_offset);
        if (dragDistance > 3) {
            window.suppressNextClickSelection = true;
        }
        _x += _x_offset / rulingSpacing;
        _y += _y_offset / rulingSpacing;
        _x_offset = 0;
        _y_offset = 0;
        panning = false;
    }

    // If it was a tap (no pan), perform a selection explicitly and suppress the synthetic click
    if (pinchZooming) {
        // Do not treat release after pinch as a tap selection
        window.suppressNextClickSelection = true;
    } else if (e.pointerId === panPointerId && !wasPanning) {
        window.suppressNextClickSelection = true;
        const [cx, cy] = getCanvasXYFromClient(e.clientX, e.clientY);
        const world = canvas2World(cx, cy);
        const selX = Math.round(world[0]);
        const selY = Math.round(world[1]);
        if (typeof window.applySelection === 'function') {
            window.applySelection(selX, selY);
        }
    }

    activePointers.delete(e.pointerId);
    try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}

    if (activePointers.size === 0) {
        // End of all touch interactions
        initialPinchDistance = null;
        initialPinchCenterCanvas = null;
        initialPinchWorld = null;
        pinchBaseRulingSpacing = null;
        pinchZooming = false;
        panPointerId = null;
        hideTooltip();
    } else if (activePointers.size === 1) {
        // Transition from pinch to pan with remaining pointer
        const [remainingId, pt] = Array.from(activePointers.entries())[0];
        panPointerId = remainingId;
        const [cx, cy] = getCanvasXYFromClient(pt.clientX, pt.clientY);
        cursor_x_initial = cx;
        cursor_y_initial = cy;
        panning = false; // will activate if movement passes threshold
        initialPinchDistance = null;
        initialPinchCenterCanvas = null;
        initialPinchWorld = null;
        pinchBaseRulingSpacing = null;
        updateTouchTooltip({ clientX: pt.clientX, clientY: pt.clientY });
    }
}

canvas.addEventListener('pointerup', endPointer, { passive: false });
canvas.addEventListener('pointercancel', endPointer, { passive: false });
canvas.addEventListener('pointerleave', endPointer, { passive: false });

function hideTooltip() {
    if (tooltipEl) tooltipEl.style.display = "none";
}

function showTooltip(text, clientXPx, clientYPx, radiusPx) {
    if (!tooltipEl) return;
    tooltipEl.textContent = text;
    // Make visible to measure height
    tooltipEl.style.display = "block";
    // Position temporarily to get correct size
    tooltipEl.style.left = `0px`;
    tooltipEl.style.top = `0px`;
    const tooltipHeight = tooltipEl.offsetHeight || 0;
    const left = Math.round(clientXPx + (radiusPx || 0));
    const top = Math.round(clientYPx - (radiusPx || 0) - tooltipHeight);
    tooltipEl.style.left = `${left}px`;
    tooltipEl.style.top = `${top}px`;
}

function updateTouchTooltip(e) {
    // For touch: show tooltip while a finger is pressed, following the finger, if over a stone
    if (!e || !tooltipEl) return;
    const [cx, cy] = getCanvasXYFromClient(e.clientX, e.clientY);
    const hovered = findHoveredStone(cx, cy);
    if (hovered) {
        const scoreStr = Number(hovered.player_score).toLocaleString();
        const tooltipText = `${hovered.player_name} (${scoreStr})\n${formatTimestamp(hovered.placement_time)}`;
        showTooltip(tooltipText, e.clientX, e.clientY, hovered.rPx);
    } else {
        hideTooltip();
    }
}

// Format epoch seconds to "YYYY-MM-DD HH:MM:SS" in the user's local time
function formatTimestamp(seconds) {
    if (seconds == null) return '';
    const d = new Date(Number(seconds) * 1000);
    const pad = (n) => String(n).padStart(2, '0');
    const yyyy = d.getFullYear();
    const mm = pad(d.getMonth() + 1);
    const dd = pad(d.getDate());
    const hh = pad(d.getHours());
    const mi = pad(d.getMinutes());
    const ss = pad(d.getSeconds());
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`;
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
    ctx.fillRect(0, 0, displayWidth(), displayHeight());

    ctx.fillStyle = "black";

    current_x = x();
    current_y = y();

    // Draw vertical rulings.
    for (var i = 0; i < displayWidth() / rulingSpacing; i++) {
        ctx.fillRect(
            (Math.ceil(current_x) - current_x + i) * rulingSpacing,
            0,
            rulingWidth * rulingSpacing,
            displayHeight()
        );
    }
    // Draw horizontal rulings.
    for (var i = 0; i < displayHeight() / rulingSpacing; i++) {
        ctx.fillRect(
            0,
            (Math.floor(current_y) - current_y + i + 1) * rulingSpacing,
            displayWidth(),
            rulingWidth * rulingSpacing
        );
    }

    // Draw hoshi.
    // Obtain first hoshi position in world coordinates.
    var hoshi_x = Math.floor(x() / rulingsPerHoshi) * rulingsPerHoshi;
    var hoshi_y = Math.floor(y() / rulingsPerHoshi) * rulingsPerHoshi;
    for (var i = 0; i < displayWidth() / rulingSpacing / rulingsPerHoshi + 1; i++) {
        for (var j = 0; j < displayHeight() / rulingSpacing / rulingsPerHoshi + 1; j++) {
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
        if (cx < -rPx || cy < -rPx || cx > displayWidth() + rPx || cy > displayHeight() + rPx) {
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
            player_score: stones[key]["player_score"] ?? 0,
            placement_time: stones[key]["placement_time"] ?? null
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
    ctx.lineWidth = 6 * rulingWidth * rulingSpacing;
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
        ctx.clearRect(0, 0, displayWidth(), displayHeight());
        drawGoban();
        // Boundary must appear above the rulings but behind stones
        drawActiveAreaBoundary();
        drawStones(stones, player);
        drawSelection();
    }, 1000 / drawRate);
}
