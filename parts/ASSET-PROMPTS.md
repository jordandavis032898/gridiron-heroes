# Sprite asset prompts

Four assets. Paste each prompt as-is. Save into `parts/` with the filename given.

## Rules that apply to every one of them

**Background: fill it with solid magenta `#FF00FF`.** Do not ask for a
transparent background. The last batch came back with a checkerboard *painted
into the pixels* at full opacity, and it had to be stripped with local-variance
detection because colour-matching ate the white pants. Solid magenta keys out
cleanly in one pass.

**Crop tight, no padding.** The renderer stretches each part to the length of
its bone. Any empty margin becomes a gap at the elbow or the knee. The limb must
touch all four edges of the canvas along its long axis.

**Style: flat vector, matching the seven parts already in `parts/`.** Hard-edged
shapes, no gradients, no soft shading, no drop shadows, no outline strokes. One
flat colour per surface with at most one darker flat tone for shadow. These
render about 30 pixels tall on screen, so shapes must read at thumbnail size.

**Palette (use these exactly):**

| Surface | Hex |
|---|---|
| Helmet and jersey | `#1f2d54` navy |
| Numbers, stripes, trim | `#c8a63c` gold |
| Pants | `#f1f1ec` bone |
| Facemask, socks | `#14161a` near-black |
| Gloves | `#191b1f` |
| Skin | `#c98f63` |
| Leather | `#7a4a28` |

---

## 1. `football.png` — 160 x 100

Side-on American football, long axis exactly horizontal, centred in the frame.
Brown leather `#7a4a28`, one slightly darker flat tone underneath for form. Four
white laces across the top centre, and a thin white ring near each pointed end.
Pointed at both tips, widest at the middle. Perfectly symmetrical left to right
and top to bottom, because the sprite is rotated in code to spiral and any
asymmetry will wobble.

*Replaces a hand-drawn oval. It is the most-watched object in the game.*

---

## 2. `football-torso-lineman.png` — 91 x 160

Same side-view torso as `football-torso.png`, same navy jersey with a gold
sleeve stripe, but built like an interior lineman: noticeably wider through the
chest and shoulders, thicker waist, heavier shoulder pads that sit squarer and
higher. Vertical, shoulders at the top edge, waist at the bottom edge, filling
the full height.

*Right now all sixteen men on the field share one body. This is what makes a
line look like a line.*

---

## 3. `football-helmet-alt.png` — 160 x 142

Same side-view helmet as `football-helmet.png`, same framing and proportions,
but a different design: a single bold gold stripe front to back over the crown,
and a heavier full-cage facemask in `#14161a` with more bars. Navy shell.

*Give me a second one too if it is easy, with no stripe and a two-bar mask.
Mixing three helmets across sixteen players is the cheapest variety there is.*

---

## 4. `football-forearm-hand.png` — 160 x 29

Same side-view forearm as `football-forearm.png` — bare skin `#c98f63`, wrist
tape — but ending in an open gloved hand, fingers spread, glove `#191b1f`.
Horizontal, elbow hard against the left edge, fingertips hard against the right
edge, filling the full width.

*Used for the stiff arm, the catch and the tackle, where the arm is currently a
plain stick.*

---

## After you generate them

Hand them back and I will key out the magenta, trim to the bone axis, and wire
them in. I am doing the three-point stance in code with bone angles rather than
as art, so it is not on this list.

---

# Batch 2: fix the stick-man look (September 2026)

Six parts. Same rules as above: **solid magenta `#FF00FF` background**, crop
tight to the part, flat vector, same palette, **side view**, navy home kit only
(the code recolours navy to crimson for the away team). Exact pixel size does
not matter; I trim and scale. The long axis must run edge to edge.

## 5. `football-thigh.png` (vertical, roughly 100 x 160)

Side view of a football player's thigh in padded game pants. Bone-white
`#f1f1ec` pants, visibly thick and rounded from the built-in thigh pad, with
one navy `#1f2d54` stripe and one gold `#c8a63c` stripe running down the outer
seam. Hip at the top edge, knee at the bottom edge, knee slightly rounded where
the knee pad sits. No skin showing. Vertical, filling the full height.

## 6. `football-lower-leg.png` (vertical, roughly 60 x 160)

Side view of a football player's lower leg from just below the knee to the
ankle, wearing a tall navy `#1f2d54` sock with a thin gold `#c8a63c` band near
the top, pulled up to the knee. Muscular calf shape under the sock. The top
edge is where the white pant leg ends (a sliver of bone-white `#f1f1ec` pant
cuff at the very top). No bare skin. Vertical, filling the full height.

## 7. `football-upper-arm.png` (horizontal, roughly 160 x 60)

Side view of a football player's upper arm: the navy `#1f2d54` jersey sleeve
stretched over a rounded shoulder pad cap at the left end, one gold
`#c8a63c` sleeve stripe, then a short band of bare arm skin `#c98f63` near the
elbow at the right end. Thick and muscular, not a tube. Horizontal, shoulder
at the left edge, elbow at the right edge.

## 8. `football-forearm.png` (horizontal, roughly 160 x 36)

Side view of a muscular forearm, skin `#c98f63`, with white athletic tape on
the wrist and a closed black glove `#191b1f` fist at the right end. Thicker
than a normal arm. Horizontal, elbow at the left edge, fist at the right edge.

## 9. `football-torso.png` (vertical, roughly 110 x 160)

Side view of a football player's torso wearing big shoulder pads under a navy
`#1f2d54` jersey with gold `#c8a63c` trim. The pads should make the shoulders
clearly wider and higher than the chest, the classic football silhouette.
Numbers are not needed (the game draws them). Shoulders at the top edge, waist
at the bottom edge, filling the full height.

## 10. `football-helmet.png` (roughly 160 x 142)

Same side-view navy helmet with the gold stripe as the current one, but the
facemask must be solid near-black `#14161a` bars with **magenta showing
through the gaps**, not a grey checkerboard. The current helmet has a
checkerboard painted inside the facemask and it shows in game.

Drop the files in `parts/` with these names (or anywhere, and tell me where).
