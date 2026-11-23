# Plan: F1 — the docking bay design system and shell

Branch `feat/add-docking-bay-design-system` (created from `main` at `3ef22cc`). PR title:
`feat(frontend): add the docking bay design system and shell`. It expands the F1 entry and the
"Look and feel: the MS deck" section of [`docs/plans/frontend.md`](frontend.md). Q1 to Q10 were
settled by grilling on 2026-11-23.

## Context

The frontend is a placeholder: GitHub-like tokens in `src/index.css`, a plain top bar in
`layouts/Root`, and two pages (`Home`, `HealthCheck`). F2–F6 build the wiki-mode pages, and each
one needs the same deck look, the same shared pieces (panels, plates, links, citations,
pagination), and a shell to render in. F1 builds those once, so the page PRs are data work only.

**Facts checked in the repo:**

- **Tokens** live on `:root` in `src/index.css` (`--color-surface`, `-surface-raised`, `-text`,
  `-text-muted`, `-border`, `-accent`, `-success`, `-danger`, `--font-family-base`,
  `--space-1..4`, `--radius-1`), redefined under `prefers-color-scheme: dark`. Consumers:
  `app/App.css`, `pages/Home/styles.css`, `pages/HealthCheck/styles.css`.
- **No `src/components/` folder yet**, no `AppParams` type (`src/types/index.ts` holds only
  `Nullable`), and no `localStorage` keys in `src/constants/index.ts`. `safeParseJSON` exists
  (`src/utils/safeParseJSON.ts`).
- **Store:** one slice (`store/health/`: `actions.ts`, `reducer.ts`, `reducer.types.ts`), field
  reducers via `combineReducers`, `initialAppState` is a module constant, and
  `AppStoreProvider` takes an optional `initialState`. Action types are in
  `store/actionTypes.ts`; `AppAction` is a union in `store/types.ts`.
- **Shell:** `layouts/Root/index.tsx` renders `#app-shell > header.top-nav-bar` (h1 + nav with
  Home, Health check) and `<main><Outlet/></main>`. `App.css` styles it. `routerConfig`
  (`app/router.tsx`) has `/` and `/health-check` only, and no catch-all route.
- **`index.html`** is minimal (no inline scripts). No CSP header in `index.html`,
  `frontend/Caddyfile` or `nginx-reverse-proxy/`.
- **Tests:** `renderWithProviders` / `WithMemoryRouter` render the real `routerConfig`
  (TEST-17). `Home/index.test.tsx` and `app/startApp.test.tsx` find the heading "Welcome aboard".
- **Storybook 10** (`.storybook/preview.tsx`) wraps every story in `AppStoreProvider` + a memory
  router + a Mirage server, and imports `@/index.css` and `@/app/App.css`. Stories are found by
  `src/**/*.stories.tsx`. There is no Storybook test runner; `pnpm build-storybook` builds them.
- **Citations:** `SourceCitationEntity` (`@/api`) has `kind` (`fandom_page`, `wikidata_item`,
  `wikipedia_en_page`, `wikipedia_ja_page`), `url`, `revision_url | null`, `license_name`,
  `license_url`, `content_license`, `retrieved_at`, `revision_id`. `PageMeta` is
  `{limit, offset, total}`.
- **Fonts:** `@fontsource-variable/oxanium` and `@fontsource-variable/jetbrains-mono` (5.3.0)
  ship latin and latin-ext variable `.woff2` files plus the OFL licence in their npm tarballs.
- **Tooling:** oxlint has no a11y plugin; `react/only-export-components` warns in `.tsx`
  (warnings count as failures). moon is not on PATH; run scripts with `pnpm` in `frontend/`
  (or export the proto PATH).
- **Standards that bind this:** REACT-1/2/3/4/6/9, REACT-12–18, REACT-22, REACT-24–27,
  REACT-30; CSS-1–18; TEST-1, TEST-5, TEST-8, TEST-14–17, TEST-23.

