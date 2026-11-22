# Plan: PR D — suit parts on spec sheets

Branch `feat/add-suit-parts-read` (created from `main` at `06f8401`). PR title:
`feat(backend): serve suit parts on spec sheets`. It expands the
[PR D section](catalog-read-api.md#pr-d--featbackend-serve-suit-parts-on-spec-sheets)
of `docs/plans/catalog-read-api.md`. It reuses what PR B (#29) and PR C (#30) built,
including the departures in PR C's **As built**. Q1 to Q7 were settled by grilling on
2026-11-22.

## Context

The suit detail serves each spec sheet's measurements, but not the parts it lists. Phase 1
(#22) built the four part tables and their spec sheet junctions. None of them has an entity
or a facade yet, and no route reads them. D5 said that parts wait for PR D, nested under
each spec sheet. Under D6, parts need no source of their own: a junction takes its sheet's
source.

**Facts checked in the repo:**

- **Part tables:** `armaments`, `equipment`, `materials` and `powerplants` share `PartDB`
  (`models/mixins/part.py`): `name`, `slug` (unique) and `fandom_page_title?` (unique),
  plus `TimestampsDB`. They have no `fandom_page_id`, no slug redirect table and no
  `relationship()`.
- **Junctions** are `JunctionBaseDB` + `CreatedAtDB`, with no `source_id`:
  - `spec_sheet_armaments`: key (armament, `mount`, sheet); `note?`, `quantity_min?`,
    `quantity_max?`. `ArmamentMount` is `fixed`, `handheld`, `optional_fixed` or
    `optional_handheld`.
  - `spec_sheet_equipment`: key (equipment, `fit`, sheet); `note?`. `EquipmentFit` is
    `standard` or `optional`.
  - `spec_sheet_materials`: key (material, `material_use`, sheet); `note?`.
    `MaterialUse` is `armor` or `frame`.
  - `spec_sheet_powerplants`: key (powerplant, sheet); `note?`, `quantity_min?`,
    `quantity_max?`.
  - Each `spec_sheet_id` is indexed (RDB-18). The enums are native Postgres enums
    (`constants/db_types.py`), so `ORDER BY mount` follows their declared order.
- **Factories** exist for all eight tables (`backend/_factories/`). So do `test_db.py`
  tests, and `models/_tests/spec_sheet_parts.py` holds their shared setup.
- **PR C's page ID precedent:**
  - `PersonDB` (`models/mixins/person.py`) declares `fandom_page_id: int | None`, unique
    and `positive`.
  - Migration `2026_11_21_2227-6da74e12d9d0_add_fandom_page_id_to_people_tables.py` adds
    the column, a unique constraint and a check per table.
  - Facades upsert on `slug` (`models/character/facade.py:125`).
- **Suit detail:** `MobileSuitFacade.get_one_by_slug` costs 7 statements
  (`models/_tests/mobile_suit/test_facade.py:373`). `_get_spec_sheets` loads the suit's
  sheets in one query and fills a named sheet's gaps from the same source's base sheet,
  through `_filled_sheet`, recording what it filled in `inherited_fields`.
- **Patterns to reuse:**
  - Junction facades in the shape of `MobileSuitDesignerFacade`
    (`models/mobile_suit_designer/facade.py`), with `select(Junction, Part)` and an
    explicit join. Because parts have no `source`, no `relationship()` or lazy-raise test
    is needed.
  - `BaseFacade._upsert` with its no-change guard, for the seed.
  - Ref entities in the shape of `MechanicalDesignerRefEntity` (`{name, slug}`).
  - `count_statements` (PYTEST-24).
- **The seeded suits' parts in the dump** (2026-11-15, SHA `89a91167…`):
  - RX-78-2 and RX-78-02 list a powerplant, armor, standard equipment and all four mounts.
  - The Zaku II lists armor and all four mounts, but no powerplant.
  - RX-78F00 lists no parts.
  - Entries carry `N ×` and `1-2 ×` counts and `~notes`. Some also carry `-sub-items` and
    `[Work]` tags.
  - Few parts have their own article: Luna Titanium Alloy (page 3877), Core Block System
    (8697), Vulcan Gun (3606) and Beam Saber (2405). "Beam Rifle" and "Minovsky
    Ultracompact Fusion Reactor" are redirects to list sections.
- **No route code changes.** `MobileSuitResponse` wraps `MobileSuitDetailEntity`, so the
  new fields reach the contract through the entity.

## Decisions (grilled 2026-11-22)

- **Q1 — Each item nests a part ref** beside the junction's own columns, as PR C's credits
  do:
  - `armaments[]`: `{armament: {slug, name}, mount, quantity_min, quantity_max, note, created_at}`
  - `equipment[]`: `{equipment: {slug, name}, fit, note, created_at}`
  - `materials[]`: `{material: {slug, name}, material_use, note, created_at}`
  - `powerplants[]`: `{powerplant: {slug, name}, quantity_min, quantity_max, note, created_at}`

  This amends the parent plan's "part cards": cards wait for a future part list route,
  and a sheet nests refs. `created_at` is the listing's.
- **Q2 — Named configurations inherit parts, in a separate field.** A named sheet with no
  rows of a kind takes the same source's base sheet list of that kind. It names the kind in
  a new `inherited_parts: list[SpecSheetPartKind]`, where `SpecSheetPartKind` is
  `Literal["armaments", "equipment", "materials", "powerplants"]`. `inherited_fields`
  stays measurements-only, so the frontend's `SpecSheetField` alias keeps its meaning.
  - Known limit, noted for 3a: a named configuration can't say it drops every part of a
    kind.
- **Q3 and Q7 — A representative seed of real rows** (option A, about 25 junction rows),
  every one read from the dump. Sub-items and `[Work]` tags are skipped, since parsing
  them is 3a's job. † marks a real article, which gets its title and page ID.
  - **RX-78-2 (base sheet):**
    - powerplant: Minovsky Ultracompact Fusion Reactor;
    - armor: Luna Titanium Alloy†;
    - standard equipment: Core Block System† and Magnet Coating (`field upgrade`);
    - fixed: 2 × 60mm Vulcan Gun;
    - handheld: BOWA-XBR-M-79-07G Beam Rifle and 2 × Beam Saber† (`2 x Beam Javelin`);
    - optional handheld: 1-2 × BLASH-XHB-L-03/N-STD 380mm Hyper Bazooka.
  - **The RX-78-2's Magnet Coating sheet** has no rows of its own, so it inherits all four
    kinds.
  - **RX-78-02:**
    - powerplant: the same reactor;
    - armor: the same alloy;
    - standard equipment: Core Block System (`refit`);
    - fixed: 2 × Vulcan Gun† and 1-2 × Beam Saber;
    - handheld: Beam Rifle;
    - optional fixed: Shoulder Cannon.
  - **Zaku II:**
    - armor: Super Hard Steel Alloy;
    - fixed: Shoulder Shield;
    - handheld: 120mm Machine Gun and Heat Hawk;
    - optional fixed: 2 × 3-tube Missile Pod;
    - optional handheld: MMP-80 90mm Machine Gun.
  - **RX-78F00:** none.
  - Optional equipment and frame materials aren't in these infoboxes, so only the factory
    tests cover them. Mixed inheritance is covered the same way.
- **Q4 — One facade per table**, following PR C and SQLA-16.
  - Four junction facades: `SpecSheetArmamentFacade`, `SpecSheetEquipmentFacade`,
    `SpecSheetMaterialFacade` and `SpecSheetPowerplantFacade`. Each has
    `get_for_sheets`, plus `create_or_update` from step 5.
  - Four part facades: `ArmamentFacade`, `EquipmentFacade`, `MaterialFacade` and
    `PowerplantFacade`, with `create_or_update` only, on `slug`.
- **Q5 — Page IDs now, redirect tables later.** `PartDB` gains
  `fandom_page_id: int | None`, unique and `positive`, as `PersonDB` has, in one
  migration for the four tables. Redirect tables wait for part detail routes (D2 ties them
  to routes, and D4 rule 3 argues against unread tables). The parent plan notes that 3a
  matches part renames on page ID from the start.
- **Q6 — Order:** by the kind's enum in declared order (mount, fit or `material_use`),
  then the part's name, then its slug (RDB-22). Powerplants go by name, then slug.
- **Default (not grilled):** the empty-list check for inheritance is per kind and per
  source, matching how `_filled_sheet` picks the base sheet.

## Steps (one commit each)

1. **Plan docs** → `docs(docs): plan the suit parts read`
   - Save this plan as `docs/plans/suit-parts-read.md`.
   - Amend `catalog-read-api.md`:
     - D5's "Parts wait for PR D" bullet, for refs and item shapes (Q1) and
       `inherited_parts` (Q2);
     - D2's page ID paragraph, for part page IDs (Q5);
     - the PR D section, for the migration step and refs, not cards.
2. **Page IDs** → `feat(backend): track page IDs for spec sheet parts`
   - `fandom_page_id` and its `positive` check go on `PartDB`.
   - An autogenerated migration, modeled on `6da74e12d9d0`, that revises the current head.
   - A `fandom_page_id` sequence on the four part factories, if the person factories
     have one.
   - `test_db.py` cases: unique, positive and nullable.
3. **Entities and read facades** →
   `feat(backend): add entities and facades for spec sheet parts`
   - Per part table, `models/<part>/entity.py`: the full entity and a ref entity.
   - Per junction, `models/spec_sheet_<part>/entity.py`: the full entity and the served
     item (Q1).
   - Per junction, `facade.py`: `get_for_sheets(sheet_ids) -> dict[uuid, list[item]]`,
     one statement, ordered by Q6. An empty id list returns `{}` without a query.
   - Tests: ordering, the empty-list shortcut, and several sheets in one call.
4. **Suit detail** → `feat(backend): add parts to spec sheets in suit details`
   - `MobileSuitSpecSheetEntity` gains the four lists and `inherited_parts`.
     `SpecSheetPartKind` lives in `models/spec_sheet/entity.py`.
   - `_get_spec_sheets` calls the four junction facades with the loaded sheet ids, and
     `_filled_sheet` inherits empty kinds (Q2).
   - The count test goes from 7 to 11, with parts at 1 and 5 rows per kind.
   - Tests:
     - full inheritance;
     - mixed inheritance, where a named sheet's own list wins and the other kinds inherit;
     - no inheritance across sources;
     - a base sheet never inherits.
5. **Seed** → `feat(backend): seed spec sheet parts for development`
   - The four part facades, plus `create_or_update` on the four junction facades, on their
     keys.
   - The Q7 rows go in `seed_dev.py`, and the docstring now names the parts.
   - Tests: the seeded RX-78-2 detail lists its parts, and its Magnet Coating sheet
     inherits them. A rerun changes nothing.
6. **Contract** → `build(frontend): regenerate the API contract for suit parts`
   - `pnpm run api:generate`, and a check that no new field is wrongly optional.
   - MONO-15 aliases:
     - the four ref entities and the four item entities;
     - `ArmamentMount`, `EquipmentFit` and `MaterialUse`;
     - `SpecSheetPartKind`, derived from `inherited_parts`, as `SpecSheetField` is.
   - `mobileSuitMocks.ts`: the Q7 rows on each sheet, with empty-list defaults in the
     `specSheet` helper.
   - Tests, and a one-off comparison against a dump of the seeded API.

## Risks to check during implementation

- **Migration chain (step 2).** Check that `alembic heads` is single after autogenerate,
  and that autogenerate emits only the four columns and their constraints.
- **Defaulted list fields come out optional** unless `json_schema_serialization_defaults_required`
  covers them. Check `api.ts` for `armaments`, `inherited_parts` and the like.
- **`SpecSheetPartKind` may be inlined** in the schema, as `SpecSheetField` is. Derive the
  alias from the field, and don't expect a named component.
- **Statement count.** `get_for_sheets([])` must not query. Otherwise a suit with no
  sheets still costs 11. Pin 11 for a suit with sheets, and 7 for one without.
- **Slugs from part names.** `BLASH-XHB-L-03/N-STD 380mm Hyper Bazooka` has a `/`, and
  `3-tube Missile Pod` and `MMP-80 90mm Machine Gun` mix digits and hyphens. Check every
  seeded slug against `SLUG_PATTERN` before the database's CHECK does.
- **Redirect titles** get a null `fandom_page_title` and page ID, because the title must
  name the part's own page. Record this in As built as a rule for 3a.
- **Counts.** `2 ×` gives min 2 and max 2, and `1-2 ×` gives min 1 and max 2. Check that
  the `quantities` CHECK (`ordered_range`) accepts min = max.
- **Import cycles.** The junction entities import the part refs, and
  `spec_sheet/entity.py` imports the junction items. Keep the part modules free of suit
  imports, as PR C's cycle shows.
- **Shared parts across seeded suits** must be one row each: the reactor, the alloy,
  Core Block and Beam Saber. The seed upserts parts once, then links them by slug.
- **Mirage drift.** The seed exists in two copies again. Step 6's API comparison catches
  drift.

## Verification

- **Backend:**
  - `scripts/backend-test.sh`, which includes the migration round trip and
    `alembic check`.
  - `uv run ruff format --check .`, `uv run ruff check .` and `uv run pyright`, in
    `backend/`.
- **Frontend:** `moon run frontend:typecheck frontend:lint frontend:format frontend:test`.
- **Contract:** `pnpm run api:generate` leaves no diff after step 6.
- **Seed:** `moon run backend:seed-dev`, run twice. The second run changes no `updated_at`.
- **Through the proxy:**
  - `/api/mobile-suits/rx-78-2-gundam` shows the base sheet's parts, and its Magnet
    Coating sheet has `inherited_parts` naming all four kinds;
  - `/api/mobile-suits/ms-06f-zaku-ii` has empty `powerplants`;
  - `/api/mobile-suits/rx-78f00-gundam` has four empty lists.
- **Fixtures:** compare them against a dump of every seeded suit route, with timestamps
  masked.
