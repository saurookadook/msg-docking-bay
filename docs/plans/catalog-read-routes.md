# Plan: PR B — catalog read routes

> **Agreed** 2026-11-20, grilled 2026-11-21. Expands the PR B section of
> [`catalog-read-api.md`](catalog-read-api.md). No code until asked.

Branch `feat/add-catalog-read-routes` (created from `main` at `31a6842`). PR title:
`feat(backend): serve mobile suits, works and continuities`.

This plan expands the PR B section of [`catalog-read-api.md`](catalog-read-api.md): D2 to D8, the
Routes table and Risks. It amends two agreed decisions, D4 rule 2 and D7's "no dev seed script", for
reasons given under Decisions.

## Context

PR A gave the frontend a generated API contract and a typed Mirage endpoint table, but the API serves
only `/api` and `/api/health-check`. PR B adds:
- **The routes:** six `GET` routes over continuities, works and mobile suits.
- **The layer they read through:** entities and facades (D4), including the upserts that a
  permanent dev seed script writes with.
- **Redirects:** the slug redirect tables that detail routes follow (D2).
- **The contract:** it regenerates the contract and adds typed Mirage fixtures. Both the seed and the
  fixtures take real values from Fandom's fresh dump.

**Facts checked in the repo that shape this plan:**
- **Models declare foreign keys but no `relationship()`** anywhere (`backend/models/*/db.py`). The
  base classes are in `db/base_db.py`:
  - `BaseDB` has a UUIDv7 `id`.
  - `JunctionBaseDB` has no `id`.
  - `RootDB` derives table names from class names.
- **No entities, facades or handlers exist yet**, and neither do `models/base/` or
  `api/routes/handlers/`.
- **`works` has no `fandom_page_id`** (`mobile_suits` does), and **no redirect tables exist**.
- **Spec sheets:**
  - `spec_sheets` is unique on `(mobile_suit_id, source_id, configuration)`, with nulls not distinct.
  - A null `configuration` is the base sheet. Named sheets store only the fields that differ.
- **Tests:**
  - The autouse `test_db_session` (`_fixtures/db.py`) binds the scoped session inside a rolled-back
    transaction, and factories use that session (`_factories/<entity>/db.py`).
  - `test_app_client` (root `conftest.py`) overrides `api_db_session`.
  - **`api/_tests/app/test_main.py::TestOperationIds` pins the exact route map**, so every new route
    updates it.
- **Migrations:**
  - The head is `16a6adcc4df8`, and file names follow `YYYY_MM_DD_HHMM-<rev>_<slug>.py`.
  - `db/migrations/env.py` lists every model in `MODELS`.
  - `db/_tests/test_migrations.py` runs a round trip and `alembic check`.
- **Database access is sync** (`psycopg`, `Session`), so routes are plain `def` (FAPI-8).
- **No standard covers query-count tests.** SQLA-10's `lazy="raise"` is the nearest safety net.
- **SQLA-25's upsert sets `updated_at` on every conflict.** D5 says the 3a loader's upserts must not.
- **The backend dev image installs the dev group (`factory-boy`); the prod image is `--no-dev`**
  (`backend/Dockerfile`).
- **The `ingest` service mounts `./ingest` and `./backend`.** 3a's loader takes a dump `<path>`.
- **Fandom's dumps were regenerated on 2026-11-15 and can be downloaded:**
  - `gundam_pages_current.xml.7z` is 22.1 MB.
  - `gundam_pages_full.xml.7z` is 80.3 MB.
  - Until now the 2025 copies sat in S3 Deep Archive. No local copy of any dump existed.

## Decisions (settled 2026-11-20 and 2026-11-21)

**Loading and entities**
- **Relationships.**
  - Add `relationship(lazy="raise", back_populates=...)` to the models these reads touch (SQLA-10).
    Facades eager-load them (SQLA-22).
  - This is ORM-only: no migration, and `alembic check` is unaffected.
  - The relationships:
    - `ContinuityDB.parent_continuity`
    - `WorkDB`: `continuity`, `parent_work`, `outgoing_relations` and `incoming_relations`
    - `WorkRelationDB`: `from_work`, `to_work` and `source`
    - `MobileSuitDB`: `continuity`, `spec_sheets`, `outgoing_relations`, `incoming_relations` and
      `appearances`
    - `MobileSuitRelationDB`: `from_mobile_suit`, `to_mobile_suit` and `source`
    - `MobileSuitAppearanceDB`: `mobile_suit`, `work` and `source`
    - `SpecSheetDB`: `source`
