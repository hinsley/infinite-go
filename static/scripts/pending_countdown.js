function epochTime() {
    return Date.now() / 1000;
}

function initiatePendingCountdown(pendingSince) {
    var timerDisplay = document.getElementById("pending-countdown");

    function pendingCountdownHandler() {
        // Expressed in seconds.
        var remainingTime = Math.floor(pendingSince + 3600 - epochTime());
        
        if (remainingTime > 0) {
            var remainingSeconds = remainingTime % 60;
            var remainingMinutes = (remainingTime - remainingSeconds) / 60;
            
            var timerDisplayText = "";

            if (remainingMinutes != 0) {
                timerDisplayText += remainingMinutes + " minutes and ";
            }

            timerDisplayText += remainingSeconds + " seconds until stone is unlocked.";

            timerDisplay.innerText = timerDisplayText;
        } else {
            timerDisplay.innerText = "Stone unlocked; refresh to update."
        }
    }

    var timerInterval = setInterval(pendingCountdownHandler, 1000);
}