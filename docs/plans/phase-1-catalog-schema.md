# Plan: Phase 1 — Catalog database schema (backend)

## Context

Phase 1 of [`data-ingestion.md`](data-ingestion.md) builds the PostgreSQL schema that the ingest service (Phases 2–5) will write to. The original sketch
had `mobile_suit` → `suit_version` → `spec_claim`. Design review with the user replaced it, for three
reasons:

- **Lineages are a graph.** For example, the Zaku II has many variants, and the Hi-Zack descends from
  both the Zaku and GM lines.
- **Parts are entities.** Pages for things like "60mm Vulcan Gun" or "Luna Titanium Alloy" need to list
  every suit that uses them.
- **Characters and organizations span many series.** Pages for Amuro Ray or the EFSF need to list
  series and suits.
- **`spec_claim` broke a standard.** It was a generic key-value table, which RDB-5 forbids.

**Outcome:** about 27 tables in three independently mergeable PRs. Each comes with migrations, factories
and mapping/constraint tests that run against real PostgreSQL. Pydantic entities and facades are
**out of scope**. They arrive in Phase 3 with their first caller, the loader.

**Standards applied:**
- `relational-databases.md` (RDB-*), `postgresql.md` (PG-*)
- `python/sqlalchemy.md` (SQLA-*), `python/alembic.md` (ALEM-*)
- `python/pytest.md` (PYTEST-*), `python/python.md` (PY-5 layout, PY-7 dependency direction)

## Design decisions (agreed)

- **Mobile suits are nodes plus typed edges, with no graph extension.**
  - `mobile_suits` has one row per Fandom page. `mobile_suit_relations` holds directed, typed edges.
  - Families come from `WITH RECURSIVE … CYCLE`.
  - Apache AGE is rejected: managed hosts rarely offer it (PG-12), it has no constraints (RDB-14), and
    SQLAlchemy and Alembic can't model it. The schema stays ready for SQL/PGQ later.
  - "Alternate version" (RX-78-2 vs RX-78-02) is one edge type. `suit_version` is dropped.
- **Specs are typed `spec_sheets`.** Each row is one suit, one source and one configuration.
  - Measurements are in SI units. `raw_infobox` (JSONB) keeps the long tail.
  - **A non-base configuration stores only its differences.** NULL on such a sheet means "same as the
    base sheet", and readers fill gaps from the base.
- **Parts are separate entities**, each with a junction to `spec_sheets`: `armaments`, `equipment`,
  `materials` and `powerplants`.
- **Characters and organizations are one row each.**
  - Series membership is in `*_appearances` junctions.
  - Pilot and organization links reference appearances through **composite foreign keys**, so "piloted
    in work W" implies both the character and the suit appear in W. A NULL `work_id` skips the check
    (MATCH SIMPLE).
  - Organizations nest through `parent_organization_id` (RDB-7). **Note:** revisit if a unit changes
    hands across eras (that would mean moving to an `organization_relations` edge table).
- **Mechanical designers are real people**, so they get their own table, separate from `characters`.
- **Works:**
  - `continuities` is a lookup table with a parent link. "Universal Century (GQ)" sits under "Universal
    Century".
  - `works` has a `work_type` enum. Seasons link to their series through `parent_work_id`.
  - `work_relations` holds edges between works: sequel, compilation, adaptation, remake and side story.
  - `work_short_names` resolves `[MSG]`-style tags.
  - Episode ranges go on `mobile_suit_appearances`.
- **Provenance:**
  - `sources` has one row per upstream page, unique on `(kind, external_id)`. Its current `revision_id`
    is updated in place on re-ingest.
  - `ingest_runs` holds `watermark_at`. The current watermark is the latest successful run's, computed
    rather than stored (RDB-1).
  - The review-list table is deferred to Phase 3.
- **One deliberate deviation from RDB-2.** `mobile_suit_pilots` and `mobile_suit_organizations` are
  three-way links with a nullable `work_id`. They get a surrogate `id` plus
  `UNIQUE NULLS NOT DISTINCT (…)` (PostgreSQL 15+), not a primary key on the foreign-key pair. Record
  this in the model docstring and the migration comment (ALEM-7).

## Conventions every table follows

- **Model files:** `backend/models/<entity>/db.py` with class `<Entity>DB(BaseDB, TimestampsDB)`
  (SQLA-4).
  - Columns are listed alphabetically, then relationships, then `__table_args__` (SQLA-6).
  - Each relationship uses `lazy="raise"` and `back_populates` (SQLA-10).
  - Junction models live in the folder of the side that owns them, e.g. `models/spec_sheet/` holds
    `spec_sheet_armaments`.