- **`id` moves to a mixin.**
  - `BaseEntityModel` holds only `model_config`: `from_attributes=True` and
    `json_schema_serialization_defaults_required=True` (the Risks fix).
  - Full entities add `id` through `IdEntityMixin`. Card and detail read models leave it out (D5).
- **Paginated reads are `get_page(...)`, returning `Page[T]`.** SQLA-16's table has no paginated
  method, so step 0 adds this row.

**Writes (amends D4 rule 2)**
- **Facades get `create_or_update` in PR B.**
  - The dev seed script is the upserts' first caller (D4 rule 3), and D4 rule 4 keeps upserts in
    facades.
  - Junction tables upsert on their primary keys. Spec sheets upsert on
    `(mobile_suit_id, source_id, configuration)`.
  - 3a extends these methods and doesn't add a parallel set.
- **Upserts don't touch an unchanged row (D5).**
  - Use `insert ... on_conflict_do_update(..., where=<row> IS DISTINCT FROM <excluded>)`, setting
    `updated_at` only in that branch.
  - A no-change rerun changes nothing, and the method still returns the row: when the guarded update
    returns nothing, it re-selects the row by its key.
  - Step 0 adds this variant to SQLA-25.

**Response shapes**
- **Spec sheets are filled in the backend.**
  - For each named configuration, the facade fills null columns from the base sheet (null
    `configuration`) of the same suit and source.
  - Every sheet carries `inherited_fields: list[SpecSheetField]`, sorted. `SpecSheetField` is a
    `Literal` of the ten SI column names, so the generated TypeScript type is a union.
  - The list names the columns that came from the base sheet. It is empty on the base sheet and on a
    named sheet with no base, which is served as stored.
- **Nested lists have fixed orders, each ending in a unique key (RDB-22):**
  - `spec_sheets[]`: the base sheet first, then `configuration`, then the source's `kind` and `url`.
  - `relations[]`: `relation_type`, then `direction`, then the other side's name or title, then its
    slug.
  - `appearances[]`: the work's D3 order (`start_date NULLS LAST`, `title`), then the work slug.
  - `/works/{slug}/mobile-suits`: debut suits first (`is_debut DESC`), then `name, id`.
- **Continuity cards carry `parent_continuity: {slug, name} | null`.** It comes from a self-join in
  the same query.
- **Work short names stay out for now.** D5 doesn't list them. Adding them later is a new field, not
  a break.
- **Filters match current slugs only.** `continuity` and `work` don't follow redirects; detail and
  sub-resource paths do (D2). An unknown filter slug gives an empty page, not a 404, because a filter
  isn't a parent (FAPI-12).

**Data and the dev seed (amends D7)**
- **The fresh dump is kept locally:**
  - `ingest/data/dumps/gundam_pages_current-2026-11-15.xml.7z`, gitignored.
  - The ingest container already sees it through the `./ingest` mount, so 3a's `fandom seed <path>`
    needs no Compose change.
  - Its name, size, `Last-Modified` and SHA-256 go in
    [`ingestion-spike.md`](../research/notes/ingestion-spike.md)'s dumps section.
- **Fixture and seed values are read from that dump**, by hand: real specs, page IDs and revision
  IDs.
- **A permanent dev seed script:** `backend/scripts/seed_dev.py` (PY-36), run by a
  `backend:seed-dev` moon task in the backend container.
  - It writes through the facades' `create_or_update`, upserting by slug, so it can be rerun.
    Factories stay test-only.
  - It refuses (non-zero exit) unless `ENVIRONMENT` is `dev` or `test`.
  - It refuses after any completed `ingest_runs` row, unless `--force`, so it never overwrites a real
    load.
  - It seeds the same rows as the Mirage fixtures, including one old-slug redirect.
- **Seed data and fixtures are two copies.** Each holds its own literal values, with a comment naming
  the other and the dump date. The later capture script regenerates the fixtures from the seeded API.

## Shared pieces (used by several steps)

