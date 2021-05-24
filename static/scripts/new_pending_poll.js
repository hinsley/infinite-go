function newPendingPoll(pollUrl) {
    setTimeout(function () {
    fetch(pollUrl)
        .then(response => response.json())
        .then(newPendingStone => {
            if (newPendingStone) {
                var cyclePendingButton = document.getElementById("cyclePending");
                cyclePendingButton.innerText = "*" + cyclePendingButton.innerText + " (NEW)*";
                document.title = "*" + document.title + "*"; // Update the tab title.
            } else {
                newPendingPoll(pollUrl);
            }
        }
    );
    }, 10000);
}
