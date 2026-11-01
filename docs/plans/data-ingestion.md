# Plan: Data ingestion from Gundam Wiki (Fandom) + Wikimedia

## Context

`docs/research/notes/crawlable-sites.md` and its synthesis `docs/research/trusted-gundam-data-sources.md`
conclude that Docking Bay's data should come from **dumps and APIs, not HTML crawling**:

- **Gundam Wiki (gundam.fandom.com)**: mobile suits, versions, pilots, appearances. CC BY-SA 3.0 text.
  Seeded from a manually downloaded XML dump. The Fandom Terms of Use require written permission for
  any automated access, so `api.php` delta sync waits for that permission (Phase 0).
  Fandom HTML returned 402 (probably Cloudflare), so HTML scraping is out.
- **Continuities** come from the Gundam Wiki's infobox `era` values. Wikidata has no confirmed
  continuity property.
- **Wikidata + Wikipedia**: works (series, films, OVAs), dates, cross-IDs. Wikidata is CC0
  (still to confirm), Wikipedia is CC BY-SA. Requests need an identified User-Agent (2026 rate limits).

**Scope:** Fandom and Wikimedia only. MAHQ and Gundam Unofficial are left for later (see the end).
Ingestion runs as a **separate service** and does batch work only. The API reads from Postgres and never
calls an upstream for a visitor.

**Caveat from the research:** none of the endpoints, rate limits, robots.txt files or infobox fields were
tested live. That is why Phase 0 is a verification spike.

## Architecture decisions

- **New `ingest/` uv project**, a moon project alongside `backend/`. It depends on the backend package by
  path (`msg-docking-bay-backend = { path = "../backend", editable = true }`), so it reuses `db/`
  (`BaseDB`, `DBSessionManager`), `config/` and `utils/logging` instead of copying them.
- **Migrations stay in `backend/db/migrations`**, with one Alembic history. The ingest service only
  writes rows.
- **Upstream modules follow the standards:** one module per upstream at `ingest/services/<upstream>.py`
  (HTTPX-2, SOUP-1), with an explicit User-Agent and timeout (SOUP-3, HTTPX-3), one module error type
  (HTTPX-4) and no live calls in tests (HTTPX-11, using saved fixtures as in SOUP-14).
- **Data model**, from the synthesis's "sourced claims on versioned suits" section: `continuity`, `work`,
  `mobile_suit`, `suit_version`, `spec_claim` (value, unit, source, retrieved_at), `source` (URL,
  revision ID, license), `appearance`, and an `ingest_run` audit table. The tables store facts plus
  attribution. Copied prose is avoided to limit share-alike obligations, and no images are ingested.
- **Runtime:** a CLI (`python -m ingest <source> <mode>`), run through an `ingest` Compose service under a
  `profiles: [ingest]` profile and a `moon run ingest:<task>` task. Scheduling comes in the last phase.

## Phases, commit checkpoints and PRs

Each phase is **one PR off `main`**. The PR title follows the commit-subject format (GIT-5) and the PR
fills in `.github/pull_request_template.md`. The "Checkpoint" lines mark where a commit belongs. Commits are made by hand, not by an
agent: at each checkpoint the agent stops and reports what changed and how it was verified. The commit messages below are
suggestions.

### Phase 0: Verification spike (docs only)
> **Done** (2026-10-31): see [`ingestion-spike.md`](../research/notes/ingestion-spike.md). The Fandom Terms
> of Use require written permission for automated access. **Every Fandom API step in this plan is gated
> on that permission being on file in `docs/research/notes/fandom/`.** Without it, use only manually
> downloaded dumps.

Branch `docs/add-ingestion-spike-findings`. Run these from a normal network (the research sandbox could not reach any of these hosts).
1. Check gundam.fandom.com `robots.txt` and the Fandom ToS scraping clause. Check `api.php?meta=siteinfo&siprop=rightsinfo` for the license.
2. Run `action=parse&page=RX-78-2_Gundam&prop=wikitext` to get the infobox template name and its parameters. Sample about 10 suits across timelines.
3. Check whether a Special:Statistics dump is available and how fresh it is. If none is available, request one through Special:Contact or the wiki's admins and stop. Make no API requests without written permission.
4. Look up Wikimedia's numeric rate limits for identified clients. Run a Wikidata SPARQL test that counts Gundam works and timelines. Confirm the CC0 license.
5. Save sample responses as test fixtures for later phases.
- **Checkpoint → commit** `docs(docs): record ingestion verification spike findings` (adds `docs/research/notes/ingestion-spike.md`).
- **Checkpoint → commit** `docs(docs): record the data ingestion architecture decision` (adds `docs/decisions/0002-data-ingestion.md`, an ADR covering the separate service, sources, claims model and licensing).
- **PR 1:** `docs(docs): add ingestion spike findings and ADR`.

