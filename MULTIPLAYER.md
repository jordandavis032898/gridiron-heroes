# Two-player online

Live at https://jordandavis032898.github.io/gridiron-heroes/

There is nothing to set up. No account, no API key, no config line to edit.

## Playing

1. One of you opens the page and clicks **PLAY ONLINE**, then **HOST**.
2. You get a four letter room code and a share link.
3. The other person either opens the link, or opens the page, clicks
   **PLAY ONLINE**, then **JOIN**, and types the four letters.
4. The game starts the moment they connect.

Host plays the Heroes. Guest plays the Rivals.

Both screens show a status line under the down and distance:
`ONLINE HOST - room AB12 - linked`, green when the link is up and red if it
drops. On the host's screen, whichever Rival the other person is driving has
a red ring under him.

## Guest controls

    WASD / arrows   move
    Shift           sprint
    1               hit the ball carrier
    2               big hit (costs more, hurts more)
    E               switch to a different Rival

The guest drives whichever Rival is nearest the ball, so when the Rivals have
possession the guest is running the ball, not defending.

## How it works

A direct browser-to-browser WebRTC data channel, opened through PeerJS on its
free public broker. The broker only introduces the two browsers to each other;
once they are talking, the traffic goes peer to peer and never touches a
server of ours, because there isn't one.

The host is authoritative. It runs the entire simulation and publishes the
world twenty times a second. The guest sends only its stick and its buttons
and draws whatever the host reports, so the two machines can never disagree
about what happened. Button taps latch on arrival, so a press can't fall
between two frames and get lost.

## Known limits

- Two players only.
- The guest cannot call plays. When the Rivals have the ball the computer
  picks the play and the guest runs it.
- The guest does not pick a hero. Only the host's signature move is in play.
- No reconnect. If either side drops, the room ends and both go back to the
  menu.
- Twenty updates a second with no interpolation, so a remote player on a bad
  connection will look slightly steppy.
- The PeerJS public broker is free and occasionally busy. If HOST says it
  cannot open a room, wait a moment and press it again; it retries a fresh
  code automatically on a collision.