- **Pagination** (D3):
  - `constants/pagination.py` holds `DEFAULT_PAGE_SIZE: Final = 50` and `MAX_PAGE_SIZE: Final = 100`.
  - Routes take `limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE` and
    `offset: Annotated[int, Query(ge=0)] = 0`.
  - `api/models/pagination.py` has `PageMeta(BaseModel)`: `limit`, `offset` and `total`, snake_case
    because it's a plain model (Risks: Envelope aliases).
  - Facades return `models/base/page.py` `Page[T]` (`items: list[T]`, `total: int`). The facade runs
    the page query, then a separate `count(*)` with the same filters (D3), so a page past the end
    still has its total. The route builds `data=page.items` and `meta=PageMeta(...)`.
- **Detail paths:** `Annotated[str, Path(pattern=SLUG_PATTERN)]`, reusing `models/mixins/checks.py`'s
  constant (D2), so a malformed slug is a 422.
- **Error mapping (FAPI-13):** `<Entity>Facade.NotFoundError` → 404 `"<Entity> not found"`. Any
  other `Exception` → logged 500 `"Error fetching <thing>"`. Each route maps inline; no handler
  module, since every route makes one facade call (FAPI-14).
- **Reference models:**
  - `ContinuityRefEntity` (`slug`, `name`) and `WorkRefEntity` (`slug`, `title`) nest inside cards.
  - Cards nest refs, not full cards, so no query fans out.

## Steps (one checkpoint and one commit each)

### 0. Standards and plan amendments → `docs(standards): describe paginated list envelopes`
- **`python/fastapi.md`:** a pagination paragraph under FAPI-12, using the placeholder domain. It
  covers:
  - `limit` and `offset` with a capped default
  - the per-resource `<Entities>ListResponse` with `meta: PageMeta`
  - a page past the end returning `data: []` with the real total
- **`python/pydantic.md` PYD-2:** `BaseEntityModel` without `id`, plus `IdEntityMixin`, and a
  sentence that served read models leave `id` out when slugs are the public key.
- **`python/sqlalchemy.md`:**
  - SQLA-16 gains the `get_page` row.
  - SQLA-25 gains the no-change variant: a guarded `DO UPDATE ... WHERE ... IS DISTINCT FROM`, with
    `updated_at` set only when a column changed, and a re-select when nothing was updated.
- **`python/pytest.md`:** a new rule. A facade method that returns nested collections gets a
  fixed-query-count test, which counts statements with SQLAlchemy's `before_cursor_execute` event
  and holds the count equal at one and at several related rows.
- **The amended decisions, in a separate `docs(docs)` commit** so the standards commit stays one
  concern:
  - `catalog-read-api.md`: D4 rule 2 (writes arrive with the seed script) and D7 (a permanent dev
    seed script).
  - `data-ingestion.md`'s 3a section: the dump location, and that 3a extends the facades' guarded
    upserts.
  - `ingestion-spike.md`: the dump record, after the download below.
- **Download the dump** into `ingest/data/dumps/`, and add the directory to `.gitignore`.

### 1. Bases → `feat(backend): add the entity and facade base classes`
- `models/base/entity.py`: `BaseEntityModel`.
- `models/mixins/entity.py`: `IdEntityMixin`, `CreatedAtEntityMixin` and
  `TimestampsEntityMixin` (`AwareDatetime`, PYD-2 and PYD-5).
- `models/base/page.py`: `Page[T]`.
- `models/base/facade.py`: `BaseFacade`.
  - `__init__(*, db_session: Session | None = None)` falls back to the scoped session for scripts
    (SQLA-16).
  - The search helper (D8):
    - `normalize_search(q) -> str | None` lowercases `q` and strips it to `a-z0-9`, returning
      `None` when nothing is left.
    - `_search_filter(columns, needle)` matches
      `regexp_replace(lower(col), '[^a-z0-9]', '', 'g') LIKE '%' || :needle || '%'`. The needle is
      bound (RDB-25).
    - `_prefix_rank(columns, needle)` is a `CASE` that sorts "starts with" first.
  - The guarded upsert helper: builds the `on_conflict_do_update` with the `IS DISTINCT FROM`
    guard, and does the re-select.
