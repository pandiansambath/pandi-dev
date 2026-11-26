# CLAUDE.md — pandi-dev

Everything about **pandi-dev.dineai.cloud**, Pandian Sambath's profile site: its
code, its content, how it is hosted, and the rules its owner has set for it.
Read this before changing anything.

---

## 1. What this repo is (and is not)

- **This repo is the public, runnable mirror of the site.** It holds all the
  site's code, the photos, the résumé, the rank list, the 3D chest model, the
  sound effects and the fonts. `npm run dev` gives you the whole site locally.
- **The live site is NOT deployed from here.** It is built and served from the
  private `mise-erp` monorepo (the DineAI product), which owns the server, the
  domain, the deploy pipeline and the S3 bucket. In that monorepo the site
  lives in:

  | monorepo path                        | here                               |
  |--------------------------------------|------------------------------------|
  | `frontend/dev/*`                     | `dev/*`                            |
  | `frontend/app/dev/page.tsx`          | `app/page.tsx` (one line differs)  |
  | `frontend/app/award/page.tsx`        | `app/award/page.tsx`               |
  | `frontend/public/dev/*`              | `public/dev/*`                     |
  | pandi-dev blocks of `app/globals.css`| `app/globals.css` (below the head) |
  | `backend/app/api/dev_site.py`        | `backend/dev_site.py` (reference)  |
  | `backend/tests/test_dev_site.py`     | `backend/test_dev_site.py`         |
  | `dev/scripts/*`                      | `ops/*`                            |
  | `resume/build_resume.py`, `resume/final/*` | `resume/*`                   |

- **To change the live site:** make the change in the monorepo, deploy it there,
  then refresh this mirror with `python scripts/sync_from_monorepo.py <path-to-mise-erp>`
  (code) and `DEV_SITE_BUCKET=<bucket> bash scripts/pull_content.sh` (content).
  Edits made only here never reach the live site.

## 2. Run it

```bash
npm install
npm run dev          # http://localhost:3000  (the profile)  ·  /award (the chest)
npm run build && npm start
npm run typecheck
```

The page reads its files through `app/api/dev-site/[...path]/route.ts`, which
serves `content/` read-only with the same allow-list as the real backend.
Uploads and edits answer **501** here — they need the live backend.
The mirror plays no music (see §8).

## 3. Map

```
app/
  page.tsx                 the profile (server component: loads the manifests, renders DevProfile)
  award/page.tsx           the award room: a real chest, hammer, gold, ancient score
  error.tsx, award/error.tsx, global-error.tsx   what stands in when a page fails (never the framework's white page)
  api/dev-site/[...path]/  read-only file server over content/ (stand-in for the backend)
  layout.tsx, fonts/       Geist, Geist Mono, Fraunces (+ Cinzel for /award), all local
  globals.css              head (this repo) + the site's CSS (synced, dev-* namespaced)
dev/                       every component of the site (see §4)
public/dev/                models/ (Poly Haven, CC0), sfx/*.mp3 (Mixkit), hammer.svg — with CREDITS.md
content/                   mirror of S3 dev-site/: album.json, full/, thumb/, profile*.webp,
                           RANK_AFF_UG_2023.pdf, resume/*, music.json (empty playlist here)
backend/                   the FastAPI router + its tests, for reference
ops/                       album build, résumé publish, page on/off switch (run from the monorepo)
resume/                    the résumé generator and the final PDF/DOCX
scripts/                   sync_from_monorepo.py, pull_content.sh, globals.head.css
```

## 4. How the site is built

**One shell, many designs.** `dev/DevProfile.tsx` is the shell every design runs
inside. It owns the state shared through `useDev()` (`dev/context.tsx`): the
intro (it opens by itself), the theme, the album, the résumé viewer, milestones, toasts,
the music player and the owner panel. A design is a whole page that reads that
context.

| design id   | name           | file                    | idea |
|-------------|----------------|-------------------------|------|
| `chain`     | Chain Reaction | `ChainDesign.tsx`       | the default and the first impression: a skill orbit, a scroll-lit chain spine, link-flip cards, the 3D ring finale |
| `metro`     | Metro          | `MetroDesign.tsx`       | his career as a transit map |
| `chronicle` | The Chronicle  | `ChronicleDesign.tsx`   | a newspaper front page with him as the lead story |
| `terminal`  | Terminal       | `TerminalDesign.tsx`    | the whole site as a console |
| `bento`     | Bento          | `BentoDesign.tsx`       | one screen of live tiles |
| `blueprint` | Blueprint      | `BlueprintDesign.tsx`   | engineering drawing sheets: a self-drawing frame, live title block and dimension line, the career as a plotted system diagram with data packets, skills as a bill of materials, DineAI as a layer section, CAD crosshairs |
| `stories`   | Stories        | `StoriesDesign.tsx`     | full-screen photo stories (tap, hold to pause, arrow keys, live stickers) beside a profile with highlight rings and a post grid |
| `ember`     | Ember          | `EmberDesign.tsx`       | a cinematic three.js scene in the immersive-WebGL school: two interlocked iridescent chrome chain links that turn with the scroll and rest when it stops, embers of the theme's colours that rise and burst with scroll speed, a light streak, corner light and moving grain, a glyph loader, chapters whose words rise out of masks, a chapter rail |

**Themes.** 15 palettes in `dev/theme.ts` (`THEMES`). A theme is a set of
`--d-*` CSS variables put inline on `.dev-root` by `themeStyle()`; every
component colours itself from those variables. Canvas and WebGL code reads them
with `readRGB()` and re-reads on `THEME_EVENT`. The Studio (`Studio.tsx`, the
palette icon in the top bar) lets a visitor switch theme and design; the switch
plays a circular View Transition. `?theme=<id>&design=<id>` in the URL also works.

