function epochTime() {
    return Date.now() / 1000;
}

function initiatePendingCountdown(pendingSince) {
    var timerDisplay = document.getElementById("pending-countdown");

    function pendingCountdownHandler() {
        // Expressed in seconds.
        var remainingTime = Math.floor(pendingSince + 86400 - epochTime());
        
        if (remainingTime > 0) {
            var remainingSeconds = remainingTime % 60;
            var remainingMinutes = ((remainingTime - remainingSeconds) % 3600) / 60;
            var remainingHours = Math.floor(remainingTime / 3600);
            
            var timerDisplayText = remainingHours.toString().padStart(2, "0") + ":" +
                remainingMinutes.toString().padStart(2, "0") + ":" +
                remainingSeconds.toString().padStart(2, "0") + " remaining until stone is unlocked.";

            timerDisplay.innerText = timerDisplayText;
        } else {
            timerDisplay.innerText = "Stone unlocked; refresh to update."
        }
    }

    var timerInterval = setInterval(pendingCountdownHandler, 1000);
}