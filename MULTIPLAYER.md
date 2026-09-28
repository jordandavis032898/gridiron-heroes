# Two-player online

The game now has a PLAY ONLINE button on the hero-select screen.

## One-time setup

1. Sign up free at https://joinplayroom.com
2. Create a game, copy the Game ID
3. Open `index.html` and paste it into the line near the top of the script:

       window.GRIDIRON_GAME_ID = "your-id-here";

   Without an ID it still runs in Playroom's dev mode, which is fine for
   testing but is not meant for a public link.

## Playing

1. Deploy the folder (Netlify Drop is the quickest) or run a local server
2. First person opens the page and clicks PLAY ONLINE
3. Playroom shows a room link. Send it to the other person
4. They open it, the game starts

Host plays the Heroes. Guest plays the Rivals.

## How it works

The host runs the whole simulation and publishes the world twenty times a
second. The guest sends only its stick and buttons, and draws whatever the
host reports. Neither machine can disagree with the other because only one
of them is ever deciding anything.

Guest controls: move, sprint, and button 1 to hit the ball carrier.
Press E to switch to a different Rivals defender.

## Known limits

- Two players only
- The guest always plays defence-side Rivals; there is no side swap yet
- No reconnect. If the host drops, the room ends
- Twenty updates a second, no interpolation, so remote players will look
  slightly steppy on a poor connection