### Phase 1: Domain schema (backend)
Branch: the current `feat/backend-database-setup`, which is empty and matches `main`, or a new branch.
Read first: `relational-databases.md`, `postgresql.md`, `python/sqlalchemy.md`, `python/alembic.md`.
- Add the models in `backend/db/models/` on `BaseDB` (`backend/db/base_db.py`): enums for work type, source kind and spec field; units as columns; unique keys on natural identifiers (`fandom_page_id`, `wikidata_qid`); a `source` table with `revision_id`, `license` and `url`.
- Add an Alembic migration, and extend `backend/db/_tests/test_migrations.py` (upgrade, then downgrade).
- **Checkpoint → commit** `feat(backend): add continuity, work and mobile suit models`
- **Checkpoint → commit** `feat(backend): add spec claim, source and ingest run models`
- **Checkpoint → commit** `feat(backend): add migration for the catalog schema`
- **PR 2:** `feat(backend): add the catalog database schema`.

### Phase 2: Ingest service scaffold
Branch `feat/add-ingest-service`.
- **Checkpoint → commit** `chore(repo): add the ingest scope to commit conventions` (`COMMIT_CONVENTIONS.md`, with a matching line in `monorepo.md` if relevant).
- Add the `ingest/` uv project: `pyproject.toml` with ruff and pyright settings copied from `backend/pyproject.toml`, `moon.yml`, `CLAUDE.md` (importing the httpx and bs4 standards), a CLI entry point, an `ingest_run` start/finish wrapper and env vars (`INGEST_USER_AGENT` with a contact address, rate-limit settings).
- **Checkpoint → commit** `feat(ingest): scaffold the ingest CLI and run tracking`
- Add `ingest/Dockerfile`, an `ingest` service in `compose.yaml` (profile `ingest`, depends on postgres plus migrations), a test service in `compose.test.yaml`, and `.env.example` entries.
- **Checkpoint → commit** `build(docker): add the ingest service to Compose`
- **PR 3:** `feat(ingest): add the ingest service scaffold`.

### Phase 3: Gundam Wiki ingestion (two PRs)
**3a. Seed from the dump.** Branch `feat/add-fandom-dump-ingest`. The Fandom Terms of Use require
written permission for any automated access, `api.php` included (see
[`ingestion-spike.md`](../research/notes/ingestion-spike.md)). So the seed comes from a dump file
**downloaded by hand**, and the service makes no requests to Fandom.
- Before this PR: download `gundam_pages_current.xml.7z` by hand. Email Fandom (support@fandom.com) to
  ask for written API permission, and use Special:Contact to request a fresh dump.
- `ingest/services/fandom_dump.py` streams a **local** 7z XML file (`py7zr` with
  `xml.etree.iterparse`). It selects ns-0 pages in the `Mobile Weapons` categories that use
  `{{Infobox/Mobile Weapon}}`.
- `ingest/parsers/fandom_infobox.py` uses `mwparserfromhell`. It handles `[SERIES]` tags, `value~note`,
  `tabs` (for version grouping) and the model number from the title prefix. A per-field unit map
  follows the Property pages (`headheight` in m, `weight` in t, `poweroutput` in kW, `turntime` in s).
  Unit helpers return `None` for unparseable values (SOUP-9 and SOUP-10). Missing required fields raise
  an error (SOUP-12).
- A loader does idempotent upserts into `continuity`, `mobile_suit`, `suit_version`, `spec_claim` and
  `source`, using the dump's revision ID as the attribution anchor.
  - It creates `continuity` rows from the distinct `era` values, such as `Universal Century`,
    `Universal Century (GQ)` and `Ad Stella`.
  - It is scoped by unit `type`. The in-scope list is decided in this PR.
  - It records the newest revision timestamp in the dump as the Fandom **sync watermark**, for 3b.
- Checkpoints: `build(deps): add mwparserfromhell and py7zr to ingest` → `feat(ingest): parse Gundam
  Wiki infoboxes into spec claims` → `feat(ingest): load a Gundam Wiki dump into the catalog`.
- **PR 4:** `feat(ingest): seed mobile suits from a Gundam Wiki dump`.

**3b. API delta sync. Only after Fandom's written permission is on file.** Branch
`feat/add-fandom-api-sync`.
- Record the permission in `docs/research/notes/fandom/`, and record any conditions it sets.
- `ingest/services/fandom_api.py` uses one httpx client (HTTPX-8), serial at about 1 req/s. It reuses
  the 3a parser and loader, and can add SMW `action=ask` for normalized values.
