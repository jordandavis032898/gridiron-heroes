# Gridiron Heroes

Arcade American football. Single HTML file plus a folder of sprite art.
No build step, no dependencies, no server.

## Run it locally

Open `index.html` in a browser. That is it.

If the players render as plain shapes instead of the drawn art, the browser is
blocking local file reads for the sprites. Serve it instead:

    python -m http.server 8000

then open http://localhost:8000

## It is already online

https://jordandavis032898.github.io/gridiron-heroes/

Push to `main` and GitHub Pages redeploys it in about a minute.
Two-player instructions are in MULTIPLAYER.md.

## Other places you could put it (free, pick one)

**Netlify Drop** - drag this whole folder onto https://app.netlify.com/drop
You get a public URL in about ten seconds. Easiest option.

**Vercel** - from inside this folder:

    npx vercel

**GitHub Pages** - push the folder to a repo, then Settings > Pages >
deploy from branch, root.

**itch.io** - zip the folder, create a new project, set Kind to HTML,
tick "This file will be played in the browser", upload the zip.

## Controls

    WASD / arrows   move
    Space           hike
    click a man     throw to him
    4 5 6 7         throw to receiver 1-4
    1               juke        (dive on defense)
    2               signature   (big hit on defense)
    3               pitch       (ground pound on defense)
    E               switch player
    Shift           sprint, and truck through a tackler

## Files

    index.html      the whole game
    parts/*.png     seven body parts, rigged onto a skeleton at runtime

## Art

Player art is original. No real player names, team marks or league branding
are used anywhere in this project.
