# Plan: Phase 1 PR B: mobile suit, spec sheet and part tables

## Context

Phase 1 of [`data-ingestion.md`](data-ingestion.md)
splits the catalog schema into three PRs. Only PR A (#16: foundations, works, provenance) has merged.
**PR B is the next one.** Phase 3a's loader writes mobile suits, spec sheets and parts, so PR B
(and PR C after it) must land first.

The table design is already settled in
[`phase-1-catalog-schema.md`](phase-1-catalog-schema.md)
(the "PR B" table and its conventions). This plan turns that design into concrete steps, using the
patterns PR A set up.

**Outcome:** one backend PR, `feat(backend): add mobile suit, spec sheet and part tables`. It adds
11 tables, each with its model, migration, factory and constraint tests run against real
PostgreSQL. It adds no Pydantic entities, facades or ORM relationships; those arrive in Phase 3a
with the loader. Branch: `feat/add-mobile-suit-schema`, off `main`. Per the global CLAUDE.md, you
create the branch and make every commit yourself; each **Checkpoint** below is a stop-and-report.

## Patterns to reuse from PR A

| Need | Reuse |
| --- | --- |
| Entity base / junction base | `BaseDB`, `JunctionBaseDB` in `backend/db/base_db.py` |
| Timestamps | `TimestampsDB`, `CreatedAtDB` in `backend/models/mixins/db.py` |
| Shared CHECKs | `not_empty`, `slug_format`, `not_own_parent` in `backend/models/mixins/checks.py` |
| Enum types | `StrEnum` in `constants/catalog.py`, `Enum(..., values_callable=enum_values, metadata=BaseDB.metadata)` in `constants/db_types.py` |
| Migration enums | `create_pg_enum`, `drop_pg_enum` in `db/migrations/alembic_utilities.py` |
| Edge model template | `backend/models/work_relation/db.py` and its migration `…cf9f30ef9574_create_work_relations_table.py` |
| Entity model template | `backend/models/work/db.py` |
| Factories | `BaseMetaFactory`, `numbered()`, `TimestampsDBMixinFactory`, `CreatedAtDBMixinFactory` (`backend/_factories/`), modeled on `_factories/work/db.py` and `_factories/work_relation/db.py` |
| Constraint assertions | `violated_constraint()` in `backend/models/_tests/integrity.py` |
| Test template | `backend/models/_tests/work_relation/test_db.py`: fixed UUID constants, a fixture that seeds parents, classes `Test<Model>Table` / `Test<Model>` / `Test<Model>Constraints` |
| Chain checks | `db/_tests/test_migrations.py` already checks one head and `alembic check`, so nothing new is needed there |

## Decisions this plan makes (small, flag any you disagree with)

1. **Each junction gets its own model folder** (`models/spec_sheet_armament/db.py`), following PR A's
   `models/work_relation/`. Phase 1's text said junctions live in the owning side's folder; update
   that line to match what PR A actually did.
2. **`__tablename__` overrides:** `table_name_for` would turn `EquipmentDB` into `equipments`, and
   `SpecSheetEquipmentDB` into `spec_sheet_equipments`. Override both to `equipment` and
   `spec_sheet_equipment`, with a comment (SQLA-2).
3. **No `relationship()`s yet.** PR A declares none. They arrive with the facades that need them
   (Phase 3a), with `lazy="raise"` (SQLA-10).
4. **A new `positive(column)` helper** in `models/mixins/checks.py`: `CHECK <col> > 0`, named
   `<col>_positive`. `spec_sheets` alone needs it 10 times. Leave the existing inline checks in
   `works` and `sources` alone.
5. **Two checks that Phase 1 left implicit:**
   - Quantities: `quantity_min >= 1`, `quantity_max >= quantity_min`, and `quantity_max IS NULL OR
     quantity_min IS NOT NULL`, so a max can't appear without a min. Episodes get the same shape
     (`first_episode >= 1`, `last_episode >= first_episode`, last requires first).
   - `raw_infobox`: `CHECK jsonb_typeof(raw_infobox) = 'object'`, so it can't hold an array or scalar.
6. **Not unique:** `mobile_suits.name` and `model_number`. Versions such as RX-78-2 and RX-78-2
   (Ver.Ka) share a model number, and `works.title` set the precedent. `slug` and `fandom_page_id`
   carry the uniqueness.

## Enums (each added in the checkpoint of the table that first uses it)

| StrEnum (`constants/catalog.py`) | PG type | Values |
| --- | --- | --- |
| `UnitType` | `unit_type` | suit, armor, fighter, man_machine, worker, pod, doll (the in-scope SMW `Unit_Type`s; Ship, Vehicle, Weapon and Bit stay out) |
| `MobileSuitRelationType` | `mobile_suit_relation_type` | variant_of, developed_from, upgrade_of, alternate_version_of |
| `ArmamentMount` | `armament_mount` | fixed, handheld, optional_fixed, optional_handheld |
| `EquipmentFit` | `equipment_fit` | standard, optional |
| `MaterialUse` | `material_use` | armor, frame |

Each one gets a docstring and, where it helps, member docstrings (e.g. the read direction for
relation types, as `WorkRelationType` has).

## Implementation order and checkpoints

Every table step follows one recipe:

1. Model `backend/models/<entity>/db.py` (+ `__init__.py`): columns alphabetical, then
   `__table_args__` (SQLA-6). Each FK states `ondelete` and gets `index=True` unless it leads the
   key (RDB-18).
2. Import it in `db/migrations/env.py` (SQLA-13).
3. `docker compose run --rm backend-migrations revision --autogenerate -m "Create <table> table"`.
   Then review it (ALEM-6): `op.f()` names, the enum created before the table and dropped after it,
   a literal value list (ALEM-9), comments on anything non-obvious, and `downgrade()` as the exact
   reverse (ALEM-8).
4. Factory `backend/_factories/<entity>/db.py`: valid defaults, `numbered()` for unique text, `id =
   LazyFunction(uuid7)` on entities, and `None` with a comment for real foreign keys.
5. Tests `backend/models/_tests/<entity>/test_db.py`: a round trip; every unique, CHECK and FK
   `ondelete` behavior asserted through `violated_constraint` (sqlstate and constraint name); a
   `Table` test for junctions (no `id`, PK column order, no `updated_at`).

### 0. Docs (Checkpoint → `docs(docs): plan the phase 1 mobile suit schema`)
- Save this plan as `docs/plans/phase-1b-mobile-suit-schema.md`.
- `phase-1-catalog-schema.md`: link it from the PR B section; change the junction-folder line
  (decision 1); add the extra checks from decision 5 to the PR B table.

### 1. `mobile_suits` (Checkpoint → `feat(backend): add the mobile_suits table`)
- `MobileSuitDB(BaseDB, TimestampsDB)`: `continuity_id?` → continuities (SET NULL, indexed),
  `fandom_page_id?` int unique with `positive`, `model_number?`, `name`, `name_ja?`, `slug` unique,
  `unit_type` (`UNIT_TYPE_DB_TYPE`).
- Checks: `not_empty` on name, name_ja and model_number; `slug_format()`.
- Docstring: one row per Gundam Wiki page; the model number comes from the title prefix.
- Tests also cover deleting a continuity, which sets `continuity_id` to NULL.

### 2. `mobile_suit_relations` (Checkpoint → `feat(backend): add the mobile_suit_relations table`)
- A direct copy of `WorkRelationDB`'s shape: PK (`from_mobile_suit_id`, `relation_type`,
  `to_mobile_suit_id`), both CASCADE, `to_mobile_suit_id` indexed, `source_id` RESTRICT indexed,
  `CHECK from <> to` named `not_self_relation`.