- **Watermark:** the cursor is the newest *upstream* revision timestamp seen. It is stored per source,
  separately from local run times. A dump load sets it; it is never set to "now".
- **Baseline:** run this once when API access is enabled. Compare the current revision IDs of every
  in-scope page against the stored ones (batched `prop=info|revisions`, about 80 calls). Re-fetch pages
  that differ, and add new pages in `Category:Mobile Weapons`. The baseline is needed because the dump
  is 14 months old.
- **Delta:** after the baseline, read `list=recentchanges` from the watermark and re-fetch the changed
  pages in batches with `prop=revisions`.
- **Re-baseline:** if the watermark is older than the wiki's recent-changes retention
  (`$wgRCMaxAge`, 90 days by default; check it at the start of this PR), run the baseline again
  instead of the delta.
- Without permission, this phase becomes "re-run 3a on each fresh dump" and needs no new code.
- Checkpoints: `feat(ingest): add the Gundam Wiki API client` → `feat(ingest): baseline Gundam Wiki
  pages against current revisions` → `feat(ingest): sync Gundam Wiki changes since the watermark`.
- **PR 5:** `feat(ingest): sync Gundam Wiki changes through the MediaWiki API`.

### Phase 4: Wikimedia ingestion
Branch `feat/add-wikimedia-ingest`.
- `ingest/services/wikidata.py` runs SPARQL against query.wikidata.org to get works and cross-IDs (type, dates, QIDs, ANN/AniList IDs, Fandom article ID `P6262`) into `work`. Continuities come from Phase 3a, not from Wikidata.
- `ingest/services/wikipedia.py` uses the Action API (EN and JA) for series-level facts and page links only, with no copied prose.
- A linker matches Fandom suits to works and creates `appearance` rows from the infobox "first appearance" and "appearances" fields. Matches it cannot resolve go to a review list and are not guessed. It also sets each work's continuity from the `era` of the Fandom suits that appear in it. Works whose suits span several eras go to the review list.
- Checkpoints: `feat(ingest): load works and cross-IDs from Wikidata` → `feat(ingest): enrich works from Wikipedia` → `feat(ingest): link mobile suits to their works`.
- **PR 6:** `feat(ingest): ingest works from Wikimedia`.

### Phase 5: Operations and attribution
Branch `feat/add-ingest-scheduling`.
- `ingest run-all` runs the steps in order (Wikidata → Fandom dump or delta → link). A schedule is set (e.g. weekly, via a cron Compose service). Each run records counts and errors in `ingest_run`.
- Attribution: the backend exposes source URL, license and revision per record, through a backend route plus `pnpm api:generate` (MONO-13 to MONO-17).
- A runbook, `docs/ingestion.md`, covers how to run it, how to download and request a dump, how to re-seed and how to review conflicts.
- Checkpoints: `feat(ingest): add the run-all pipeline and schedule` → `feat(backend): expose source attribution on catalog records` → `docs(docs): add the ingestion runbook`.
- **PR 7:** `feat(ingest): schedule ingestion and surface attribution`. This can be split into ingest and backend PRs if it grows.

### Later (out of scope now)
- **MAHQ:** ask Accidental Pilot for permission first. Check `wp-sitemap.xml` and `/wp-json/`. Write `ingest/services/mahq.py` as a polite crawler that adds cross-check `spec_claim`s and flags disagreements for review. The claims model already supports a second source.
- **Gundam Unofficial:** manual spot checks only, unless Mark Simmons gives permission.

## Verification

- **Each PR:** `moon run backend:test` and an `ingest:test` task (pytest in Compose against a fresh Postgres), ruff and pyright strict, and fixture-based parser tests with no network calls (HTTPX-11).
- **Phase 1:** run `moon run backend:migrate` on a clean database, then confirm in `psql` that the migration upgrades and downgrades cleanly.
- **Phase 3a:** load the real dump locally (`docker compose --profile ingest run --rm ingest fandom seed <path>`). Spot-check RX-78-2, RX-78-02 and RX-78F00 as separate versions, each with its spec claims and source revision. Re-run the load and confirm no duplicate rows (idempotency).
- **Phase 3b/4:** run the delta sync twice and confirm the second run is a no-op. Confirm that works such as GQuuuuuuX and Witch from Mercury exist with QIDs and are linked to their suits.
- **Phase 5:** run `run-all` end to end, then inspect `ingest_run` and the attribution fields in an API response.
