function newPendingPoll(pollUrl) {
    setTimeout(function () {
    fetch(pollUrl)
        .then(response => response.json())
        .then(newPendingStone => {
            if (newPendingStone) {
                var cyclePendingButton = document.getElementById("cyclePending");
                cyclePendingButton.innerText = "*" + cyclePendingButton.innerText + " (NEW)*";
            } else {
                newPendingPoll(pollUrl);
            }
        }
    );
    }, 10000);
}