## Decisions (grilled 2026-11-23)

- **Q1. Shift has three states: Auto, Day, Night.** Auto follows `prefers-color-scheme`;
  Day forces light, Night forces dark. Stored as `'auto' | 'day' | 'night'`.
- **Q2. Shift lives in a `preferences` store slice** (`store/preferences/`), REACT-12 shape:
  `setShift({ dispatch, shift })` dispatches `SET_SHIFT` and writes `SHIFT_LS_KEY`. F7 adds
  `mode` and F9 adds `condition` to the same slice. Components read it via `useAppStore()`.
  - *Default:* the initial `shift` comes from `readStoredShift()` (`store/preferences/storage.ts`,
    `safeParseJSON`, validated, `'auto'` on junk or a throwing `localStorage`), read by
    `AppStoreProvider`'s `useReducer` initializer when no `initialState` is passed. Tests pass
    `initialState` or clear `localStorage` in `beforeEach` (TEST-8).
  - *Default:* `Root` keeps `<html data-shift>` in sync in an effect; `auto` removes the
    attribute.
- **Q3. Fonts: Oxanium (display) + JetBrains Mono (readouts), vendored** into
  `src/assets/fonts/`, latin + latin-ext subsets only (**Q8**), with `unicode-range`
  `@font-face` rules in `index.css` and both `OFL.txt` licences beside them. Files are copied
  from the `@fontsource-variable/*` 5.3.0 npm tarballs (`npm pack`); no package dependency is
  added and no request goes to Google at build or run time. Japanese text falls back to the
  system font.
- **Q4. Nav shows all five bay signs.** A sign whose route doesn't exist yet renders as
  **offline**: not a link, `aria-disabled="true"`, an "OFFLINE" tag. The nav is a typed
  config array in `layouts/Root` (`{ label, to, commissioned }`); F2–F4 each flip their sign
  to `commissioned: true`. **Plus a 404 page**: a `path: '*'` child route rendering
  `pages/NotFound` ("Cage empty — no unit assigned", link back to the deck).
- **Q5. No mode toggle and no search hint in F1.** The status bar holds the bay name, the shift
  toggle and a `StatusLamp`. F5 adds the `Ctrl/⌘+K` hint; F7 adds the Wiki ⇄ Hangar toggle.
- **Q6. `FilterBar` moves to F2**, built against the real filters.
- **Q7. `Home` is restyled** as a small deck welcome (`StencilHeading`, a `DeckPanel` with a
  `Readout` "MS DECK 01 · STANDING BY", links to the bays), keeping the `h2` "Welcome aboard".
  **Health check leaves the nav** for a footer "Deck systems" link.
- **Q9. The shift toggle is a segmented radio group**: `<fieldset>` with legend "Shift" and
  three radios (Auto, Day, Night) styled as a breaker switch.
- **Q10. The stored shift is applied before first paint by an inline script in `index.html`**
  that reads `SHIFT_LS_KEY`, validates it, and sets `<html data-shift>`. *Default:* a test reads
  `index.html` and asserts the script uses the same key as `SHIFT_LS_KEY` and the same allowed
  values, so the copy outside TypeScript can't drift.

Carried over from the first draft (not contested):

- **D1. Token set.** Replace the GitHub palette with deck tokens named by purpose (CSS-10):
  `--color-surface`, `-surface-raised`, `-surface-sunken`, `-text`, `-text-muted`, `-border`,
  `-border-strong`, `-accent` (hazard yellow), `-accent-contrast`, `-danger` (alert red),
  `-success`, `-readout` (terminal green), `-readout-alt` (amber), `-hologram` (cyan),
  `-glow` (translucent); `--font-family-display`, `--font-family-mono`, `--font-family-base`;
  `--space-1..5`; `--radius-1`. Existing consumers move to the new names in the same commit.