- Docstring: read as "from is a *type* of to"; `alternate_version_of` is written in one direction
  only (the loader picks it in Phase 3a).
- **Extra test file** `models/_tests/mobile_suit_relation/test_families.py`: a
  `WITH RECURSIVE … CYCLE` family query (PostgreSQL 14+ syntax) over a small fixture graph:
  Zaku II ← Worker Zaku (variant_of); Hi-Zack developed_from both Zaku II and GM. It also adds a
  deliberate cycle (A upgrade_of B, B upgrade_of A) to show the `CYCLE` clause stops it. The query
  lives in the test for now; Phase 3a moves it into the facade.

### 3. `mobile_suit_appearances` (Checkpoint → `feat(backend): add the mobile_suit_appearances table`)
- `JunctionBaseDB, CreatedAtDB`: PK (`mobile_suit_id`, `work_id`), both CASCADE, `work_id`
  indexed, `source_id` RESTRICT indexed, `is_debut` bool `server_default=false()`,
  `first_episode?` / `last_episode?` with the decision 5 checks.
- No "one debut per suit" constraint, since a suit can debut in a manga and an anime at once. Say so
  in the docstring.

### 4. `spec_sheets` (Checkpoint → `feat(backend): add the spec_sheets table`)
- `SpecSheetDB(BaseDB, TimestampsDB)`: `configuration?` (`not_empty`), `empty_weight_kg?`,
  `generator_output_kw?`, `gross_weight_kg?`, `head_height_m?`, `max_acceleration_g?`,
  `max_speed_kmh?`, `mobile_suit_id` (CASCADE; leads the unique key, so no separate index),
  `overall_height_m?`, `raw_infobox: dict[str, Any]` (`server_default=text("'{}'::jsonb")`),
  `sensor_range_m?`, `source_id` (RESTRICT, indexed), `total_thrust_kg?`, `turn_time_s?`.
