# Ingestion Verification Spike: Gundam Wiki (Fandom) and Wikimedia

Phase 0 of [`docs/plans/data-ingestion.md`](../../plans/data-ingestion.md). Run on 2026-10-31 (UTC
2026-11-01) from a normal home network. The earlier research could not reach any of these hosts.
Every request used an identified User-Agent, `msg-docking-bay-ingest-spike/0.1
(+https://github.com/saurookadook/msg-docking-bay)`, ran one at a time with a pause between calls, and
sent no browser User-Agent. About 25 requests were made in total.

## Takeaway

> **Update, same day:** the Fandom Terms of Use (read from a saved copy, see below) require **express
> written permission for any automated access**, `api.php` included. Until Fandom grants permission,
> the SMW/API approach described next cannot be used for ingestion. The compliant route is the
> manually downloaded XML dump. The technical findings below are still accurate.

The plan holds, with one big change. **The Gundam Wiki runs Semantic MediaWiki (SMW), and its
`action=ask` API returns every mobile weapon's infobox fields already normalized to SI units, in a single
request.** That makes SMW the primary seed source, not the XML dump. The dump turns out to be 14 months
old (2025-08-26). Raw wikitext is still needed for what SMW drops: per-series tags such as `[MSG]`,
`~` notes, and the version tabs. Wikidata covers works well, with CC0 data and 762 franchise-linked items,
but has only about 50 mobile suits. Fandom HTML, `robots.txt` and the ToS are all behind a Cloudflare
challenge for non-browser clients, while `api.php` is not.

## Gundam Wiki (gundam.fandom.com)

### Access and license
- `api.php` answers with HTTP 200 to an identified UA. Response from
  `meta=siteinfo&siprop=general|rightsinfo|statistics`:
  - Generator: **MediaWiki 1.43.9**
  - License: `rightsinfo` = **"CC-BY-SA"**, linked to `https://www.fandom.com/licensing`. This confirms
    CC BY-SA for the text. The version number is not in the string; Fandom's licensing page says 3.0.
  - Statistics: 10,893 articles, 149,757 pages, 702,668 edits, 120 active users.
- **`/robots.txt` and `www.fandom.com/terms-of-use` both returned 403 to scripts.** The response came
  from `server: cloudflare` with `cf-mitigated: challenge`. A human saved both pages from a browser on
  2026-10-31; the copies are in [`fandom/`](fandom/).

### robots.txt ([`fandom/robots.txt`](fandom/robots.txt))
- `User-agent: *` gets **`Allow: /api.php?action=`** (and the same for each language path). It is
  disallowed from `/wiki/Special:`, `User:`, `Template:` and `Help:`. Article pages are not disallowed.
- **AI crawlers are disallowed from everything:** GPTBot, CCBot, ClaudeBot, OAI-SearchBot, the xAI
  bots, meta-externalagent and others. Our ingest client is not one of them and identifies itself.
  Note, though, that this spike was run by an AI coding agent acting for the maintainer.
- Sitemaps are listed at `https://gundam.fandom.com/sitemap-newsitemapxml-index.xml`.

### Terms of Use ([`fandom/Terms-of-Use.html`](fandom/Terms-of-Use.html), last revised 2025-12-19)
**This is the blocking finding.** robots.txt allows the API, but the Terms of Use forbid automated access
without written permission. Quoted:
- "You further agree: … not use any robot, spider, scraper or other automated means to access the
  Services **for any purpose without our express written permission**".
- Under prohibited uses: "Use any robot, spider, site search and/or retrieval application, or other
  device to scrape, extract, retrieve or index any portion of the content".
- "Without our express, prior written consent, use or copy the content for the development of any
  software program, including, but not limited to, training a machine learning or artificial
  intelligence (AI) system".
- The no-scrape and no-reproduce clause has an exception for community text "as permitted as set forth
  at our licensing page" (CC BY-SA). That exception covers **reusing** the text. It does not appear to
  cover the **automated access** clauses, which are separate list items.
- It also forbids bypassing "measures we may use to prevent or restrict access … including robot
  exclusion headers". The Cloudflare challenge is one such measure, which is why the spike did not try
  to get past it.

**Reading (not legal advice):**
- The CC BY-SA license makes the wiki *text* reusable. The ToS still requires written permission to
  fetch it *by automated means*, including through `api.php`.
- The spike's ~20 requests to `gundam.fandom.com/api.php` were automated access without that
  permission. They were few and slow, and robots.txt allows them, but they are not ToS-compliant.
- Fandom publishes the database dump for anyone to download, and its own help page calls it useful
  "for bot use". **A person downloading the dump and the ingest service parsing the local file** is the
  route that fits the ToS as written.
- `meta=userinfo&uiprop=ratelimits` lists only write-action limits for anonymous users (edit 6/min,
  purge 30/min, …). **No read rate limit is published.** Plan for about 1 req/s with no concurrency, as
  the research recommended.

