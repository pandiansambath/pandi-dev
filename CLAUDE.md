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
  award/page.tsx           the award room: 3D chest, hammer, coin, ancient score
  api/dev-site/[...path]/  read-only file server over content/ (stand-in for the backend)
  layout.tsx, fonts/       Geist, Geist Mono, Fraunces (+ Cinzel for /award), all local
  globals.css              head (this repo) + the site's CSS (synced, dev-* namespaced)
dev/                       every component of the site (see §4)
public/dev/                chest.glb (CC0), sfx/*.mp3 (Mixkit), hammer.svg — with CREDITS.md
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
position (a named view timeline, `--dev-card`): it starts tiny and far on the LEFT
(a card still to come, passing behind the portrait column, which sits at `z-[2]`),
swings round behind the crystal divider growing, arrives full size on the RIGHT
facing you (the present), then carries on round, shrinking, back to tiny on the
left. Behind the divider it paints under it (z-index 0), in front over it (3). A
phone orbits the middle (the divider is centred behind the cards there).

**The crystal spine (`ChainSpine.tsx`, `.dev-crystal`).** The divider is a column
of crystal vertebrae (an SVG mask over a theme gradient) with a light running down
it inside its own clip — nothing in it may move a full-height box, or the page
grows past its end (that happened once).

**Inside each card.** `CardChrome` (`flourish.tsx`) adds one water-crystal texture
layer (`.dev-liquid`): `liquid.ts` paints a watercolour-and-crystal-vein picture
once per theme in its colours and hands it to every card as `--dev-liquid`; the
layer only moves with the card's scroll. Plus a light band in the face-on moment
(`.dev-sweep`), the chain-link mark turning (`devLinkTurn`), titles arriving with a
glitch (`devGlitch`). Everything inside a card uses `--dev-card`: a card clips its
edges, which makes it its own scroll box, so a child's own `view()` timeline would
measure against the card and could stick invisible ("empty cards").

**Smoothness rules (measured 0.3 → ~50 fps, 22 Nov).** No backdrop blur anywhere
on the default page; no `filter: blur` on moving layers; no custom-property
animations (they repaint every frame); no permanent animations on every card;
motion inside cards is scroll-linked only. Check with a frame-time measurement,
not by eye — and warm the browser up first (the first run is always slow).

**The dust (`DustField.tsx`).** One quiet WebGL layer of motes behind the page:
they drift towards you always and faster with the scroll (zoom IN only, never
out), and part in widening rings where the pointer moves (a tap on a phone) — the
"stone in water" cursor. Half-rate when idle, asleep when hidden.

**The finale (`ChainRing.tsx`).** A 3D ring of interlocked iridescent chrome links
(three.js, RoomEnvironment) with drifting motes; the links gather with the scroll,
the ring flashes when it closes (`onAssembled` brings in the slogan) and turns;
pointer lean, drag to spin; draws only while visible.

`flourish.tsx` holds the shared touches: `Wave` (letters swell under the
cursor) and `CardChrome` (turning gradient edge + chain-link mark).

**The album (`Album.tsx`).** Grid → slideshow with Ken Burns motion. Photos come
in three tiers per id `pNN`: `full/` (1800px WebP), `thumb/` (720px) and a 24px
LQIP inline in `album.json`. Tap the portrait to open it.

**The award room (`app/award`, `AwardStage.tsx`, `chestBits.ts`).**
three.js scene with the CC0 chest: strike it with the hammer, it cracks, shakes
and bursts open; a "1 GRAM" gold coin rises in golden rays. The canvas stays
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
- **What it does:** upload photos to the album (≤20 at a time) and remove them;
  upload songs, rename, reorder, choose where each plays (everywhere / site only
  / album only), set the default volume. Double-clicking a month block edits
  milestones; the Studio can save the default theme and design.
- **Security:** the password is checked **only on the server** against a
  bcrypt hash kept in the private bucket (`dev-site/private/editor.hash`, never
  served). After 8 failed tries in 15 minutes an IP is locked out (429).
  **Never put the password or the hash in this repo**, in code, in docs or in
  tests. Removed photos keep their files and their ids are never reused (the
  old image may still be in visitors' caches).

## 8. Music

- `dev/music.ts`: one player for the site. Two `<audio>` elements take turns so
  songs crossfade (2.4 s); a single song crossfades into itself at the loop.
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

- 3D chest: "pirate treasure chest" by dook, Poly Pizza, **CC0**.
- Sound effects: **Mixkit Free License** (see `public/dev/sfx/CREDITS.md`).
- Fonts: Geist and Geist Mono (OFL), Fraunces (OFL), Cinzel (OFL).
- Photos, résumé, rank list and personal text: © Pandian Sambath, all rights
  reserved.
- The site was built with AI-assisted development.
