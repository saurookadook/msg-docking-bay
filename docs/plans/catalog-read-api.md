# Plan: Catalog read API

> **Agreed** (2026-11-13 to 2026-11-15): D1 to D8 were reviewed one at a time. D7 follows
> `aoam-property-plan`'s Mirage pattern and adds a mock mode. No code until asked.

## PRs

- [x] PR A: `build(frontend): generate API types from the backend's OpenAPI schema`
- [x] Mock mode PR: `feat(frontend): add a mock API mode to the dev server`
- [x] PR B: `feat(backend): serve mobile suits, works and continuities`
- [x] PR C: `feat(backend): serve characters, organizations and designers`
- [x] PR D: `feat(backend): serve suit parts on spec sheets`

## Context

The frontend has nothing to read. The backend serves only `GET /api/health-check` and `GET /api`, and
the frontend's API types are written by hand (`frontend/src/types/index.ts`). Phase 1 built the catalog
tables (#16, #22, #23), but no entity, facade or route reads them yet.
[`data-ingestion.md`](data-ingestion.md) doesn't plan any catalog routes: Phase 3a adds entities and
facades for its loader, and Phase 5 adds only attribution.

Phase 3a is also slowed by data. The 2025 dump can't be downloaded, and the 2022 copy is good for
development but too old to be the real seed (see
[`ingestion-spike.md`](../research/notes/ingestion-spike.md#dumps-and-delta-sync)).

**This plan adds the read side as its own track, so frontend work can start now.** Nothing in it needs
a dump. Tests build rows with the backend's factories, and the frontend develops against typed Mirage
mocks until a real load exists.

**Outcome:** five PRs.

- **PR A:** the generated API contract (MONO-13 to MONO-15), proven on the health check.
- **Mock mode PR:** the running app on Mirage fixtures (D7), after PR A. It was split out of PR A on
  2026-11-17 because it's a `feat` and PR B doesn't need it.
- **PR B:** read routes for continuities, works and mobile suits.
- **PR C:** read routes for characters, organizations and mechanical designers.
- **PR D:** suit parts (armaments, equipment, materials and powerplants) on each spec sheet. It
  doesn't depend on PR C, so it can land before or after it.

Frontend pages are a separate plan, written once PR B's response shapes are agreed.

## Design decisions

### D1. Where the generated contract lives (**Agreed** 2026-11-13: Option 1)

MONO-13 puts the contract in `shared/`, a pnpm workspace that `frontend` depends on. But `frontend/` is
the Node root here (its own `package.json`, lockfile and tooling), the repo root has no Node files, and
`shared/` holds only a `CLAUDE.md`.

- **Option 1 (chosen): generate into `frontend/` for now.**
  - The export script writes `frontend/src/api/generated/openapi.json`.
  - `openapi-typescript` writes `frontend/src/api/generated/api.ts`.
  - MONO-15 aliases go in `frontend/src/api/index.ts`.
  - `shared/` stays empty until there is framework-free code that a second consumer needs.
  - This keeps one pnpm project and one lockfile. Like the frontend-root decision, it diverges from
    MONO-13's paths, so update `monorepo.md` or note the divergence when this lands.
- **Option 2: make `shared/` a real pnpm package now.**
  - This follows MONO-13 as written, but needs a workspace that spans `frontend/` and `shared/`. Today
    that means either root Node files (which were deliberately removed) or a workspace rooted in
    `frontend/` that reaches `../shared`.
  - Check that pnpm allows a workspace package outside the workspace root before choosing this.

### D2. Detail routes take slugs, which follow renames (**Agreed** 2026-11-13)

Every catalog table has a unique `slug`, so detail paths use it:
`GET /api/mobile-suits/{mobile_suit_slug}`. Frontend URLs then read well (`/mobile-suits/rx-78-2-gundam`),
and no slug-to-ID lookup is needed.

- **Slugs are a steadier public key than IDs.** Reseeding from a fresh dump gives every row a new
  UUIDv7. A slug derived from the page title comes out the same.
- FAPI-10 says path IDs SHOULD be `UUID`, so a malformed ID is rejected by validation. The slug
  parameter gets the same protection from `Path(pattern=SLUG_PATTERN)`, which reuses the constant in
  `models/mixins/checks.py` that the database's `slug_format` CHECK already uses. An unknown slug is a
  404 (FAPI-13).

**Slugs are part of the public contract, so these rules bind the Phase 3a loader:**

- **A slug follows its page title.** When a page is renamed upstream, the row gets the new slug, and
  the old one goes into a redirect table, so old links keep working.
  - There is one table per entity with a detail route: `mobile_suit_slug_redirects`,
    `work_slug_redirects`, `character_slug_redirects`, `organization_slug_redirects` and
    `mechanical_designer_slug_redirects`. Each has `old_slug` (primary key, `slug_format`) and a
    foreign key to its entity (`ON DELETE CASCADE`). A single polymorphic table would have no foreign
    key.
  - A current slug always beats a redirect. If a row takes a slug that is listed as some other row's
    old slug, the loader deletes that redirect row in the same transaction. No constraint can check
    this across the two tables, so a loader test covers it.
  - PR B adds the suit and work redirect tables and PR C adds the people ones, because the routes are
    the first to read them. The 3a loader writes them.
- **Resolving an old slug.** The facade's `get_one_by_slug` checks the redirect table when the slug
  misses. The route returns 200 with the entity, whose `slug` field holds the current slug, and the
  frontend replaces the URL when the two differ. There is no HTTP redirect: the generated client
  stays simple, and either way the frontend has to notice the change.
- **Collisions.** An existing row keeps its slug, and a new or renamed row whose slug is already
  taken gets `-<fandom_page_id>` appended. The page ID never changes on Fandom, so the result doesn't
  depend on load order. A work with no Fandom page uses its Wikidata QID, lowercased (`-q123`).
- **Non-ASCII titles.** Titles are ASCII-folded, with a small hand-kept symbol map for characters
  that folding would drop (for example `∀` → `turn-a`, as in *SYSTEM-∀99 ∀ Gundam*). A title that
  still contains an unmapped character goes to 3a's review list, and no slug is guessed.

**Renames are matched by page ID (agreed 2026-11-13).** `mobile_suits` already stores
`fandom_page_id`, but `works`, `characters`, `organizations` and `mechanical_designers` store only
`fandom_page_title`. On those four tables, a rename would look like a new page to the loader.

- Each of the four gets `fandom_page_id int UNIQUE`, nullable, with the `positive` CHECK, as
  `mobile_suits` has. It's nullable because a work can come from Wikidata alone.
- `fandom_page_title` stays and stays unique. It's the display and lookup value, and it is what
  changes on a rename.
- The 3a loader upserts on `fandom_page_id` and updates the title and slug in place.
- The migrations go with the redirect tables: `works` in PR B, the other three in PR C.
- *Amended 2026-11-22 (PR D, Q5):* the four part tables (`armaments`, `equipment`, `materials`
  and `powerplants`) get the same `fandom_page_id` in PR D, so 3a matches part renames from
  the start. Their redirect tables wait for part detail routes. A part whose title is a
  redirect to a list section has no page of its own, so its title and page ID stay null.

### D3. Lists use limit/offset pagination with a total (**Agreed** 2026-11-13)

RDB-23 requires a capped page size. The catalog is a few thousand rows (3,191 mobile weapons in the
2022 dump) and changes only when an ingest runs, so offset pagination's weak points (slow deep offsets,
rows moving between pages) barely apply. In exchange, the frontend gets page numbers, jump-to-page and
infinite scroll. Keyset pagination would allow only next and previous.

- **Parameters:** `limit` and `offset`, not `page` and `page_size`. `limit` defaults to 50, with a cap
  of 100 (`MAX_PAGE_SIZE` in a constants module). `offset` defaults to 0. The frontend works out the
  page as `offset / limit`.
- **Order:** fixed per resource, ending in `id` (RDB-22). Suits sort by `name, id`; works by
  `start_date NULLS LAST, title, id`. A `sort` parameter waits until a screen needs one, and then uses
  SQLA-21's allowlist.
- **Total:** a separate `SELECT count(*)` with the same filters. `count(*) OVER ()` on the page query
  would return no total once the offset goes past the end.
- **Envelope:** `{"data": [...], "meta": {"limit", "offset", "total"}}`. A page past the end returns
  `data: []` with the real total, not a 404.
  - Each resource gets its own envelope (`MobileSuitsListResponse`, with `meta: PageMeta`), as in
    FAPI-12's examples. A generic `ListResponse[T]` would put Pydantic's generated names
    (`ListResponse_MobileSuitCardEntity_`) into the contract.
- **Standards:** `meta` is new to FAPI-12. PR B adds a pagination paragraph to `fastapi.md`, using the
  standards' placeholder domain.

### D4. Entities and facades come from this track, and 3a adds writes (**Agreed** 2026-11-13)

`data-ingestion.md` says 3a adds the Pydantic entities and facades "with the loader as their first
caller". This track is likely to need them first, so the first caller is a route instead.

1. **PR B and PR C create the bases and the entities their routes read.**
   - The bases are `BaseEntityModel`, `TimestampsEntityMixin` (PYD-2) and `BaseFacade` (SQLA-16).
   - Per table: the full entity (PYD-3), the card and detail read models (PYD-4), and a facade with
     read methods only.
   - PR B covers continuity, work, work relation, mobile suit, mobile suit relation, mobile suit
     appearance, spec sheet and source. PR C covers character, organization, mechanical designer
     and their junctions.
2. **No write methods are stubbed ahead of time.** A write method arrives with its first caller.
   *Amended 2026-11-21:* PR B's dev seed script (D7) is that caller for the tables PR B reads, so
   PR B adds their `create_or_update`, with D5's no-change guard. 3a extends those methods for the
   loader, and adds them for tables PR B doesn't touch.
3. **Whoever needs a table first creates its entity.** Tables no route reads, such as 3a's review
   list, are 3a's to create.
4. **Upserts stay in facades, even in bulk.** If 3a loads in batches, it adds a batch upsert method to
   the facade, not SQL in `ingest/`.

**Sequencing with 3a.** Of 3a's three checkpoints, only the last (`load a Gundam Wiki dump`) touches
`backend/models/`. The dependency and parser checkpoints can run alongside PR B, and the loader
checkpoint starts from PR B's merged facades. If 3a reaches its loader first after all, the roles
swap: whichever comes second extends what's there and doesn't add a parallel set.

**After this review**, update the 3a section of `data-ingestion.md` to match (step 0).

### D5. What responses contain (**Agreed** 2026-11-13)

Responses use narrow read models (PYD-4). Each docstring says what it leaves out and why.

**Suit card** (lists): `slug`, `name`, `name_ja`, `model_number`, `unit_type`,
`continuity: {slug, name} | null`, `created_at` and `updated_at`. No spec sheets: loading them for 50
rows would cost an N+1 or a large join that nothing renders. Other resources' cards follow the same
pattern.

**Suit detail** (PR B), with its children loaded in a fixed number of queries (`selectinload`,
SQLA-22):

```txt
slug, name, name_ja, model_number, unit_type, continuity, created_at, updated_at
spec_sheets[]:  configuration, the ten SI columns, source, created_at, updated_at
relations[]:    relation_type, direction ("outgoing" | "incoming"), mobile_suit: <card>, source, created_at
appearances[]:  work: <work card>, first_episode, last_episode, is_debut, source, created_at
```

- **Units are in the field names** (`head_height_m`, PY-16). The frontend formats values, and the API
  sends no display strings.
- **Relations read from the viewed suit's side.** The detail returns every edge that touches the suit.
  `outgoing` means this suit is `<relation_type>` the other one; `incoming` means the other one is
  `<relation_type>` this suit. The frontend turns type and direction into wording.
- **Direct edges only.** The whole family tree (Phase 1's recursive query) becomes its own route,
  `GET /api/mobile-suits/{mobile_suit_slug}/family`, when a screen needs it. Large families would
  otherwise make every detail response heavy.
- **Parts wait for PR D.** Parts hang off spec sheets, so PR D nests `armaments[]`, `equipment[]`,
  `materials[]` and `powerplants[]` under each spec sheet. They need no `source` of their own,
  because their junctions take the spec sheet's.
  - *Amended 2026-11-22 (PR D, Q1 and Q2):* each item nests a `{slug, name}` ref of its part,
    next to the listing's own columns, as in `{armament: ref, mount, quantity_min, quantity_max,
    note, created_at}`. A named configuration with no rows of a kind takes the same source's
    base sheet list of that kind, and names it in `inherited_parts`. `inherited_fields` stays
    measurements-only. See [`suit-parts-read.md`](suit-parts-read.md).

**Timestamps are this app's row times.** `created_at` and `updated_at` say when this database created
or last changed the row. They say nothing about when upstream edited the page: `source.retrieved_at`
and `source.revision_id` (D6) cover that. Junction rows have only `created_at`. Every model's
docstring makes the distinction.

- **This binds the 3a loader:** an upsert must not touch `updated_at` unless a column actually
  changed. An upsert sets `updated_at` itself (`models/mixins/db.py`), so a re-load that writes every
  row would make every row look freshly updated. Use `ON CONFLICT ... DO UPDATE ... WHERE` with the
  row `IS DISTINCT FROM` the incoming values, and test it with a no-change re-load.

**Left out of every response:**

- `spec_sheets.raw_infobox`. It's bulky, and it holds copied wiki text, which the plan keeps out of
  anything served (share-alike).
- `id`. Slugs are the public key (D2), and the UUID changes on a reseed.

**Part notes (PR D, binds 3a).** The `note` columns on the part junctions are free text from the
infobox. They're served as stored, and 3a's parser caps their length, sending longer ones to the
review list. That keeps longer copied text out of the database in the first place.

### D6. Facts carry their source now (**Agreed** 2026-11-13)

`sources` holds one row per upstream page, updated in place on re-ingest, so `revision_id` and
`retrieved_at` describe the copy the catalog holds now. Spec sheets, relations, appearances and the
pilot, organization and designer links each cite one. Part junctions take their spec sheet's (D5).

Serving it now means the first public page that shows Gundam Wiki data can carry its CC BY-SA
attribution, and it costs no extra query: the facts' loading joins the source anyway.

- **Fields:** `kind`, `url`, `content_license`, `revision_id` and `retrieved_at`. `external_id` stays
  out: `url` already identifies the page, and a raw page ID or QID means nothing to a reader.
- **License name and URL come from the backend.** A constants map from each `ContentLicense` to its
  name and license URL, exposed as computed fields `license_name` and `license_url` (PYD-11).
  Otherwise the frontend would keep its own copy of the table and drift from the backend's.
- **A permalink to the exact revision:** a computed `revision_url`, built per `kind` through a
  registry dict (PY-35). It's `?oldid=<revision_id>` for Fandom and Wikipedia, and the revision link
  for Wikidata. It's null when `revision_id` is null. Share-alike attribution points at the version
  used, not the live page.
- **Inline on each fact, not deduplicated.** A suit page cites one to three pages, so repeating the
  source object costs a few hundred bytes. A top-level `sources` map would need a public source key
  (D5 drops `id`), and every frontend component would have to look facts up in it.
- **CC0 sources are returned too.** Wikidata doesn't require attribution, but uniform provenance
  keeps the contract simple. The frontend can show those sources more quietly.
- **Phase 5 shrinks to the site-wide part:** a footer and a license page, with "Gundam Wiki
  contributors" wording linking to page history, and the copyleft notice for derived text. The
  per-record attribution in its `expose source attribution` checkpoint moves to this track.

The source read model, the license map and the `revision_url` builder land in PR B, step 4, with
tests for each kind and for a null `revision_id`.

### D7. Frontend data before a real load comes from Mirage, driven by an endpoint table (**Agreed** 2026-11-13)

The frontend already mocks through Mirage. Today `frontend/src/__mocks__/mirageServer.ts` registers
`GET /health-check` by hand, and tests and stories share it (TEST-18). Hand-registering every catalog
route doesn't scale, so this follows the pattern in `aoam-property-plan`'s frontend, adapted to this
repo's standards.

**Kept from aoam-property-plan:**

- **One table of endpoint configs drives every route.** aoam's `endpointConfigs` list is read by its
  test server, its Storybook server and its Express mock data server, so a route is declared once.
- **One route-path builder** turns a config into a Mirage path. aoam keeps a single
  `buildRoutePath` after two diverging builders sent the same request to different fixtures under
  Storybook and vitest.
- **List, detail and sub-resource routes** are the three shapes, with detail fixtures looked up by
  the path parameter.
- **A capture script** fills fixtures from a running API, and refuses a non-200 response or a body
  that isn't JSON (aoam's `scripts/capture-fixtures.sh`).

**Changed to fit this repo:**

- **The table is keyed by the generated contract.** Each config names an OpenAPI path from the
  generated `paths` type, for example `'/api/mobile-suits/{mobile_suit_slug}'`. Its handler's return
  type is derived from that path's 200 response. A config for a route the API doesn't have, or a
  fixture of the wrong shape, fails typecheck (TEST-10, MONO-14). aoam's configs are untyped
  (`KeyedObject`, `any`). The route builder strips the leading `/api`, because `makeMirageServer`
  already sets that namespace, and turns `{mobile_suit_slug}` into Mirage's `:mobile_suit_slug`. So
  `/api/mobile-suits/{mobile_suit_slug}` registers as `/mobile-suits/:mobile_suit_slug`. The keys stay
  the exact OpenAPI paths, since that's what lets `paths` check them.
- **Fixtures are typed TypeScript modules, not gzipped JSON.** They live in `__mocks__/<entity>Mocks.ts`
  (TEST-2), named `mock<Thing>`, `create<Thing>Mock` and `find<Thing>Mock`, with fixed values
  (TEST-20). Imported JSON would widen enum strings like `unit_type` to `string`, so it can't satisfy
  the generated types without the casts TEST-10 forbids.
- **There is one Mirage server, not three.** aoam needs an Express server because a browser can't read
  gzipped files. Here, fixtures are modules, so Storybook bundles them and runs the same
  `makeMirageServer` that tests use, as TEST-18 already says. `makeMirageServer({ environment,
  overrides })` keeps its signature. The table only replaces the hand-written `this.get(...)` calls,
  and `overrides` still runs after it.
- **Behaviour follows the agreed API, not aoam's fallbacks:**
  - **List routes** go through one `paginate()` helper that applies `limit` and `offset` and returns
    `meta` (D3). An empty list is 200 with `data: []`, not aoam's 400 `emptyResultMessage`.
  - **Detail routes** look the slug up with `find<Thing>Mock` and return 404
    `{"detail": "<Entity> not found"}` (FAPI-13) when it's missing, never the list fixture.
    One fixture answers to an old slug, so the frontend's URL replacement (D2) can be tested.
  - **Filters** are opt-in. A config may supply a predicate when a page test needs a filter.
    Otherwise filter parameters are ignored. A `q` predicate uses one shared `normalizeSearch()`
    that mirrors the backend's normalization (D8).
  - **Errors** stay per test, through `overrides`. The table holds only the happy path.
- **No response cache, polling or Express logging.** Mirage's own `logging` option sits behind a
  `makeMirageServer` argument, off by default.
- **The capture script writes TypeScript.** Once 3a has loaded the 2022 dump into the dev database,
  `frontend/scripts/capture-fixtures.sh` fetches a fixed list of routes from the local API, checks
  each response as aoam's does, and writes `__mocks__/<entity>Mocks.ts` with the generated type
  annotations, then runs oxfmt. A shape change becomes a typecheck failure instead of a stale fixture.
  The fixed list keeps the fixtures small: RX-78-2, RX-78-02, RX-78F00, a Zaku II, a couple of works
  and continuities, and two list pages.

**Until 3a loads data,** the fixtures are written by hand for those same suits, and the capture
script replaces them later. The API and frontend don't change when a fresh dump replaces an old one.

*Amended 2026-11-21 (PR B grilling):*
- **The values come from Fandom's fresh dump.** `gundam_pages_current.xml.7z` was regenerated on
  2026-11-15. It's kept in the gitignored `ingest/data/dumps/` and recorded in
  [`ingestion-spike.md`](../research/notes/ingestion-spike.md).
- **There is a dev seed script after all, and it's permanent.**
  - `backend/scripts/seed_dev.py`, run by `moon run backend:seed-dev`, writes the same suits,
    works and continuities as the fixtures into the dev database, so `dev` and `dev-mock` show the
    same rows.
  - It upserts by slug through the facades, so it can be rerun.
  - It refuses outside `dev` and `test`, and refuses after a completed ingest run unless `--force`,
    so it never overwrites a real load.
- **The seed data and the fixtures are two copies of the same values**, each naming the other.
  Details are in [`catalog-read-routes.md`](catalog-read-routes.md).

**Mock mode for the running app** (agreed 2026-11-13). Unlike aoam, the dev app itself can run on
the fixtures, started with `moon run root:dev-mock`.

- **The flag:** a `MOCK_API` variable, passed to the browser through Vite's `define` as
  `import.meta.env.MOCK_API`, the same way `LOG_LEVEL` is passed (NODE-10). It isn't a `VITE_`
  prefixed variable. `vite.config.ts` forces it to `false` for `vite build`, so a production image
  can't turn it on by accident.
- **Starting Mirage:** `main.tsx` checks the flag before rendering. When it's set, a dynamic `import()`
  loads `@/__mocks__/mirageServer` and calls `makeMirageServer({ environment: 'development' })`.
  When it's off, the constant `false` lets Vite drop the import, so neither Mirage nor the fixtures
  reach the production bundle. The mock mode PR checks that by searching `dist/` for `miragejs`.
- **Unmocked routes go to the real API.** The `development` environment passes unhandled requests
  through, so routes in the endpoint table are mocked and everything else reaches the backend behind
  the proxy. A page can be built on fixtures while its other routes stay live.
- **It runs in Compose, not on the host.** The dev server lives in the `frontend` service behind the
  proxy (`frontend/moon.yml` explains why a host Vite can't work). So:
  - `compose.yaml`'s `frontend` service gets `environment: { MOCK_API: "${MOCK_API:-false}" }`, and
    `.env.example` lists `MOCK_API=false` (ENV-1: it lands with its first reader).
  - The root `moon.yml` gets a `dev-mock` task: the same command as `dev`
    (`docker compose up --build --watch --attach-dependencies all`), with `env: { MOCK_API: 'true' }`
    and the `server` preset.
  - The full stack still starts, backend and Postgres included, because the proxy depends on the
    backend being healthy and unmocked routes pass through to it. A lighter variant without the
    backend would need a Compose override that resets the proxy's `depends_on`. Add it only if
    starting the backend becomes a problem.
- **Changing modes:** `MOCK_API` is read when the container starts, so changing modes means stopping
  one task and starting the other. Compose recreates `frontend` because its environment changed.

**Standards:** TEST-18 gains a generic paragraph on the endpoint table and the typed path keys, using
the standards' placeholder domain.

### D8. Search is a normalized substring match (**Agreed** 2026-11-15)

Plain `ILIKE` on `name` misses how people type Gundam names: `rx782` doesn't match `RX-78-2`, and
`turn a` doesn't match `∀ Gundam`. At this size a trigram index or fuzzy search is overkill, so `q` is
a normalized substring match.

1. **Both sides are normalized.** The query is lowercased and stripped to `a-z0-9`, and so is the
   column, with `regexp_replace(lower(col), '[^a-z0-9]', '', 'g')`. `rx782`, `RX 78-2` and `rx-78-2`
   all become `rx782`.
2. **The match is on `slug` and `model_number`, not `name`.**
   - D2 makes each slug an ASCII-folded copy of the title, through the symbol map, so `∀ Gundam`
     becomes `turn-a-gundam` and `turn a` finds it.
   - Characters and organizations match on `slug` only, since they have no model number.
   - **Amended by BE-1** ([`catalog-search.md`](catalog-search.md) Q6, 2026-11-23): every `q`
     also matches the English display name (`name`, or a work's `title`). Japanese names don't
     survive normalization, so they're deferred to
     [#34](https://github.com/saurookadook/msg-docking-bay/issues/34).
   - Nothing that survives normalization is a `LIKE` wildcard, so no escaping is needed. The value is
     still bound (RDB-25).
   - Known false positive: a collision suffix such as `-48213` can match a digits-only `q` such as
     `482`. It's rare and harmless, so there's no separate search column.
3. **Prefix matches rank first.** With `q`, a `CASE` expression on "starts with" goes in front of the
   D3 fixed order (`name`, `id`), so `zaku` lists "Zaku II" before "Act Zaku". The order still ends in
   `id`, so pages stay deterministic.
4. **Input rules.**
   - `q` is `Query(max_length=100)`. A longer value is 422.
   - A `q` that's blank after normalization (such as `" -- "`) means no filter, not an error, so an
     empty search box doesn't break the list.
   - No minimum length: a one-character search scans about 3,200 rows.
5. **One shared helper.** The normalization and the prefix rank live in `BaseFacade`, so suits,
   characters and organizations can't drift apart. Mirage's opt-in `q` predicate (D7) applies the same
   normalization in TypeScript, so mock mode behaves like the real API.
6. **Deferred.**
   - No index. Revisit if the suit count grows tenfold or a query shows up as slow.
   - No cross-entity `/api/search`. A global search box gets its own decision when the frontend needs
     one. **Resolved by BE-1:** `GET /api/search` ([`catalog-search.md`](catalog-search.md)).

**Tests** (PR B steps 1, 4 and 5):
- `rx782` finds `RX-78-2`, and `turn a` finds `∀ Gundam`.
- `%` and `_` match nothing special.
- A prefix match ranks before a substring match.
- A blank `q` returns the unfiltered list.
- A 101-character `q` is 422.

## Routes

Route names follow FAPI-6. They become the operation IDs, and so the generated client's names
(`operation_id_from_route_name` in `api/app/main.py`).

**PR B**

| Route | Function | Returns |
| --- | --- | --- |
| `GET /api/continuities` | `read_continuities_list` | All continuities, by name (a short list, so unpaginated) |
| `GET /api/works` | `read_works_list` | Paginated work cards. Filters: `continuity` (slug), `work_type`, `q` (slug and title, D8; added by BE-1) |
| `GET /api/works/{work_slug}` | `read_work` | A work, with its continuity, parent work and related works |
| `GET /api/works/{work_slug}/mobile-suits` | `read_work_mobile_suits` | Paginated suit cards that appear in the work, with episodes and the debut flag |
| `GET /api/mobile-suits` | `read_mobile_suits_list` | Paginated suit cards. Filters: `continuity`, `work` (slugs), `unit_type`, `q` (slug, name and model number, D8) |
| `GET /api/mobile-suits/{mobile_suit_slug}` | `read_mobile_suit` | A suit, with spec sheets, direct relations with their `direction`, appearances, and a source on each (D5) |

**PR C**

| Route | Function | Returns |
| --- | --- | --- |
| `GET /api/characters` | `read_characters_list` | Paginated character cards. Filters: `work`, `q` (slug and name, D8) |
| `GET /api/characters/{character_slug}` | `read_character` | A character, with appearances and the suits they pilot |
| `GET /api/organizations` | `read_organizations_list` | Paginated organization cards. Filters: `work`, `q` (slug and name, D8) |
| `GET /api/organizations/{organization_slug}` | `read_organization` | An organization, with its parent and child organizations as refs, and its appearances |
| `GET /api/organizations/{organization_slug}/mobile-suits` | `read_organization_mobile_suits` | Paginated, one item per suit with its `links` (role, work, source). Filter: `role`, on both suits and links |
| `GET /api/mechanical-designers` | `read_mechanical_designers_list` | Paginated designer cards. Filter: `q` (slug and name, D8) |
| `GET /api/mechanical-designers/{mechanical_designer_slug}` | `read_mechanical_designer` | A designer |
| `GET /api/mechanical-designers/{mechanical_designer_slug}/mobile-suits` | `read_mechanical_designer_mobile_suits` | Paginated suit cards the designer is credited with, each with its source |

PR C also adds `pilots`, `organizations` and `designers` to `read_mobile_suit`, as refs
with their work and source. That changes an existing response, so PR C regenerates the
contract (MONO-14).

An organization's and a designer's suits are paged sub-resources, not lists in the
detail: in the 2026-11-15 dump, Kunio Okawara is the designer on 438 infoboxes and the
Earth Federation the operator on 603 (RDB-23). The grilling that settled these routes is
in [`people-read-routes.md`](people-read-routes.md).

**BE-1** ([`catalog-search.md`](catalog-search.md)) adds `q` to `read_works_list`, and makes
every list's `q` match the English name or title too (the rows above):

| Route | Function | Returns |
| --- | --- | --- |
| `GET /api/search` | `read_search` | The first `limit` cards of each kind (1 to 20, default 5), matched by each list's `q`, with every kind's total in `meta.totals`. A blank `q` lists the first rows of each kind |

**PR D** adds no routes. It adds the four part lists and `inherited_parts` to each spec sheet
in `read_mobile_suit`, and regenerates the contract.

Each resource gets its own router in `api/routes/<resources>.py` (FAPI-4) and its own envelopes in
`api/models/<resource>.py` (FAPI-12). Routes stay thin (FAPI-14): one facade call, or a handler in
`api/routes/handlers/` when a detail response combines several facades.

## Implementation order and checkpoints

At each checkpoint the agent stops and reports what changed and how it was verified. Commits are made
by hand.

### 0. Docs (Checkpoint → `docs(docs): plan the catalog read API`)
This file, plus `data-ingestion.md`:

- The 3a section takes the loader rules from D2 (slugs, redirects and page IDs), D4 (facades) and D5
  (`updated_at` and part notes).
- Phase 5 shrinks to site-wide attribution (D6).

### PR A — `build(frontend): generate API types from the backend's OpenAPI schema`
Branch `build/generate-api-contract`. This assumes D1 Option 1; Option 2 changes the paths and scopes.
**Detailed plan: [`generated-api-contract.md`](generated-api-contract.md).**

1. **Export script** (Checkpoint → `feat(backend): add an OpenAPI schema export script`).
   `backend/scripts/export_openapi.py`, a runnable module (PY-36), writes `app.openapi()` with sorted
   keys. Importing `api.app.main` must not touch the database. Check that `init_logging` at import time
   doesn't print into the output.
2. **Generator** (Checkpoint → `build(frontend): generate API types with openapi-typescript`).
   - Add `openapi-typescript` as a dev dependency.
   - Add an `api:generate` script that runs the export through `uv --directory ../backend`, then the
     generator, then oxfmt.
   - Have oxlint ignore the generated directory (FMT-11).
3. **First consumer** (Checkpoint → `refactor(frontend): use the generated health check types`).
   - Replace the hand-written `HealthCheck` types with MONO-15 aliases.
   - Retype `healthMocks.ts` with them.
   - Remove the TODO in `frontend/src/types/index.ts`.
4. **Endpoint table** (Checkpoint → `refactor(frontend): drive the Mirage server from an endpoint
   table`).
   - Add the config type keyed by the generated `paths` type, the route-path builder and `paginate()`
     (D7).
   - `makeMirageServer` registers routes from the table; its signature and `overrides` don't change.
   - Health check becomes the first entry, and the existing health check tests and stories pass
     unchanged.
   - Add a typecheck test: a config naming an unknown path, or returning the wrong shape, fails with
     `@ts-expect-error` and a reason (TEST-22).
   - Add a unit test of the route builder: `/api/health-check` → `/health-check` and
     `/api/mobile-suits/{mobile_suit_slug}` → `/mobile-suits/:mobile_suit_slug`, so no route
     registers as `/api/api/...`.
5. **Standard** (Checkpoint → `docs(standards): describe the typed Mirage endpoint table`).
   The TEST-18 paragraph (D7), plus notes in MONO-13 and CI-5 that the contract and `node-setup` are
   rooted at `frontend/` here.
6. **Drift check** (Checkpoint → `ci(repo): fail when the generated API contract is stale`).
   CI runs `api:generate` and fails on any change to the generated files, new files included
   (MONO-14, CI-9). The `contract` job starts `backend-test.yml`.

### Mock mode PR — `feat(frontend): add a mock API mode to the dev server`
Branch `feat/add-mock-api-mode`, after PR A merges. **Detailed plan: the "Follow-up PR" section of
[`generated-api-contract.md`](generated-api-contract.md).**

1. **Mock mode** (Checkpoint → `feat(frontend): add a mock API mode to the dev server`).
   - `MOCK_API` in `vite.config.ts` (forced off for builds), the dynamic Mirage start in `main.tsx`,
     the `frontend` service's `environment`, `.env.example`, and the root `dev-mock` moon task (D7).
   - Verify, with the full stack running in both modes (the proxy needs a healthy backend, D7):
     - Under `moon run root:dev-mock`, the page shows the fixture's values, and the backend's log has
       no `/api/health-check` line. Mirage answered it in the browser.
     - Under `moon run root:dev`, the same page load shows the request in the backend's log.
     - A production build's `dist/` has no `miragejs`.
2. **Standard** (Checkpoint → `docs(standards): document the mock API mode`).
   A line in `docker-and-environment.md` or `nodejs.md` if their task or env tables list `dev` and
   `LOG_LEVEL`.

### PR B — `feat(backend): serve mobile suits, works and continuities`
Branch `feat/add-catalog-read-routes`. **Detailed plan: [`catalog-read-routes.md`](catalog-read-routes.md).**

0. **Standard** (Checkpoint → `docs(standards): describe paginated list envelopes`).
   A pagination paragraph under FAPI-12 in `fastapi.md`: `meta` with `limit`, `offset` and `total`;
   per-resource envelopes; an empty page past the end (D3).
1. **Bases** (Checkpoint → `feat(backend): add the entity and facade base classes`).
   `BaseEntityModel` sets `json_schema_serialization_defaults_required=True` (see Risks), so
   defaulted fields are required in the contract.
   `BaseEntityModel`, `TimestampsEntityMixin` and `BaseFacade`, with tests (SQLA-28).
   `BaseFacade` holds the search helper: the normalized match and the prefix rank (D8), tested on
   its own for normalization, wildcards and blank input.
2. **Slug redirects and page IDs** (Checkpoint → `feat(backend): track slug redirects and page IDs
   for suits and works`).
   - `mobile_suit_slug_redirects` and `work_slug_redirects`, each a model with its migration (ALEM-4)
     and a factory (D2).
   - `works.fandom_page_id`, in its own migration, and added to the work factory.
3. **Continuities and works** (Checkpoint → `feat(backend): add continuity and work entities and
   facades`).
   - Entities, card models, and the paginated `get_all_by_...` with filters pushed into the query
     (SQLA-20). Facade tests use the factories.
   - `get_one_by_slug` falls back to the redirect table, with tests for a current slug, an old slug
     and an unknown one.
4. **Mobile suits and sources** (Checkpoint → `feat(backend): add mobile suit and source entities and
   facades`).
   - The source read model, with the license map and `revision_url` (D6).
   - The card model, and the detail model with spec sheets, relations, appearances and sources.
   - A test that fixes the detail read's query count, to catch N+1s.
   - A test that loads a row without its relationships (PYD-3).
   - Search tests on the suit list: `rx782` finds `RX-78-2`, `turn a` finds `∀ Gundam`, and a prefix
     match ranks first (D8).
5. **Routes** (Checkpoint → `feat(backend): add continuity, work and mobile suit routes`).
   - The PR B routes and envelopes, plus the `meta` model and page-size constants.
   - `TestClient` tests with the session overridden (FAPI-20): 404 on an unknown slug, 422 on a bad
     `limit`, 422 on a 101-character `q`, a blank `q` treated as no filter, filter combinations and
     page boundaries.
6. **Contract** (Checkpoint → `build(frontend): regenerate the API contract for catalog routes`).
   - Run `api:generate`.
   - Add MONO-15 aliases for the new envelopes and entities.
   - Add an endpoint table entry for each route, with hand-written fixtures in
     `__mocks__/<entity>Mocks.ts` for the fixed set of suits and works (D7). Cover pagination, a 404
     and an old slug.
   - Make PR A's `paginate()` validate `limit` and `offset` as step 5's routes do: the
     `MAX_PAGE_SIZE` cap, and a 422 with the route's error body for a bad value, so a mock never
     serves a page the API would reject. *Deferred from PR A's review, 2026-11-20.*

### PR C — `feat(backend): serve characters, organizations and designers`
Branch `feat/add-people-read-routes`. The same steps as PR B:

- The character, organization and mechanical designer slug redirect tables, and `fandom_page_id` on
  those three tables.
- Then entities and facades, routes and the contract.
- It also makes the `read_mobile_suit` additions.
- Its decisions (Q1 to Q10) and steps are in
  [`people-read-routes.md`](people-read-routes.md):
  - Q1: an organization's and a designer's suits are paged sub-resources.
  - Q3: a designers list, with `q`.
  - Q6: a character's detail nests the suits they pilot.
  - Q7: an organization's suit list has one item per suit, its links grouped.
  - Q8: character and organization details nest their appearances.
  - Q9: `role` filters both the suits and their links.
  - Q10: an organization's detail names its parent and children.

### PR D — `feat(backend): serve suit parts on spec sheets`
Branch `feat/add-suit-parts-read`.

- **Entities and facades** for armaments, equipment, materials and powerplants and their spec sheet
  junctions (D4 rule 3: this is their first caller).
- **Part refs** (`{slug, name}`), ready for part detail routes later. *Amended 2026-11-22:* this
  was "part cards", but a sheet nests refs, as PR C's credits do. Cards wait for a part list
  route.
- **Page IDs:** `fandom_page_id` on the four part tables (D2, amended).
- **Suit detail:** `read_mobile_suit` nests the four part lists under each spec sheet, still loaded in
  a fixed number of queries. Named configurations inherit empty kinds (`inherited_parts`).
- **Seed:** the real parts of three of the seeded suits.
- The grilled plan is [`suit-parts-read.md`](suit-parts-read.md).
- **Contract:** run `api:generate`, then update the MONO-15 aliases, the endpoint table and the
  fixtures.

### After 3a loads the 2022 dump — `build(frontend): capture Mirage fixtures from the local API`
Branch `build/capture-mirage-fixtures`. This is a small PR, separate from PR B to D because it needs
real data.

- `frontend/scripts/capture-fixtures.sh` fetches the fixed route list from the local API, rejects a
  non-200 or non-JSON response, writes typed `__mocks__/<entity>Mocks.ts` modules and runs oxfmt (D7).
- It replaces the hand-written fixtures. Tests that assert specific values are updated to match.

## Risks to check during implementation

- **Deriving response types from `paths`: confirmed 2026-11-13.** A throwaway app shaped like PR B's
  routes was built with the backend's real `BaseResponseModel`, `UnitType`, `SLUG_PATTERN` and
  operation-ID function, under FastAPI 0.143 and Pydantic 2.14. Its schema went through
  `openapi-typescript` 7.13.0 and was typechecked with the frontend's `tsc` (7.0.2) and
  `tsconfig.common.json`.
  - *Added 2026-11-17 in PR A:* the generator itself can't run on TypeScript 7. It builds its
    output with TypeScript's JS compiler API (`ts.factory`), which the native TS 7 compiler doesn't
    ship, and its peer range is `typescript ^5.x`. PR A runs it from a `frontend/tools/api-codegen`
    workspace package with its own TypeScript 5.9.3. The generated types still typecheck under
    7.0.2 (see [`generated-api-contract.md`](generated-api-contract.md) step 2).
  - Direct indexing of
    `paths[P]['get']['responses'][200]['content']['application/json']` works without a cast, and so
    does reading path parameters from `paths[P]['get']['parameters']`.
  - A mapped union of per-path configs checks each table entry against its own path.
  - These fail typecheck, as intended: an unknown path, a wrong enum value, a list body without
    `meta`, a misspelled path parameter, another route's body, and a JSON-imported fixture (D7's
    reason for `.ts` fixtures).
  - The `{param}` → `:param` route builder produced the expected Mirage paths at runtime.
  - `UnitType` appears once in the schema as a named component, not inlined per field.
- **Defaulted fields come out optional (found by the same test).** Pydantic leaves a field with a
  default, such as `model_number: str | None = None`, out of the serialization schema's `required`
  list. So the generated type is `model_number?: string | null`, although the API always sends the
  key, and the frontend would have to handle `undefined` too.
  - **Fix, in PR B step 1:** set `json_schema_serialization_defaults_required=True` on
    `BaseEntityModel`'s `model_config` and on any read-model base. With it, the test schema gave
    `model_number: string | null` and `continuity: … | null`, without splitting the schema into
    input and output variants.
  - The PR B contract step checks that no response field in `api.ts` is optional unless the API can
    really omit it.
- **Envelope aliases.** `BaseResponseModel` camel-cases envelope field names, so `meta` must stay a
  single word. The fields inside `meta` belong to a plain model, so they stay snake_case.
- **Work-unknown rows.** Pilot and organization links with `work_id` NULL (from PR C's schema) need a
  defined place in responses. PR C settled it (Q2): they stay in the same flat list with
  `work: null`, sorted after the links that name a work, never dropped or grouped.
  3a's loader keeps a pair to either a work-unknown row or work-specific rows, never both
  ([`data-ingestion.md`](data-ingestion.md) 3a), so that group holds only pairs with no specific row.
- **Empty database.** Every list returns `{"data": [], "meta": {..., "total": 0}}` before the first load
  (FAPI-12), never a 404.

## Verification

- **Each PR:** `moon run backend:test`, ruff and pyright strict, plus the frontend's typecheck, tests
  and lint. From PR A on, the contract drift check passes.
- **PR A:** delete the generated files, run `api:generate`, and confirm the output is byte-identical
  to the committed files.
- **PR B and PR C:** run the stack and confirm each route through the proxy at `/api/...`.
- **After 3a loads the 2022 dump:**
  - Spot-check `/api/mobile-suits/rx-78-2-gundam` for its spec sheets, the RX-78-02 and RX-78F00
    relations, appearances, and source URLs with revision IDs.
  - Page through `/api/mobile-suits` to the end, and confirm the totals match a `count(*)` in `psql`.