- `models/_tests/conftest.py`: the query-count fixture.
- Tests (`models/_tests/base/`):
  - normalization: `RX 78-2` → `rx782`, `∀`-only → `None`, `%_` → `None`
  - `json_schema_serialization_defaults_required` making a defaulted field required in the
    serialization schema
  - the scoped-session fallback
  - the query-count fixture counting known statements
- Search behaviour gets its SQL tests through the suit facade in step 4, and the upsert helper
  through each facade in steps 3 and 4.

### 2. Redirects and page IDs → `feat(backend): track slug redirects and page IDs for suits and works`
- **The two redirect models,** `models/mobile_suit_slug_redirect/db.py` and
  `models/work_slug_redirect/db.py`:
  - Each is `JunctionBaseDB, CreatedAtDB`, with `old_slug` as the primary key under
    `slug_format("old_slug")`.
  - The FK to the entity is `ON DELETE CASCADE` and indexed.
  - The tables come out as `mobile_suit_slug_redirects` and `work_slug_redirects`.
- **`WorkDB.fandom_page_id`:** `Mapped[int | None] = mapped_column(unique=True)` with `positive(...)`,
  as on `mobile_suits` (D2).
- **Migrations:** three, autogenerated, committed with their models (ALEM-4): the two redirect
  tables, then `works.fandom_page_id`. Both new models go in `env.py`'s `MODELS`.
- **Factories** `_factories/<entity>/db.py` for both redirect tables. `WorkDBFactory` gets
  `fandom_page_id = None`.
- Tests `models/_tests/<entity>/test_db.py`:
  - a round trip
  - the `slug_format` CHECK
  - cascade on entity delete
  - `works.fandom_page_id` unique and positive

### 3. Continuities and works → `feat(backend): add continuity and work entities and facades`
- **Relationships** on `ContinuityDB`, `WorkDB` and `WorkRelationDB`.
- **`models/continuity/entity.py`:**
  - `ContinuityEntity`: full, alphabetical (PYD-3).
  - `ContinuityRefEntity`.
  - `ContinuityCardEntity`: `slug`, `name`, `parent_continuity: ContinuityRefEntity | None`, and
    the timestamps.
- **`ContinuityFacade`:**
  - `get_all()`: every card, ordered by `name, id`, with the parent joined. It's unpaginated,
    because the list is short (Routes table).
  - `create_or_update(*, payload)` on `slug`.
- **`models/work/entity.py`:**
  - `WorkEntity`.
  - `WorkRefEntity`.
  - `WorkCardEntity`: `slug`, `title`, `title_ja`, `work_type`, `start_date`, `end_date`,
    `continuity: ContinuityRefEntity | None`, and the timestamps.
  - `WorkDetailEntity`: the card plus `parent_work: WorkRefEntity | None` and `relations[]`.
  - Each `relations[]` item is `relation_type`, `direction` (`Literal["outgoing", "incoming"]`),
    `work: WorkCardEntity`, `source: SourceEntity` and `created_at`.
  - The work side of D5's relation rule: outgoing means this work `<relation_type>` the other.
  - `SourceEntity` is added in this step, and step 4 adds its computed fields.
- **`WorkFacade`:**
  - `get_page(*, continuity_slug, work_type, limit, offset) -> Page[WorkCardEntity]`, ordered
    `start_date NULLS LAST, title, id` (D3).
  - `get_one_by_slug(slug) -> WorkDetailEntity` eager-loads the continuity, the parent, both
    relation directions with each other work's continuity, and the sources. Relations come back in
    the fixed order.
  - If the slug misses, `get_one_by_slug` looks it up in `work_slug_redirects` (D2). It raises
    `NotFoundError` when both miss (SQLA-17).
  - `create_or_update(*, payload)` on `slug`.
  - Upserts for `work_relations` and `work_slug_redirects`.
- **`SourceFacade.create_or_update`** on `(kind, external_id)`.
- Tests (`models/_tests/<entity>/test_facade.py`, `test_entity.py`):
  - every method, with its not-found case
  - a current slug, an old slug and an unknown one
  - filters, alone and combined
  - an empty page past the end with the real total
  - order ties broken by `id`
  - one row validated without its relationships failing as PYD-3 expects
  - each upsert: a create, an update that sets `updated_at`, and a no-change rerun that leaves
    `updated_at` alone and still returns the row