**The intro (`BootSequence.tsx`, `opening.ts`, `openingArt.ts`, `stage.ts`).** Nothing is
shown until everything is loaded: the portraits, the first song, three.js, the chest model,
the award room's code and the sound effects are all fetched while the counter runs
(`bootTasks` in `DevProfile.tsx`). There is NO ENTER button: when the last of it has come
the site opens by itself. What stands on the door goes to dust (every dot of its ink is
read off a 2D canvas) and falls, swirling, into one point; a breath; the point bursts; the
page is there inside the shock front; the dust that hangs there afterwards spirals home into
the galaxy at the head of the skeleton (no galaxy in sight: into the portrait), which forms
out of it. One raw WebGL canvas, every grain moved in the vertex shader — it was a 2D canvas
first, and two thousand drawing commands a frame cost 25 ms. The door is `[data-boot]`
(`loading` → `sealed` → `open`, then gone): tests wait for that. Rules it rests on:
- Behind something truly OPAQUE a browser paints nothing, and then the whole page is painted
  in the very moment it opens (0.7 s of stall). So the door is 99.7 % opaque while it loads,
  nothing behind it is hidden with `opacity: 0`, and what `entered` sets moving is held at
  its END until the burst (painted, all of it) and then played from its first frame.
- `stage.ts` knows whether the page can be seen: canvases draw a few frames behind the door
  and hold still (`holder`), what plays once plays when it is first seen (`whenOpen`,
  `useOpened`), heavy builds keep out of the opening (`atLeisure`).
- It gives its context back if the browser takes any of the page's away; no graphics, lost
  graphics, or reduced motion: the door simply fades. Coming back from the award room it
  goes straight to the point of light.

**Chain Reaction pieces.** `SkillOrbit.tsx` (3D rings of skills, drag to spin),
`ChainField.tsx` (background strands, turn with scroll), `ChainSpine.tsx`
(the line that lights as you scroll), `MonthChain.tsx` (one block per month
since 1 Jan 2024; single click = details, double click = edit), `Terminal.tsx`
(the Shell card: type or tap commands), `SkillClusters.tsx`, `Highlights.tsx`,
`Resume.tsx`, `Finale.tsx` + `ChainRing.tsx` (the 3D chain that assembles,
closes with a flash and turns; tilt follows the pointer, drag spins it).
**The orbit (globals.css `devRevolve` / `devRevolvePhone`, `orbit.ts`).** Every right-hand
card (`[data-link]`) lives one life by its own scroll position (a named view timeline,
`--dev-card`): it comes out of the crystal divider as a ball, unwinds to full size on the RIGHT
facing you (the present, 40–60 % of the way), winds itself up again and goes back into the
divider. As it lets go of its place it floats (the page goes on under it), so that what happens
at the divider is seen a fifth of the way down the screen, not at its edge. On a phone (one
column, the divider behind its middle) it swings out a little and in. Transforms only — no
z-index in the keyframes (that drags the whole orbit onto the main thread). THE SAME NUMBERS are
in `dev/orbit.ts` (the browser moves the card; what draws its ball must know where it is): change
both. CSS also shows a card's words only in the present (`devChainReveal`).

**Surfaces (`CardGL.ts`, `registerSurface`).** The popups and the sound menu
wear the same glass and water as the cards (a surface is always open and flat, no
ball). Their buttons are glass (`.dev-glassbtn`) over the water.

**Words that can be read (24 Nov: "text should be clearly visible, dude").** A card's words are
there ONCE: the page's own in the present, the painted ones (`cardInk`) either side, never both
(the first card waits exactly at the edge of its present: it goes by its own leaving, or its
painted words lie over its own, "10" and "10"). Behind words the water is quiet (`uInkHas` in
`cardScene`: its bright veins crossed the letters), their edge is a fine dark one, the faintest
inks a step plainer on the cards' column (`.dev-words` in globals.css). The sheet's words are
painted at 2–2.5× and sampled a little sharp: one may stop the scroll half wound and read them.
The orbit of skills goes a sixth slower than it did, and its pace is his (owner panel → Portrait,
`pace` in `portrait.json`).

