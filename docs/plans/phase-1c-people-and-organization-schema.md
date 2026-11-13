# Plan: Phase 1 PR C: character, organization and designer tables

## Context

Phase 1 of [`data-ingestion.md`](data-ingestion.md) splits the catalog schema into three PRs.
PR A (#16: foundations, works, provenance) and PR B (#22: mobile suits, spec sheets, parts) have
merged. **PR C is the last one.** Phase 3a's loader writes pilots, operators and designers, so it
must land first.

The table design is already settled in
[`phase-1-catalog-schema.md`](phase-1-catalog-schema.md)
(the "PR C" table and its conventions). This plan turns that design into concrete steps, using the
patterns PRs A and B set up, and the decisions PR B's review added.

**Outcome:** one backend PR, `feat(backend): add character, organization and designer tables`. It
adds 8 tables, each with its model, migration, factory and constraint tests run against real
PostgreSQL. It adds no Pydantic entities, facades or ORM relationships; those arrive in Phase 3a
with the loader. Branch: `feat/add-people-and-organization-schema`, off `main`.

## Patterns to reuse from PRs A and B

| Need | Reuse |
| --- | --- |
| Entity base / junction base | `BaseDB`, `JunctionBaseDB` in `backend/db/base_db.py` |
| Timestamps | `TimestampsDB`, `CreatedAtDB` in `backend/models/mixins/db.py` |
| Shared CHECKs | `not_empty`, `slug_format`, `not_own_parent` in `backend/models/mixins/checks.py`; names use full column names (SQLA-3, settled in PR B review) |
| Shared columns | `PartDB` in `backend/models/mixins/part.py` is the template for a column mixin that builds its checks per table |
| Self-referencing parent | `backend/models/continuity/db.py` and its tests |
| Appearance template | `backend/models/mobile_suit_appearance/db.py` and its tests |
| `NULLS NOT DISTINCT` unique key | `backend/models/spec_sheet/db.py` |
| Explicitly named multi-column index | `backend/models/ingest_run/db.py` (the `ix` convention would repeat the table name per column) |
| Recursive query test | `backend/models/_tests/mobile_suit_relation/test_families.py` |
| Enum types | `StrEnum` in `constants/catalog.py`, `Enum(..., values_callable=enum_values, metadata=BaseDB.metadata)` in `constants/db_types.py`; `create_pg_enum` / `drop_pg_enum` in migrations |
| Factories | `BaseMetaFactory`, `numbered()`, `TimestampsDBMixinFactory`, `CreatedAtDBMixinFactory` |
| Constraint assertions | `violated_constraint()` in `backend/models/_tests/integrity.py` |

## Decisions this plan makes

1. **A `PersonDB` mixin** in `models/mixins/person.py`, shared by `characters` and
   `mechanical_designers`: `fandom_page_title?` unique, `name`, `name_ja?`, `slug` unique, with
   `not_empty` on the three text columns and `slug_format()`. Built like `PartDB`.
   `organizations` writes its columns out: it has a parent and no `name_ja`. *Chosen by the user.*
2. **Plain foreign keys alongside the composite ones.** A composite foreign key is MATCH SIMPLE, so
   a NULL `work_id` skips the whole check, including `character_id` (or `organization_id`) and
   `mobile_suit_id`. So `mobile_suit_pilots` and `mobile_suit_organizations` also get single-column
   foreign keys to `characters` / `organizations` and `mobile_suits` (CASCADE). Phase 1's table did
   not list them. Each is led by its composite foreign key's index, so it needs no index of its own.
3. **Composite-key indexes are named explicitly** (`ix_mobile_suit_pilots_character_id_work_id`),
   as `ingest_runs` does. The unique key leads with one of them, but not with both columns of
   either composite foreign key, so both get an index (RDB-18).
4. **The role enum is `MobileSuitOrganizationRole`**, PG type `mobile_suit_organization_role`
   (manufacturer, operator, developer), named after its table as the relation types are.
5. **The appearance tables are two checkpoints**, not one, since each is a table on its own.
6. **`organizations.fandom_page_title` is unique**, as the conventions require of every external
   ID (Phase 1's table left the word out).
7. *Changed during implementation:* the `mobile_suit_organizations` unique key is named
   `mobile_suit_organizations_link_key` by hand. The derived name,
   `mobile_suit_organizations_mobile_suit_id_organization_id_role_work_id_key`, is 73 characters,
   over PostgreSQL's 63-character identifier limit.

## Implementation order and checkpoints

Every table step follows PR B's recipe: model (columns alphabetical, then `__table_args__`), import
in `db/migrations/env.py`, autogenerate through `backend-migrations` and review the revision
(ALEM-6, ALEM-8, ALEM-9), factory, then tests with `violated_constraint`. Per the user's grant,
each checkpoint is committed as it passes.

### 0. Docs (`docs(docs): plan the phase 1 people and organization schema`)
- Save this plan; link it from the PR C section of `phase-1-catalog-schema.md`, and add decisions 2
  and 6 to its PR C table.

### 1. `characters` (`feat(backend): add the characters table`)
- Adds the `PersonDB` mixin. `CharacterDB(BaseDB, TimestampsDB, PersonDB)`.
- Docstring: one row per character, however many series they appear in.

### 2. `organizations` (`feat(backend): add the organizations table`)
- `fandom_page_title?` unique, `name`, `parent_organization_id?` → self (SET NULL, indexed,
  `not_own_parent`), `slug` unique. Checks: `not_empty` on name and page title, `slug_format()`.
- Docstring: the revisit note from Phase 1 (a unit that changes hands across eras would need an
  `organization_relations` edge table).
- **Extra test file** `models/_tests/organization/test_hierarchy.py`: a `WITH RECURSIVE … CYCLE`
  sub-unit query over Earth Federation Forces → Titans → Titans Test Team, with the Principality
  of Zeon outside it, plus a deliberate two-row parent loop that the `CYCLE` clause stops.

### 3. `mechanical_designers` (`feat(backend): add the mechanical_designers table`)
- `MechanicalDesignerDB(BaseDB, TimestampsDB, PersonDB)`. Docstring: real people, kept apart from
  `characters`.

### 4. `character_appearances` (`feat(backend): add the character_appearances table`)
- `JunctionBaseDB, CreatedAtDB`: PK (`character_id`, `work_id`), both CASCADE, `work_id` indexed,
  `source_id` RESTRICT indexed.

### 5. `organization_appearances` (`feat(backend): add the organization_appearances table`)
- Same shape: PK (`organization_id`, `work_id`).

### 6. `mobile_suit_pilots` (`feat(backend): add the mobile_suit_pilots table`)
- `BaseDB, CreatedAtDB` (the deliberate RDB-2 deviation; still a link, so `created_at` only,
  RDB-17): `character_id`, `mobile_suit_id`,
  `source_id` (RESTRICT, indexed), `work_id?`.
- `UNIQUE NULLS NOT DISTINCT (character_id, mobile_suit_id, work_id)`.
- Composite FKs (CASCADE): (`character_id`, `work_id`) → `character_appearances`,
  (`mobile_suit_id`, `work_id`) → `mobile_suit_appearances`, each with a named index; plain FKs
  per decision 2.
- The docstring and the migration comment record the deviation and MATCH SIMPLE (ALEM-7).
- Tests: a `work_id` with no matching appearance (for the character, and for the suit) fails with
  `23503`; a NULL `work_id` is accepted, but a second NULL row for the same pair is rejected
  (`23505`); a NULL-work row still needs a real character and suit; deleting either appearance
  cascades; deleting the source is blocked (`23001`).

### 7. `mobile_suit_organizations` (`feat(backend): add the mobile_suit_organizations table`)
- Same shape, plus `role` in the unique key: `UNIQUE NULLS NOT DISTINCT (mobile_suit_id,
  organization_id, role, work_id)`; composite FKs to `organization_appearances` and
  `mobile_suit_appearances`. Adds the role enum.
- Tests as step 6, plus: one organization can be manufacturer and operator of one suit.

### 8. `mobile_suit_designers` (`feat(backend): add the mobile_suit_designers table`)
- `JunctionBaseDB, CreatedAtDB`: PK (`mechanical_designer_id`, `mobile_suit_id`), designer RESTRICT,
  suit CASCADE, `mobile_suit_id` indexed, `source_id` RESTRICT indexed.
- Tests: deleting a designer a suit still cites is blocked (`23001`); deleting the suit cascades.

### PR: `feat(backend): add character, organization and designer tables`
Fill `.github/pull_request_template.md`, assign and label it as #22 was, request Copilot, run
`/code-review` against `main` with this plan as the spec, answer every thread, then squash-merge
(*chosen by the user*).

## Risks to check during implementation

- **Autogenerate and composite FKs:** check the rendered `ForeignKeyConstraint` column order and
  `ondelete`, and that `alembic check` shows no diff afterward.
- **Table order in a migration:** the pilot and organization links need the appearance tables
  first; the revision chain already gives that.
- **CASCADE through two paths:** deleting a character removes its pilot rows through both the plain
  and the composite FK. Test it rather than assume it.
- **CHECK names are invisible to Alembic** (PR B lesson): keep the `violated_constraint` name
  assertions, which are the only guard.
- **Docstring width (W505):** 72 columns.

## Verification

- Prefix moon with `export PATH="$HOME/.proto/shims:$HOME/.proto/bin:$PATH"`.
- `moon run backend:lint backend:format backend:typecheck`.
- `moon run backend:test`: migrations, the downgrade-to-base round trip, one head, `alembic check`,
  every new `test_db.py` and `test_hierarchy.py`.
- Dev database: `upgrade head`, `downgrade base`, `upgrade head` through `backend-migrations`; in
  `psql`, `\d mobile_suit_pilots` shows both composite FKs and `NULLS NOT DISTINCT`.
- `moon run ingest:test` still passes against the new head.
