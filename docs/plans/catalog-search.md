# Plan: BE-1 — search across the catalog

> **Agreed** 2026-11-23: Q1 to Q9 were settled by grilling.

Branch `feat/search-across-the-catalog` (created from `main` at `966e13b`). PR title:
`feat(backend): search across the catalog`. It expands the **BE-1** item in
[`docs/plans/frontend.md` § PRs](frontend.md#prs-in-order). It builds on PR B (#29), PR C
(#30) and PR D (#32), including the departures in their **As built** sections.

## Context

F5 (the deck search terminal: a `Ctrl/⌘+K` overlay and a `/search` page) needs one call that
searches every entity kind. Today `q` exists on four list routes only, and
`catalog-read-api.md` D8.6 deferred a cross-entity `/api/search` "until the frontend needs one".
It needs one now. BE-1 also adds `q` to `/api/works`, and decides whether `q` should match
display names as well as slugs.

**Facts checked in the repo:**

- **D8 matching** lives in `BaseFacade` (`backend/models/base/facade.py`): `normalize_search`
  (lowercase, keep `a-z0-9`, blank → `None`), `_search_filter(columns, needle)` (normalized
  substring), and `_prefix_rank(columns, needle)` (`CASE`, prefix first).
- **`get_page` with `q`** exists on `MobileSuitFacade` (slug and `model_number`),
  `CharacterFacade`, `OrganizationFacade` and `MechanicalDesignerFacade` (slug only). Each
  returns `Page[Card]` (`models/base/page.py`) in 2 statements: the page and a `count`.
- **`WorkFacade.get_page`** (`models/work/facade.py:39`) has no `q`. It orders by
  `start_date NULLS LAST, title, id`.
- **`/api/works`** (`api/routes/works.py`) still uses hand-written `try/except`, not
  `run_read` (`api/routes/handlers/reads.py`), which every PR C route uses.
- **Display names cannot match through D8 normalization in Japanese.** `name_ja` and
  `title_ja` normalize to the empty string, and a Japanese `q` normalizes to `None` (no
  filter). English `name` / `title` normalize to almost exactly the slug, because D2 builds
  each slug from the title.
- **`work_short_names`** (`models/work_short_name/db.py`) holds wiki series tags such as `MSG`
  and `08th MS Team`. It has a factory, but no facade, and the seed writes none.
- **Constants:** `MAX_SEARCH_LENGTH = 100` and `DEFAULT_PAGE_SIZE` / `MAX_PAGE_SIZE` are in
  `constants/pagination.py`.
- **Envelopes:** `BaseResponseModel` camel-cases only its own fields, so envelope fields are
  single words (`data`, `meta`). `PageMeta` is a plain model (`api/models/pagination.py`).
- **Operation IDs** are route function names (`api/app/main.py`), and `TestOperationIds`
  (`api/_tests/app/test_main.py`) checks them.
- **Contract:** `pnpm run api:generate` (in `frontend/`) regenerates `openapi.json` and
  `api.ts`. MONO-15 aliases live in `frontend/src/api/index.ts`.
- **Mirage:** `frontend/src/__mocks__/endpoints.test.ts` asserts that `endpointConfigs`
  registers **every** GET path in the contract. So `/api/search` needs a Mirage handler in the
  contract commit. Mirage applies no `q` anywhere yet: there is no TypeScript
  `normalizeSearch`.

## Decisions (grilled 2026-11-23)

- **Q1 — `meta` carries per-kind totals:**
  `{limit, totals: {mobile_suits, characters, organizations, mechanical_designers, works}}`.
  F5 can link "see all 12" to `/mobile-suits?q=…`. Each total is the kind's `get_page`
  count.
- **Q2 — A search facade owns the fan-out.**
  `models/search/facade.py: CatalogSearchFacade(BaseFacade).search(*, q, limit)` calls the
  five facades' `get_page(q=q, limit=limit, offset=0)` on its own session. The route stays
  thin.
- **Q3 — `limit` is per kind, default 5, max 20.** `SEARCH_DEFAULT_LIMIT` and
  `SEARCH_MAX_LIMIT` go in `constants/pagination.py`. A value outside `1..20` is 422.
- **Q4 — A blank `q` is no filter (D8.4).** A `q` that is blank after normalization returns
  the first N of each kind in its list order, with real totals.
- **Q5 — A missing `q` is the same as a blank one.** `q` is optional, with
  `max_length=MAX_SEARCH_LENGTH`.
- **Q6 — Every `q` also matches the English display name.** Suits match slug, name and
  model number. Characters, organizations and designers match slug and name. Works match
  slug and title. This changes the four existing list routes too, so D8.2 is amended, and
  the `q` descriptions in the routes say "names".
- **Q7 — Japanese search is deferred.** `name_ja` and `title_ja` normalize to `''`, so they
  can't match cheaply under D8.
  [#34](https://github.com/saurookadook/msg-docking-bay/issues/34) records the findings: why
  it fails, the escaped-`ILIKE` option and the files it touches.
- **Q8 — Works don't match `work_short_names` yet.** There is no facade and no seeded data.
  This is a follow-up for when 3a ingests the series tags. It's listed in `frontend.md`'s
  Follow-ups.
- **Q9 — Mirage gets real matching for `/api/search` only.** It ports `normalizeSearch` and
  the prefix rank to TypeScript, matching the same columns as Q6. The list routes' Mirage
  `q` stays with F2, which reuses the helper.
- **Defaults (not grilled):**
  - The entities are `CatalogSearchResultsEntity` (the five card lists) and
    `CatalogSearchMeta`/`CatalogSearchTotals` (plain models, `snake_case`), with the envelope
    `CatalogSearchResponse {data, meta}` in `api/models/search.py`.
  - The route is `GET /api/search`, function `read_search`, in `api/routes/search.py`
    (`search_router`).
  - Within a group, prefix matches on any matched column rank first, then the kind's list
    order. Works keep `start_date NULLS LAST, title, id` behind the rank.
  - The groups hold the existing card entities, so no new card shapes are added.

## Steps (one commit each)

1. **Plan docs** → `docs(docs): plan the catalog search`
   - Open the Japanese search issue (Q7): #34.
   - Save this plan as `docs/plans/catalog-search.md`.
   - Amend `catalog-read-api.md`: D8.2 (names are now matched, Q6), D8.6 (the
     cross-entity search is now `/api/search`), and the Routes table.
   - Amend `frontend.md`: the BE-1 item's final shape (Q1, Q3), and the Japanese search
     follow-up.
2. **Names in `q`** → `feat(backend): match display names in catalog search`
   - Add `name` to the `columns` tuple in the four `get_page` methods.
   - Update the four routes' `q` descriptions.
   - Tests: a name-only match per facade, for example a row whose slug has a collision
     suffix or a symbol fold.
3. **Works `q`** → `feat(backend): search works by slug and title`
   - `WorkFacade.get_page(q=…)` matches slug and title, with the prefix rank in front of the
     existing order.
   - `/api/works` gains `q` and moves to `run_read`.
   - Tests: normalized match, prefix first, blank `q` is no filter, and a 101-character `q`
     is 422.
4. **Search facade** → `feat(backend): add a catalog search facade`
   - `CatalogSearchFacade.search` and the result entities.
   - Tests:
     - 10 statements, whether `q` is given or blank;
     - per-kind `limit` with real totals;
     - blank `q` gives the unfiltered top N;
     - matches across kinds.
5. **Route** → `feat(backend): add the catalog search route`
   - `api/routes/search.py`, `api/models/search.py` and the constants.
   - Include the router in `main.py`, in alphabetical order.
   - Route tests: a happy path, blank and missing `q`, `limit` 0, 20 and 21, a 101-character
     `q`, and a fixed 500. Also `TestOperationIds`.
6. **Contract** → `build(frontend): regenerate the API contract for catalog search`
   - `pnpm run api:generate`, and MONO-15 aliases.
   - Mirage: `normalizeSearch` and the prefix rank (Q9), the `/api/search` handler over the
     fixtures, and the endpoint-list test entry.
   - Tests: `rx782`, a blank `q`, the per-kind limit and totals, and a `limit` of 21 is 422.

## Risks to check during implementation

- **Statement count.** Five kinds × (page + count) = 10 statements. Pin it with
  `count_statements` (PYTEST-24).
- **Name matching widens existing results (step 2).** Check that the existing `q` tests
  still pass. A name match could reorder prefix ranks, for example `zaku` against
  "Act Zaku" (its name doesn't start with `zaku`, so it stays second).
- **Session sharing.** `CatalogSearchFacade` must pass its `db_session` to every child
  facade, or the route's session dependency is bypassed.
- **Mirage drift.** The TypeScript normalization must strip exactly what
  `[^a-z0-9]` strips after lowercasing. Test `RX 78-2` and `∀ Gundam`.
- **The Japanese `q` now gives the unfiltered top N (Q4 + Q7).** That's expected; record it
  in the issue.
- **Nested `data` field names.** The entity inside `data` must keep `snake_case`
  (`mobile_suits`). Check that `BaseResponseModel`'s alias generator doesn't reach it.
- **Defaulted lists come out optional** in `api.ts`. Check each group is required.
- **Operation ID uniqueness.** `read_search` must not clash with an existing name.
- **Works ordering.** The prefix rank goes in front of `start_date NULLS LAST`. A blank `q`
  must leave the order unchanged.
- **`/api/works` moving to `run_read`.** Keep its 500 detail (`"Error fetching works"`) so the
  existing tests still pass.

## Verification

- **Backend** (in `backend/`): `scripts/backend-test.sh`; `uv run ruff format --check .`,
  `uv run ruff check .` and `uv run pyright`.
- **Frontend:** `moon run frontend:typecheck frontend:lint frontend:format frontend:test`.
- **Contract:** a second `pnpm run api:generate` leaves no diff.
- **Through the seeded API:** `/api/search?q=rx782`, `?q=amuro`, `?q=zeon`, `?q=okawara`,
  `?q=%20--%20` (blank), and a 101-character `q` (422). Also `/api/works?q=…`.

## As built (2026-11-23)

Where the implementation differs from the steps above:

- **A refactor commit before step 3.** `works.py` was the last router mapping its 404s and
  500s by hand. All three works routes moved to `run_read` in
  `refactor(backend): map the works routes' errors with run_read`, with their details
  unchanged. Step 3 then added only `q`.
- **The facade's return type.** `CatalogSearchFacade.search` returns `CatalogSearch`
  (`results` and `totals`), as `get_page` returns `Page`. `CatalogSearch`,
  `CatalogSearchResultsEntity` and `CatalogSearchTotals` live in `models/search/entity.py`.
  Only `CatalogSearchMeta` and `CatalogSearchResponse` are in `api/models/search.py`.
- **The route's 500 detail** is `"Error searching the catalog"`.
- **Mirage.**
  - The matching is in `frontend/src/__mocks__/search.ts`: `normalizeSearch`, and
    `searchList`, which filters and ranks one list.
  - The handler is `searchCatalog` in `endpoints.ts`, exported for its tests.
  - `MAX_SEARCH_LENGTH`, `SEARCH_DEFAULT_LIMIT` and `SEARCH_MAX_LIMIT` were added to
    `frontend/src/constants`, as mirrors of the backend's.
  - The `q` length check counts code points, as FastAPI does.
- **Seeded API check.** Through the proxy: `rx782`, `amuro`, `zeon` and `okawara` find
  their rows. A blank `q` and `大河原` both list the first rows, with totals of 2, 3, 4,
  3 and 5, the same as Mirage's. `limit=21` and a 101-character `q` are 422.
- **Review fixes (2026-11-23).** The comprehensive review's chosen fixes landed as their own
  commits:
  - `BaseFacade._search_clauses(q, columns)` returns a `SearchClauses` filter and rank, or
    `None` for a blank `q`. The five list facades call it instead of copying the block.
  - `read_works_list` takes its filters, `q` and paging keyword-only (PY-19).
  - The search facade's count test reads one, then three, matches of every kind, with
    continuities and parent organizations loaded (PYTEST-24).
  - The `/api/search` docstring says why the path is singular (FAPI-5), and the contract
    was regenerated for it.
  - Mirage: `searchList` takes named arguments (TS-19) and `Nullable` (TS-12 and TS-25).
    `searchCatalog` derives its results and totals from one typed table of kinds. A test
    in `src/constants/index.test.ts` checks the mirrored page and search limits against
    `openapi.json` (MONO-16).
  - The Routes table in `catalog-read-api.md` now lists the name-aware `q`, works' `q` and
    `/api/search`.
- **Query plans (PG-21).** `scripts/explain_search.py` runs the search as the route does
  and logs `EXPLAIN (ANALYZE, BUFFERS)` for each of its ten statements, in a read-only
  transaction that it rolls back. The same command works on any configured database:
  - local stack: `docker compose run --rm --build backend python -m scripts.explain_search`;
  - Railway: `railway ssh -s msg-docking-bay-backend -- python -m scripts.explain_search`,
    once this branch is deployed.

  On the seeded dev database (at most five rows a table), every statement is a sequential
  scan that finishes in under 0.2 ms, which is expected at that size. D8 keeps "no index"
  until the suit count grows. After 3a loads the dump (about 3,200 suits), run the Railway
  command and record the plans here. Add the trigram index from PG-11 if a scan shows up
  as slow.
