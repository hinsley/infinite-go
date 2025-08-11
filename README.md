# infinite-go

[Infinite Go](http://infinite-go.com) is a variant of the board game [Go](https://en.wikipedia.org/wiki/Go_(game)) which supports any number of simultaneous players on an infinite board. Because the game never ends, players cannot win or lose; instead, they aim to continually develop and secure regional territories by battling one another.

[Join our Discord!](https://discord.gg/dzhBtPZbEz)

# Usage

Rename `config.json.template` to `config.json` and change all instances of `CHANGE ME`.

## Viewer auto-refresh and board deltas

The full-board viewer (`/viewer`, template `templates/viewer.html`) performs an optimistic client-side update when a player clicks "Place stone" and then persists the move via the JSON endpoint `/go-json`.

To ensure the client reflects the authoritative board state after any server-side validations, status evolutions, or captures, the client requests an efficient change log from the server and reloads the page if any changes occurred since the page loaded.

- Server endpoint: `GET /board-changes?since=<epoch_seconds>` returns a JSON list of board mutation events (placements, status changes, removals) strictly after the provided timestamp.
- Event source: the server appends to a `board_events` table whenever stones are placed, removed (including captures and suicide), or statuses change. See `stone_db.py` functions `place_stone`, `remove_stone`, `update_status`, and helper `get_events_since`.
- Client behavior: after `/go-json` completes, the viewer fetches `/board-changes` with `since` set to the time the page loaded. If events are present, it navigates to `/viewer?x=<selectedX>&y=<selectedY>` to refresh the entire viewport.

This flow guarantees that the viewer does not drift from true server state and that future features should consider emitting appropriate board events when mutating the board.