- **Inherited columns:** `id` (uuidv7) comes from `BaseDB`, in `backend/db/base_db.py`.
  `created_at` and `updated_at` come from the new `models/mixins/db.py` `TimestampsDB` (SQLA-7).
  Junction tables get `created_at` only (RDB-17).
- **Foreign keys:**
  - Every foreign key states `ondelete` (RDB-15).
  - Every foreign key has `index=True`, unless it leads a primary key or unique constraint (RDB-18,
    SQLA-8). This includes the extra indexes composite foreign keys need.
- **Names:** constraint names come from `NAMING_CONVENTION`. Every `CheckConstraint` is named (SQLA-3).
- **Slugs:** every page-able entity has `slug text UNIQUE` with
  `CHECK slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'`. Name columns get `CHECK char_length(name) > 0`.
- **External IDs:** `fandom_page_id` / `fandom_page_title` are nullable `UNIQUE` columns (RDB-13).
- **Enums:**
  - The `StrEnum`s live in `constants/catalog.py`. Their named types live in `constants/db_types.py`
    (SQLA-11), and values are stored, not names.
  - Migrations create and drop the types explicitly with `create_pg_enum` / `drop_pg_enum` from the
    new `db/migrations/alembic_utilities.py` (ALEM-11). Migrations write enum values as literal lists
    and never import app code (ALEM-9).
- **Wiring each model in:** import it in `db/migrations/env.py` (SQLA-13) and create it with
  `uv run alembic revision --autogenerate -m "Create <table> table"` (ALEM-4, ALEM-5), through the
  `backend-migrations` Compose service.
  - **Review every revision** (ALEM-6): `op.f()` names, enum types created before their table and
    dropped after, and no leftover autogenerate comments.
  - `downgrade()` is the exact reverse (ALEM-8).
  - **One migration per table**, committed together with its model, factory and tests (RDB-31, ALEM-4).
- **Tests and factories for each model:**
  - A factory `_factories/<entity>/db.py` (PYTEST-11, PYTEST-13): defaults are valid, unique columns
    use `factory.Sequence`, `id` uses `LazyFunction(uuid7)`, and foreign keys get no random UUIDs.
  - `models/_tests/<entity>/test_db.py` (SQLA-28, PYTEST-4, PYTEST-5), testing:
    - a mapping round trip;
    - each unique, CHECK and FK `ondelete` behavior, asserting `IntegrityError` `orig.sqlstate` and
      `diag.constraint_name` (RDB-29);
    - test names written as sentences, grouped in classes (PYTEST-7).

## Tables

Notation: `?` marks a nullable column. *E* marks an enum.

**PR A — foundations, works, provenance**
| Table | Key columns and constraints |
| --- | --- |
| `continuities` | name, slug, `parent_continuity_id?` → self (SET NULL), CHECK not self |
| `works` | title, `title_ja?`, slug, `work_type` *E* (tv_series, film, ova, ona, manga, novel, video_game, other), `continuity_id?` (SET NULL), `start_date?`/`end_date?` date with CHECK end ≥ start, `parent_work_id?` → self (SET NULL, CHECK not self), `wikidata_qid?` (unique, CHECK `^Q[0-9]+$`), `anilist_id?`/`ann_id?` int unique, `fandom_page_title?` unique |
| `work_short_names` | PK `short_name`, `work_id` (CASCADE, indexed) |
| `work_relations` | PK (`from_work_id`, `to_work_id`, `relation_type` *E*: sequel_of, compilation_of, adaptation_of, remake_of, side_story_of), CASCADE, CHECK from ≠ to, index `to_work_id`, `created_at` |
| `sources` | `kind` *E* (fandom_page, wikidata_item, wikipedia_page), `external_id`, UNIQUE (kind, external_id), `url`, `license` *E* (cc_by_sa_3_0, cc_by_sa_4_0, cc0_1_0), `revision_id?` bigint, `retrieved_at` |
| `ingest_runs` | `source_kind` (same enum type as `sources.kind`), `status` *E* (running, succeeded, failed), `started_at`, `finished_at?` (CHECK ≥ started_at), `watermark_at?`, `pages_seen`/`rows_written`/`error_count` int default 0, CHECK ≥ 0, `error_summary?` (sqlstate and constraint names only), index (source_kind, status, started_at) |

