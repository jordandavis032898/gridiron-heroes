# Gridiron Heroes: handoff

Everything a new session needs to pick this up. Read this before touching
`game.html`.

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

- `game.html` — the whole game source (flat view). EDIT THIS ONE.
  `index.html` (what the live link serves, 3D) and `demo3d.html` are
  GENERATED from it: run `python tools/build_demo3d.py` after every change.
  About 190 KB, one file, no framework. Canvas 2D. The only external script is PeerJS from unpkg.
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
s=io.open('game.html',encoding='utf-8').read()
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
- The lower leg (tall sock), upper arm and forearm were replaced in Sept 2026.
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

**Tackling.** Contact is a hit, not a touch. A defender who reaches the
carrier takes a chunk of his 100 HP (more on a dive or head on), then wraps
up and hangs on, dragged along with him; the wrap drains the rest. Hold time
scales with tackler power over carrier power. When it runs out, or the
carrier jukes or spins, the tackler falls off, goes down, and has to get up
before he can try again (`breakWrap`, `tackleCd`). Nothing drains from merely
being close.

**Line play.** Blockers pass-set between the rusher and the quarterback.
While engaged both sides hand-fight, and every so often the rusher tries a
move from `RUSH_MOVES` (rip, swim, spin, bull). Win it (`0.34 * power ratio`)
and he is through and the blocker is left flat-footed (`beat`); lose it and
the block holds longer. A spin is drawn as a turn (width through zero), not a
cartwheel.

**Line collisions.** Blockers are solid (`LINE_COL`): a rusher who is not
locked up with that blocker is pushed to the edge of him and slides round
the side nearer the ball, which bends the rush into a pocket. Locked pairs
(`locked`, `lockDir`) face each other, lean in, hands on chests.

**Feel.** Squash and stretch from velocity jolts (`sq`). Late in a pass the
landing spot drifts onto a receiver who is already close (magnet), and the
target raises his hands (`catchT`). No hit-stop, by request.

**Passing.** The throw leads the target off his velocity at release, then
the target plays the ball: he runs to the landing spot instead of finishing
his route. Before that, a man caught mid-cut or coming back to a scrambling
passer left the ball ten yards short of everyone.

**3D view (`index.html`, also `demo3d.html`).** Generated, never hand-edited: `python
tools/build_demo3d.py` rebuilds both from `game.html` with anchored patches
(broadcast camera, row-by-row perspective ground, stands, dynamic camera
that fits the play every frame, sideline out-of-bounds area, double-turn
spin). Change gameplay in `game.html`, then rebuild. The main link is 3D;
V toggles flat. Syntax check `game.html` and `index.html` before pushing.

**Rig joints.** Knees bend back (shin angle = thigh minus flex) and elbows
bend forward (forearm = upper arm plus flex). They were both reversed
once, which made every runner look like he was running backwards.

**Impact.** Outlines are baked into every body part once at load
(`outlinePart`, drawn with `drawPart` so joints still meet); `drawGuy` just
draws. A per-frame outline pass used to cost more than the players and made
every click feel late. The 3D world canvas is patched with dirty rectangles
(`dirtyRects3`) instead of repainted whole. A fresh stun launches the man (`vz`), and he lands and skids.
Rocket passes trail fire. There is deliberately NO hit-stop: Jordan read the
freeze on every hit as the game lagging, so it was removed. `say()` only
shows words matching `SAY_OK` (fumble, pick, first down, sack, touchdown,
turnover); every other callout is swallowed on purpose.

**Ball in hand.** `heldBall` draws the ball between the upper arm and the
forearm, swaying with the stride and rattling harder as HP drops or while
wrapped. A hit that leaves the carrier under 30 HP has a 2.5% chance to
jar it loose. A fumble pops up (`G.loose.h`, `vz`), bounces, and cannot be
recovered while it is above head height.

**After the play.** `postPlay(txt)`: banner (only if it passes `SAY_OK`),
then after 1.5s the hero card slides in from the right while that player
celebrates (`cel`: hop, fists pumping), then back to the play call.

**Dropback and pocket.** `DROP_YDS` per call (max 6); the QB backpedals facing
downfield (`backpedal`, stride runs in reverse) until the stick is touched.
Within `POCKET_YDS` (6) behind his snap spot and behind the line he stays a
passer: faces downfield, ball at his chest (`pocket`). Past it he runs.

**After the play (checklist).** `logPlay` picks the card: touchdown (scorer,
`td` dance), sack (sacker, `flex`), first down (carrier, pump), out of
bounds on offence (carrier), tackle for 5 or less (tackler, `flex`,
"DEFENSIVE STOP!" banner). The card slides from off the left to centre.

**Stances.** `STANCES`/`stancePose` per position (three/four point, backer
crouch, DB, WR stagger, QB), built from rig angles plus a body lean and
drop. Pre-snap fidgets (breathing, shuffles, claps, glances) run on each
man's own clock seeded by his number.