- `positive()` on every measurement, plus the `jsonb_typeof` check.
- `UniqueConstraint("mobile_suit_id", "source_id", "configuration", postgresql_nulls_not_distinct=True)`.
- Docstring: NULL on a non-base sheet means "same as the base sheet"; `raw_infobox` keeps the
  CC BY-SA raw values (ADR 0002).
- Tests: a second base sheet (both `configuration` NULL) for the same suit and source is rejected
  (`23505`, `spec_sheets_mobile_suit_id_source_id_configuration_key`); a second named
  configuration is accepted; deleting the source is blocked (`23001`); deleting the suit cascades.
- Verify the migration in `psql` (`\d+ spec_sheets`) shows `NULLS NOT DISTINCT`; hand-edit
  `postgresql_nulls_not_distinct=True` into the revision if autogenerate drops it.

### 5–8. Parts, one checkpoint each, with two migrations per checkpoint
- 5: `armaments` + `spec_sheet_armaments` (Checkpoint → `feat(backend): add the armament tables`)
- 6: `equipment` + `spec_sheet_equipment` (Checkpoint → `feat(backend): add the equipment tables`)
- 7: `materials` + `spec_sheet_materials` (Checkpoint → `feat(backend): add the material tables`)
- 8: `powerplants` + `spec_sheet_powerplants` (Checkpoint → `feat(backend): add the powerplant tables`)

Part entity (all four have the same shape): `fandom_page_title?` unique (`not_empty`), `name`
(`not_empty`), `slug` unique (`slug_format`).

Junctions on `JunctionBaseDB, CreatedAtDB`, with columns in alphabetical order (alphabetical
order is the PK order):

| Junction | PK | Other columns |
| --- | --- | --- |
| `spec_sheet_armaments` | (`armament_id`, `mount`, `spec_sheet_id`) | `note?`, `quantity_min?`, `quantity_max?` |
| `spec_sheet_equipment` | (`equipment_id`, `fit`, `spec_sheet_id`) | `note?` |
| `spec_sheet_materials` | (`material_id`, `material_use`, `spec_sheet_id`) | `note?` |
| `spec_sheet_powerplants` | (`powerplant_id`, `spec_sheet_id`) | `note?`, `quantity_min?`, `quantity_max?` |

- The part FK is RESTRICT; `spec_sheet_id` is CASCADE and indexed, since it does not lead the key.
- There's no `source_id`: the sheet's source covers its part links (Phase 1's stated exception).
  Say so in each docstring.
- `note` gets `not_empty`.
- Tests: one armament can be listed on a sheet as both fixed and handheld; a duplicate
  (part, mount, sheet) is rejected; deleting a part that a sheet still lists is blocked (`23001`);
  deleting the sheet cascades; the quantity checks behave as decision 5 describes.

### PR: `feat(backend): add mobile suit, spec sheet and part tables`
Fill in `.github/pull_request_template.md`. You open it, after step 8.

## Risks to check during implementation

- **Autogenerate rendering:** `postgresql_nulls_not_distinct`, the `jsonb` server default and
  `server_default=false()` may render imperfectly. Hand-edit, check `\d+`, and the existing
  `alembic check` test must still pass.
- **Enum ownership:** each new enum type is created and dropped by the migration of the first
  table that uses it. None are shared across tables in this PR.
- **`table_name_for` plurals:** confirm `MaterialDB` → `materials` and `PowerplantDB` → `powerplants`
  in each `Table` test, not only the `equipment` overrides.
- **pyright strict on factories:** use the `# pyright: reportIncompatibleVariableOverride=false`
  header, as PR A's factories do; report rather than suppress anything new (PY-10).

## Verification

- Prefix moon with `export PATH="$HOME/.proto/shims:$HOME/.proto/bin:$PATH"`.
- `moon run backend:lint backend:format backend:typecheck`.
- `moon run backend:test`: fresh PostgreSQL 18, migrations at session start, the downgrade-to-base
  round trip, one head, `alembic check`, and every new `test_db.py` plus `test_families.py`.
- On the dev database: `moon run backend:migrate`, then through `backend-migrations`
  `downgrade base` and `upgrade head`. In `psql`, spot-check `\d+ spec_sheets`,
  `\d+ spec_sheet_armaments`, `ix_mobile_suit_relations_to_mobile_suit_id` and
  `ck_spec_sheets_head_height_m_positive`.
- `moon run ingest:test` still passes, since its schema guard compares against the new head.