**PR B — mobile suits, specs, parts**
| Table | Key columns and constraints |
| --- | --- |
| `mobile_suits` | name, `name_ja?`, `model_number?`, slug, `unit_type` *E* (suit, armor, fighter, man_machine, worker, pod, doll), `continuity_id?` (SET NULL), `fandom_page_id?` int unique |
| `mobile_suit_relations` | PK (`from_mobile_suit_id`, `to_mobile_suit_id`, `relation_type` *E*: variant_of, developed_from, upgrade_of, alternate_version_of), CASCADE, `source_id` (RESTRICT, indexed), CHECK from ≠ to, index `to_mobile_suit_id`, `created_at` |
| `mobile_suit_appearances` | PK (`mobile_suit_id`, `work_id`), CASCADE, `source_id` (RESTRICT), `is_debut` bool default false, `first_episode?`/`last_episode?` int, CHECK 1 ≤ first ≤ last, index `work_id` |
| `spec_sheets` | `mobile_suit_id` (CASCADE), `source_id` (RESTRICT, indexed), `configuration?` (CHECK ≠ ''), UNIQUE NULLS NOT DISTINCT (mobile_suit_id, source_id, configuration); double precision measurements, each with CHECK > 0: `head_height_m?`, `overall_height_m?`, `empty_weight_kg?`, `gross_weight_kg?`, `generator_output_kw?`, `total_thrust_kg?`, `sensor_range_m?`, `max_acceleration_g?`, `max_speed_kmh?`, `turn_time_s?`; `raw_infobox` jsonb default '{}' |
| `armaments` / `equipment` / `materials` / `powerplants` | name, slug, `fandom_page_title?` unique |
| `spec_sheet_armaments` | PK (`spec_sheet_id`, `armament_id`, `mount` *E*: fixed, handheld, optional_fixed, optional_handheld), `quantity_min?`/`quantity_max?` with CHECK 1 ≤ min ≤ max, `note?`; sheet CASCADE, armament RESTRICT, index `armament_id` |
| `spec_sheet_equipment` | PK (sheet, equipment, `fit` *E*: standard, optional), `note?` |
| `spec_sheet_materials` | PK (sheet, material, `material_use` *E*: armor, frame), `note?` |
| `spec_sheet_powerplants` | PK (sheet, powerplant), `quantity_min?`/`quantity_max?`, `note?` |

**PR C — people and organizations**
| Table | Key columns and constraints |
| --- | --- |
| `characters` / `mechanical_designers` | name, `name_ja?`, slug, `fandom_page_title?` unique |
| `organizations` | name, slug, `fandom_page_title?`, `parent_organization_id?` → self (SET NULL, CHECK not self) |
| `character_appearances` / `organization_appearances` | PK (entity_id, work_id), CASCADE, `source_id` (RESTRICT), index `work_id` |
| `mobile_suit_pilots` | surrogate `id`, `mobile_suit_id`, `character_id`, `work_id?`, `source_id`; UNIQUE NULLS NOT DISTINCT (suit, character, work); composite FKs (character_id, work_id) → `character_appearances` and (mobile_suit_id, work_id) → `mobile_suit_appearances` (CASCADE), each with an index |
| `mobile_suit_organizations` | same shape, plus `role` *E* (manufacturer, operator, developer) in the unique key; composite FKs to `organization_appearances` and `mobile_suit_appearances` |
| `mobile_suit_designers` | PK (`mobile_suit_id`, `mechanical_designer_id`), CASCADE / RESTRICT, index designer |

## Implementation order, checkpoints and PRs

Under the global CLAUDE.md, every **Checkpoint** is a stop-and-report. The user commits (or runs
`/commit`), and the messages below are suggestions in the `COMMIT_CONVENTIONS.md` format.

### PR A — `feat(backend): add catalog foundations, works and provenance tables`
Branch: the current `feat/backend-database-setup`.

0. **Docs alignment** (Checkpoint → `docs(docs): plan the phase 1 catalog schema`):
   - Done when this plan was saved: this file, plus a reference and summary in `data-ingestion.md`
     covering Phase 1 and the Phase 3 scope addition.
   - Done: ADR 0002's data rules were amended to the new schema. Typed `spec_sheets` replace
     `spec_claim`, parts, characters and organizations are entities, and lineages are typed edges.
1. **Dependencies:** `uv add --dev factory-boy` (Checkpoint → `build(deps): add factory-boy to the
   backend dev group`).