**Stadium (3D build).** Towers, scoreboard, benches, tents and sideline
players are anchored in world space (projected with `proj3`), never screen
space: the first towers were drawn at fixed screen spots and slid with every
pan. The field is framed `STAND_OFF` below centre so the stands show. The crowd
is three pre-painted frames cycled (faster on a touchdown). `sidelineGuys` are
drawn only when on screen.

**Kicks and intro.** Touchdown is 6, then `startPAT` kicks from the 15 (94%).
`heroIntro` spotlights the star at midfield with his card and stars before
the first play call.

**Passing physics.** Short throws are faster and flatter, deep ones slower
and higher. Wobble (`wob`) grows with pressure at release. Contested balls
(receiver in the window, defender within 16) are a weighted roll: catch,
break-up or pick.

**Super moves.** Play-counted cooldowns (`abSpend`). A move a person fires
gets `superMoment`: a half-second spotlight and a corner banner. The CPU's
moves stay quiet on purpose. J = juke/dive, K = special/big hit. Keyboard
movement eases in over ~0.1s. Picks, fumbles and touchdowns set
`G.broadcast`, which zooms the camera onto the playmaker while his card is up.

**Game start.** Star intro (Space or the Skip button), then `startCoinToss`
(1/2 or click; the winner receives), then `startKickoff`.

**The kicking game.** One meter for every kick (`kickMeter`, `KM`): an aim
needle then a power bar, Space/Enter/click to lock each; the CPU runs it on
its own (aim spread grows with distance). Kickoffs are live plays: cover team
from its 35 in lanes, returner deep with lead blockers, the ball is a
`G.thrown` with `kickoff:true`; `G.los` is moved to the receiving goal after
the kick so pursuit runs at full speed (it was jogging and every return
scored). Deep in the end zone is a touchback. `startFieldGoal` (fg and pat)
snaps a real unit against six rushers; `fgKickTick` gives the operation
1.05s and a rusher at the hold can block it (rare). `launchFieldGoal` turns
aim/power into good, wide or short; `afterKick` kicks off after a try or a
made field goal. Goalposts (`drawGoalposts`, `goalX`) stand on both end
lines; good kicks are still rising at the posts (`hf`). Delayed steps check
they still belong to the same game (`g0`).

**Playbook, play art, audibles.** Play cards draw each play from the same
route shapes the players run (`pdRoute`, `drawPlayDiagram`). Before the snap,
hold C or the right mouse button for play art on the turf (`drawPlayArt`),
X for the audible bar (`callAudible` re-runs `setupPlay` on the same down).

**Tips and swats.** A contested ball the defender wins can pop up
(`tipBall`) and belongs to whoever gets under it (`resolveTip`). K on
defence with the ball in the air swats (`swatAt`). Drag tackles lock onto
the carrier when the drag points roughly at him.

**Knockdowns.** `knockPose` turns `down`/`stun` time into a posed timeline on
the rig: fall back, lie flat, sit up, one knee, stand. Game logic freezes a
man until both reach zero, so the get-up finishes exactly as he can move.

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

- **The soft pass rush, and backs running alongside the carrier.** Same
  cause. Every defender pursues toward the carrier plus a sideways `lane`
  offset (up to about three yards) so they arrive on angles, and it was held
  all the way in, so a rusher parked beside a passer who stood still and a
  back ran level with a runner instead of hitting him. The lane now fades to
  nothing over the last few yards. Separately, the block's hard line only
  checked width, so a rusher already yards past his blocker was snapped back
  to the blocker's side of the line; a block now needs contact.
- **Knocked-down players sliding sideways.** `down` only counted off in
  `deadTick`, after the whistle. A man flattened mid-play stayed drawn flat
  for the rest of it while the AI (or your stick) ran him at full speed. It
  counts off live now, and nobody moves while down.

The pattern: when something looks wrong on screen, find the line that writes
the value, do not tune the numbers around it.

**Testing headless.** The reliable way to measure behaviour is to load a copy
of `game.html` in Playwright with a hook exposing `freshGame`, `setupPlay`
and `step`, stub `requestAnimationFrame`, and call `step(1/60*GAME_SPEED)`
yourself. Two traps: juke, dive and sidestep windows are on
`performance.now()`, so replace it with a clock you advance 1000/60 ms per
step or one juke lasts the whole run; and `G.stats.log` is capped at 60
entries, so detect the end of a play from `G.phase`, not the log length.
Run plays in one game rather than a fresh game each, or every ability is off
cooldown every snap.

---

## Outstanding

- Real thigh and lower leg art.
- Graphics work that needs no art: turf texture, proper soft shadows,
  outlines so players pop off the grass, and a stadium instead of black
  around the field.
- The guest cannot pick plays for the Rivals' offence from a hero they chose
  themselves in every respect; check this if you touch the hero system.
- No reconnect in multiplayer. If either side drops, the room ends.
