# Plan: F4 — personnel, faction, operation and designer pages

Branch `feat/add-entity-detail-pages` (created from `main` at `8842df2`). PR title:
`feat(frontend): add personnel, faction, operation and designer pages`. It expands the F4
entry of [`docs/plans/frontend.md`](frontend.md#prs-in-order) and the Character,
Organization, Work and Mechanical designer page templates there, and builds on F3 as built
([`mobile-suit-dossier.md`](mobile-suit-dossier.md#as-built-2026-11-23)). Q1 to Q9 were
settled by grilling on 2026-11-26.

## Context

F2 shipped the five rosters, and F3 the first detail page. Every personnel, faction, work and
designer link (roster rows, dossier credits, appearances) still lands on "Cage empty". F4
adds the other four detail pages, which completes browsing (F5 search and F6 compare
follow). F3 set the detail pattern (store, `useCatalogDetail`, `<Navigate replace>` old-slug
swap, 404, numbered footnoted sources) that these pages share.

**Facts checked in the repo:**

- **Contract** (`frontend/src/api/generated/openapi.json`):
  - `GET /api/characters/{slug}` → `CharacterDetailEntity`: card (`name`, `name_ja`) +
    `appearances: CitedWorkEntity[]` (`work` card, `source`) + `piloted_mobile_suits:
    PilotedMobileSuitEntity[]` (`mobile_suit` card, `work?` ref, `source`).
  - `GET /api/organizations/{slug}` → `OrganizationDetailEntity`: `name`,
    `parent_organization?` ref, `child_organizations: OrganizationRefEntity[]` (no source),
    `appearances: CitedWorkEntity[]`. **Its suits are not embedded:**
    `GET /api/organizations/{slug}/mobile-suits?role=&limit=&offset=` →
    `OrganizationMobileSuitEntity {mobile_suit, links[{role, work?, source}]}`; `total`
    counts suits; `role` keeps only suits with that role, and only those links.
  - `GET /api/works/{slug}` → `WorkDetailEntity`: card (`title`, `title_ja`, `work_type`,
    `start_date`, `end_date`, `continuity?`) + `parent_work?` ref + `relations:
    RelatedWorkEntity[]` (`relation_type` sequel_of / compilation_of / adaptation_of /
    remake_of / side_story_of, `direction`, `work` card, `source`). Suits come from
    `GET /api/works/{slug}/mobile-suits` → `MobileSuitAppearanceCardEntity` (suit card +
    `first_episode`, `last_episode`, `is_debut`; **no source**), debuts first.
  - `GET /api/mechanical-designers/{slug}` → card fields only (**no source at all**).
    Suits come from `GET /api/mechanical-designers/{slug}/mobile-suits` →
    `DesignedMobileSuitEntity {mobile_suit, source}`.
  - Every sub-list route takes `limit`/`offset`, resolves old slugs, and 404s an unknown
    parent.
- **Mirage serves all eight routes already** (`__mocks__/endpoints.ts`, `detailHandler`,
  `subListHandler`), with old-slug redirects (`findBySlugOrRedirect`, `msg` →
  `mobile-suit-gundam`). The organization sub-list **ignores `role`**
  (`organizationMocks.ts`: "Mirage filters are opt-in (D7)"). Fixtures mirror
  `backend/scripts/seed_dev.py`: **no organization has a parent or child**; Zeonic has no
  appearances; only `compilation_of` work relations exist; It Moves? has none.
- **Store:** `works` has `detailsBySlug` + `fetchWork`; `characters`, `organizations`,
  `mechanical-designers` have `list` only. `catalogList.ts` has `fetchCatalogDetail`,
  `setDetailUnderSlugs`, `fetchCatalogList`, `ListState` (stale responses dropped by
  `query`). `useCatalogDetail` (`store/hooks.ts`) fetches once per slug; `useCatalogList`
  builds its query from URL `keys` and takes a `fetchList(dispatch, query)` that knows its
  path, so it can't take a slug.
- **F3 pieces F4 needs, now page-local to `pages/MobileSuitDetails/`:** the loading / error
  / 404 / old-slug shell and `PendingSection` in `index.tsx`, the grid in `styles.css`,
  `SuitStrip`, `SuitHeader`, `components/PendingPanel`, `utils/citations.ts`'s `Cite` type,
  `utils/format.ts`'s `formatEpisodes` (with the private `formatRange`),
  `utils/entryList.tsx`, `SuitAppearances`, and `SuitLineage`'s tiered nested-list CSS.
  Already shared: `numberCitations` (`@/utils`), `CitationMark`, `SourceCitations` (returns
  nothing for an empty list), `SpecPlate` (`isCompact`), `VisualSlot` (`shape`),
  `EntityLink`, `StencilHeading`, `StatusLamp`, `DeckPanel`, `RosterTable` +
  `rosterColumnHelper`, `Pagination` (writes `?offset=` only), `CatalogRoster` (heading +
  filter bar + status/error/empty/table/pagination), `slugify`, `plain-list`,
  `WORK_TYPE_LABELS`, `UNIT_TYPE_LABELS`, `SOURCE_KIND_LABELS`.
- **Routing:** `routerConfig` (`app/router.tsx`) has list routes for all four kinds and only
  `mobile-suits/:mobileSuitSlug` for details. `AppParams` already derives
  `characterSlug`, `organizationSlug`, `workSlug`, `mechanicalDesignerSlug` from
  `ENTITY_KINDS`. Storybook's `preview.tsx` takes a `path` parameter (F3).
- **Tooling:** moon is not on PATH; run `pnpm` scripts in `frontend/`. Mock mode outside the
  proxy: `MOCK_API=true APP_DOMAIN=127.0.0.1 PROXY_HTTPS_PORT=5199 FRONTEND_PORT=5199 pnpm
  start:dev`.
- **Gundam Wiki live check:** Fandom answers automated fetches with 402, so the templates come
  from `frontend.md`'s page templates.
- **Standards that bind this:** REACT-1/2, REACT-9, REACT-12–18, REACT-24–27, CSS-1/4/10–17,
  TEST-10, TEST-15–18, TEST-20, TEST-23.

## Decisions (grilled 2026-11-26)

### Shared frame and layout

- **Q1. `components/CatalogDetail`** owns F3's loading (`StatusLamp busy` in
  `role="status"`), error (`role="alert"` with the API's message), 404 (`NotFound`) and
  old-slug swap (`<Navigate replace>` to `entityPath({ kind, slug })`, keeping `search`).
  Props: `detailState`, `kind`, `slug` (the URL's), `id`, `loadingHeading`,
  `loadingLabel`, and a render prop `children(detail)`. It is to details what
  `CatalogRoster` is to lists.
- **Q7. Every detail page uses two columns with a sticky infobox** (image on top), as F3.
- **Q7a. `components/DossierLayout`** holds that grid, with `strip`, `header`, `infobox`
  and body (`children`) slots. Its `styles.css` owns the grid areas, the
  `minmax(16rem, 20rem)` column, the sticky infobox and the 40rem stacking.
- **Q7b. Every page gets a phone strip.** `SuitStrip` becomes the shared
  `components/DossierStrip` (a small `VisualSlot`, an eyebrow and the name), pinned on
  phones. The eyebrow is the model number for suits, and the kind's framing label otherwise
  (Personnel file, Faction registry, Operation log, Engineering credits).
- **D1. Shared homes for F3's page-local helpers**, moved unchanged in behaviour:
  `SuitHeader` → `components/DossierHeader` (eyebrow, name, `nameJa` with `lang="ja"`, class
  line); `PendingPanel` + `PendingSection` → `components/PendingPanel`; `Cite` →
  `components/CitationMark`; `formatEpisodes` / `formatRange` → `utils/formatEpisodes.ts`;
  `entryList` → `components/SpecPlate`; the appearance list →
  `components/WorkAppearances`, taking items with optional episodes and debut, so a
  `CitedWorkEntity` renders too; the lineage tier CSS → a `tiered-list` utility in
  `index.css`, for the org chart and related works.

### Sub-lists

- **Q2. Sub-list state.** `works.mobileSuits`, `mechanicalDesigners.mobileSuits` and
  `organizations.mobileSuitsByRole: Record<MobileSuitOrganizationRole, ListState>`. Each
  `query` holds the whole request (`<slug>?<query>`), so a response for another parent,
  role or page is dropped. A new `useCatalogSubList({ fetchSubList, apiQuery,
  selectList, slug })` mirrors `useCatalogList`; `apiQuery` builds the API query from the
  URL (so an org section maps `operator_offset` to `role=operator&offset=`).
- **Q3. The sub-list fetches after the detail**, with the detail's **current** slug: an
  old-slug visit makes one sub-list request, and a 404 comes only from the detail.
- **Q4. The sub-list body is shared with the rosters.** A refactor extracts
  `CatalogRoster`'s status / error / empty / table / pagination into `RosterBody`; a
  sub-list is a `RosterBody` under an `h3`. Page size is the API's default (50).
- **Q5. Organization suits in three role sections** — Manufactured, Operated, Developed —
  each its own request with `?role=` and its own pager. Mirage's organization sub-list
  applies `role` as the API does (only suits with that role, and only those links). A suit
  with two roles shows in both sections, each row with its work when tagged.
- **Q5a. Each section pages in its own URL param.** `Pagination` gains an `offsetParam`
  prop (default `'offset'`, so rosters don't change); the sections write
  `manufacturer_offset`, `operator_offset`, `developer_offset`.
- **Q5b. An empty role section keeps its heading** and reads "None on file" (not "DATA
  PENDING": the catalog holds the links).
- **Q6. Sub-list sources are numbered** after the detail's: each row on the current page
  gets a footnote mark, and the source list adds those sources.

### Pages

- **D2. Character — personnel file** (`pages/CharacterDetails/`, `/characters/:characterSlug`):
  header (name, `name_ja`); infobox: portrait `VisualSlot`, Registry rows pending
  (Affiliation, Rank, Gender, Age, Voice actors); **Qualified units** — piloted suits as
  `EntityLink`s with model number, the work when tagged, and a mark; **Appearances**;
  pending Personality, Skills, History, Relationships, Quotes; sources.
- **D3. Organization — faction registry** (`pages/OrganizationDetails/`): header; infobox:
  `VisualSlot` (**Q8**: no generated insignia until the images plan), parent organization,
  pending Type, Headquarters, Leaders, Founded, Dissolved; **Org chart** (parent → this →
  child units as a tiered list, hidden when there are none); **Appearances**; **Mobile
  weapons** in three role sections (Q5); pending History; sources.
- **D4. Work — operation log** (`pages/WorkDetails/`): header (title, `title_ja`, type ·
  continuity); infobox: `VisualSlot`, type, dates (Q9), continuity, parent work, pending
  Studio, Episodes; **Related works** grouped by type × direction (`utils/relations.ts`:
  "Sequel to" / "Sequels", "Compilation of" / "Compiled in", "Adaptation of" /
  "Adaptations", "Remake of" / "Remakes", "Side story of" / "Side stories"), hidden when
  empty; **Mobile weapons appearing** sub-list (model number, name, unit type, episodes,
  debut lamp); pending Staff, Characters, Plot; sources.
- **Q9. Work dates** use `Intl.DateTimeFormat('en', { dateStyle: 'medium', timeZone:
  'UTC' })`: `Apr 7, 1979 – Jan 26, 1980`, a single date when only the start is known or
  both are equal, and DATA PENDING with no start. The row reads "Aired" for TV series and
  ONAs, "Published" for manga and novels, "Released" otherwise.
- **D5. Designer — engineering credits** (`pages/DesignerDetails/`): header (name,
  `name_ja`); infobox: portrait `VisualSlot`, pending Born, Studio; **Designed units**
  sub-list (model number, name, unit type, continuity, a mark per row); sources.
- **D6. Each page's root** is a `section` titled by its `h2`, as F3 as built. Japanese names
  use `lang="ja"`. One fixed `SOURCE_ID_PREFIX` per page.

## Steps (one commit each)

1. `docs(docs): plan the entity detail pages` — this plan to
   `docs/plans/entity-detail-pages.md`; `frontend.md`'s F4 entry links it, and its
   Character / Organization / Work templates gain the role sections, the pending insignia
   and the phone strip.
2. `refactor(frontend): share the catalog detail frame` — Q1, Q7a, Q7b and
   `DossierHeader`: `CatalogDetail`, `DossierLayout`, `DossierStrip`, `DossierHeader`;
   `MobileSuitDetails` moves onto them.
3. `refactor(frontend): share the dossier's sections and helpers` — the rest of D1.
4. `refactor(frontend): share the roster body` — Q4's `RosterBody`, and Q5a's
   `offsetParam`.
5. `feat(frontend): add personnel, faction and designer details to the store` — detail
   slices for three kinds, with `catalogSlices.test.ts` cases (old slug, 404, error).
6. `feat(frontend): add suit sub-lists to the store` — Q2, Q3, `useCatalogSubList`, the
   Mirage `role` filter, with tests.
7. `feat(frontend): add the personnel file page` — D2, route, tests, stories.
8. `feat(frontend): add the faction registry page` — D3, Q5–Q5b.
9. `feat(frontend): add the operation log page` — D4, Q9.
10. `feat(frontend): add the engineering credits page` — D5.
11. `docs(docs): record the entity detail pages as built` — only if there are departures.

## Risks to check during implementation

- **Refactor fidelity.** Steps 2–4 must leave every `MobileSuitDetails`, roster and
  `Pagination` test and story passing unchanged, with the dossier's sticky infobox and
  360 px strip unchanged in the browser.
- **Render prop and hooks.** `CatalogDetail`'s `children(detail)` must render a component
  (`<Dossier suit={…} />`), not call hooks inline, so hook order holds across states.
- **Old-slug swap with sub-lists.** `/works/msg?offset=50` must swap once to
  `mobile-suit-gundam`, keep the params, and fetch the sub-list once (Q3). Back skips the
  old URL.
- **Stale sub-lists.** Moving between two works (a related-work link) before the first
  sub-list answers must not show the first work's suits: the `<slug>?<query>` key drops it.
- **Three org sections.** Each section's request, state and pager must stay separate:
  paging Operated must not refetch or reset Manufactured. Test with Mirage `overrides` and
  `?limit=`-sized pages.
- **Mirage `role` filter.** It must drop the other roles' links, not just the suits, and
  answer an unknown role with the API's 422. `endpoints.ts` is 485 lines: put the filter in
  `organizationMocks.ts` or `listFilters.ts`.
- **`useCatalogSubList` effect deps.** `apiQuery` and `fetchSubList` must be stable
  (module-level), or the effect refetches every render.
- **Footnotes with sub-lists.** Numbers must stay right as a sub-list pages (sources after
  the detail's), the same source in two org sections gets one number, and a designer with
  no suits shows no source list.
- **Store test churn.** New `detailsBySlug`, `mobileSuits` and `mobileSuitsByRole` fields
  change initial-state expectations in `catalogSlices.test.ts`.
- **Fixture gaps.** No org parent/child, one relation type: tests and stories use Mirage
  `overrides` for org charts and every relation type × direction (test every pair).
- **Dates.** UTC formatting must not shift a day in negative-offset time zones; test with a
  `TZ`-independent assertion.
- **`react/only-export-components`.** Helpers live in `.ts` files.

## Verification

Run in `frontend/` (moon not on PATH):

- `pnpm format:check && pnpm lint && pnpm typecheck` — clean, no warnings.
- `pnpm test` — all pass; `pnpm test:cov` — every new file covered, uncovered lines tested
  or removed.
- `pnpm build` — succeeds; note the bundle size against F3's 398 kB (124 kB gzip).
- `pnpm build-storybook` — succeeds with the new stories.
- `pnpm dlx markdownlint-cli2 docs/plans/entity-detail-pages.md docs/plans/frontend.md` from
  the repo root.
- In a browser (app with `MOCK_API=true`, and Storybook): from each roster and from the
  dossier's credits to each page; `/works/msg` swaps to `mobile-suit-gundam` and Back skips
  it; related-work links; sub-list paging with `?limit=1`; each org role section pages on
  its own; footnotes jump to their source; unknown slugs show "Cage empty"; the dossier is
  unchanged after the refactors; both shifts; 360 px with the strip pinned; no console
  errors beyond `safeFetch`'s logged 404.