### 4. Mobile suits and sources → `feat(backend): add mobile suit and source entities and facades`
- **Relationships** on `MobileSuitDB`, `MobileSuitRelationDB`, `MobileSuitAppearanceDB` and
  `SpecSheetDB`.
- **Sources (D6):**
  - A license map in `constants/catalog.py`: `ContentLicense` → name and license URL.
  - `SourceEntity` gets computed fields `license_name`, `license_url` and `revision_url` (PYD-11).
  - `revision_url` dispatches through a registry dict keyed by `SourceKind` (PY-35). Each builder
    adds `oldid=<revision_id>` with `urllib.parse`, so Fandom's `?curid=` query survives.
  - `revision_url` is null without a `revision_id`. `external_id` stays out of the response.
- **`models/mobile_suit/entity.py`:**
  - `MobileSuitEntity`.
  - `MobileSuitCardEntity` (D5 card).
  - `MobileSuitDetailEntity`: the card plus `spec_sheets[]`, `relations[]` and `appearances[]`.
  - Each `spec_sheets[]` item is `configuration`, the ten SI columns, `inherited_fields`, `source`,
    `created_at` and `updated_at`. `raw_infobox` is left out.
  - Each `relations[]` item is `relation_type`, `direction`, `mobile_suit: MobileSuitCardEntity`,
    `source` and `created_at`.
  - Each `appearances[]` item is `work: WorkCardEntity`, `first_episode`, `last_episode`,
    `is_debut`, `source` and `created_at`.
  - `SpecSheetField` is the `Literal` of the ten SI column names.
  - Each docstring says what it leaves out and why (PYD-4, D5).
- **`MobileSuitFacade`:**
  - `get_page(*, continuity_slug, work_slug, unit_type, q, limit, offset)`, ordered `name, id`. With
    a `q` that normalizes to something, it matches `slug` and `model_number` (D8), and the prefix
    rank goes first.
  - `get_page_by_work_slug(work_slug, *, limit, offset)` for the sub-resource:
    - It returns `Page[MobileSuitAppearanceCardEntity]`: the suit card plus `first_episode`,
      `last_episode` and `is_debut`.
    - It's ordered debut first, then `name, id`.
    - It resolves the work through `WorkFacade`'s slug lookup, redirects included, and raises
      `WorkFacade.NotFoundError` for an unknown work.
  - `get_one_by_slug(slug)`:
    - It has the same redirect fallback.
    - It fills the spec sheets and records `inherited_fields`.
    - Nested lists come back in the fixed orders.
  - `create_or_update(*, payload)` on `slug`.
  - Upserts for `spec_sheets`, `mobile_suit_relations`, `mobile_suit_appearances` and
    `mobile_suit_slug_redirects`.
- **Tests:**
  - every method
  - D8: `rx782` → `RX-78-2`, `turn a` → `turn-a-gundam`, `%` and `_` literal, prefix before
    substring, a blank `q` = no filter
  - spec sheets: filling from the base sheet with the right `inherited_fields`, a named sheet with
    no base, and two sources kept apart
  - relation direction from both ends
  - the nested orders, and debut first on the work's suit list
  - source: `revision_url` for each kind and for a null revision
  - each upsert's create, update and no-change rerun
  - **a fixed query count for the detail read**, using step 1's fixture: the same count at 1 and
    at 5 related rows

### 5. Routes → `feat(backend): add continuity, work and mobile suit routes`
- **Routers** `api/routes/continuities.py`, `works.py` and `mobile_suits.py` (FAPI-4), included in
  `main.py` in alphabetical order.
- **Envelopes** in `api/models/<resource>.py` (FAPI-12):
  - `ContinuitiesListResponse`: `data` only.
  - `WorksListResponse` and `WorkResponse`.
  - `WorkMobileSuitsListResponse`.
  - `MobileSuitsListResponse` and `MobileSuitResponse`.
  - Every list envelope except continuities has `meta: PageMeta`.
- **The six routes** from the Routes table, named per FAPI-6, with FAPI-15 docstrings.
  - `q: Annotated[str | None, Query(max_length=100)]`, and enum filters are typed with the
    `StrEnum`.
  - A filter is never named `status` (FAPI-10).