### Semantic MediaWiki: the main finding
- The namespaces include `Property` (302), `Concept` (308) and `smw/schema` (312), and pages carry SMW
  properties.
- `action=browsebysubject&subject=RX-78-2_Gundam` returns typed properties: `Head_Height` 18,
  `Weight` 43400, `Max_Weight` 60000, `Powerplant_Output` 1380000, `Rocket_Thrust` [24000, 1870],
  `Sensor_Range` 5700, `Turn_Time` (in hours), `First_Seen`/`Last_Seen` dates, `Era`, `Unit_Type`,
  `Pilot`, `Operator`, `Manufacturer`, the armament lists, `Mechanical_Designer` and `Series`.
- **Units are declared on `Property:` pages**, using `Has type::Quantity` with `Corresponds to::`
  conversions:
  - `Head_Height`: base unit m
  - `Weight`: base unit kg (displayed in tonnes)
  - `Powerplant_Output`: base unit W (so the RX-78-2's 1380 kW is stored as 1380000)
  - `Turn_Time`: base unit h
- **Bulk query:** `action=ask&query=[[Category:Mobile Weapons]]|?Unit_Type|limit=5000` returned all
  **3,976** results in one response, with no `query-continue-offset`. Quantity printouts come back as
  `{"value": 10.8, "unit": "m"}`.
- Split by `Unit_Type`: Suit 2,840 · Ship 367 · Vehicle 280 · Armor 188 · Fighter 93 · none 90 ·
  Weapon 34 · Worker 30 · Pod 25 · Man-Machine 16 · Doll 8 · Bit 5.
- Quirks seen:
  - One `Weight` value came back with `unit: "kgkg"` (29H-A-MS Murphy), so units must be normalized
    defensively.
  - **SMW flattens the per-series tags** (`Amuro Ray [MSG]`) and the `~` notes (`19.85~MS mode`,
    `1.1~after magnet coating upgrade`). It also keeps only some multi-valued entries.
  - `Category:Mobile Weapons` reports 3,948 pages and 14 subcategories, while SMW returned 3,976. The
    gap is probably subobjects or subcategory pages and needs checking in Phase 3.

### Infobox (wikitext)
- Sampled 13 pages across 9 eras: RX-78-2, RX-78-02, RX-78F00, MS-06F Zaku II, MSZ-006 Zeta, RX-0
  Unicorn, GMS-Ω GQuuuuuuX (UC), Wing (AC), Shining (FC), Exia (AD), Barbatos (PD), Aerial (AS) and
  Freedom (CE). Every one starts with **`{{Infobox/Mobile Weapon`**. The 14th title, "Gundam Unicorn", is
  a disambiguation page.
- **There is no model-number parameter.** The model number is the prefix of the page title (`MS-06F
  Zaku II`), and `english` holds the display name when it is present.
- Most common parameters: `image`, `type`, `era`, `mechdesigner`, `kanji`, `transformable`,
  `manufacturer`, `operator`, `pilot`, `paccommodation`, `fixedArmaments`, `handheldArmaments`,
  `standardEquipment`, `archetype`, `first`, `armor`, `series`, `usage`, `emptyweight`, `production`,
  `last`, `powerplant`, `tabs`, `optionalHandheldArmaments`, `other names`, `headheight`, `debut`,
  `height`, `weight`, `poweroutput` and `propRocketThrusters`. There is also a long tail of
  era-specific parameters, such as `weightCEBF`, `wingabilitylevels` and `mmi`.
- Value syntax the parser must handle:
  - newline-separated lists
  - `value~note`
  - `name [SERIES-TAG]`
  - `series~firstEp~lastEp`
  - `N × item`
  - `tabs=Page;Label, …`, which links the versions of one suit
- **Versions confirmed as separate pages:** RX-78-2 (rev 706484), RX-78-02 (rev 700004) and RX-78F00
  (rev 665053) each have their own page and infobox. The `tabs` parameter lists all eight related
  versions, which can feed `suit_version` grouping.
- RX-78-2 is in the categories `Mobile_Weapons`, `Universal_Century_Mobile_Weapons` and
  `One_Year_War_Mobile_Weapons`. The subcategories of `Mobile Weapons` include era buckets (After War,
  Anno Domini, Cosmic Era, …), `Mobile Armor`, `Super Deformed Mobile Weapons` and two `… Ships`
  categories.

### Dumps and delta sync
- The S3 dump URLs exist:
  - `https://s3.amazonaws.com/wikia_xml_dumps/g/gu/gundam_pages_current.xml.7z`: 21.0 MB, last
    modified **2025-08-26**
  - `…/gundam_pages_full.xml.7z`: 76.1 MB, same date
- Only an admin can request a new dump. Anyone else must go through Special:Contact, at most once every
  7 days (Fandom Help:Database download, read through the community wiki's `api.php`).
- `list=recentchanges` works (ns 0, with `revid`, `old_revid`, `timestamp` and `rccontinue`), so
  incremental sync from a stored timestamp is practical.

## Wikimedia

### Wikidata
- `meta=siteinfo&siprop=rightsinfo`: "All structured data from the main and property namespace is
  available under the Creative Commons **CC0** License". **CC0 confirmed.**
- Franchise item: **Q732120** "Gundam", described as "science fiction media franchise". The first TV
  series is Q1134906.
- SPARQL over `wdt:P8345` (media franchise) or `wdt:P179` (part of the series) = Q732120 returns **762
  distinct items**, most of them not works. Type counts: anime character 290, fictional human 249, video
  game 185, manga character 174, video game character 130, manga series 85, **mobile suit 50**, anime
  TV series 28, anime film 21, OVA series 10, ONA series 4. Filter on `P31` work types.
- Spot checks:
  - GQuuuuuuX: Q131383827, 2025-04-09
  - Iron-Blooded Orphans: Q20668445, 2015-10-04
  - Hathaway film: Q109289213, 2021-07-01
  - Witch from Mercury is modeled as **seasons** (Q117475449, Q117475450), so the loader has to roll
    seasons up to a work.
- Cross-IDs are sparse: ANN ID (`P1985`) on 50 items, AniList (`P8729`) on 59, **Fandom article ID
  (`P6262`) on 453**. P6262 is a possible join key to Gundam Wiki pages, still to be checked.
- No timeline or continuity property was confirmed. Continuity will probably come from the Fandom `era`
  field rather than Wikidata.

### Wikipedia and Wikimedia rate limits
- `en.wikipedia.org/w/api.php` returned 200 to the identified UA. Its text is CC BY-SA.
- [Wikimedia APIs/Rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits), read through
  the mediawiki.org API, gives per-minute limits that are "new in 2026 and subject to experimentation":
  unidentified **10/min**; **compliant User-Agent 200/min**; authenticated new users 200/min;
  established editors 2,000/min; flagged bots exempt. Best practices: at most **3 concurrent requests**
  and honoring `Retry-After` on 429.
- The [Access policy](https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy) prefers a User-Agent
  of the form `<client>/<version> (<contact: URL or email>) <library>/<version>`.

## Effect on the plan

> The table assumes API access is permitted. Under the Terms of Use it holds only once Fandom has
> granted written permission. Without permission, Phase 3a parses a manually downloaded dump instead,
> and Phase 3b's API delta sync is replaced by periodic fresh dumps.

| Plan item | Change |
| --- | --- |
| Phase 3a "seed from dump" | **Seed from SMW `action=ask`** for typed fields (a few requests), plus batched `prop=revisions` (50 titles per call, about 80 calls) for wikitext. The dump becomes an optional fallback, not a dependency, so `py7zr` and dump streaming are dropped. |
| Units parsing | Use SMW's normalized base units (m, kg, W, h) and keep the wikitext value as the raw claim. Unit helpers are still needed for wikitext-only fields and for SMW quirks like `kgkg`. |
| `suit_version` | Group versions with the infobox `tabs` parameter. Each version is its own page with its own revision ID. |
| `mobile_suit.model_number` | Take it from the page-title prefix. There is no infobox field. |
| `continuity` | Seed from the Fandom `era` values (`Universal Century`, `Universal Century (GQ)`, `Ad Stella`, …), not from Wikidata. |
| Phase 4 linking | Try Wikidata `P6262` (Fandom article ID) as a join key before fuzzy title matching. Roll seasons up to works. |
| User-Agent | `msg-docking-bay-ingest/<ver> (+https://github.com/saurookadook/msg-docking-bay) httpx/<ver>`. |
| Throughput | Fandom: about 1 req/s, serial. Wikimedia: at most 200/min and at most 3 concurrent; honor `Retry-After`. |

## Still open (needs a human or a later phase)

- **Decide how to handle the Fandom ToS.** Options: use the dump only, ask Fandom for written
  permission to use the API (support@fandom.com, which the ToS lists as its contact), or both. Ask the
  Gundam Wiki admins or Special:Contact for a fresh dump. The current one is from 2025-08-26, and
  requests are limited to one every 7 days.
- Explain the 3,976 vs 3,948 difference between SMW and the category count, and decide which `Unit_Type`
  values belong in scope. Probably Suit, Armor, Fighter, Man-Machine, Worker, Pod and Doll, with Ships
  and Vehicles left for later.
- Check whether Wikidata `P6262` values point to gundam.fandom.com or to other Fandom wikis.
- No raw responses were committed. Phase 3 should re-capture fixtures through the ingest client and
  store them gzipped next to its tests (SOUP-14 style).