**The top menu is written, not drawn (`TopBar.tsx`).** Three menus that drew
something behind the buttons (a black bar, a water bar, liquid capsules) each pulled
the eye, so nothing is drawn: small spaced mono capitals in the page's own hand
(MAIL · LINKEDIN · GITHUB · INSTAGRAM · RÉSUMÉ · THEMES, the music's bars first) in
quiet ink that brightens under the cursor, every item one style (the résumé only in
the accent colour), a halo of the page's ground behind the letters for legibility.
Each word decrypts into place on arrival (on the clock, not per frame); under the
cursor a hairline draws beneath the word and ends in a small ring — a link of chain.
It tucks away while you read downwards (`data-tucked`; one small node stays in the
corner) and returns on any scroll up, a mouse at the top of the screen or a tap on
the node; never while its menus are open. A phone shows the same items as thin line
icons with nothing behind them. His name joins the PS mark only while the nameplate
(`[data-hero-name]`) is off screen. No WebGL in it — see the next paragraph.

**Smooth on a phone (measured, §101.9).** A mobile profile found the page saturated
before any scroll: the chips' painted rim held a 51 KB data URL in a CSS custom property
and 20 chips restyled through it every frame (~60 ms a chip). Rules that came out of it:
never put a large value (a data URL) in a custom property on elements restyled per frame;
write per-frame styles only when they change; never make or drop WebGL contexts while
scrolling — the card pool is FIXED and WARM (3 on a phone, made during the intro, shaders
compiled with `compileAsync`, handed out only when ready, never retired) and the finale's
ring is built once in idle time and kept; only the soft canvases (dust, cards) render at lower resolution on a phone;
no layout reads inside a frame (cache positions); nothing repaints every frame (the
name's sheen is still on touch screens).

**A phone has only a few WebGL contexts (`glGuard.ts`).** Chrome on Android keeps
about eight live WebGL contexts per page and, past that, kills the OLDEST — and
paints the dead canvas WHITE with a broken-picture mark (his "white white boards").
Reproduce with Chrome's `--max-active-webgl-contexts=8` at phone size. So: a phone's
card pool is 3 canvases and gives one back while the award room or a no-photo portrait
piece claims a context (`claimContext()`); the finale's ring is built once and kept; the orbit's chips on a phone wear PAINTED water instead of a WebGL
canvas; the award room frees its context on close. Every WebGL canvas is guarded:
taken away by the browser, it marks itself `data-gl-lost` (hidden by CSS — the dark
ground shows, never white) and the card pool cuts its cap. Our own clean-ups free
contexts on purpose: take the guard off first. An app's own browser (Instagram's) loses
them too: the no-photo piece and the skeleton ask for a fresh canvas a few times
(`useComeBack.ts`), and a still of the piece (`[data-core-still]`) stands there until it is
drawn — never an empty place in the orbit. The background does not come back (asking again
took the portrait's piece away).

**What a card LOOKS like is drawn in WebGL (`CardGL.ts`, `cardScene.ts`), its words painted on
it (`cardInk.ts`).** `CardChrome` (`flourish.tsx`) only puts a slot in the card; a small pool of
WebGL canvases moves from card to card, near the screen only (`CardGL`: who has a canvas, where it
is in its orbit, the cursor). What is in it is `cardScene`: one sheet of dark glass with the
theme's painted water (`liquid.ts`) in it. Flat, it is the card. As it leaves, it WINDS ITSELF UP:
its right edge lifts towards you, curls over and winds to the left, turn upon turn, a scroll;
then the scroll opens out, is drawn in to its poles and closes as a ball of that same glass, the
turns still inside it, the water running round them, drops going round it. It opens the same way.
The shape is worked out column by column on the CPU (how tight the scroll is at each place) and
handed to one mesh; glass is seen through, so the half of it behind its middle is drawn first,
from the outside in, and the half before it after, from the inside out (two index buffers, no
depth). It is lit by the spine: a strip of light mirrored along the bends, cut edges that glow,
thin-film colours, air in the glass, the light that went through gathered on the far side.
(On 24 Nov it closed into real planets for four hours: the owner hated them, "too comic", "a
planet is awkward" beside a skeleton. Do not go back. Calm: "don't make [it] too bright… also
don't make [it] too dull".)
In the present the words are the page's own text; either side of that they are a PICTURE of those
words on the sheet, or they would stand still while the card turns ("text words are not following,
see"). `cardInk` reads each card once (boxes, hairlines, icons, letters line by line, with the
scroll's animations off: `data-inking`) and paints it with the same fonts in the same places; the
page's own words go out in the few pixels of scroll in which the painted ones come
(`devChainReveal`, `ink` in CardGL) and do not move, or the two are seen apart. What counts (a
clock) is painted again just before it is needed. It is drawn every frame only while it winds; a
ball at rest every third, and the browser moves the canvas. Do NOT go back to CSS layers for a
card: a dozen layers a card measured 318 layers / 76 MP of layer pixels — past the GPU budget, so
tiles were thrown away mid-scroll (flicker).

**The crystal spine (`CrystalSpine.tsx`, inside `ChainSpine.tsx`).** A 3D column of real
VERTEBRAE — body, pedicles, lamina, transverse and spinous processes, facets, the canal —
modelled offline as signed distance fields (`ops/art/vertebra.py`), meshed, decimated and
packed with their own baked ambient light (`public/dev/spine/bone_*.bin`, `spineBone.ts`):
two of them, in two finenesses (triangles much smaller than a few pixels cost the GPU the
same pixels several times over), with clear discs between, seated like a spine on one
curve, about the cord behind their bodies. Their crystal (an iridescent film, a clear coat,
a dark room of the theme's lights) is baked into two small pictures as it turns
(`spineBake.ts`). A sticky canvas in the divider's lane; the bones are laid out in the
column's coordinates, grow out of nothing at its ends, and rise into place as the site
opens. Round it: a dense, slow sleeve of bokeh and bubbles and fast sparks that surge upward
when you scroll. The line and the dot that runs down and stops at each card are DOM
(ChainSpine).

**Touched, the skeleton breaks and is born again (`spineBreak.ts`, `spineBake.ts` SHATTER,
`spineBone.ts`).** A click or a tap on the bones (a strip down the lane, `data-spine-touch`;
the galaxy's heart has its own): cracks run up and down the column with the cord's light in
them, then it bursts, the struck bone first; the light dies, the pieces hang and sink in the
dark; a heart beats where the cord was; the pieces spiral home and the cracks heal. Each
vertebra really is in nineteen pieces, modelled offline from the same distance field
(`ops/art/fracture.py`: their rough faces fit each other), and every piece's flight is worked
out in the bones' own shader from which bone and which piece it is: the CPU only says how far
along each bone is (`boneLife`). The spine's canvas is 1240 px wide meanwhile (made so in the
moment of the blow, put back when nothing scrolls); `.dev-root[data-shatter]` dims the cord,
and thins the cards' glass on a phone, where the skeleton stands behind them. Its sound
(`spineSound.ts`, synthesised) plays only while the music does. What runs through the spine
besides bone — nerves, the beaded cords either side, ligaments, impulses along them — is
`spineNerves.ts`: ribbons as wide as they are on the screen.

**The ball goes into the skeleton (`orbit.ts`, `guests.ts`, `spineGuests.ts`, 25 Nov).** "When I
scroll, that ball is disappearing: instead make that ball dissolve inside the skeleton." A ball
near the bones cannot be drawn on its card's canvas (that canvas is behind the skeleton, on a
phone before it), and one that goes INTO the bones has to be among them. So, closed, and come
within the skeleton's lane, its card lets go of it (`CardGL.handed`: its own canvas is emptied in
that very frame) and the skeleton draws it: the same ball (`cardScene`, `bare`) to a small picture
of its own, hung in the skeleton's scene as deep at every pixel as a ball is there
(`gl_FragDepth`), so bones stand in it and out of it. The bones answer the ball nearest them
(`spineBake` GUESTS): in it they are larger (a ball of water is a lens) and under water — its light
in moving nets, its skin a bright line where a bone comes out — and as it soaks in, its light runs
up and down them in veins, with the nerves and the light in the gaps. The ball thins, is drawn to
the cord, and is eaten away from its rim inwards in the pattern of its own water, every edge a
line of light (as wide on the screen wherever it runs: by `fwidth`); its drops go round the bones
and into them, and it fizzes. All of it is a matter of how far one has scrolled, so it runs
backwards: that is a card's birth. The skeleton asks the cards where their balls are at the moment
it draws (`guestsAt`), or they would lag the scroll by a frame. Everything is drawn once, out of
sight, before the door opens. Where there is no skeleton to take it in, a ball fades there.

**The hand in the water (`flow.ts`, 24 Nov).** The cursor does not drop rings on a lake any
more: there is water over the whole screen — a coarse grid of it (81 by 38 on a laptop), worked
out on the CPU in about a millisecond (stable fluids, its eddies kept alive in the wake only; a
surface with waves, in FIXED steps of 1/100 s — a step that follows the frame turns to a
checkerboard; how TORN each place is) and only while something moves: it comes to rest and stops.
How torn follows how FAST the hand goes (nothing under about 200 px/s, all of it at 700): a slow
hand, reading or on its way to a link, only ripples it. The background and every card are handed
the numbers as two small half-float textures (`flowTexture`: what moves, and the surface's slopes
— a slope read off a height between its neighbours shows the grid) and are bent and lit by them
(`SURFACE_LIGHT`); the chain's blocks, the drifting words and the orbit's chips sway
(`water.at`). A mouse stirs it, a press (a tap) is a hand put in; a finger that scrolls stirs
nothing. In a shader read it with `textureLod`.

**What the hand passes over comes APART (`scatter.ts`, 24 Nov).** Not only what is behind things:
the name, the words, the photo, the skeleton, the cards ("the font is looking the same, the
skeleton is looking the same… I thought my photo will scatter… erasing and again rejoin[ing]").
Nothing on a page can reach the pixels of the rest of it, but the browser can, when it draws a
pane of glass over it: a fixed pane whose `backdrop-filter: url(#…)` moves what is behind it by a
picture (`feImage` → `feDisplacementMap`: red sideways, green down, blue whether at all). The
picture is made every frame there is one to make: the screen is a honeycomb of 11 px cells; those
the water has torn hard enough let go of their piece of the page, which goes with the water, out
of the hand's way, and comes home. Over the pane a canvas (raw WebGL2) draws what the page has
not got: the dark of the hole, the light on each piece, its shadow, dry strokes where the page
was pulled. Things that matter: the picture is an UNCOMPRESSED BMP packed in a worker and shown
by object URL (a data URL of that size costs 11 ms a frame, a PNG 30; an `href` to an element of
the page draws nothing in a backdrop filter); between a piece and the rest the picture is the
middle of both channels, or everything in between is drawn as outlines; it and the canvas's
drawing of the same moment are shown in the same frame; the pane is no larger than what goes on
(it costs by its area) and not there at rest; the first such filter and the first use of each
shader stop the page, so all of it is drawn once, unseen, above the door; `backdrop-filter` is
set from JavaScript (the stylesheet's builder drops what it does not know). Chromium only
(`canScatter`); elsewhere `water.apart` stays true and the background's and the cards' own
shaders come apart by themselves (`COME_APART`).
A FINGER does it too (25 Nov: "in mobile too… if I move my touch I need to feel the same"): one
that sets off SIDEWAYS, and then goes where it likes, and one that taps; one that sets off up or
down scrolls the page, as ever (`.dev-root { touch-action: pan-y pinch-zoom }` on a coarse
pointer). There the canvas over the pane is a plain 2D one drawn from four stamps (a phone keeps
only a few WebGL contexts), the cells are larger, the picture finer (its steps are seen at 2.75),
and a phone that cannot keep up gives it up by itself (`tooSlow`).

**Smoothness rules (measured 0.3 → ~50 fps, 22 Nov).** No backdrop blur anywhere
on the default page; no `filter: blur` on moving layers; no custom-property
animations (they repaint every frame); no permanent animations on every card;
motion inside cards is scroll-linked only. Check with a frame-time measurement,
not by eye — and warm the browser up first (the first run is always slow).

**Nothing asks the page where it is in the middle of a frame (24 Nov).** `scrollY`, `scrollX`,
`getBoundingClientRect`, `offsetWidth` in a rAF loop or a scroll handler make the browser work
out every style changed so far, on the spot (10–20 ms on a slow laptop), and again at the
frame's end. Use `pageY()` (`scrollPos.ts`: a scroll timeline's own number; a phone is asked
as before), boxes measured in ResizeObservers, sticky worked out by arithmetic (`box` in
CrystalSpine), and in handlers read in a `setTimeout(0)`, when the frame is done. And what
MOVES carries nothing: an element restyled every frame (an orbit chip, a card with a
scroll-driven animation) has only its transform; its gradients, its `var()`s and its inherited
text styles are on a child, or on the column (`.dev-words`). The drifting words are drawn by
the chain's canvas on a desktop (thirty animated elements fewer). Find such things with a
trace of `UpdateLayoutTree`/`Layout` with JavaScript stacks.

**A 2D canvas is paid by the command, and a canvas drawn FROM by the canvas (24 Nov).** Thirty
drifting words, each a small canvas of its own, thirty times a second, were more than half of
what the page cost the graphics at rest: now they are one sheet, an `ImageBitmap`. The chain is
drawn in a few shades, each in one stroke; the chrome of the name in slanted strips of 5 px. What
does not change is handed over once (`kept` in plateKit). And a pointer handler asks the layout
nothing in a stroke (`letterSwell` waits until the pointer slows: finding the letter under it is
12 ms of every frame).

**A scroll never waits for the graphics (24 Nov).** The hitches left in the scroll, 50–150 ms
each, were all the page standing still for an answer from the GPU process:
- a canvas given another size (`setSize`) as it was handed from card to card. The cards'
  drawing surfaces are now made large enough behind the door, never made smaller, drawn in
  only as far as the card needs (a viewport), and a card takes the smallest free one it fits
  (`CardGL.ts`: `need`, `freeFor`, `presize`). The background on a phone is `100lvh`, so
  the address bar sliding away does not resize it;
- three asking about every shader the first time it is used: `quiet(renderer)` (`glGuard.ts`)
  turns that off unless the address says `?glcheck`, and everything a renderer draws is drawn
  once, unseen, behind the door (with its camera in place: what is culled is not warmed);
- `new AudioContext()` (music, below).
Find them with a wrapper round the GL calls that logs any that take over 8 ms with a stack,
or a trace (`GLES2::GetGLError`, `CheckFramebufferStatus`, `GetProgramiv` on the main
thread). In a shader never `pow()` something that can be negative (garbage on some phones):
`sq2()`. Hold the page behind a popup with `holdScroll()` (`scrollLock.ts`, on the
`<html>`): a body told to hide its overflow becomes a scroll box, and every sticky thing in
it lets go. A canvas steps its sharpness down only when its GPU time AND the page's frames
are late (`sharp.ts`): a chip with little to do slows its clock and reads high.

**The background (`DustField.tsx`, `decor`).** One WebGL layer under the
content. For the Chain design it also paints the room — the corner washes, three
drifting blooms, the waves, the vignette and the dot grid — which used to be five
full-screen layers: ~100 MB of GPU memory on a phone at DPR 2.75, past its tile
budget (Chrome then fills undrawable tiles with a layer's background colour: the
orbit's chips came back as black boxes). Keep new full-screen decor in this
canvas, not in DOM layers; test with `--force-gpu-mem-available-mb=64`. Also: the cards' watercolour across the whole page, quiet,
zooming IN endlessly with the scroll (never out), and dust drifting towards you.
Where the pointer moves (a tap on a phone) rings run out like a stone in water —
through the dust AND the watercolour. Half-rate when idle, asleep when hidden.

**The two ends of the spine (`CrystalSpine.tsx`, `ChainSpine.tsx`, `Finale.tsx`,
`DustField.tsx`).** THE TOP is a portal, a small galaxy: a disc of dust in perspective along two
spiral arms, turning once in ~75 s and drifting in towards a glowing heart with a rim of
light (on its own real-time clock; a grain's angle is the disc's turn plus a twist that
depends only on how far in it is — never clock × speed-at-this-radius, which whirled
faster the longer the page was open), more dust drawn up into it from round the first
bones — which condense out of the dust, small and loose,
before settling — forming, as the site opens, out of the dust that comes home to it; the
spine's core light rises out of its heart. The lane reaches `SPINE_HEAD` (130 px) above
the column for it. THE BOTTOM: over the column's last 320 px the vertebrae break apart
while interlocking links form among them, and the chain is lowered to just through the
finale's surface and on 40 px past it, so the last link crosses the line and fades
below it — the lane's length below the column is MEASURED to `[data-surface]`
(ChainSpine writes `data-tail`; a fixed figure fell short on a big screen). On a phone
the portal is lifted 54 px, clear of the first card the spine stands behind. The
finale's top is no border but a surface of light, the panel's glass and outline fading
in below it; DustField draws rings spreading across it in perspective from where the
chain dips in, and, while it is on screen, eight STREAMS of dust pulled in from both
sides, narrowing to a thread at the chain and plunging down it into the water (spray
thrown back up), building as the surface rises; as it passes 72 % of the screen a
shockwave crosses the water and light runs up the chain; shafts of light pour in. A HIDDEN EASTER EGG: touch the
galaxy's heart (`[data-galaxy-heart]`, an unmarked button in the lane) and it draws in,
swells to several times its size, bursts across the page in streaks and shockwaves,
hangs as a cloud, and spirals home (`GalaxyBurst.ts`: a 2D canvas over the page for ~5 s
— no extra WebGL context — removed when it is over; the spine plays its half to the same
`BURST` clock; a phone vibrates). The finale has NO
scroll-driven entrance: the cards' `dev-reborn` tilted and lowered it as it came in,
sliding the surface away from the chain.

**How sharply a canvas is drawn (`sharp.ts`, `spineBake.ts`, `ringBake.ts`).** A phone's
chains are drawn at its screen's own resolution (spine 2.5, ring 2.75 pixels per CSS pixel;
award room and no-photo pieces 2), anti-aliased. They used to be cut to 1–1.25 "for
smoothness" — but what cost the GPU was the MATERIAL, worked out at every pixel (a thin
film's rainbow, a clear coat, reflections, three lights): 10.1 ms a frame for the spine at
full resolution, 1.2 ms without the bones. So on a phone the material is drawn once per
theme, by the real `MeshPhysicalMaterial`, onto a small picture of every direction a surface
can face, and a pixel looks itself up; the lights that move are still worked out live. The
spine at 2.5× costs what it cost at 1× (3.4 ms against 3.5 on a laptop's chip), the ring
2.7 against 2.1 (and its 22 draws are one). A desktop draws the materials themselves.
`watchGpu()` times each canvas on the device (EXT_disjoint_timer_query_webgl2, else frame
pacing) and steps its resolution down only if that device proves it cannot keep up,
remembered in `localStorage`. `?sharp=spine:2,ring:1.5` sets it by hand and records the GPU
times in `window.__sharp`. The spine's canvas on a phone is `100lvh` (with `dvh` it was
remade each time the address bar slid away).

**No opacity animation on a group inside a tilted card.** A group whose opacity may
animate (even one whose animation has not begun) is drawn to a picture of its own first, and
under a perspective transform the browser makes that picture at 1x: on a phone the first
card's words, at rest on the first screen, came out with rows missing. That card's reveal
animates transform only; `CardGL` marks it `data-away` as it starts to leave and a short
transition fades the words.

**The orbit (`SkillOrbit.tsx`).** 20 seats on three rings, planned (`planOrbit`) from his
list of skills — `copy.skills` (owner panel → Template: take any out, add any, ★ = always in
sight; saved with his words) or, by default, the résumé's (`DEFAULT_ORBIT` in `skills.ts`).
Pinned chips never change; the others take the next skill each time they pass behind the
portrait. What he adds goes first in the list and takes a seat at once; names are 15 letters
at most (longer ones collide on a phone); a short list has one seat per skill. Each chip is dark glass with
the skill crisp in the middle and the cards' water only in a thin liquid rim round its
edge (painted into the border — the owner found water behind the words unreadable). The
orbit stops moving while it is off screen. The portrait's photos and their pace come
from `portrait.json` (owner panel → Portrait), defaults in `dev/portraits.ts`.

**The portrait's designs (`PortraitDesign.tsx`, `PortraitCore.tsx`).** Not colour
filters but ways of showing him: Natural · Aura (no frame: the face sharp, the edges
dissolving into a glow of the photo's own colours, a brighter rim) · Immersive (the photo
sunk into the page behind the orbit's rings, large, soft and graded, the face clear at the
centre) · Halftone (a real dot screen, drawn on a 2D canvas, in the theme's colours) ·
Code (his face written in his own skills, auto-levelled) · Hologram (two-tone, red and blue
fringes, scanlines, a flicker). And with NO PHOTO, a living 3D piece in its place (one
WebGL canvas, claimed on a phone): Star (granulation, sunspots, corona, prominences, solar
wind) · Crystal (dark iridescent shards out of rock, a heartbeat of light) · Chain knot
(interlocking links in a trefoil, a light running round) · Neural (neurons, synapses,
pulses firing) · Black hole (a shadow, a photon ring, the disc's far side bent over the
top). Chosen only behind the PS door (`look` in `portrait.json`); `PortraitLooks.tsx`
holds the SVG filters (graded, duotone, the hologram's colour fringes) built from the live
theme.

**The Template (`copy.ts`, `words.ts`).** It reaches EVERY word of the page: the name's
area, the menu, the door, all nine cards (headings, labels and their data), the finale, the
award room, the links. Every editable text has a key and its original words, in groups
(`COPY_GROUPS`); pages read `word(copy, key)`, and a design that needs the facts reads
`useData()` — the same facts built from his words (`dataOf`). His changes live in
`texts.json` (owner panel → Template, `PUT /dev-site/texts`): live as he types, a search box
over all of them, "bring it back" beside each; a word left empty is left out of the page. A
new editable text is one line in `copy.ts`. The name's font, colour and design are there too.
On a wide screen the Template stands at one side with the page in clear view beside it, and
clicking into a word takes the page to where it stands (`whereItSays`).

**The name's area (`Nameplate.tsx`, `plates.ts`, `PlateDesigns.tsx`).** HELLO I'M · the
name · role and company · place and time, in the design chosen in the Template
(`style.plate` in `texts.json`): Classic (the default, as it began) or nine others, loaded
only when chosen — The page's water (the cards' own painted water in crystal-edged letters,
standing on its surface, with drops, ripples and a moving reflection) · Stardust (grains
that gather, scatter at a touch and come home) · Forged (struck letter by letter, white-hot
to gold) · Liquid chrome · Neon sign (a pull chain switches it off) · Drafted (an engineer's
drawing with true measurements) · Signal (tears and locks) · Departure board (split flaps,
the clock turning every second) · Console (typed). The name is always real text: the drawn
ones (`plateArt.ts`) lay ONE 2D canvas over it (`PlateName.tsx`, letters placed where the
browser set them, `plateKit.ts`) — never WebGL; they idle at half rate, stop off screen,
wait while a phone scrolls, and stand still for reduced motion.

**Every letter answers the cursor (`letterSwell.ts`).** The letters under a
hovering pointer are made transparent in place with a CSS Custom Highlight (its
`::highlight` rule is added at run time — the build's CSS minifier drops it) and
drawn swelling in an overlay: the Wave effect on all text, without touching the
text React owns. Skips `.dev-wave`, inputs, SVG, gradient text, `[data-noswell]`.

**The finale (`ChainRing.tsx`).** A ring of 3D links laid ALONG the ring, every
other one turned a quarter round its long axis, so each passes through its
neighbours (an earlier version stood them radially, like spokes). Iridescent
metal tinted in a gradient of the theme round the ring, reflecting a dark env of
coloured panels. Each link is forged from rising light as the section scrolls in;
the ring flashes when it closes (`onAssembled` brings in the slogan), rays open
behind it, a pulse runs round it and a slow wave rolls through the chain. The
camera keeps the phone's distance on every screen and the lens narrows to frame
the ring round the slogan's measured width. Draws only while visible.

`flourish.tsx` holds the shared touches: `Wave` (letters swell under the
cursor) and `CardChrome` (the slot a card's WebGL canvas goes into).

**The album (`Album.tsx`).** Grid → slideshow with Ken Burns motion. Photos come
in three tiers per id `pNN`: `full/` (1800px WebP), `thumb/` (720px) and a 24px
LQIP inline in `album.json`. Tap the portrait to open it.

**The award room (`app/award`, `AwardStage.tsx`, `awardRoom.ts`, `awardHall.ts`,
`awardCoin.ts`, `awardLens.ts`, `awardDoor.ts`, `AwardLink.tsx`, `chestBits.ts`,
`awardFiles.ts`, `Kural.tsx`).** An ancient hall (three.js), entered through a pair of bronze doors with
no loading icon. On a desktop the whole room — scene, pictures, shaders, first frame — is
built in the profile page's idle moments as the way in comes near (`warmAward`) and handed
over; a phone, whose graphics memory the profile needs, gets the files early and builds
behind the doors. The back wall is carved
(24–25 Nov, `ops/art/bake_wall.py`: 4096 wide, handed on as what the light needs — its SLOPES, an
8-bit height has steps a raking light shows — how open and how worn each place is, its height for
how it hides itself, its gold; a phone has the middle of it, at its own sharpness): a temple
wheel, pilasters, elephants, arches, lotus bands, creepers, courses of cut stone; weathered, with
petals on a floor that mirrors it. In it, on two panels (one band on a tall screen), THIRUKKURAL
400 in Tamil, cut by the shader from a distance field (sharp at any size): under the visitor's
light it turns to English and back (`uTell`), and in the smallest letters under it stand the whole
couplet and what it says. A click on it — or on the quote, one clear line over the coin, with no
Tamil behind it — opens its palm leaves (`Kural.tsx`): the couplet, how it is said, its words one
by one, what it means, what it has meant to him; all of it his, in the Template (the Kural keys of
`copy.ts`). THE POINTER IS A TORCH: a point light with its own shadow map
travels with it (a finger on a phone), and a light over the WHOLE screen (`.award-shade`); the dark
brightens where it goes; the lamps catch from it; dust turns in its light.
A photo-scanned chest and cross-pein hammer (Poly Haven, CC0; simplified) seen
three-quarters. The hammer follows the mouse; a tap swings it down in 75 ms onto the spot
tapped, and the blow's sound is SCHEDULED on the audio clock to be heard on that frame (the
output latency taken off; every sound file starts at its own attack). Sparks, dust, a dent
left in the wood, a dead stop, a recoil. The last blow: the lock snaps off and clanks to
rest on its back, the lid bursts open, the gold inside lights up, coins leap out, bounce
(each heard) and settle, light pours out, and the COIN rises: struck, not painted — relief,
inscriptions, a reeded edge, its field dark under a raking light, so its details are read straight
on (`strikeFace`). It is turned by hand (a drag; it settles); a click goes to the link he set in
the Template (`coinLink`). No label under it.
Every picture and bone is asked for again where it does not come or cannot be read (`ask.ts`, past
the browser's own copy): one of eighteen that did not was a WHITE chest on his phone (25 Nov); what
still has none is its own colour, never white. Under the light one brings, the letters in the wall
are ink (gold on lit stone does not read); a coin's rim is a lathe listed from the outside in (the
other way round it is hollow).
Costs, on an Intel UHD 620 (his laptop): VSM shadows were 28 of 42 ms (PCF now), full-screen
MSAA 8 ms (its own small HDR lens with bloom and FXAA 5 ms, desktop only), a runtime PMREM
3 s (baked: `env.webp`), and `compileAsync` must run with the same render target bound or
everything is built twice. The pictures (wall, gold inlay, coin faces, env, doors) are made
offline by the scripts in `ops/art`.
Its music is the owner's chosen track ("Ancient Empire" by The Mountain, 128 kbps) at
`music/award-ancient-empire.mp3` in the bucket (`AWARD_TRACK` in `dev/music.ts`): it fades
in to ~45%, loops, shares the site's mute, starts on the first tap if the browser holds
sound back, and is fetched during the intro. Like the other songs it lives in S3, not in
this repo. Its rank link opens page 35 of the university rank list PDF.

It never ends in an error page (`chunks.ts`, `Medal.tsx`). Every lazily loaded piece comes
through `arrive()`: if its code is missing — a page left open across a deploy — the page
reloads itself ONCE, and if that does not help, a stand-in is shown (for the room: the plain
medal). Graphics taken away, or a browser that died twice building the room (counted in
`sessionStorage`), also end in the medal; after one death the room is built lighter. On the
live site the previous build's hashed files stay on the server for one more deploy
(`keep-last-static.mjs` in the monorepo).

**The ball goes into the skeleton (§107–110).** A card winds up into a glass ball as it leaves its
place (`orbit.ts` rows = the CSS keyframes); once closed and within the skeleton's reach it is handed to
the skeleton (`guests.ts`, `spineGuests.ts`), which draws it among the bones: the bones draw it in, its
skin lets go as it enters, and what was in it becomes a liquid winding round the cord (sheets of one
cloud at their own depths, so the bones stand in it) with a thousand drops on their own turns, soaking
into the bones' veins and nerves. The melt runs in its own time (`MELTS` 2 s); a melt begun is undone
only by a clear scroll back (`UNDO`): a phone's screen grows and shrinks as its address bar slides and
made it melt twice. The next card comes out of the bones the same way.

**The background is flown through (§108.2).** `flight.ts` holds the shared speed; `DustField` draws
deep dust as instanced streaks (head to where it was a shutter's time ago), clouds in the water's own
small picture, a light ahead; it gathers speed with the scroll and glides on; streaks keep to the
view's edges; the words in `ChainField` come out of the distance and pass.

**Guidance (§107.4).** One quiet line at a time (`Guide.tsx`), gone once its thing is done (`did.ts`,
events `dev-did`); every word in the Template; nothing ever points at PS or the photo.

**KAL · கல் (being built, shown by `?design=kal` only).** A temple cut from one rock (docs in the
monorepo: `docs/TEMPLE_DESIGN.md`, `docs/temple/ART.md`, `WORDS.md`). Carvings are baked by
`ops/art/sculpt.py` + `bake_kal.py` into slope/height/material pictures (`public/dev/kal`, map in
`dev/kal/map.json`) and lit live by one raw-WebGL2 canvas that rides with the page (`dev/kal/stone.ts`,
`world.ts`): a torch at the hand, rows of clay lamps, the moon; tiles so each pays only for the light
that reaches it; cut letters (`letters.ts`) drawn by the browser and filled with gold; raw rock that lets
go cell by cell; the water at the foot with lamps afloat and two fish. Halls are plain HTML with
`data-stone` / `data-cut` marks (`Hall.tsx`, `Halls.tsx`).

**Dates are always live.** Every number derived from time (years in the chain,
months, days, the "3 YEARS IN …" countdown, the finale's day count) is computed
in the browser from `CAREER_START` (1 Jan 2024) and ticks. Never hard-code one.

## 5. Hosting (the live site)

- Domain `pandi-dev.dineai.cloud`. The monorepo's Next middleware maps the
  subdomain to `/dev`, so `/` shows the profile; `/award` is the award room.
- One EC2 box (eu-west-2) runs Docker: Caddy (TLS) → Next.js frontend +
  FastAPI backend. Deploys run from the monorepo's GitHub Actions workflow.
- **Files** are served by the backend router `backend/dev_site.py` at
  `/api/dev-site/<name>`, out of the private S3 folder `dev-site/`. Only names
  matching its allow-list are reachable. Manifests that the owner can edit
  (`album.json`, `music.json`, `milestones.json`, `site.json`) are `no-store`;
  photos and files are cached.
- The page can be switched off without a deploy (`ops/toggle_dev_site.sh`).

## 6. Content pipelines

- **Album:** `ops/build_dev_album.py` turns originals into the three tiers,
  bakes in camera rotation and **strips all EXIF (GPS included)**, writes
  `album.json`, syncs to S3. Photos uploaded from the owner panel go through the
  same steps on the server.
- **Résumé:** `resume/build_resume.py` writes the PDF and DOCX;
  `ops/publish_resume.py` renders page previews, writes `resume/resume.json`
  (with a content version) and syncs to S3. The site shows it in an in-place
  viewer with PDF and Word downloads.
- **Milestones** (awards, promotions, notes on the month chain): edited on the
  site itself, stored in `milestones.json`; defaults in `dev/profile.ts`.

## 7. The owner panel (hidden)

- **The door:** three quick taps on the "PS" monogram in the top bar. Then the
  password.
- **What it does** (every file picker is a hidden input opened by a button — the
  bare "Choose File" boxes did not open inside the panel): upload photos to the
  album (≤20 at a time) and remove them;
  upload songs, rename, reorder, choose where each plays (everywhere / site only
  / album only), set the default volume and HOW THE MUSIC BEGINS; set the PORTRAIT — add, remove,
  reorder his photos and the seconds each one shows (`POST`/`PUT
  /dev-site/portrait`); REPLACE THE RÉSUMÉ — a new PDF (≤6
  pages, <10 MB) and optionally its Word file: the server draws the pages with
  PDFium (`pypdfium2`, BSD — not PyMuPDF, which is AGPL) and rewrites
  `resume.json`; without a Word file the Word download is removed rather than
  left offering the old résumé. Double-clicking a month block edits
  milestones. THE PORTRAIT'S DESIGN (a tap previews it on the page; "Make this
  the site's look" saves it); THE TEMPLATE (his words for the site, see above); THE
  SITE tab makes the theme and design on his screen the site's default (the Studio
  no longer can).
- **Security:** the password is checked **only on the server** against a
  bcrypt hash kept in the private bucket (`dev-site/private/editor.hash`, never
  served). After 8 failed tries in 15 minutes an IP is locked out (429).
  **Never put the password or the hash in this repo**, in code, in docs or in
  tests. Removed photos keep their files and their ids are never reused (the
  old image may still be in visitors' caches).

## 8. Music

- `dev/music.ts`: one player for the site. Every song fades in (2.6 s) at its
  start and out (3.2 s) at its end, with a short quiet (1.4 s) before the next
  fades in — a single song too, each time it comes round (the owner's rule: no
  crossfade, no hard cut). Two `<audio>` elements take turns so the next song
  loads during the fade-out; switches he makes (the album, a new playlist) use a
  quick version. The award room's own track loops the same way (never
  `el.loop`).
  Volume and fades go through WebAudio gain nodes because phones ignore an
  audio element's own volume. Opening the album restarts the album playlist
  from its first song; closing it returns to the site playlist. A visitor's mute
  and volume are remembered on their device. The award room plays its own track
  (above) and shares the mute.
- A browser refuses sound before the visitor has touched the page, and nothing is pressed
  on the way in: the music begins with the FIRST touch, click or key anywhere (`arm`), or at
  once where the browser allows it (`wake`). Until then a few quiet words stand beside the
  note for a while (`soundHint` in the Template). The audio graph is made while the page
  loads: `new AudioContext()` stops the main thread for 0.2–1.9 s.
- `music.json`: `{"tracks":[{"id","title","file","scope":"landing|album|both"}],"volume":0.6,"start":"auto|touch|button"}`.
  `start` is how it begins (owner panel → Sound): by itself where the browser allows it (else at
  the first touch), at the first touch anywhere, or only by the music button (the award room
  waits for it too: `musicWaits`). `music.ts` is a client module: the page (a server one) may
  import its types only.
- **The song files live in S3 only, not in this repo** — the owner's choice. The
  live playlist is his licensed ringtone "Zulfein", streamed from the bucket's
  `dev-site/music/`; he downloads it from there when needed. The mirror's
  `music.json` is an empty playlist, so the sound button does not appear here.
  To hear music locally, put a file in `content/music/<id>.mp3` and list it in
  `content/music.json` (both are git-ignored).

## 9. House rules (from the owner — follow them)

1. **The default page is the first impression.** It has to be creative and
   alive in animation and in every detail; plain is a bug.
2. **A new design is a whole new site**, with its own layout, motion and idea —
   never a reskin of an existing one. Phones get full parity.
3. **Never write "just" or "only"** in the site's copy: it reads as boastful
   or dismissive.
4. **Single click shows details, double click edits** (behind the password).
5. **Load everything before the site opens** (by itself: no button) so nothing lags once inside.
6. **Every date-based number is live** and visibly running.
7. Photos and the résumé are his own and already public on his Instagram and
   the live site; this repo was made public with his approval. They are **not**
   licensed for reuse.

## 10. Testing and gotchas

- Check every change at **1440×900 and 390×844** with Playwright and look at the
  screenshots. Launch plain Chromium for the profile (SwiftShader flags make its
  canvases stall screenshots); use `--use-angle=swiftshader
  --enable-unsafe-swiftshader` for `/award` in headless runs.
- **The door:** wait for `[data-boot]` to be gone; there is nothing to click. Playwright's
  `evaluate`/`waitForFunction` count as a user gesture: to test what a visitor really hears,
  use a raw CDP `Runtime.evaluate` with `userGesture: false`.
- **Phone overflow:** a CSS grid with no explicit columns sizes its one track
  to the content's min-content width; a row of fixed cells then pushes the whole
  column past the screen edge. The Chain layout uses
  `grid-cols-[minmax(0,1fr)]` and flex children that hold grids need `min-w-0`.
- **`Wave` text:** letters are inline-block spans; spaces must stay plain text
  between them or the line can never wrap.
- **Next 16.2.7 can drop a space between JSX text and an element** in the
  compiled output even when the source has it. The monorepo guards this with
  `scripts/check-jsx-spaces.mjs`; when someone reports a missing space, check
  the rendered page, not the source.
- Theme colours must come from `--d-*` variables, never hard-coded, or a theme
  switch leaves pieces behind.
- Keyframes are namespaced `dev*` and classes `dev-*` because in the monorepo
  they share one stylesheet with the DineAI product.

## 11. Credits and licences

- 3D models and textures: Poly Haven, **CC0** — Treasure Chest (Rico Cilliers), Cross Pein
  Hammer (Tics), Large Sandstone Blocks 01 and Sandstone Blocks 08 (Rob Tuytel); see `public/dev/models/CREDITS.md`.
- Sound effects: **Mixkit Free License** (see `public/dev/sfx/CREDITS.md`).
- Fonts: Geist and Geist Mono (OFL), Fraunces (OFL), Cinzel (OFL); the hall's verse is set in Noto Serif Tamil (OFL).
- Photos, résumé, rank list and personal text: © Pandian Sambath, all rights
  reserved.
- The site was built with AI-assisted development.
