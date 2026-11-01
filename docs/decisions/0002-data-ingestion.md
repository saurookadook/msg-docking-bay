# 0002 — How catalog data is ingested

- **Status:** Proposed
- **Date:** 2026-10-31

## Context

Docking Bay needs a catalog of continuities, works and mobile suits. The research
([`trusted-gundam-data-sources.md`](../research/trusted-gundam-data-sources.md),
[`notes/crawlable-sites.md`](../research/notes/crawlable-sites.md)) found no Gundam API worth
depending on. It names the Gundam Wiki on Fandom as the suit source and Wikidata/Wikipedia as the
works source, and it rules out HTML crawling. The verification spike
([`notes/ingestion-spike.md`](../research/notes/ingestion-spike.md)) then found four things:

- The Gundam Wiki runs Semantic MediaWiki. Its `action=ask` API returns typed, unit-normalized infobox
  fields for all 3,976 mobile weapons in one request.
- The Fandom XML dump is 14 months old.
- Fandom HTML and `robots.txt` are behind a Cloudflare challenge, while `api.php` is not.
- robots.txt allows `/api.php?action=`, but the Fandom Terms of Use (revised 2025-12-19) forbid
  "any robot, spider, scraper or other automated means to access the Services for any purpose without
  our express written permission". The wiki text is CC BY-SA, so reuse is fine; automated *fetching*
  needs permission.

MAHQ and Gundam Unofficial are all-rights-reserved and are out of scope for now.

## Options

1. **Ingest inside the backend.** CLI commands in `backend/` sharing its package.
2. **A separate `ingest/` service.** Its own uv project, image and Compose service. It depends on
   the backend package for models and the database session, and migrations stay in the backend.
3. **A scheduled long-running worker.** Option 2 plus an in-process scheduler from the start.

## Decision

**Option 2.** Ingestion is a separate `ingest/` uv project and moon project. It runs as a batch CLI
through a Compose service under the `ingest` profile. It imports `db/`, `config/` and
`utils/logging` from the backend package by path. **The backend owns the schema and Alembic history,
and the ingest service only writes rows.** The API serves from PostgreSQL and never calls an upstream
on a visitor's behalf.

The rules for sources:

- **Gundam Wiki, without permission (now):** a maintainer downloads the "current pages" XML dump by
  hand from Special:Statistics or its S3 link, and asks for a fresh one through Special:Contact (at most
  once every 7 days). The ingest service parses only that local file. It never makes requests to
  `gundam.fandom.com`. Units are inferred per infobox field and kept alongside the raw values.
- **Gundam Wiki, with written permission (later):** once Fandom's written permission is on file
  (record it in `docs/research/notes/fandom/`), add SMW `action=ask` for normalized values and
  `list=recentchanges` for delta sync, serial at about 1 req/s. HTML is never scraped either way.
- **Wikidata (CC0):** works and cross-IDs come from SPARQL. Continuities come from the Fandom `era`
  field.
- **Wikipedia (CC BY-SA):** facts and page links only, never copied prose.
- **Every request** carries a User-Agent of the form
  `msg-docking-bay-ingest/<ver> (+https://github.com/saurookadook/msg-docking-bay) httpx/<ver>`.
  Fandom is read serially at about 1 req/s. Wikimedia stays at or below 200 req/min with at most
  3 concurrent requests and honors `Retry-After`.
- **Nothing tries to get past a bot challenge.** A 403 or a challenge is an error to report, not
  something to work around.

The rules for data:

- **Spec values are stored as claims.** Each claim has a value, a unit, a source and a retrieved-at
  time, and belongs to a suit *version*.
- **Every claim points to a `source` row** that holds the URL, the revision ID and the license.
- **Facts-only boundary:**
  - Normalized facts are stored as data: numbers with units, names, model numbers, dates, and links
    between entities.
  - No images and no article prose are ingested.
  - This keeps the amount of CC BY-SA text small. It does not remove the license's obligations.
- **Retained text keeps its license.** Any raw wikitext value or note kept beside a normalized fact,
  such as `1.1~after magnet coating upgrade`, keeps its source article's CC BY-SA terms. Attribution
  and a license link are always required, and ShareAlike applies when that text is redistributed. The
  `source` row's license field records which terms apply. (General reading, not legal advice.)

## Consequences

- The ingest service needs a second Python image, a second set of tests and a new `ingest` commit
  scope. In return, scraping dependencies and upstream failures stay out of the API process.
- Schema changes for ingestion land in `backend/` PRs before the ingest code that uses them.
- Until permission arrives, the data is only as fresh as the last dump, and refreshes need a manual
  download. The ingest service needs `py7zr` and a streaming XML parser.
- Fandom may refuse permission. The dump route still works in that case, so the decision does not
  depend on the answer.
- If API access is granted, SMW does not replace the wikitext parser: it flattens per-series tags,
  `~` notes and some multi-valued entries. The loader keeps the raw wikitext value next to any
  normalized one.
- Attribution (source URL, license, revision) must be exposed wherever catalog data is shown. This
  is Phase 5 of the plan.
- MAHQ or Gundam Unofficial can be added later as additional claim sources without changing the
  schema. Conflicting claims are flagged for review and never auto-resolved.
