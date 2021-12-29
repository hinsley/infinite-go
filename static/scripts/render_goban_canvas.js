const rulingSpacing = 50; // Pixels.
const rulingWidth = 2; // Pixels.
const hoshiRadius = 2; // Pixels.

const canvas = document.getElementById("goban");
const ctx = canvas.getContext("2d");

var x = Math.round(rulingSpacing / 2);
var y = Math.round(rulingSpacing / 2);

function drawRulings() {
    ctx.fillStyle = "black";

    // Draw vertical rulings.
    for (var i = 0; i < 13; i++) {
        ctx.fillRect((Math.ceil(x / rulingSpacing) + i) * rulingSpacing - x, 0, 1, canvas.height);
    }
    // Draw horizontal rulings.
    for (var i = 0; i < 13; i++) {
        ctx.fillRect(0, (Math.ceil(y / rulingSpacing) + i) * rulingSpacing - y, canvas.width, 1);
    }
}

function world2Viewport(x, y) {
    return [x - this.x, y - this.y];
}

drawRulings();
