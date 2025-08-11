## Infinite Go — Rules for Go players

If you already play Go, think of Infinite Go as Go on an infinite board with no turns, no scoring, and a locality lock that paces exchanges within fights.

- **Board and players**: Infinite grid; any number of players can play at any time. All moves are persistent.
- **Capture**: Liberties and group capture work exactly as in Go. **Suicide is allowed.**
- **Ko**: There is **no ko rule**; immediate recapture is permitted.
- **Scoring/ending**: There is no end and no score. The meta‑goal is to grow, secure, and defend live shapes over time.
- **Opening seed**: The game starts with a single unlocked stone by the non-player `SAI`. This is the only stone `SAI` places.

### Locality system (Locked → Pending → Unlocked)
Every time anyone plays a stone, consider the 13×13 box centered on that point (the “local region,” radius 6 in each direction). Stones in that box update status to throttle how fast one player can add further stones locally:

- **Locked**: A newly placed stone starts Locked.
- **Pending**: When any stone is played in a local region, all Locked stones in that region become Pending.
- **Unlocked**: When you play in a local region, any of your Pending stones in that region become Unlocked. Pending stones also auto‑unlock after 1 day.

Intuition: you play, your stone locks the area for you; an answer locally loosens the area; you then have a window to respond before others can accelerate.

### Legal move (relative to the local 13×13 region)
A move at a point is legal iff all are true:
- The point is empty.
- There is at least one stone already somewhere in the 13×13 box centered on that point.
- You do not currently have any Locked stone in that 13×13 box.
- If there are any Pending stones in that box, they all belong to you.

These constraints are in addition to normal Go legality; after placement, captures (including suicide) are resolved.

### Capture and suicide resolution
After a legal placement:
- Opponent groups with no liberties are removed (standard capture).
- If no captures were made, the just-played stone’s own group may be removed if it has no liberties (**suicide is allowed**).

### Practical consequences vs. normal Go
- **No turns**: Anyone can play at any time; the locality system creates de facto “turns” within each 13×13 neighborhood.
- **No ko**: Typical ko fights collapse into immediate recaptures. Life-and-death still matters.
- **Local tempo**: After you play locally, you generally cannot immediately add another local move; someone else must respond locally or 24 hours must pass to unlock.
- **Connectivity requirement**: You cannot start a brand-new island far away; a legal move must have at least one stone already in its 13×13 box. The `SAI` seed bootstraps the initial play.

### Quick reference
- Infinite board, many players, persistent stones.
- Same liberties and capture as Go; suicide allowed; no ko.
- 13×13 local box per move.
- New stone: Locked → any Locked in-box become Pending → your in-box Pending become Unlocked → after 1 day, Pending auto‑unlock.
- Legal if: empty; some stone already in-box; you have no Locked in-box; any in-box Pending are yours.

Play it like Go: read locally, fight for life, and use the locality timer to pace exchanges and secure frameworks over time.