- **D2. Scheme precedence:** `[data-shift="day"]` > `[data-shift="night"]` > OS preference.
  One token block per scheme, shared by selector lists (`:root[data-shift="night"]` and the
  `prefers-color-scheme: dark` block for `:root:not([data-shift])`), so values aren't duplicated.
- **D3. Condition Red** is `data-condition="red"` on `<html>`, re-pointing `--color-accent*` to
  red. F1 ships the tokens and a story; nothing sets it until F9.
- **D4. Named breakpoints** documented in an `index.css` banner: `phone` = `max-width: 40rem`,
  `tablet` = `max-width: 64rem` (CSS-17).
- **D5. Motion** behind `prefers-reduced-motion: no-preference`, `@keyframes` in the file that
  uses them (CSS-18): lights-on row stagger in the shell, hazard crawl on `HazardStripe` hover,
  beacon spin on `StatusLamp` `busy`, type-on on `Readout` (CSS `steps()` clip; full text always
  in the DOM).
- **D6. `AppParams`** in `src/types/index.ts` with every planned param (`mobileSuitSlug`,
  `characterSlug`, `organizationSlug`, `workSlug`, `mechanicalDesignerSlug`), and an
  `entityPath(kind, slug?)` helper in `src/utils/entityPath.ts` that `EntityLink` and the nav
  use.
- **D7. `EntityLink` icons** are small inline SVGs, `aria-hidden`, one per kind.
- **D8. `SourceCitations`** renders `<section aria-labelledby>` "Sources": per citation, a kind
  label (Gundam Wiki, Wikidata, Wikipedia (EN), Wikipedia (JA)), a link to `url`, a "revision"
  link when `revision_url` is set, and the licence linked to `license_url`. An empty list
  renders nothing.
- **D9. `Pagination`** takes `meta: PageMeta`, builds `?offset=` links from the current search
  params (keeping the others), shows previous/next and "N–M of T", inside
  `<nav aria-label="Pagination">`. Nothing renders when `total <= limit`.
- **D10. Every component** gets `index.tsx`, a class-scoped `styles.css` (CSS-4), an
  `index.stories.tsx`, and an `index.test.tsx` for behaviour beyond markup;
  `src/components/index.ts` barrel (REACT-2).

## Steps (one commit each)

1. `docs(docs): plan the docking bay design system` — save this plan to
   `docs/plans/design-system.md`; amend `frontend.md`: F1 entry (no `FilterBar`, no mode
   toggle/search hint), F2 gains `FilterBar` and flipping its nav sign, F5 the search hint,
   F7 the mode toggle into `preferences`; the Type line (Oxanium + JetBrains Mono, vendored).
2. `build(frontend): vendor the Oxanium and JetBrains Mono fonts` — `src/assets/fonts/`:
   4 `.woff2` files + 2 `OFL.txt`, from the npm tarballs.
3. `feat(frontend): add the day and night shift tokens` — rewrite `index.css`: `@font-face`,
   tokens (D1–D4), element defaults (body background, headings in display face, `code`/`kbd`
   mono, `:focus-visible` ring); move `App.css`, `Home`, `HealthCheck` styles to the new names.
4. `feat(frontend): add the preferences store slice` — `SHIFT_LS_KEY` (REACT-30),
   `store/preferences/*`, `readStoredShift`, `SET_SHIFT`, `AppStoreProvider` initializer,
   reducer and storage tests.
5. `feat(frontend): apply the stored shift before first paint` — the `index.html` inline script
   and its drift test (Q10).
6. `feat(frontend): add the shift toggle` — `components/ShiftToggle` (Q9), test + story.
7. `feat(frontend): add the deck signage components` — `StencilHeading`, `HazardStripe`,
   `CageNumber`, `StatusLamp`, with stories and tests.
8. `feat(frontend): add the deck panel components` — `DeckPanel`, `SpecPlate`, `Readout`,
   `VisualSlot`, with stories and tests.
