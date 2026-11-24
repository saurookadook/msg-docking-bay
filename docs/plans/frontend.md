# Plan: Frontend — the Docking Bay (wiki mode + hangar mode)

> **Agreed** 2026-11-22: one app with two modes, procedural mechs plus holograms in hangar mode, and
> the backend PRs included. No code until asked.

## Context

The backend now serves the catalog, including the parts on each spec sheet (PR B, PR C and
PR D, #32), but the frontend is still a placeholder (`pages/Home`, `pages/HealthCheck`).
`catalog-read-api.md` says "Frontend pages are a separate plan" — this is it.

Goal: one React app where a user searches and browses mobile suits, characters, organizations, works
and mechanical designers, and feels like they're walking an MS deck. Two **modes over the same routes
and data** (agreed):

1. **Wiki mode** — a fast, accessible, wiki-style site, dressed as hangar signage and terminals. It
   is also the fallback when WebGL is unavailable or the user prefers reduced motion.
2. **Hangar mode** — a three.js scene of the same entity: maintenance cages, catwalks, cranes,
   holograms. In the cages stand **original, procedurally generated mech frames** plus a holographic
   panel with the suit's data (agreed; no Gundam 3D assets exist that we may use).

The plan includes the small backend PRs the frontend needs (agreed).

### Facts checked in the repo

- Paginated list routes: `limit`/`offset`, envelope `{data, meta:{limit,offset,total}}`; details
  `{data}`; old slugs resolve and return the current `slug` (frontend must `replace` the URL when
  they differ — D2). `/api/continuities` is the one exception: it returns `{data}` only, with no
  `limit`/`offset` or `meta`. `q` exists on mobile suits, characters, organizations, designers
  (slug/model-number match, prefix first); **not** on works; **no cross-entity search**. Filters:
  suits `continuity`, `work`, `unit_type`; works `continuity`, `work_type`; characters/orgs `work`;
  org suits `role`.
- **No image fields anywhere** in models or contract. Image rights research
  (`docs/research/image-rights.md`) requires self-hosted copies, credit, link-back and an
  "unofficial" disclaimer — so images are a separate ingest/storage plan; this plan only reserves slots.
- PR D (#32) regenerated `openapi.json`, so the contract already has the parts (armaments,
  equipment, materials, powerplants).
- Existing frontend pieces to reuse: `safeFetch` (`src/utils/safeFetch.ts`), the store pattern
  (`src/store/health/*`, `useAppStore()` in `store/hooks.ts`), `routerConfig` (`src/app/router.tsx`),
  `Root` layout, type aliases in `src/api/index.ts`, Mirage mock mode (`__mocks__/endpoints.ts`,
  `paginate()`, `MOCK_API=true`), `renderWithProviders`, `DEFAULT_PAGE_SIZE`/`MAX_PAGE_SIZE`.
- Standards that bind this: REACT-1/2 (page folders, page-local `components/`), REACT-12–17 (one store
  slice per domain, action creators own fetches), REACT-22 (render loops/listeners clean up),
  REACT-24–27 (routes in `routerConfig`, kebab paths, `AppParams`), REACT-30 (localStorage keys in
  constants), CSS-1/2/4/10–13/17/18 (scoped `styles.css`, tokens only, light+dark via tokens, named
  breakpoints, motion behind `prefers-reduced-motion`), TEST-10/17/18.

**Gundam Wiki reference.** Fandom returned HTTP 402 to automated fetches, so page templates below come
from the repo's ingestion spike (`Infobox/Mobile Weapon` parameters, `docs/research/notes/ingestion-spike.md`)
and the wiki's standard page layouts. Verify against a live page in a browser before each page PR.

## Look and feel: the MS deck

A carrier's mobile suit deck, as in the classic shows: a long, dim bay; mechs standing in numbered
**maintenance cages** with fold-out **gantries and catwalks**; **yellow-black hazard stripes** on
edges; **amber sodium lamps** and rotating **warning beacons**; **overhead cranes** on rails;
stenciled signage (`MS DECK 02 · CAGE 07`); intercom chatter; a **catapult** at the far end opening
to space. Everything else is a deck terminal: monospace readouts, scanlines, green/amber phosphor.

Design system (PR F1):

- **Tokens** (CSS-10/13): steel/gunmetal surfaces, hazard yellow, alert red, terminal green/amber,
  hologram cyan. Light scheme = **"Day shift"** (floodlights on, painted steel); dark = **"Night
  shift"** (sodium lamps, glow). A third flourish, **"Condition Red"**, tints accents red during the
  launch sequence.
- **Type:** Oxanium for stencils + JetBrains Mono for readouts, vendored as latin and latin-ext
  `.woff2` files in `src/assets/fonts/` with their OFL licences (F1,
  [`design-system.md`](design-system.md) Q3).
- **Shared components** (`src/components/`): `DeckPanel` (riveted panel with corner brackets),
  `StencilHeading`, `HazardStripe`, `SpecPlate` (label/value plate), `Readout` (terminal text with
  optional type-on), `StatusLamp`, `CageNumber`, `Pagination`, `FilterBar` (F2), `EntityLink`
  (typed by entity; icon per kind), `SourceCitations` (CC BY-SA attribution per `SourceCitation`),
  `VisualSlot` (image placeholder: blueprint silhouette + "NO VISUAL ON FILE").
- **Shell** (`layouts/Root`): top **deck status bar** (bay name, shift toggle Auto/Day/Night,
  status lamp; F5 adds the search key hint and F7 the mode toggle Wiki ⇄ Hangar), nav as hanging
  bay signs (Mobile Suits · Personnel · Organizations · Works · Designers; a sign is "offline"
  until its route exists), footer with the unofficial-fan-project disclaimer, source credits and
  a "Deck systems" health-check link. Unknown paths render a "Cage empty" 404 page.
- **Motion** (behind `prefers-reduced-motion: no-preference`): lights clunk on row by row at load,
  hazard stripes crawl on hover, beacon spin on loading states, readouts type on.

## Routes (REACT-24/25)

| Path | Page | Wiki-mode framing |
| --- | --- | --- |
| `/` | `Hangar` (home) | Deck overview: search terminal, decks by continuity, featured cage, "Sortie a random unit" |
| `/mobile-suits` | `MobileSuitList` | Cage roster; filters continuity / work / unit type; `q` |
| `/mobile-suits/:mobileSuitSlug` | `MobileSuitDetails` | Maintenance dossier |
| `/characters`, `/characters/:characterSlug` | `CharacterList/Details` | Personnel files ("Personnel" in nav) |
| `/organizations`, `/organizations/:organizationSlug` | `OrganizationList/Details` | Faction registry |
| `/works`, `/works/:workSlug` | `WorkList/Details` | Operation logs |
| `/mechanical-designers`, `/mechanical-designers/:mechanicalDesignerSlug` | `DesignerList/Details` | Engineering credits |
| `/search` | `Search` | Full results for `?q=` grouped by kind |
| `/compare` | `Compare` | Cage A vs Cage B (`?a=&b=` suit slugs) |

Filters and pagination live in URL search params (shareable, back-button safe). **Mode** is a
preference (`localStorage`, key in `constants`) overridable by `?view=hangar|wiki`; every route renders
in either mode.

## Page templates (from Gundam Wiki layouts, mapped to today's data)

Each lists the wiki's sections; ✅ = data available now, ⏳ = shown as an empty-state slot
("DATA PENDING") and tracked as a backend/ingest follow-up.

- **Mobile suit** (wiki infobox `Infobox/Mobile Weapon`). Header: model number stencil + name, `name_ja`,
  unit type, continuity ✅. Infobox: designers ✅, manufacturer/operator/developer orgs ✅, pilots ✅,
  first appearance (debut) ✅, height/weight ✅, powerplant ✅, armor/frame materials ✅, image ⏳,
  `kanji`/`other names`/`archetype`/`production` ⏳. Sections: **Specifications** (spec sheets as
  configuration tabs; inherited fields marked "per base spec") ✅; **Armaments** grouped fixed /
  handheld / optional ✅; **Special Equipment & Features** ✅; **Variants & lineage**
  (`relations` as a small dev-tree: developed from / upgrade of / variants) ✅; **Appearances** ✅;
  **History**, **Gallery**, **Trivia** ⏳. Fun: **height lineup** silhouette vs a human and an 18 m
  reference frame.
  *Amended 2026-11-23 (F3,* [`mobile-suit-dossier.md`](mobile-suit-dossier.md)*):* the infobox is a
  sticky column with the image on top (a slim sticky strip on phones) and follows the spec tab
  picked in `?spec=`; the ⏳ infobox rows move to a "Registry" plate under the header.
- **Character** (wiki `Infobox/Character`). Name, `name_ja` ✅; appearances ✅; **mobile weapons
  piloted** ✅ (as a "qualified units" rack). ⏳ affiliation, rank, gender, age, voice actors,
  personality, skills, history, relationships, quotes. Framing: a pilot ID card.
- **Organization.** Name, parent ✅, child units ✅ (as an org chart), appearances ✅, mobile weapons by
  role (manufactured / operated / developed) ✅. ⏳ type, headquarters, leaders, founded/dissolved,
  insignia, history. Framing: faction registry with a generated insignia badge.
- **Work.** Title, `title_ja`, type, dates, continuity ✅; parent work and relations (sequel,
  compilation, adaptation, remake, side story) ✅; **mobile weapons appearing** (with debut flag,
  episode range) ✅. ⏳ staff, studio, episodes, characters list, plot. Framing: operation log.
- **Mechanical designer.** Name, `name_ja` ✅; designed mobile weapons ✅. Framing: engineering credits.
- **Every detail page:** `SourceCitations` lists each `SourceCitation`, labelled by `kind` (Gundam
  Wiki, Wikidata, Wikipedia EN/JA), linking its `url` and its `revision_url` when present, with the
  content license. A Gundam Wiki link appears only for `fandom_page` citations.
  *Amended 2026-11-23 (F3 Q11):* the list is numbered and de-duplicated (by kind, URL and
  revision), and each sourced item on the page links to its entry with a footnote mark.

## Hangar mode (three.js)

- **Stack:** `three` + `@react-three/fiber` + `@react-three/drei` (React-native scene graph, cleanup
  handled by unmount — fits REACT-22). Loaded only via `React.lazy` so wiki mode ships no 3D code.
- **Entry gate:** WebGL2 check + `prefers-reduced-motion` → falls back to wiki mode with a toast
  ("Hangar lights offline").
- **Scene kit** (`src/hangar/`): deck floor/walls with hazard decals, instanced cages and catwalks,
  overhead crane on a rail, sodium point lights + baked-feel ambient, volumetric-ish beams via cheap
  cone sprites, rotating beacons, floating dust. Postprocessing bloom for holograms (optional, behind
  a quality setting).
- **Procedural mech** (`src/hangar/mech/`): an original frame assembled from primitives (head, torso,
  backpack, arms, legs). Parameters come from data: `unit_type` picks the body plan (suit humanoid,
  armor bulky, fighter jet-form, pod ball, worker utility), `overall_height_m` sets scale, slug seeds
  proportions/antenna/visor, operator organization picks a paint palette (small lookup for major
  factions, hashed palette otherwise). Idle "maintenance" motion: visor flicker, cage arms retract.
- **Hologram panel** beside the cage: the `VisualSlot` image (later), model number, top stats, pilot
  cards — rendered as an HTML overlay (drei `Html`) so text stays crisp and selectable.
- **Navigation:**
  - Home deck = rows of cages for the current page of suits; continuity = which deck/bay.
  - Search terminal on a console; picking a result **flies the camera along the crane rail** to that
  cage (or loads the cage on demand).
  - Suit detail = close-up orbit of that cage; Personnel/Organizations/Works pages = in-world terminal
  screens on the catwalk showing the same wiki content.
  - **Launch sequence** ("Sortie"): mech walks to the catapult, Condition Red lights, catapult fires,
  then navigates to a random suit. `[Pilot name], launching!` uses the suit's first pilot from data.
- **Performance:** instancing, one draw-call-light material set, `frameloop="demand"` when idle, DPR
  cap, dispose on unmount; budget ~60 fps on an integrated GPU with 24 cages.

## Data layer

- Store slices (REACT-12): `mobile-suits`, `characters`, `organizations`, `works`, `designers`,
  `search`. Each holds `list {items, meta, query, requestInProgress, error}` and `detailsBySlug`.
  Action creators wrap `safeFetch` with generated types (`paths[...]`); detail actions `replace`
  the URL when the returned slug differs from the requested one.
- `continuities` is unpaginated and has no detail route, so its slice holds only
  `{items, requestInProgress, error}`, fetched once and reused by filters and decks.
- Mirage: extend `endpoints.ts` handlers to apply `q` and filters, and add enough fixtures
  (several continuities, a suit with full parts and relations) to make both modes demo-able with
  `MOCK_API=true`. BE-1 adds `/api/search` and the TypeScript `normalizeSearch` and
  `searchList` (`src/__mocks__/search.ts`), which F2's list handlers reuse to apply `q`
  (`catalog-search.md` Q9). Fixtures stay a mirror of `backend/scripts/seed_dev.py`; tests
  that need more rows use Mirage `overrides` (`catalog-browser.md` Q5).

## PRs (in order)

Backend:

- [x] **BE-1** `feat(backend): search across the catalog` — `GET /api/search?q=&limit=` returning
  `{data:{mobile_suits, characters, organizations, mechanical_designers, works}, meta:{limit,
  totals}}` (top N each, `limit` 1–20, default 5; a blank `q` lists the first N), reusing each
  facade's `q` matching; add `q` to `/api/works`; every `q` also matches the English `name` /
  `title`. Japanese names are deferred to
  [#34](https://github.com/saurookadook/msg-docking-bay/issues/34). Regenerate contract.
  Plan: [`catalog-search.md`](catalog-search.md).
- (Images — ingest, storage, CDN, credit fields — are a **separate plan**, tracked as a follow-up.)

Frontend:

- [x] **F0** `build(frontend): regenerate the API contract for suit parts` — done in PR D (#32).
- [x] **F1** `feat(frontend): add the docking bay design system and shell` — tokens, fonts, shared
  components, Root layout, shift toggle, breakpoints, `AppParams`, Storybook stories for each component.
  Plan: [`design-system.md`](design-system.md).
- [x] **F2** `feat(frontend): browse the catalog` — store slices, list pages with filters/pagination
  in URL params, `FilterBar` (live, debounced `q`), rosters as `@tanstack/react-table` tables
  (no sorting), Mirage filters; `?work=` is honoured and shown as a chip; commission the list
  routes' nav signs. Plan: [`catalog-browser.md`](catalog-browser.md).
- [ ] **F2b** `feat(frontend): pick a work in the filter bar` — an accessible combobox over
  `/api/works?q=` in `FilterBar`'s work slot, replacing the URL-only chip (after F2).
- [ ] **F3** `feat(frontend): add the mobile suit dossier` — detail page, spec tabs, parts, lineage,
  height lineup. Plan: [`mobile-suit-dossier.md`](mobile-suit-dossier.md).
- [ ] **F4** `feat(frontend): add personnel, faction, operation and designer pages`.
- [ ] **F5** `feat(frontend): add the deck search terminal` — `Ctrl/⌘+K` overlay + `/search` page
  and the status bar's key hint (needs BE-1).
- [ ] **F6** `feat(frontend): add compare and random sortie`.
- [ ] **F7** `feat(frontend): add hangar mode scene` — lazy R3F chunk, WebGL gate, mode toggle
  (`mode` in the `preferences` store slice F1 adds),
  deck/cage/crane/lighting, placeholder mech boxes.
- [ ] **F8** `feat(frontend): generate mechs for hangar cages` — procedural mech + hologram panels;
  suit detail in 3D.
- [ ] **F9** `feat(frontend): navigate the hangar` — crane fly-to from search, decks per continuity,
  in-world terminals for other pages, launch sequence.

F1–F6 deliver a complete wiki mode; F7–F9 layer hangar mode on top without changing routes or store.

## Verification

- Per PR: `moon run :format :lint :typecheck` and `moon run frontend:test` (role-based tests with
  `renderWithProviders` + Mirage, TEST-17/18); backend `moon run backend:test` for BE-1.
- Run the app with `MOCK_API=true` (and against the seeded backend via `moon run root:dev`) and walk
  each route in a browser in both shifts and both modes; check old-slug URL replacement, filter
  params surviving reload/back, keyboard-only navigation, reduced-motion fallback, and WebGL-disabled
  fallback to wiki mode.
- Hangar mode: check frame rate with the browser performance panel on the home deck (24 cages) and
  that leaving the route disposes the renderer (no growth in GPU memory across navigations).
- Storybook for every shared component and page state (loading, empty "DATA PENDING", error).

## Follow-ups (not in this plan)

- Images plan (self-hosted copies, credits, takedown process) — fills `VisualSlot`.
- Japanese search on `name_ja` / `title_ja` ([#34](https://github.com/saurookadook/msg-docking-bay/issues/34)),
  and works matching their series tags (`work_short_names`) once 3a ingests them.
- Ingest fields for the ⏳ sections (character bio fields, org HQ/leaders, work staff, suit
  history/trivia), each needing schema + routes.
- Server-side sorting for the rosters: a `sort` param on the list routes, then sortable
  headers in `RosterTable` (`catalog-browser.md` Q10).
- Optional: ambient deck audio (intercom, crane hum) behind an explicit "sound on" toggle.
