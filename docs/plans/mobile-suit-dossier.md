# Plan: F3 — the mobile suit dossier

Branch `feat/add-mobile-suit-dossier` (created from `main` at `ee16d8b`). PR title:
`feat(frontend): add the mobile suit dossier`. It expands the F3 entry of
[`docs/plans/frontend.md`](frontend.md#prs-in-order) ("detail page, spec tabs, parts,
lineage, height lineup") and the mobile suit page template there, and builds on F2 as built
([`catalog-browser.md`](catalog-browser.md#as-built-2026-11-23)). Q1 to Q11 were
settled by grilling on 2026-11-23.

## Context

F2 shipped the five rosters, but every roster row's `EntityLink` lands on "Cage empty":
no detail page exists. F3 adds the first one, `/mobile-suits/:mobileSuitSlug`, as a
maintenance dossier: header, infobox, spec sheets as configuration tabs with their parts,
lineage, appearances, a height lineup and source credits. It also sets the detail pattern
(store, hook, old-slug swap, 404) that F4 copies for the other four kinds.

**Facts checked in the repo:**

- **Contract** (`src/api/generated/openapi.json`): `GET /api/mobile-suits/{mobile_suit_slug}`
  → `MobileSuitResponse {data: MobileSuitDetailEntity}` (the schema lists 200 and 422; the
  route also answers 404 for an unknown slug). `MobileSuitDetailEntity` = card fields +
  `designers[]` (`DesignerCreditEntity`), `organizations[]` (`OrganizationCreditEntity`,
  `role` manufacturer/operator/developer, `work?`), `pilots[]` (`PilotCreditEntity`,
  `work?`), `relations[]` (`RelatedMobileSuitEntity`: `relation_type` variant_of /
  developed_from / upgrade_of / alternate_version_of, `direction` outgoing/incoming,
  `mobile_suit` card), `appearances[]` (`WorkAppearanceEntity`: work card,
  `first_episode`, `last_episode`, `is_debut`), `spec_sheets[]`. Every credit, relation,
  appearance and sheet carries a `source`.
- **Spec sheets** (`backend/models/mobile_suit/facade.py` `_get_spec_sheets`,
  `_filled_sheet`): base sheets (`configuration: null`) first, then by configuration, then
  source. A named sheet's gaps are **already filled** from the same source's base sheet;
  `inherited_fields` / `inherited_parts` name what was filled. Ten measurements, all
  nullable: `overall_height_m`, `head_height_m`, `empty_weight_kg`, `gross_weight_kg`,
  `generator_output_kw`, `total_thrust_kg`, `max_acceleration_g`, `max_speed_kmh`,
  `sensor_range_m`, `turn_time_s`. Parts: `armaments` (mount fixed / handheld /
  optional_fixed / optional_handheld, `quantity_min/max`, `note`), `equipment` (fit
  standard/optional, `note`), `materials` (`material_use` armor/frame), `powerplants`
  (quantities, `note`). Parts are `{slug, name}` refs with no route of their own.
- **Relations read from the viewed suit's side** (`catalog-read-api.md`): `outgoing` = this
  suit is `<relation_type>` the other; `incoming` = the other is `<relation_type>` this one.
  Direct edges only; the frontend owns the wording.
- **Aliases** exist in `src/api/index.ts` for every type above, plus `SpecSheetField` and
  `SpecSheetPartKind`.
- **Mirage already serves the detail** (`__mocks__/endpoints.ts:424`, `detailHandler`,
  `findMobileSuitMock` with the `rx-78-2` → `rx-78-2-gundam` redirect, 404 via `notFound`).
  Fixtures (`__mocks__/mobileSuitMocks.ts`): RX-78-2 has two sheets (base + "Magnet
  Coating", which inherits 8 fields and all 4 part kinds), full parts, one designer, one
  manufacturer, one pilot with a work, two incoming `alternate_version_of` relations, a
  debut with episodes 1–43. RX-78-02 has a pilot with no work and two designers. Zaku II
  has manufacturer + operator and no powerplant. **No fixture has `overall_height_m`**
  (all give `head_height_m`), and only `alternate_version_of` relations exist.
- **Store pattern to copy** (`store/works/*`, `store/catalogList.ts`): `DetailState`,
  `DetailsBySlug`, `requestDetail` / `setDetail` / `setDetailError`; `fetchWork` is a
  hand-written REQUEST → `safeFetch.call` → SET / SET_ERROR with `isNotFound` on 404; the
  works `SET_WORK` reducer also stores an old slug's detail under its current slug.
  `catalogErrorMessage` formats errors. `store/mobile-suits` has only `list`.
- **Hooks** (`store/hooks.ts`): `guardDispatch`, `useCatalogList`, `useWorkFilterChips`
  (fetches a detail when its slug's state is `undefined`; swaps an old slug with
  `replace`).
- **Reusable pieces:** `SpecPlate` (label/value, `null` → "DATA PENDING", `isInherited` →
  "per base spec"), `SourceCitations` (keys `kind-url`, so duplicates must be removed
  first), `VisualSlot`, `EntityLink` + `entityPath`, `StencilHeading` (`eyebrow`, `level`),
  `DeckPanel`, `CageNumber`, `Readout`, `StatusLamp status="busy"`, `HazardStripe`,
  `NotFound` (reads `pathname`), `UNIT_TYPE_LABELS`, `WORK_TYPE_LABELS`, `.stencil-label`,
  `.visually-hidden`. Japanese names render with `lang="ja"` (F2 as built).
- **Routing:** `routerConfig` (`app/router.tsx`) has `mobile-suits` only; `AppParams`
  already has `mobileSuitSlug`. Storybook's router (`.storybook/preview.tsx`) mounts every
  story at `path: '*'`, so `useParams` gets no slug there today.
- **Breakpoints:** phone `max-width: 40rem`, tablet `64rem` (`src/index.css:142`).
- **Tooling:** moon is not on PATH; run `pnpm` scripts in `frontend/`.
- **Gundam Wiki live check:** Fandom answers automated fetches with 402 (`frontend.md`), so
  the template comes from that plan's mobile suit section and the ingestion spike.
- **Standards that bind this:** REACT-1/2 (page-local `components/`, `utils/`), REACT-8,
  REACT-9 (semantic markup; ARIA tabs), REACT-12–18, REACT-19, REACT-20/21, REACT-24–27,
  CSS-1/4/10–17, TEST-2, TEST-10, TEST-15–18, TEST-20, TEST-23.

## Decisions (grilled 2026-11-23)

### Layout

- **Q1. Two columns, the infobox sticky.** At tablet width and above, the main column
  scrolls on the left and the infobox column sits on the right, `position: sticky` under
  the deck status bar, with `VisualSlot` at its top, so the image stays in view. The
  sticky column is plain: no inner scrolling and no height cap. On phones (`max-width:
  40rem`) the infobox stacks above the tabs, and a **slim sticky header strip** (a small
  `VisualSlot` thumbnail, the model number and the name) stays pinned instead.
- **Q2. The infobox follows the selected spec sheet.** Top to bottom: image; the selected
  sheet's name (configuration, or "Base spec"), head/overall height, gross weight,
  powerplant(s) and armor/frame materials; then the credits: designers, organizations by
  role (Manufacturer / Operator / Developer, with the work when tagged), pilots (with the
  work when tagged) and the debut (the `is_debut` appearance, with its episode range).
  Both the infobox and the tabs read the sheet from `?spec=`, so no state is lifted.
- **Q3. Pending (⏳) slots show as DATA PENDING, outside the sticky column.** A
  **Registry** `SpecPlate` sits in the main column under the header, with Other names,
  Archetype and Production as `null` rows. History, Gallery and Trivia are small
  `DeckPanel`s near the foot of the main column.

### Spec sheets

- **Q4. The selected sheet lives in `?spec=`.** The value is the slugified configuration
  (`?spec=magnet-coating`); no param means `spec_sheets[0]`. When two sheets would share a
  value (two base sheets from different sources), the source kind is appended
  (`base-wikidata`). An unknown value shows the first sheet and leaves the URL alone. The
  mapping lives in `pages/MobileSuitDetails/utils/specSheets.ts` (`specSheetKeys`,
  `selectSpecSheet`), and a page-local `useSelectedSpecSheet` reads it.
- **Q5. Switching tabs replaces the history entry** (`setSearchParams(…, { replace: true
  })`), and other params stay. Picking the first sheet removes `spec`.
- **Q6. The tabs are ARIA tabs** (REACT-9): a tablist with arrow, Home and End keys and a
  roving `tabIndex`, plus a labelled panel. A suit with one sheet shows the panel with no
  tablist. Tab labels: the configuration, or "Base spec", with the source kind added when
  two sheets collide.
- **D4. Measurements** are formatted with `Intl.NumberFormat('en')` and the SI unit from
  the field name (`18 m`, `43,400 kg`, `1,380 kW`, `0.93 G`, `165 km/h`, `5,700 m`,
  `1.5 s`). Inherited fields show "per base spec" through `SpecPlate`.
- **D5. Parts.** Armaments are grouped Fixed / Handheld / Optional, where Optional holds
  both optional mounts and marks each item fixed or handheld. Equipment is grouped
  Standard / Optional. Counts read `2 ×` or `1–2 ×`, and notes follow the name. Parts are
  plain text (no part routes). Inherited part kinds show "per base spec" on their group
  heading.

### Lineage and lineup

- **Q7. Lineage is a tiered dev-tree.** Ancestors (outgoing `developed_from`,
  `upgrade_of`, `variant_of`) → this suit → descendants (incoming: "Developed into",
  "Upgraded into", "Variants"), with alternate versions (either direction) beside this
  suit. It is built as nested, labelled lists with CSS connectors, so screen readers get
  grouped lists. Each node is an `EntityLink`. The wording for every type × direction is
  in `utils/lineage.ts`. The section is hidden when there are no relations.
- **Q8. Height lineup.** It uses `overall_height_m`, or else `head_height_m`, and says
  which one. It's an inline SVG with a 1.7 m human, an original 18 m reference frame and
  the suit at scale, and it follows the `?spec=` sheet. It sits in the main column under
  the measurements, as `role="img"` with a text name that gives the three heights. It is
  hidden when the sheet has no height. Fills use tokens only.

### Data and sources

- **Q9. Share the detail fetch first.** A refactor commit adds `fetchCatalogDetail` and
  `setDetailUnderSlugs` (store under the requested slug, and under the current one when
  it differs) to `store/catalogList.ts`. `fetchWork` and the works reducer use them, and
  the tests don't change. F3 and F4 reuse them.
- **D2. Store:** `mobileSuits.detailsBySlug`, with `REQUEST_MOBILE_SUIT`,
  `SET_MOBILE_SUIT`, `SET_MOBILE_SUIT_ERROR` and `fetchMobileSuit({ dispatch, slug })`.
- **D3. `useCatalogDetail({ fetchDetail, selectDetails, slug })`** in `store/hooks.ts`
  fetches when the slug's state is `undefined`, returns that `DetailState`, and is
  guarded by `guardDispatch`.
- **Q10. Old slugs swap with `<Navigate replace>`.** Once the detail arrives and
  `detail.slug` differs from the param, the page renders `<Navigate replace to={{
  pathname: entityPath(…current), search }} />`. It doesn't use `useNavigate` in render
  (REACT-26), and it doesn't refetch, because the detail is already stored under the
  current slug.
- **Q11. One de-duplicated, numbered source list at the foot, with per-item footnotes.**
  `utils/citations.ts` collects every source on the page in reading order (infobox
  credits, spec sheets, lineage, appearances). It de-duplicates them by `kind` + `url` +
  `revision_id` and gives each a number. `SourceCitations` becomes an ordered list with
  an `id` per entry (`idPrefix` prop), and a new shared `CitationMark` renders the
  superscript `[n]` link, named "Source n". Marks go on each credit row, lineage node and
  appearance, and on each spec sheet (by the panel heading, and in the infobox's sheet
  name).
- **D6. Loading / error / 404:** loading shows `StatusLamp busy` in a `role="status"`
  region. A 404 renders `NotFound`. Any other error shows `role="alert"` with the API's
  message.
- **D1. Page folder** `pages/MobileSuitDetails/`, with page-local `components/`
  (`SuitHeader`, `SuitInfobox`, `SpecSheetTabs`, `SuitParts`, `SuitLineage`,
  `HeightLineup`, `SuitAppearances`) and `utils/` (`format.ts`, `specSheets.ts`,
  `lineage.ts`, `citations.ts`, `hooks.ts`).

## Steps (one commit each)

1. `docs(docs): plan the mobile suit dossier`: save this plan to
   `docs/plans/mobile-suit-dossier.md`, and amend `frontend.md` (the F3 entry links the
   plan; the mobile suit template gains the sticky infobox, the Registry plate and
   footnoted sources; "Every detail page" gains the numbered, de-duplicated list).
2. `refactor(frontend): share the catalog detail fetch`: Q9.
3. `feat(frontend): add mobile suit details to the store`: D2 and D3, with tests in
   `catalogSlices.test.ts` (an old slug stored twice, a 404 sets `isNotFound`, 422 and
   500 messages, a stale response dropped).
4. `feat(frontend): number source citations for footnotes`: Q11's `SourceCitations`
   change and `CitationMark`, with their tests and stories.
5. `feat(frontend): add the mobile suit dossier page`: the route
   `mobile-suits/:mobileSuitSlug`, `SuitHeader`, the Registry plate, the two-column
   layout with the sticky `SuitInfobox` (Q1–Q3), `specSheets.ts` and
   `useSelectedSpecSheet` (reading only), `SuitAppearances`, the pending panels,
   `citations.ts` and the footnotes, D6 and Q10. Storybook's `preview.tsx` gains a `path`
   parameter (default `'*'`) so stories get route params. Page tests, and stories for the
   default, old slug, 404, error, loading and sparse (RX-78F00) states.
6. `feat(frontend): add spec sheet tabs and parts`: `SpecSheetTabs` (Q4–Q6, writing
   `?spec=`), the measurements plate (D4) and `SuitParts` (D5), with tests and stories.
   The infobox now follows the tab.
7. `feat(frontend): add the suit lineage`: Q7, with tests that use Mirage `overrides` for
   the relation types the fixtures lack.
8. `feat(frontend): add the height lineup`: Q8, with tests and a story.
9. `docs(docs): record the mobile suit dossier as built`: only if there are departures.

## Risks to check during implementation

- **Old-slug swap loops.** `<Navigate>` must render once: the current slug's state must
  already hold the detail (`setDetailUnderSlugs`), so the swapped URL doesn't refetch.
  `search` (`?spec=`) must survive. Test that Back skips the old URL.
- **Stale detail.** Going from one suit to a related suit before the first answers: the
  guard must drop the old response, and each slug's state stays separate.
- **Refactor fidelity.** `fetchWork`'s tests and `useWorkFilterChips`' old-slug swap must
  pass unchanged after step 2.
- **`?spec=` keys.** Slugify must be stable and ASCII-safe, collisions must get the source
  kind, and an unknown key must fall back without a URL write (no loop with the tabs'
  `replace`). Switching suits must not carry an invalid `spec` into a wrong sheet.
- **Sticky column.** It must not overlap the deck status bar (use its height token, or
  measure it). A column taller than the viewport simply scrolls with the page (agreed: no
  inner scrolling). On phones, the header strip must not cover the content's anchors:
  footnote jumps need `scroll-margin-top`.
- **Footnote accuracy.** Each mark's number must match its source's entry after
  de-duplication. Test a source shared by two items (one entry, the same number), and two
  revisions of one page (two entries). Ids must be unique on the page (`useId` prefix).
- **SourceCitations change.** It has no other users yet, but its stories and tests change.
  Keep the existing assertions (link names, licence) passing.
- **ARIA tabs.** `aria-controls` / `aria-labelledby` ids from `useId`; only the selected
  tab in the tab order; the panel gets `tabIndex={0}` when it has no focusable child.
- **Height data.** No fixture has `overall_height_m`; test the fallback label with an
  override. The human must stay visible at its minimum size next to 18 m, and the labels
  must stay legible at phone width.
- **Relation wording** for all 4 types × 2 directions: test every pair.
- **Storybook `path` parameter** defaults to `'*'`, so no other story changes.
- **Store test churn.** `mobileSuits.detailsBySlug` changes the initial-state
  expectations in `catalogSlices.test.ts`.
- **`react/only-export-components`.** Helpers live in `.ts` files.
- **`endpoints.ts` size** (485 lines): no new handlers expected.
- **Links to F4 pages** (designers, organizations, pilots, works) reach "Cage empty"
  until F4, as F2 Q4 accepted.

## Verification

Run in `frontend/` (moon not on PATH):

- `pnpm format:check && pnpm lint && pnpm typecheck` — clean, no warnings.
- `pnpm test` — all pass; `pnpm test:cov` — every new file covered, uncovered lines tested
  or removed.
- `pnpm build` — succeeds; note the bundle size change.
- `pnpm build-storybook` — succeeds with the new stories.
- `pnpm dlx markdownlint-cli2 docs/plans/mobile-suit-dossier.md docs/plans/frontend.md`
  from the repo root.
- In a browser (Storybook, and the app with `MOCK_API=true` if it starts): roster row →
  dossier; `/mobile-suits/rx-78-2` swaps to `rx-78-2-gundam` and Back skips the old URL;
  Magnet Coating tab shows "per base spec" rows and sets `?spec=magnet-coating` (Back
  leaves the page, the infobox follows, reload keeps it); the infobox stays pinned while
  scrolling, and the phone strip shows at 360 px; footnote marks jump to their source;
  arrow keys move between tabs; lineage links open the related suit; unknown slug shows
  "Cage empty"; both shifts; phone width;
  no console errors.

## As built (2026-11-23)

Where the implementation differs from the steps above:

- **Three extra commits.** `refactor(frontend): share the source kind labels` (before step 5)
  moves `SOURCE_KIND_LABELS` to `constants`, since spec sheet keys and labels name the source
  kind. `refactor(frontend): share the blueprint silhouette` (before step 8) moves the
  `VisualSlot` path to `components/VisualSlot/blueprint.ts` for the height lineup.
  `fix(frontend): keep part counts legible on the day shift` (after step 8) swaps the part
  counts from `--color-accent` (a fill colour, unreadable on Day shift) to
  `--color-readout-alt`.
- **`useCatalogDetail` has no `guardDispatch` (D3).** The REQUEST dispatch defines the slug's
  state, so the effect re-ran, its cleanup flipped the guard, and the SET was dropped. Each
  slug's state is kept apart and the store is app-wide, so a late response is stored under its
  own slug and replaces nothing. The store tests cover the old slug, the 404, a 503 and a 422
  instead of a "stale response dropped" case.
- **`numberCitations`, `citationKey` and `citationID`** live beside `SourceCitations`
  (`components/SourceCitations/citationNumbers.ts`), not in the page's `utils/citations.ts`,
  since F4's pages number their sources the same way. The page keeps `collectCitations`
  (credits, then sheets, relations and appearances) and a fixed `SOURCE_ID_PREFIX`
  (`mobile-suit-source`), not a `useId` prefix: there is one source list per page.
- **The deck status bar is not sticky**, so the infobox sticks at `--space-3` from the top
  with no overlap to manage (Q1 risk).
- **Infobox (Q2):** a row whose part kind was inherited but holds nothing of its own use (the
  Magnet Coating sheet's Frame) shows plain "DATA PENDING", not "per base spec". This landed
  in step 6, with the tabs that make it reachable. Its `VisualSlot` is 4:3 with a fixed-height
  blueprint, since the slot's 60% SVG height overflowed the aspect ratio in a flex column.
- **Spec panel (Q6, D5):** each panel holds the sheet's name with its source mark, the ten
  measurements, the height lineup, then the parts. The parts show all four kinds (armaments,
  equipment, powerplant, materials), each "DATA PENDING" when empty.
- **Lineage (Q7):** alternate versions from both directions share one "Alternate versions"
  group. The section is headed "Variants & lineage", and the current suit is marked
  `aria-current="page"`.
- **Height lineup (Q8):** `utils/lineup.ts` lays the figures out in metres
  (`lineupHeight`, `lineupLayout`). The lineup rescales when a suit is taller than 18 m (the
  `TallSuit` story). The human is a plain head and body block.
- **Stories:** page-local components have no stories of their own; the page's stories cover
  them (`Default`, `NamedConfiguration`, `SingleSheet`, `TallSuit`, `OldSlug`, `Sparse`,
  `NotFound`, `RequestFailed`, `Loading`). `CitationMark` has a story.
- **Bundle:** the app's JS grows from 375 kB (117 kB gzip) after F2 to 397 kB (124 kB gzip).
- **Mock mode outside the proxy** needs `APP_DOMAIN` and `PROXY_HTTPS_PORT` set:
  `MOCK_API=true APP_DOMAIN=127.0.0.1 PROXY_HTTPS_PORT=5199 FRONTEND_PORT=5199 pnpm start:dev`.
- **Browser check** ran in the app with `MOCK_API=true`, and in Storybook. Checked: roster row
  → dossier; `/mobile-suits/rx-78-2?spec=magnet-coating` swaps to the current slug, keeping
  `spec`, and Back skips the old URL; tab clicks and arrow keys move the selection and focus,
  and the infobox follows; picking Base spec removes `spec`; a footnote mark targets its
  source; the infobox stays pinned while scrolling; at 360 px (in an iframe, since the window
  would not resize) the phone strip pins and nothing overflows; Day shift (which found the
  part-count contrast); no console errors. Not checked: a full keyboard-only walk.
- **Flaky F2 tests.** Under `pnpm test:cov` load, the roster tests "searches as the user
  types" (`MobileSuitList`, `CharacterList`) timed out once and passed on four reruns. This PR
  doesn't touch them.