9. `feat(frontend): add entity links and source citations` — `AppParams`, `entityPath`,
   `EntityLink`, `SourceCitations`, with stories and tests (fixtures from
   `__mocks__/catalogMocks.ts`).
10. `feat(frontend): add catalog pagination` — `Pagination` (D9), story and test.
11. `feat(frontend): add the cage empty page` — `pages/NotFound`, `path: '*'` route, test + story.
12. `feat(frontend): dress the shell as the MS deck` — `Root`: status bar (bay name,
    `ShiftToggle`, `StatusLamp`), bay-sign nav with offline signs (Q4), `data-shift` effect,
    footer (unofficial-fan-project disclaimer, source credits, "Deck systems" link); `App.css`;
    restyled `Home` (Q7); shell tests; a `Layouts/Root` story.
13. `docs(docs): record the design system as built` — only if there are departures.

## Risks to check during implementation

- **Token rename breaks existing pages.** Grep every `var(--` in `src/` after step 3; any unset
  token renders silently. Check `HealthCheck` and `Home` in all three shifts.
- **Scheme precedence.** `auto` must follow the OS live (toggle OS dark mode with the app open);
  `day` on a dark OS and `night` on a light OS must both win.
- **Inline script vs TypeScript drift.** The key, the JSON encoding and the allowed values live
  twice; the step 5 test must fail if either side changes. The script must not throw on junk or
  a throwing `localStorage`. Vite must keep the inline script in the built `index.html`.
- **`localStorage` throws** (private mode, disabled storage) and holds junk: `readStoredShift`
  and `setShift` both guard it.
- **Store state in tests.** Reading storage in the provider means a test that sets a shift can
  leak into the next; clear `localStorage` and `<html data-shift>` in `beforeEach`.
- **Fonts in Vite, Storybook and Vitest.** `url()`s in `index.css` must resolve under all three;
  `pnpm build` must hash them into `dist/assets` and emit no external font URL (grep `dist/`).
- **Contrast.** Hazard yellow on steel, amber readouts on dark, offline signs: WCAG AA for text
  (4.5:1). Check each text/background token pair.
- **Offline signs.** `aria-disabled` spans must not be focusable as links; screen readers must
  still hear the label and "offline".
- **Type-on `Readout` and screen readers.** The clip must not hide text from AT, and the full
  text shows under reduced motion.
- **`react/only-export-components` warning** if a component file also exports a helper: keep
  helpers (`entityPath`, label maps, nav config) in `.ts` files.
- **Shell test churn.** `Home/index.test.tsx` and `startApp.test.tsx` query "Welcome aboard";
  the health link moves from the nav to the footer.
- **Catch-all route** must not swallow `/health-check` or future routes; React Router ranks
  `*` last, but test an unknown path and a known one.
- **Pagination edge cases:** `total = 0`, `offset >= total` (bad URL), partial last page,
  `limit` missing from the URL vs `meta.limit`.
- **CSS nesting depth ≤ 3 and alphabetical declarations** (CSS-5, CSS-14) are not linted;
  review by eye.

## Verification

Run in `frontend/` (moon not on PATH):

- `pnpm format:check && pnpm lint && pnpm typecheck` — clean, no warnings.
- `pnpm test` — all pass; `pnpm test:cov` — every new file covered, uncovered lines explained.
- `pnpm build` — succeeds; fonts hashed into `dist/assets`; `grep -r "fonts.g" dist/` empty;
  inline shift script present in `dist/index.html`; no Mirage in the bundle.
- `pnpm build-storybook` — succeeds with every new story.
- `pnpm dlx markdownlint-cli2` on the new and changed plan docs.
- In a browser (Storybook, and the app with `MOCK_API=true` via `moon run root:dev` if the stack
  is up): all three shifts; the shift survives reload with no flash; Auto follows an OS change;
  reduced-motion emulation stops all motion; keyboard-only nav reaches every link/radio with a
  visible focus ring and skips offline signs; unknown path shows "Cage empty"; phone/tablet
  widths.