- **Tests** `api/_tests/routes/test_routes_<resources>.py` (FAPI-20, PYTEST-14):
  - 200 bodies under `["data"]` and `["meta"]`
  - an empty database giving `data: []` with total 0 (Risks)
  - 404 on an unknown slug, and 200 with the current slug on an old one
  - 422 on a malformed slug, on `limit=0`, on `limit=101`, on `offset=-1` and on a 101-character
    `q`
  - filter combinations and page boundaries
  - a 500 through `mocker.patch(..., autospec=True, side_effect=RuntimeError)`
- **`TestOperationIds`** gains the six new IDs.

### 6. Dev seed → `feat(backend): add a dev seed script`
- **`backend/scripts/seed_dev.py`** (PY-36): `main(argv) -> int`, with a `--force` flag. It owns its
  session and commits (PY-36, SQLA-15).
  - **The environment guard:** it refuses unless `ENVIRONMENT` is `dev` or `test`.
  - **The load guard:** it refuses when `ingest_runs` has a completed run, unless `--force`.
  - **The data:** RX-78-2, RX-78-02, RX-78F00 and a Zaku II, their works, continuities and sources,
    with base and named spec sheets, relations, appearances and one old-slug redirect.
  - **Where the values come from:** the 2026-11-15 dump. The docstring names the dump and points at
    the Mirage fixtures.
  - It writes everything through the facades' `create_or_update`, in dependency order.
- **The moon task:** `backend:seed-dev` runs it in the backend container (`docker compose run --rm
  backend python -m scripts.seed_dev`).
- **Tests** `backend/scripts/_tests/test_seed_dev.py`, against the test database:
  - it seeds every route's data
  - a rerun changes no `updated_at`
  - it refuses outside dev and test
  - it refuses after a completed ingest run, and runs with `--force`

### 7. Contract → `build(frontend): regenerate the API contract for catalog routes`
- **Regenerate:** run `pnpm run api:generate`.
- **Optional fields:** read `api.ts` and confirm that no response field is optional unless the API
  can omit it (Risks). If one is, fix the model's config and regenerate.
- **Aliases:** add MONO-15 aliases in `frontend/src/api/index.ts` for each new envelope, card, detail
  and nested item, plus `PageMeta`, `SpecSheetField` and the enums.
- **Endpoint table:**
  - Widen `EndpointConfig`'s handler to return `OkBody<P> | MirageResponse`, so detail routes can 404
    and list routes can 422.
  - Make `paginate()` validate as the routes do. A `limit` outside `1..MAX_PAGE_SIZE`, or a negative
    or non-integer `offset`, returns 422 with the FAPI-23 body: `{"detail": [{loc, msg, type}]}`.
    This was deferred from PR A's review.
  - Mirror `DEFAULT_PAGE_SIZE` and `MAX_PAGE_SIZE` as frontend constants, with a comment naming the
    backend's.
- **Fixtures** `__mocks__/<entity>Mocks.ts` (D7, TEST-20):
  - Hand-written from the 2026-11-15 dump: the same rows and values as the dev seed, each file
    naming the other copy.
  - RX-78-2, RX-78-02, RX-78F00 and a Zaku II, their works and continuities, and two list pages.
  - `find<Thing>Mock` helpers, and the same old-slug suit as the seed.
  - Each route gets an endpoint table entry.
- **Tests** in `endpoints.test.ts`:
  - `paginate`'s new 422 cases
  - a detail 404
  - the old-slug fixture
- No `q` predicate yet: D7 makes filters opt-in when a page test needs one.

## Verification
- **Backend:** `moon run backend:test`, and from `backend/`:
  `uv run ruff format --check . && uv run ruff check . && uv run pyright`. The migration tests
  include the round trip and `alembic check`.
- **Frontend:** `moon run frontend:typecheck frontend:lint frontend:format frontend:test`.
- **Contract:** CI's `backend / contract` job passes.
- **Through the stack:**
  - Run `moon run backend:seed-dev`, and run it again: the second run changes no `updated_at`.
  - With `moon run root:dev`, request each route through the proxy at `/api/...`.
  - Check an old slug, a 404, a page past the end, `?q=rx782`, a named spec sheet's
    `inherited_fields`, and debut suits first on a work's suit list.
  - Compare a seeded value with its Mirage fixture under `moon run root:dev-mock`.
