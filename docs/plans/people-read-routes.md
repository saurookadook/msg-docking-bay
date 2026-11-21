# Plan: PR C — people read routes

Branch `feat/add-people-read-routes` (created from `main` at `d4afeb3`). PR title:
`feat(backend): serve characters, organizations and designers`. It expands the PR C section of
`docs/plans/catalog-read-api.md` and reuses what PR B (#29) built. Q1 to Q10 were settled by
grilling on 2026-11-21.

## Context

PR B serves continuities, works and mobile suits. The people and organization tables from Phase 1
PR C (#23) still have no entities, facades or routes. PR C adds them:

- read routes for characters, organizations and mechanical designers;
- pilots, organizations and designers on the suit detail;
- the slug redirect tables and `fandom_page_id` that D2 requires;
- seed and Mirage data for the new rows;
- a regenerated contract.

**Facts checked in the repo:**

- **Models:**
  - `characters` and `mechanical_designers` use `PersonDB` (`models/mixins/person.py`): `name`,
    `name_ja?`, `slug` and `fandom_page_title?`.
  - `organizations` has `parent_organization_id?`, pointing to another organization.
  - `character_appearances` and `organization_appearances` are `JunctionBaseDB` on (entity, work),
    each with a `source_id`.
  - `mobile_suit_pilots` and `mobile_suit_organizations` (`role`: manufacturer, operator,
    developer) are `BaseDB` rows with `work_id?`. A null `work_id` means the work is not recorded.
  - `mobile_suit_designers` is a `JunctionBaseDB` keyed on (designer, suit), with a `source_id`.
  - None of these has a `relationship()`.
- **Reused from PR B:**
  - `models/base/{entity,page,facade}.py`: `_has_slug` and `_current_slug_first`,
    `_search_filter` and `_prefix_rank` with `normalize_search`, and the guarded `_upsert`.
  - `models/mixins/entity.py`.
  - `api/models/pagination.py`, `constants/pagination.py`, and the route shape in
    `api/routes/works.py`.
  - The `count_statements` fixture (PYTEST-24).
  - `backend/scripts/seed_dev.py`.
  - Mirage's `endpoints.ts`, with `paginate` and `notFound`, and `catalogMocks.ts`, which holds
    the shared sources and `mockNow`.
- **Some lists are long.** In the 2026-11-15 dump, `mechdesigner=Kunio Okawara` starts 438
  infoboxes, and `operator=Earth Federation` starts 603. This is why Q1 pages them.
- **The suit detail costs 4 statements now** (`models/_tests/mobile_suit/test_facade.py`).

**Carried over unchanged:**

- D2: slugs and redirects, where a current slug always wins.
- D3: `limit` and `offset`, with a separate count.
- D5: cards and details, with no `id`.
- D6: a source on every fact.
- D8: `q` matches the normalized slug only, for people and organizations.
- Filters match current slugs, and an unknown filter slug gives an empty page.
- Guarded upserts, used by the seed.
- D7: Mirage filters are opt-in.

## Decisions (grilled 2026-11-21)

- **Q1 — Paged sub-resources** for an organization's suits and a designer's suits. Detail responses
  nest no suits, for RDB-23.
- **Q2 — A null `work` in a flat list.** Pilot and organization links carry
  `work: WorkRefEntity | null`, sorted after the known works. They are not grouped.
- **Q3 — A designers list.** Add `GET /api/mechanical-designers`: paginated, with `q`.
- **Q4 — Seed and fixtures grow from the dump**, in both copies, tied to the four seeded suits:
  - characters: Amuro Ray and Amuro Ray (Origin);
  - organizations: the Earth Federation, the Principality of Zeon and Zeonic;
  - designers: Kunio Okawara, Hajime Katoki and Masaki Kawahara;
  - one real wiki redirect on each new table.

  The exact links (roles, works and sources) are read from each suit's infobox.
- **Q5 — Refs in the suit detail.**
  - `pilots[]` is `{character: {slug, name}, work, source, created_at}`.
  - `organizations[]` is `{organization: {slug, name}, role, work, source, created_at}`, ordered
    by role, work and name.
  - `designers[]` is `{mechanical_designer: {slug, name}, source, created_at}`.
- **Q6 — The character detail nests the suits they pilot:**
  `{mobile_suit: card, work, source, created_at}`.
- **Q7 — One item per suit in an organization's suit list:**
  `{mobile_suit: card, links: [{role, work, source, created_at}]}`.
  - `meta.total` counts suits.
  - The page is of distinct suits, ordered by `name, id`. Their links load in one more query.
- **Q8 — Character and organization details nest their appearances:**
  `{work: card, source, created_at}`, first released first.
- **Q9 — `?role=` filters both the suits and their links.**
- **Q10 — The organization detail shows `parent_organization` and `child_organizations`**, as
  refs.

## Routes

| Route | Function | Returns |
| --- | --- | --- |
| `GET /api/characters` | `read_characters_list` | Character cards, paged. Filters: `work`, `q` |
| `GET /api/characters/{character_slug}` | `read_character` | Appearances (Q8) and piloted suits (Q6) |
| `GET /api/organizations` | `read_organizations_list` | Organization cards (each with a parent ref), paged. Filters: `work`, `q` |
| `GET /api/organizations/{organization_slug}` | `read_organization` | Parent and children (Q10), and appearances (Q8) |
| `GET /api/organizations/{organization_slug}/mobile-suits` | `read_organization_mobile_suits` | One item per suit with `links` (Q7). Filter: `role` (Q9) |
| `GET /api/mechanical-designers` | `read_mechanical_designers_list` | Designer cards, paged. Filter: `q` (Q3) |
| `GET /api/mechanical-designers/{mechanical_designer_slug}` | `read_mechanical_designer` | The designer |
| `GET /api/mechanical-designers/{mechanical_designer_slug}/mobile-suits` | `read_mechanical_designer_mobile_suits` | `{mobile_suit: card, source, created_at}`, paged, by name |

- `read_mobile_suit` gains `pilots`, `organizations` and `designers` (Q5). A suit detail then
  costs 7 statements.
- A sub-resource returns 404 for an unknown parent, and follows the parent's old slugs.

## Steps (one commit each)

1. **Redirects and page IDs** → `feat(backend): track slug redirects and page IDs for people`.
   - Three tables, `character_slug_redirects`, `organization_slug_redirects` and
     `mechanical_designer_slug_redirects`, modeled on `models/work_slug_redirect/db.py`.
   - `fandom_page_id` (with `positive`) on `characters`, `organizations` and
     `mechanical_designers`.
   - Autogenerated migrations, the `env.py` `MODELS` list, factories and `test_db.py` tests.
2. **Entities and facades** → `feat(backend): add character, organization and designer entities
   and facades`.
   - `lazy="raise"` relationships, only for what the queries load.
   - For each table:
     - the full, ref, card and detail entities;
     - `get_page`, `get_one_by_slug`, and `get_id_by_slug` (it follows redirects);
     - the sub-resource pages (Q7 and Q9 for organizations, plain for designers);
     - upserts for every row the seed writes.
   - Tests:
     - fixed statement counts at 1 and 5 related rows;
     - a link with no work sorting last;
     - Q9's role filter on both suits and links;
     - old slugs;
     - not found;
     - PYD-3 lazy-raise failures.
3. **Suit detail additions** → `feat(backend): add pilots, organizations and designers to the suit
   detail`.
   - Three more queries in `MobileSuitFacade.get_one_by_slug`. The count test changes to 7.
4. **Routes** → `feat(backend): add character, organization and designer routes`.
   - The eight routes above.
   - Envelopes in `api/models/{character,organization,mechanical_designer}.py`.
   - Route tests and `TestOperationIds`.
5. **Seed** → `feat(backend): seed people and organizations for development`.
   - Q4's rows go into `seed_dev.py`, read from the dump. It is already extracted in the
     scratchpad, with its SHA checked.
   - Tests: every new route has data, and a rerun changes nothing.
6. **Contract** → `build(frontend): regenerate the API contract for people routes`.
   - Run `pnpm run api:generate` and check that no field is wrongly optional.
   - MONO-15 aliases.
   - Fixtures that match the seed:
     - `characterMocks.ts`, `organizationMocks.ts` and `mechanicalDesignerMocks.ts`;
     - additions to `mobileSuitMocks.ts`;
     - `find*Mock` helpers, and old slugs.
   - Endpoint table entries.
   - Tests, and a one-off comparison against a dump of the seeded API.
7. **Plan docs** → `docs(docs): plan the people read routes`.
   - Save this plan as `docs/plans/people-read-routes.md`.
   - Amend `catalog-read-api.md`: the PR C Routes table and the PR C section (Q1, Q3, Q6 to Q10).
   - Amend the "Work-unknown rows" risk (Q2).

## Verification

- **Backend:**
  - `scripts/backend-test.sh`, which includes the migration round trip and `alembic check`.
  - `uv run ruff format --check .`, `uv run ruff check .` and `uv run pyright`.
- **Frontend:** `moon run frontend:typecheck frontend:lint frontend:format frontend:test`.
- **Seed:** `moon run backend:seed-dev`, run twice. The second run changes no `updated_at`.
- **Fixtures:** check them against a dump of every seeded route, with timestamps masked.
- **Through the proxy:**
  - a character's old slug;
  - a 404;
  - a page past the end;
  - `?q=amuro`;
  - `/api/organizations/earth-federation/mobile-suits?role=operator`;
  - the suit detail's new lists.

## As built (2026-11-21)

Where the implementation differs from the steps above:

- **Entity names.**
  - The suit detail's credits are `PilotCreditEntity`, `OrganizationCreditEntity` and
    `DesignerCreditEntity`.
  - An organization's suit items are `OrganizationMobileSuitEntity`, with
    `OrganizationLinkEntity` links. A designer's are `DesignedMobileSuitEntity`.
  - Character and organization appearances share `CitedWorkEntity`.
  - `CharacterDetailEntity` lives in `models/character/detail.py`, apart from the cards, to break
    an import cycle with the suit entities.
- **Link upserts moved to step 5.** `MobileSuitFacade.create_or_update_pilot`,
  `create_or_update_organization` and `create_or_update_designer` landed with the seed, their only
  caller. A null `work_id` upserts onto the same row, because the key treats nulls as equal.
- **`MAX_SEARCH_LENGTH`** moved from the suits route to `constants/pagination.py`, so every `q`
  shares it.
- **Masaki Kawahara has no wiki page.** His row has no page ID or title, and the RX-78F00 page is
  the source for his credit.
- **Mirage.** The cards and refs are in `peopleMocks.ts`, so the suit details can name their
  credits without an import cycle. `characterMocks.ts`, `organizationMocks.ts` and
  `mechanicalDesignerMocks.ts` derive each person's suit list from the suit details.
- **Commit subjects.** Steps 2 and 3 are shorter than planned, to fit the 72-character limit:
  - `feat(backend): add entities and facades for people and organizations`
  - `feat(backend): add pilots, organizations and designers to suit details`