## As built (2026-11-23)

Where the implementation differs from the steps above:

- **A tooling commit before step 2.** The pre-commit hook's `oxfmt --check` exits 2 when every
  staged file is one it can't format, so the fonts-only commit failed.
  `build(repo): let the format hook pass a commit of assets alone` adds
  `--no-error-on-unmatched-pattern` to the format task in `.moon/tasks/javascript.yml`, as the
  lint task already had (user's choice).
- **Tokens use `light-dark()`, not a duplicated Night block (D2).** A selector list can't span
  `:root[data-shift="night"]` and a `prefers-color-scheme` block, so each color token is
  written once as `light-dark(<day>, <night>)`, and the shift sets only `color-scheme`
  (`light dark`, `light` or `dark`). postcss-preset-env lowers it for older browsers and still
  honours the attribute. This departs from CSS-13's wording (tokens redefined in a media
  block) but keeps its intent; amending CSS-13 is a follow-up (user's choice).
- **The Q2 default for loading the shift is overturned.** REACT-14 forbids `localStorage` in
  initial-state builders, so `AppStoreProvider` is unchanged. Instead:
  - `index.html`'s script paints the stored shift before first render (Q10);
  - `Root` dispatches `hydrateShift` on mount, which reads storage and records the shift;
  - `setShift` owns the side effects: it applies `<html data-shift>` and writes storage.
  There is no effect in `Root` that syncs the attribute from the store.
- **New tokens:** `--color-link` (hazard yellow fails AA as text on Day steel),
  `--color-scanline` and `--color-hologram-faint`, the last two from a browser check
  (`fix(frontend): give scanlines and the blueprint grid their own tokens`). `index.css` also
  gains a `.visually-hidden` utility.
- **The drift test (Q10)** imports `index.html?raw` and runs its script with `new Function`
  (one named `typescript/no-implied-eval` suppression), for every value in `SHIFTS`, junk, and
  a throwing `localStorage`.
- **Test setup** (`utils/testing/setupTests.ts`) now clears `localStorage` and
  `<html data-shift>` and restores spies after each test.
- **Home has no bay links (Q7).** Every bay is offline in F1, so Home keeps its health check
  link and says the bays come online as their pages land.
- **`VisualSlot` is named by `aria-label`** ("No visual on file for …"), with the caption
  `aria-hidden`: jsdom's name computation joins a figcaption's spans without spaces.
- **`Pagination`'s arithmetic** lives in `components/Pagination/pageOffsets.ts`, tested on its
  own. A stale offset past the end shows "None of T" and steps back to the last real page.
- **A refactor commit after step 12.** `BaySign` (`layouts/Root/components/BaySign`) renders
  one sign, so the commissioned-link branch that F2 first uses is tested now.
  `BAY_SIGNS` lives in `layouts/Root/baySigns.ts`; F2–F4 flip `isCommissioned`.
- **Fixture:** `mockWikidataSource` in `__mocks__/catalogMocks.ts`, not in the seed, covers the
  non-wiki citation kinds.
- **Commit message slip.** The body of `feat(frontend): add the cage empty page` says the
  offline signs land on the 404 page; they are not links, so only typed or stale URLs do.
- **Browser check** ran in Storybook, not in the app with `MOCK_API=true` (the Compose stack
  was not started). Checked: Night (Auto on a dark OS) and Day, the stored shift returning on
  reload, keyboard focus skipping offline signs, arrow keys switching shifts, both vendored
  fonts loading, and a 390 px viewport with no horizontal scroll. Not checked in a browser:
  Auto following a live OS change, and reduced-motion emulation; every animation was confirmed
  by reading to sit inside `prefers-reduced-motion: no-preference`.
