function newPendingPoll(pollUrl) {
    setTimeout(function () {
    fetch(pollUrl)
        .then(response => response.json())
        .then(payload => {
            // Backward compatible: old server returned boolean
            if (payload === true) {
                var cyclePendingButton = document.getElementById("cyclePending");
                if (cyclePendingButton && !cyclePendingButton.innerText.includes('(NEW)')) {
                    cyclePendingButton.innerText = "*" + cyclePendingButton.innerText + " (NEW)*";
                }
                document.title = "*" + document.title + "*";
                return; // do not schedule another poll to avoid spamming until user acts or next page load
            }
            if (payload && payload.hasNew) {
                var cyclePendingButton = document.getElementById("cyclePending");
                if (cyclePendingButton && !cyclePendingButton.innerText.includes('(NEW)')) {
                    cyclePendingButton.innerText = "*" + cyclePendingButton.innerText + " (NEW)*";
                }
                document.title = "*" + document.title + "*";
                // Trigger region auto-refresh and keep client state in sync without requiring a click
                if (typeof window.onNewPendingStone === 'function') {
                    window.onNewPendingStone({ x: Number(payload.x), y: Number(payload.y) });
                }
                return; // stop polling further on first detection
            }
            // No new pending stones yet; continue polling
            newPendingPoll(pollUrl);
        }
    );
    }, 10000);
}