2. **Test support** (Checkpoint → `test(backend): add factory base classes and fixed instants`):
   - `_mocks/temporal.py` (`get_mock_utcnow()` = 2026-04-20T11:15:00Z, PYTEST-18)
   - `_factories/base_meta.py` (`BaseMetaFactory[T]`)
   - `_factories/mixins/timestamps.py` (`TimestampsDBMixinFactory`)
   - a `mock_utcnow` fixture in `backend/conftest.py`
   - every new folder gets an `__init__.py`
3. **Layout and helpers** (Checkpoint → `feat(backend): add the timestamps mixin, enum helpers and
   model packages`):
   - `models/__init__.py`, `models/mixins/db.py`, `constants/catalog.py`, `constants/db_types.py`
   - `db/migrations/alembic_utilities.py` (`create_pg_enum`, `drop_pg_enum`)
   - `pyproject.toml`: add `constants` and `models` to `[tool.hatch.build.targets.wheel] packages`
     (PY-5)
   - `pytest.ini` and `pytest.ci.ini`: add `models` to `testpaths`
4. **Tables, one checkpoint each** (Checkpoint → `feat(backend): add the <table> table`):
   `continuities` → `works` → `work_short_names` → `work_relations` → `sources` → `ingest_runs`.
   Each checkpoint includes its model, migration, factory, tests and `env.py` import.
5. **Migration chain checks** (Checkpoint → `test(backend): require one migration head and no pending
   autogenerate`). In `db/_tests/test_migrations.py`:
   - tighten `<= 1` to `== 1` heads;
   - add a test that runs `command.check(alembic_config())` (ALEM-14). The repo has no CI workflow
     yet, so the test suite is where this check runs.

### PR B — `feat(backend): add mobile suit, spec sheet and part tables`
Branch: `feat/add-mobile-suit-schema`, off `main` after PR A merges.
- One checkpoint per table: `mobile_suits` → `mobile_suit_relations` → `mobile_suit_appearances` →
  `spec_sheets` → `armaments` + `spec_sheet_armaments` → the same for equipment, materials and
  powerplants. Each part table and its junction can share a commit, with two migrations.
- Extra tests:
  - a `WITH RECURSIVE … CYCLE` family query over a small fixture graph (Zaku II → Worker Zaku;
    Zaku II + GM → Hi-Zack). This proves the edge design and the cycle guard.
  - the `NULLS NOT DISTINCT` unique key rejects a second base sheet.

### PR C — `feat(backend): add character, organization and designer tables`
Branch: `feat/add-people-and-organization-schema`, off `main` after PR B merges.
- One checkpoint per table: `characters` → `organizations` → `mechanical_designers` →
  `character_appearances` / `organization_appearances` → `mobile_suit_pilots` →
  `mobile_suit_organizations` → `mobile_suit_designers`.
- Extra tests for the composite foreign keys:
  - a pilot row with a `work_id` that has no matching appearance fails with sqlstate `23503`;
  - a NULL `work_id` is accepted;
  - deleting an appearance cascades to its pilot rows.
- Also test the recursive sub-unit query for organizations.

## Risks to check during implementation

- **factory-boy and pyright strict:** factory-boy ships no type information. Use `BaseMetaFactory`
  and the per-file `# pyright: reportIncompatibleVariableOverride=false` from PYTEST-11. If strict
  mode still complains, report it rather than adding suppressions (PY-10).
- **Autogenerate gaps:**
  - It may not render `postgresql_nulls_not_distinct`, composite FKs or named CHECKs exactly as
    modeled. Hand-edit and verify in `psql` (`\d+ <table>`).
  - `alembic check` must then show no diff.
- **Shared enum type:** `ingest_runs.source_kind` reuses the `source_kind` type, so its migration
  references the type with `create_type=False` and does not drop it.

## Verification (each PR)

- Prefix every moon command with `export PATH="$HOME/.proto/shims:$HOME/.proto/bin:$PATH"` (proto is
  not on PATH on this machine).
- **Tests:** `moon run backend:test` runs pytest in the `backend-test` Compose project against a
  fresh PostgreSQL 18. It covers:
  - the migration upgrade at session start;
  - the downgrade-to-base / upgrade-to-head round trip;
  - one head, and `alembic check`;
  - every `test_db.py`.
- **Lint and types:** `moon run backend:lint backend:format backend:typecheck` (Ruff and pyright
  strict).
- **Development database:**
  - `docker compose --profile tools run --rm backend-migrations upgrade head`, then `downgrade base`
    and `upgrade head` again.
  - Spot-check names in `psql`, e.g. `spec_sheets_mobile_suit_id_fkey`,
    `ck_works_end_after_start`, `ix_mobile_suit_relations_to_mobile_suit_id`.
