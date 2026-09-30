# Two-player online

Live at https://jordandavis032898.github.io/hail-mythery/

There is nothing to set up. No account, no API key, no config line to edit.
A computer and a phone can play each other: the iPhone app loads this same
page.

## Playing

1. One of you opens the page and taps **2 PLAYERS**, then **Start a room**,
   and picks a hero.
2. You get a four letter room code and a share link.
3. The other person either opens the link, or opens the page, taps
   **2 PLAYERS**, then **Use a code**, and types the four letters.
4. They pick a hero and the game starts.

Host plays the Heroes. Guest plays the Rivals. Each of you calls your own
plays.

Both screens show a status line under the down and distance:
`ONLINE HOST - room AB12 - linked`, green when the link is up and red if it
drops.

## Controls

The guest has the same controls as the host, on a phone or a computer (see
the How to Play card or the CONTROLS button in the pause menu).

## How it works

A direct browser-to-browser WebRTC data channel, opened through PeerJS on its
free public broker. The broker only introduces the two browsers to each other;
once they are talking, the traffic goes peer to peer and never touches a
server of ours, because there isn't one.

The host is authoritative. It runs the entire game and sends it to the guest
thirty times a second: everything on the game state and on every player, so
a feature added to the game shows up on the guest's screen without any
multiplayer code changing. Only drawing caches (fields starting with `_`) and
the few things each screen keeps for itself (`NET_GLOCAL` in game.html) stay
home. Each packet carries only what changed since the one before, with a
whole copy every second, which keeps it around 40 to 60 KB a second.

The guest slides every player and the ball smoothly between packets, runs its
clock on the host's so timed effects line up, and plays the host's effects,
callouts, player cards and super banners on its own screen. Callouts said
from the host's side are turned round for the guest (YOUR BALL / THEIR BALL).
A callout about a move one person made (`say(text, ms, 'H' or 'A')`) is shown
only to that person.

The guest sends its stick and its taps and swipes. Taps latch on arrival, so a
press can't fall between two frames and get lost.

## Known limits

- Two players only, and only with a code: there is no matchmaking with
  strangers.
- No reconnect. If either side drops, the room ends and both go back to the
  menu.
- Both screens must be on the same version: after a push, reload both.
- The PeerJS public broker is free and occasionally busy. If HOST says it
  cannot open a room, wait a moment and press it again; it retries a fresh
  code automatically on a collision.
