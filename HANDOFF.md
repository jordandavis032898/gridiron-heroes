# Gridiron Heroes: handoff

Everything a new session needs to pick this up. Read this before touching
`index.html`.

---

## What it is

Arcade American football in the browser. Seven on seven, four downs, a three
minute clock, signature moves. One player against the computer, or two
players online.

- **Live:** https://jordandavis032898.github.io/gridiron-heroes/
- **Repo:** https://github.com/jordandavis032898/gridiron-heroes (public, which
  free GitHub Pages requires, so the source is readable by anyone)
- **Local:** `C:\Users\jorda\Desktop\gridiron-heroes`

## Shape of the project

- `index.html` — the whole game. About 181 KB, one file, no build step, no
  framework. Canvas 2D. The only external script is PeerJS from unpkg.
- `parts/*.png` — character sprite parts
- `parts/fx/*.png` — effect sprites
- `MULTIPLAYER.md`, `README.md`, `parts/ASSET-PROMPTS.md`

## Running and shipping

```bash
python -m http.server 8777        # then open http://127.0.0.1:8777
```

Deploying is `git push origin main`. GitHub Pages republishes in about 60 to
90 seconds. There is no other deploy step. Verify with:

```bash
curl -s https://jordandavis032898.github.io/gridiron-heroes/ | grep -c "<some string you just added>"
```

---

## Things that will waste your time if you do not know them

**Your local browser tab lies.** Chrome throttles `requestAnimationFrame` in
a background tab to roughly one frame a second. Driving the game through the
browser tools usually leaves the tab unfocused, so the simulation runs about
twenty times slow and looks frozen or broken. Hours went into "bugs" that
were only this. Screenshots are trustworthy; anything time-dependent is not.

**Jordan's screenshots are better test data than local runs.** Several real
bugs were diagnosed from a single screenshot he sent after the local repro
failed.

**Patch the file with anchored Python scripts, not sed.** Write the script
with the Write tool and run it. Every substitution must assert it matched
exactly once, and the script must not write the file if any anchor missed.
Two separate times a script exited on a failed anchor after reporting
successes, and nothing was written at all while the log looked fine.

**Always syntax check before claiming anything works:**

```bash
python -c "
import io
s=io.open('index.html',encoding='utf-8').read()
i=s.index(chr(10)+'<script>'+chr(10)); j=s.rindex('</script>')
io.open('/tmp/gh.js','w',encoding='utf-8').write(s[i+10:j])
" && node --check /tmp/gh.js
```

**`window.GH.state()`** in the console reports phase, possession, which side
you are, who you control, and the dive cooldowns. Use it instead of guessing
at input problems.

---

## Art pipeline

**Character parts** are generated on a solid magenta `#FF00FF` background and
keyed out here. Never ask a generator for transparency: it returns a
checkerboard *painted into the pixels* at full opacity, and colour-matching
it out eats the white pants.

**Effect sprites** are painted white on solid **black** and composited with
`globalCompositeOperation='lighter'`. Black adds nothing, so there is no key
and no fringe, and they tint by multiplying with a colour (cached by sprite
and colour in `fxTint`).

**Each part is stretched to its bone length**, so the art must be cropped
tight with no padding or you get a gap at the joint. Vertical parts run top
to bottom, horizontal parts left to right.

### The art that is still wrong

- **`football-thigh.png` is not a thigh.** It is a skin-coloured blob with a
  hairline stripe. The thigh is currently drawn in code by `thighBone()`.
  Swap back to `boneV(S.thigh,...)` when there is real art.
- **`football-lower-leg.png`** is a bare calf with a sock only at the ankle.
  It should be a tall sock.
- `parts/ASSET-PROMPTS.md` has the prompts. The five-part batch (thigh, lower
  leg, cleat, upper arm, forearm) was written but never delivered.

---

## Systems

**Rig.** Seven body parts on a bone hierarchy, `boneV` and `boneH`. Pose
branches in `drawSprite`: down, moving, idle. The line uses a heavier torso,
odd shirt numbers get the second helmet, a reaching arm gets the gloved hand.

**Playbook.** Six offensive plays, five defensive. The sheet numbers itself,
so plays can be added without renumbering hotkeys. Defensive calls genuinely
differ: rushers, man versus zone, cushion, zone depth, and a spy on contain.

**Abilities.** Thirteen across ten positions, on Q, R and T, in `ABIL` and
`KITS_AB`. Cooldowns are counted in plays, not seconds, keyed by shirt in
`G.abCd` so they survive the snap that rebuilds every player. Four, five or
six plays by power. The computer plays out of the same kits through the same
`fireAbility`.

**Stats.** Every play is logged in `G.stats`. Box score and play by play
behind the STATS card.

**Netcode.** PeerJS, free public broker, four letter room codes, no account.
Host is authoritative and publishes the world at 20Hz; the guest sends input
only. Both sides call their own plays. See MULTIPLAYER.md.

**One dial worth knowing:** `GAME_SPEED` (currently 0.70) scales the whole
simulation. Route timing, pass rush timing and movement all read the same
game clock (`G.gt`), so they cannot drift apart when you change it.

---

## Bugs that recurred, and what they actually were

Useful because several took multiple attempts.

- **Players running sideways when knocked down.** Four attempts. The real
  cause was the separation pass, which writes straight to `x` and `y` and is
  outside the velocity system, so damping and pose work never touched it.
  Downed bodies are now barely shoved.
- **The whole team vanishing.** `dist` used two lines before it was declared.
  Undefined, so the throw scatter went NaN, the ball's target went NaN, and
  every defender chasing it took NaN coordinates.
- **Deep passes always incomplete.** The ball was led by a fixed 0.42
  seconds. Correct for a five yard out, five to seventeen yards short on
  anything deep.
- **Receivers quitting routes.** A scramble drill fired on a timer at 2.6
  seconds, before a deep ball could develop.
- **The defence running in single file.** Every defender solved the same aim
  point, so they arrived as one lump and separation squeezed it into a queue.
- **The defence running away.** Leading the carrier is right for a trailing
  defender and backwards for one already downfield.
- **The dive never working.** `driveHuman` rewrites velocity from the stick
  every frame. A juke survives because it sets `jukeUntil`; a dive set
  nothing, so the lunge was erased sixteen milliseconds later.

The pattern: when something looks wrong on screen, find the line that writes
the value, do not tune the numbers around it.

---

## Outstanding

- **The pass rush is soft.** Rushers hover about eight yards off the passer
  and do not close. Diagnosed, not fixed. This is the biggest gameplay gap.
- Real thigh and lower leg art.
- Graphics work that needs no art: turf texture, proper soft shadows,
  outlines so players pop off the grass, and a stadium instead of black
  around the field.
- The guest cannot pick plays for the Rivals' offence from a hero they chose
  themselves in every respect; check this if you touch the hero system.
- No reconnect in multiplayer. If either side drops, the room ends.
