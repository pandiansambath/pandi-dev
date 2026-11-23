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
intro and ENTER, the theme, the album, the résumé viewer, milestones, toasts,
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

**The intro (`BootSequence.tsx`).** Nothing is shown until everything is loaded:
the portraits, the first song, three.js, the chest model, the award room's code
and the sound effects are all fetched while the counter runs (`bootTasks` in
`DevProfile.tsx`). ENTER is the first tap, which is also what lets the browser
start the music.

**Chain Reaction pieces.** `SkillOrbit.tsx` (3D rings of skills, drag to spin),
`ChainField.tsx` (background strands, turn with scroll), `ChainSpine.tsx`
(the line that lights as you scroll), `MonthChain.tsx` (one block per month
since 1 Jan 2024; single click = details, double click = edit), `Terminal.tsx`
(the Shell card: type or tap commands), `SkillClusters.tsx`, `Highlights.tsx`,
`Resume.tsx`, `Finale.tsx` + `ChainRing.tsx` (the 3D chain that assembles,
closes with a flash and turns; tilt follows the pointer, drag spins it).
**The orbit (globals.css `devRevolve` / `devRevolvePhone`).** Every right-hand
card (`[data-link]`) lives one orbit round the divider, driven by its own scroll
position (a named view timeline, `--dev-card`): far and small on the LEFT (a card
still to come, passing behind the portrait column, which sits at `z-[2]`), round
behind the crystal divider, full size on the RIGHT facing you (the present), then
on round and away. A phone orbits the middle (the divider is centred behind the
cards there). Transforms only — no z-index in the keyframes (that drags the whole
orbit onto the main thread); the divider and the portrait column sit above the
cards for good. CSS also fades a card's words in only in the present
(`devChainReveal`).

**Surfaces (`CardGL.ts`, `registerSurface`).** The popups and the sound menu
wear the same glass and water as the cards (a surface is always open and flat; no
orb). Their buttons are glass (`.dev-glassbtn`) over the water.

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
contexts on purpose: take the guard off first.

**What a card LOOKS like is drawn in WebGL (`CardGL.ts`).** `CardChrome`
(`flourish.tsx`) only puts a slot in the card; a small pool of WebGL canvases (6 on
a desktop, 4 on a phone) moves from card to card, near the screen only. For its
card's place in the orbit (the same progress as the CSS timeline) a canvas draws:
the card — dark glass with the theme's painted water (`liquid.ts`) drifting in two
sheets, an iridescent rim in the card's own colour — flat in the centre and curved
like a piece of the cylinder it travels round as it turns away; the ORB it is when
away — a wobbling sphere of the same water wound into a spiral, an atmosphere, a
ragged halo, a disc of bubbles; and the change between them — the card opens out
of its heart along a ragged glowing front. The cursor stirs the water (rings,
colour split, a soft light) and draws each card's few motes of dust. A card with
no canvas wears plain glass, shown only in the present. Do NOT go back to CSS
layers for this: a dozen layers a card measured 318 layers / 76 MP of layer pixels
— past the GPU budget, so tiles were thrown away mid-scroll (flicker). Now ~235 /
27 MP. Measure with the CDP LayerTree domain.

**The crystal spine (`CrystalSpine.tsx`, inside `ChainSpine.tsx`).** A 3D column
of vertebrae (lumpy bones, wings, spurs, discs, thorns, crystal shards) in dark
glass with an oil-slick film, reflecting a dark environment lit by panels in the
theme's colours (a white room turned it to porcelain). A sticky canvas in the
divider's lane; the bones are laid out in the column's coordinates and grow out
of nothing at its ends. Round it: a dense, slow sleeve of bokeh and bubbles and
fast sparks that surge upward when you scroll. The line and the dot that runs down
and stops at each card are DOM (ChainSpine).

**Smoothness rules (measured 0.3 → ~50 fps, 22 Nov).** No backdrop blur anywhere
on the default page; no `filter: blur` on moving layers; no custom-property
animations (they repaint every frame); no permanent animations on every card;
motion inside cards is scroll-linked only. Check with a frame-time measurement,
not by eye — and warm the browser up first (the first run is always slow).

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
before settling — opening like an iris when the spine first comes into view; the
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

**The Template (`copy.ts`).** Every editable text has a key and its original words; the
page reads `word(copy, key)` from DevContext; his changes live in `texts.json` (owner panel
→ Template, `PUT /dev-site/texts`): his name with its font (serif, sans, mono) and colour
(the sheen, the theme's gradient, gold, plain, two colours of his), the greeting, role,
company, place, the menu's line, the finale's words, a title. Live as he types; one click
puts every word back. A new editable text is one line in `copy.ts`.

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

**The award room (`app/award`, `AwardStage.tsx`, `chestBits.ts`, `awardFiles.ts`).**
A real room (three.js): a photo-scanned chest and cross-pein hammer on a sandstone floor
(Poly Haven, CC0; the chest's vertices quantized with KHR_mesh_quantization), studio
environment light, VSM soft shadows, seen three-quarters. The hammer is held from your side,
raised, and follows the mouse; a tap swings it down in 75 ms onto the spot tapped, and the
blow's sound is SCHEDULED on the audio clock to be heard on that frame (the output latency
taken off; every sound file starts at its own attack). Sparks, dust, a dent left in the
wood, a dead stop, a recoil. The last blow: the lock snaps off and clanks to rest on its
back, the lid bursts open, the gold inside lights up, coins leap out, bounce (each heard)
and settle, light pours out, and the "1 GRAM" coin rises. Everything is drawn once unseen
before the room appears, so the first blow has nothing to compile. The canvas stays
hidden until its first full frame (no half-loaded flashes), the hammer lands on
the sound, DPR is capped at 1.5. Its music is the owner's chosen track ("Ancient
Empire" by The Mountain, 128 kbps) at `music/award-ancient-empire.mp3` in the
bucket (`AWARD_TRACK` in `dev/music.ts`): it fades in to ~45%, loops, shares the
site's mute, starts on the first tap if the browser holds sound back, and is
fetched during the intro. Like the other songs it lives in S3, not in this repo.
Its rank link opens page 35 of the university rank list PDF.

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
  / album only), set the default volume; set the PORTRAIT — add, remove,
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
- `music.json`: `{"tracks":[{"id","title","file","scope":"landing|album|both"}],"volume":0.6}`.
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
5. **Load everything before ENTER** so nothing lags once inside.
6. **Every date-based number is live** and visibly running.
7. Photos and the résumé are his own and already public on his Instagram and
   the live site; this repo was made public with his approval. They are **not**
   licensed for reuse.

## 10. Testing and gotchas

- Check every change at **1440×900 and 390×844** with Playwright and look at the
  screenshots. Launch plain Chromium for the profile (SwiftShader flags make its
  canvases stall screenshots); use `--use-angle=swiftshader
  --enable-unsafe-swiftshader` for `/award` in headless runs.
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
  Hammer (Tics), Large Sandstone Blocks 01 (Rob Tuytel); see `public/dev/models/CREDITS.md`.
- Sound effects: **Mixkit Free License** (see `public/dev/sfx/CREDITS.md`).
- Fonts: Geist and Geist Mono (OFL), Fraunces (OFL), Cinzel (OFL).
- Photos, résumé, rank list and personal text: © Pandian Sambath, all rights
  reserved.
- The site was built with AI-assisted development.
