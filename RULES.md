# Infinite Go rules

In Infinite Go, there is no score and players do not take turns. The game allows any number of players at any given time and all moves played are persistent, forever. Stones may be captured as usual, but no [ko](https://en.wikipedia.org/wiki/Rules_of_Go#Ko) rule is used. Suicide moves are allowed.

The game begins with a single unlocked stone placed on the board by the non-player user `SAI`. This is the only move `SAI` will ever place.

## Locks, self-locks, and valid moves

Every time a player places a stone, a local 13x13 region centered at that stone is considered.

The stone is in a "locked" state once it is placed. When a stone is placed, any locked stone in the local region is "self-locked", and any self-locked stone in the local region belonging to the player is unlocked. 

In order for the move to be valid, the following criteria must be met:

- The stone may not be placed where another stone already exists.
- There must be at least one stone already within the local region.
- There may not already be a locked stone belonging to the player within the local region.
- Any self-locked stones present in the local region must belong to the player.

 Self-locked stones are automatically unlocked after five minutes.