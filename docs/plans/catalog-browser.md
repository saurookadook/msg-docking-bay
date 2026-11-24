# Plan: F2 — browse the catalog

Branch `feat/browse-the-catalog` (created from `main` at `10d8674`). PR title:
`feat(frontend): browse the catalog`. It expands the F2 entry of
[`docs/plans/frontend.md`](frontend.md#prs-in-order) ("store slices, list pages with
filters/pagination in URL params, `FilterBar`, Mirage filters; commission the list routes'
nav signs") and builds on F1 as built ([`design-system.md`](design-system.md#as-built-2026-11-23)).
Q1 to Q10 were settled by grilling on 2026-11-23.

## Context

F1 shipped the deck shell, the shared components and `Pagination`, but every bay sign is
offline: no catalog page exists. F2 adds the five list pages (Mobile Suits, Personnel,
Organizations, Works, Designers), their store slices, URL-driven filters and paging, and
makes mock mode filter like the API, so wiki mode can be browsed end to end. Detail pages
are F3/F4.

**Facts checked in the repo:**

- **List routes** (`src/api/generated/openapi.json`): every list takes `limit` (1–100,
  default 50), `offset` (≥ 0) and `q` (≤ 100 chars). Filters: `/api/mobile-suits`
  `continuity`, `work`, `unit_type`; `/api/works` `continuity`, `work_type`;
  `/api/characters` and `/api/organizations` `work`; `/api/mechanical-designers` none.
  Envelope `{data, meta:{limit, offset, total}}`. `/api/continuities` is `{data}` only.
- **Filter semantics** (`backend/models/{mobile_suit,character,organization,work}/facade.py`):
  `continuity_slug` and `work_slug` match **current slugs only, exactly** (no child
  continuities, no redirects); an unknown slug gives an empty page, not a 404. `work` means
  "appears in that work" (appearance junctions). A bad enum value is a 422.
- **Cards:** `MobileSuitCardEntity` {slug, name, name_ja, model_number, unit_type,
  continuity?}; `WorkCardEntity` {slug, title, title_ja, work_type, start_date, end_date,
  continuity?}; `CharacterCardEntity` / `MechanicalDesignerCardEntity` {slug, name,
  name_ja}; `OrganizationCardEntity` {slug, name, parent_organization?}. `UnitType` = suit,
  armor, fighter, man_machine, worker, pod, doll; `WorkType` = tv_series, film, ova, ona,
  manga, novel, video_game, other. `WorkResponse` carries the current `slug`.
- **Store** (`src/store/`): slices `health` and `preferences`; field reducers via
  `combineReducers` (`FieldReducerEntry`); constants in `actionTypes.ts`; `AppAction` union
  in `types.ts`. `fetchHealthCheck` (`store/health/actions.ts`) is the async model: REQUEST
  → `safeFetch.call<Response>` → SET, or SET_ERROR with `SafeFetchError.detail` (string)
  or a fallback. `pages/HealthCheck` guards stale dispatches with an `isActive` flag.
- **F1 pieces reused:** `Pagination` (`components/Pagination`, keeps other params, writes
  `offset`, past-the-end handled by `pageOffsets`), `EntityLink` + `entityPath`,
  `StencilHeading`, `DeckPanel`, `CageNumber`, `StatusLamp` (`busy`), `Readout`,
  `.visually-hidden`, `.stencil-label`. `ENTITY_KINDS` (`constants/index.ts`) holds
  `listPath`, `navLabel`, `isCommissioned`; `BaySign` already tests the link branch.
- **Mirage** (`src/__mocks__/endpoints.ts`, 369 lines): list handlers are
  `paginate(items, request)` with no `q` or filters. `searchList` (`__mocks__/search.ts`)
  and the per-kind `searchKinds.columns` table in `endpoints.ts` already encode `q`
  matching (catalog-search Q9: "until F2, the mock list routes ignore `q`"). Appearances
  are on the detail mocks: `findWorkMobileSuitsMock`, and character/organization detail
  `appearances`.
- **Fixtures mirror `backend/scripts/seed_dev.py`**: 4 suits, 2 characters, 3 orgs, 5
  works, 3 designers, **1 continuity** (Universal Century).
- **`@tanstack/react-table` 9.3.1**: MIT, peer `react >=18`, released 2026-10-12 (past
  pnpm's minimum release age).
- **Tests:** `renderWithProviders({initialEntries})` with `makeMirageServer({environment:
  'test', overrides})`; `setupTests.ts` restores spies and clears storage after each test.
- **Tooling:** moon is not on PATH; run `pnpm` scripts in `frontend/`.
  `react/only-export-components` warns when a `.tsx` exports a non-component.
- **Standards that bind this:** REACT-1/2, REACT-6, REACT-8, REACT-9, REACT-11 (`maxLength`
  on `q`), REACT-12–18, REACT-19, REACT-20 (app-wide hooks in `store/hooks.ts`),
  REACT-21/22 (debounce timer cleanup), REACT-24/25, REACT-28; CSS-1/4/10/14/16/17/18;
  TEST-2, TEST-15–18, TEST-20, TEST-23.

## Decisions (grilled 2026-11-23)

- **Q1. One slice per kind, built from a shared factory.** Slices `mobile-suits`,
  `characters`, `organizations`, `works`, `mechanical-designers` (REACT-12 three files
  each) plus `continuities`. Each `list` field comes from
  `createListFieldReducer({ requestType, setType, errorType })` in
  `store/catalogList.ts`, which also exports `ListState<Card>` (`{ items, meta, search,
  requestInProgress, errorMessage }`) and `fetchCatalogList` (the shared REQUEST →
  safeFetch → SET/ERROR body). Each slice's `actions.ts` exports a thin
  `fetchMobileSuits({ dispatch, search })` etc. Action types per kind:
  `REQUEST_MOBILE_SUITS`, `SET_MOBILE_SUITS`, `SET_MOBILE_SUITS_ERROR`, … F3/F4 add
  `detailsBySlug` per slice.
- **Q2. Five pages, shared roster parts.** `pages/MobileSuitList`, `CharacterList`,
  `OrganizationList`, `WorkList`, `DesignerList` own their columns and filter set; they
  share `components/FilterBar`, `components/RosterTable`, `components/CatalogRoster` (the
  frame: heading, `FilterBar` slot, status, error, empty state, table, `Pagination`) and a
  `useCatalogList` hook in `store/hooks.ts`.
- **Q3. Work filter: `?work=` honoured now, typeahead later.** F2 sends `work` to the API
  and shows it in `FilterBar` as a removable chip. A new PR after F2 in `frontend.md`,
  **F2b** `feat(frontend): pick a work in the filter bar`, adds an accessible combobox over
  `/api/works?q=` in that slot.
- **Q4. Rows link with `EntityLink` now.** Until F3/F4 land, those links reach the
  "Cage empty" page.
- **Q5. Fixtures stay a mirror of the seed.** Filter and paging tests pass `limit` in the
  URL or use Mirage `overrides`; stories do the same. No new seed rows.
- **Q6. `q` is live and debounced.** The input's draft is `useState` (REACT-19); the URL
  updates after a pause. *Default:* 300 ms, no minimum length, a blank `q` is removed
  from the URL, and the draft resyncs from the URL when it changes from outside (back,
  forward, a chip). Selects (continuity, unit type, work type) apply on change.
- **Q7. History: push once, then replace.** The first debounced change of a typing run
  pushes; later ones in the run `replace`. A run ends on blur or on any other URL change.
  Filters, chips and `Pagination` always push.
- **Q8. Page size: the API default.** No `limit` is sent unless the URL has one;
  `Pagination` uses `meta.limit`.
- **Q9. The work chip's title comes from the works slice.** F2 adds `detailsBySlug` and
  `fetchWork` (`REQUEST_WORK`, `SET_WORK`, `SET_WORK_ERROR`) to `works`. The chip shows
  the title, the slug while loading, and "Unknown work" on a 404. When the API answers
  with a different current slug, the page replaces `?work=` with it (filters match
  current slugs only).
- **Q10. Rosters are semantic tables rendered with `@tanstack/react-table`**
  (`getCoreRowModel` only), with a `<caption>` and per-kind columns: suits — cage number,
  model number, name, unit type, continuity; works — title, type, dates, continuity;
  personnel and designers — name, Japanese name; organizations — name, parent. **No
  sorting** (the API has no sort param and pages server-side); `frontend.md` gains a
  follow-up for server-side sort (backend `sort` param + sortable headers).

Carried over from the first draft (not contested):

- **D1. The URL is the source of truth for list state.** Pages read `q`, filters and
  `offset` (and `limit`) from `useSearchParams`; the slice stores the last page and the
  `search` string it was fetched for. Params are passed through; the API's 422 is shown
  as the error. A helper `listSearch({ searchParams, keys })` (`utils/listSearch.ts`)
  builds the API query string from the allowed keys, sorted, so equal states compare equal.
- **D2. Fetch in `useCatalogList`'s effect keyed on that search string**, with
  `HealthCheck`'s `isActive` guard so a slow older response never lands after a newer one.
- **D3. Changing `q` or a filter drops `offset`** (`withSearchParam` in
  `utils/listSearch.ts`); `Pagination` keeps everything else.
- **D4. Enum labels** `UNIT_TYPE_LABELS` and `WORK_TYPE_LABELS` live in
  `constants/index.ts`, typed `Record<UnitType, string>` / `Record<WorkType, string>`.
- **D5. States:** loading shows `StatusLamp status="busy"` in a `role="status"` region;
  empty shows a `DeckPanel` "No units match these filters" with a clear-filters link;
  errors show `role="alert"` with the API's detail (or a fallback).
- **D6. Continuities load once**: the continuity select dispatches
  `fetchContinuities` when the slice is empty and idle, and lists every continuity.
- **D7. Commission all five bay signs** (`isCommissioned: true` in `ENTITY_KINDS`) and
  replace Home's "under construction" copy with a bay directory built from
  `ENTITY_KINDS`, keeping the health check link.
- **D8. Mirage filters like the API** (`endpoints.ts`): `q` via the existing
  `searchKinds` columns and `searchList`; `continuity` and `unit_type`/`work_type` by exact
  match on the card; `work` by the work's appearance lists (current slug only); a bad
  enum or over-long `q` returns the API's 422 body, as `searchCatalog` does.

## Steps (one commit each)

1. `docs(docs): plan the catalog browser` — save this plan to
   `docs/plans/catalog-browser.md`; amend `frontend.md`: F2 entry (TanStack rosters,
   `?work=` chip, no sort, links to the plan), new **F2b** entry (work typeahead), a
   Follow-ups line for server-side sort, and the Data layer paragraph (mock list routes
   now apply `q`; fixtures stay a mirror of the seed).
2. `feat(frontend): filter the mock list routes like the API` — D8 in `endpoints.ts`, with
   tests in `endpoints.test.ts` for each filter, `q` ordering, an unknown slug (empty
   page) and the 422s.
3. `feat(frontend): add the catalog list store slices` — `store/catalogList.ts`, the six
   slices, action types, `AppState` registration, `works.detailsBySlug` + `fetchWork`
   (Q9), reducer and action tests (through Mirage).
4. `feat(frontend): add the roster table` — `pnpm add @tanstack/react-table`;
   `components/RosterTable` (generic over the row type, takes `columns`, `rows`,
   `caption`, `getRowId` from the slug, REACT-8), styles with a phone stacked layout,
   story and test.
5. `feat(frontend): add the filter bar` — `utils/listSearch.ts` (D1, D3) with tests;
   `components/FilterBar`: debounced search (Q6, Q7), select filters, removable chips,
   "Clear filters"; story and tests with fake timers.
6. `feat(frontend): add the mobile suit roster` — `useCatalogList` (D2),
   `components/CatalogRoster` (D5), `pages/MobileSuitList` (continuity, unit type, work
   chip, `q`), D4 labels, the `/mobile-suits` route, page test and story. This page
   proves the shared parts before they are copied.
7. `feat(frontend): add the personnel, faction, operation and designer rosters` — the
   other four pages and routes, tests and stories, including the work chip's old-slug
   replacement (Q9).
8. `feat(frontend): commission the catalog bays` — D7: `ENTITY_KINDS` flags, Home bay
   directory, updated `Root`/`Home` tests and stories.
9. `docs(docs): record the catalog browser as built` — only if there are departures.

## Risks to check during implementation

- **Generic factory vs the `AppAction` union.** A field reducer built from type constants
  must narrow `action.payload` per kind; if TypeScript can't narrow through generics, the
  factory takes a `selectPayload` function rather than casting. No `as` on payloads.
- **Stale responses.** Typing fast fires several requests; the `isActive` guard plus the
  stored `search` must leave the newest page shown. Test with a delayed Mirage response.
- **Debounce vs back/forward.** Resyncing the draft from the URL must not re-trigger a push,
  and a pending timer must be cleared on unmount and on outside URL changes (REACT-22).
  Test: type, wait, Back → the input shows the old `q`.
- **Push-then-replace bookkeeping.** "Run" state lives in a ref; verify Back after a run
  lands on the pre-search list, not a partial `q`.
- **Offset drop.** A filter change on page 3 must request offset 0; Pagination must keep
  `q` and filters (already tested in F1, re-check through a page).
- **Search string equality.** Param order in the URL must not cause refetches or a
  mismatch with the stored `search` (sorted keys in `listSearch`).
- **Unknown params** (`?foo=1`) must not reach the API; only each page's allowed keys go.
- **Work chip old slug.** Replacing `?work=` must use `replace`, keep other params, and
  not loop when the slug is already current; a 404 chip must still be removable.
- **TanStack in tests and the bundle.** Check `pnpm build` size growth is modest and that
  headless rendering keeps the `<table>/<caption>/<th scope>` semantics.
- **`react/only-export-components`.** Column definitions with JSX cells stay
  module-local in each page's `index.tsx`, or in a page-local `.tsx` that exports only
  components; helpers live in `.ts`.
- **`endpoints.ts` size.** It grows toward 500 lines; if it passes that, move the list
  filter table into `__mocks__/listFilters.ts`.
- **Mirage `work` filter fidelity.** Suits use the work's appearance list; characters and
  organizations use their detail mocks' `appearances`. Old work slugs must give an empty
  page (current slugs only), not the redirected work's rows.
- **Shell and Home test churn.** Commissioning flips every bay sign to a link; `Root`,
  `BaySign` and `Home` tests and stories that assert "Offline" change in step 8.
- **Contrast and phone layout** of the stacked table rows and chips (CSS-17 `phone`).
- **Loading region chatter.** `role="status"` must not announce on every keystroke's
  refetch more than once; keep its text stable.

## Verification

Run in `frontend/` (moon not on PATH):

- `pnpm format:check && pnpm lint && pnpm typecheck` — clean, no warnings.
- `pnpm test` — all pass; `pnpm test:cov` — every new file covered, uncovered lines tested
  or removed.
- `pnpm build` — succeeds; no Mirage in the bundle; note the bundle size change from
  TanStack.
- `pnpm build-storybook` — succeeds with the new stories.
- `pnpm dlx markdownlint-cli2 docs/plans/catalog-browser.md docs/plans/frontend.md` from
  the repo root.
- In a browser (Storybook; and the app with `MOCK_API=true` if the stack can be started):
  each bay sign opens its roster; typing in search filters live and Back returns to the
  unfiltered list; continuity and unit type selects narrow suits; `?work=` shows a
  titled chip and removing it widens the list; `?limit=2` shows Pagination and paging
  keeps filters; reload keeps state; a bad `?unit_type=x` shows the API error;
  keyboard-only use; both shifts; phone width.

## As built (2026-11-23)

Where the implementation differs from the steps above:

- **Two extra commits.** `refactor(frontend): share the mock routes' query validation` comes
  before step 2: it pulls the page and `q` checks out of `paginate` and `searchCatalog`, so a
  list route reports every bad param in one 422, as FastAPI does. `build(deps): add
  @tanstack/react-table` comes before step 4, since `COMMIT_CONVENTIONS.md` gives dependency
  additions the `deps` scope.
- **No `createListFieldReducer` (Q1).** TypeScript can't narrow the `AppAction` union through
  a generic action type without casting payloads, and REACT-14 wants field reducers that
  `switch` on `action.type`. Each slice's `list` field switches on its own three types and
  calls shared, typed transitions in `store/catalogList.ts` (`requestList`, `setList`,
  `setListError`, and `requestDetail`/`setDetail`/`setDetailError` for works). `setList` and
  `setListError` drop a response whose `search` isn't the latest request's, so the slice
  itself guards against stale pages, on top of `useCatalogList`'s unmount guard (D2).
- **`fetchCatalogList` takes callbacks** (`onRequest`, `onSuccess`, `onError`), so each
  slice's `fetch<Kind>` dispatches its own actions. A 422's errors show as
  `<param>: <msg>`, joined by semicolons (`catalogErrorMessage`).
- **The enum labels (D4) land in step 2**, not step 6: the mock 422s take their allowed
  values from the labels' keys.
- **Mock filter helpers live in `__mocks__/listFilters.ts`** from the start: with them,
  `endpoints.ts` passed 500 lines (a named risk). `listHandler` stays in `endpoints.ts`.
- **The work chip is built in step 6**, not step 7: the suit roster already uses `?work=`.
  `useWorkFilterChips` and `useContinuities` sit beside `useCatalogList` in `store/hooks.ts`.
- **Blur writes a pending search (Q6, Q7).** Leaving the box, by Tab or by picking a select,
  writes the draft at once and ends the run; Enter also writes it at once. Only a URL change
  made while the box keeps focus (Back by keyboard, a link) drops the pending draft.
- **`SEARCH_DEBOUNCE_MS`** (300) is in `constants/index.ts`.
- **`isCommissioned` stays in `ENTITY_KINDS`**, now `true` for all five kinds. `BaySign`
  keeps its offline branch for a future kind; its comment no longer names F3/F4.
- **Organization rows link their parent** with `EntityLink`, and Japanese names render with
  `lang="ja"`. The suit roster's cage number is the row's place in the whole list
  (`offset + index + 1`) on deck 01.
- **Bundle:** the app's JS grows from 326 kB (103 kB gzip) on `main` to 375 kB (117 kB gzip),
  for TanStack Table, the store slices and five pages. `pnpm build-storybook` warns about
  chunks over 500 kB, as it does on `main`.
- **Browser check** ran in Storybook, not in the app with `MOCK_API=true`. Checked: the suit
  roster's columns and links, live search narrowing to one suit, the work chip titling the
  old slug `msg`, paging with a filter kept (`1–2 of 3`, then `3–3 of 3` with cage 03), and
  the Works roster; no console errors. Not checked in a browser: the phone layout (the
  window would not resize; the unit test checks each cell's `data-label`), the Day shift,
  and keyboard-only use.
- **Review fixes.** The comprehensive review before the PR changed these:
  - The list state's `search` (the API query string) is now `query`, in the slices,
    payloads and `fetchCatalogList`. D1 and D2 above still say `search`.
  - `fetchCatalogList` is generic over the generated `<Kind>ListResponse`, and it and
    `fetchWork` store the page outside the `try`, so a store bug is no longer shown as a
    failed request.
  - The continuities slice has `continuitiesLoaded`, so an empty answer is not
    refetched in a loop (D6).
  - Swapping an old `?work=` slug keeps `offset` (a plain set, not `withSearchParam`).
  - Rosters mark their naming column with `meta: { isRowHeader: true }`, typed through
    the roster's `tableFeatures({ columnMeta })`, in place of a `rowHeaderColumnID` prop.
  - `useDebouncedSearch` moved to `components/FilterBar/utils/hooks.ts`. The select
    options are `UNIT_TYPE_OPTIONS`, `WORK_TYPE_OPTIONS` and `useContinuityOptions`. The
    mock enum filters come from `enumFilter`. Page tests read rows with
    `findRowHeaderTexts` from `utils/testing`.
  - The phone layout was checked headless at 360 px and 600 px. At 360 px the cage plate
    ran past the table's edge, so a value too wide for its row now wraps under its label.
