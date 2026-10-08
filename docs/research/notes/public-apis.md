# Free / Public APIs for Mobile Suit Gundam Franchise Data (universes, series, mobile suits)

> Method note for the report writer: research done 2026-10-03. The sandbox's network proxy returned `CONNECT tunnel failed, response 403` for direct `curl` calls to gundam-api.pages.dev and gundam.fandom.com. WebFetch refused hand-built API query URLs ("PROVENANCE_REQUIRED"), and wikidata.org / mediawiki.org were "cache-only". Fandom's own pages returned HTTP 402. So **most endpoints were NOT live-tested**. Findings come from the documentation pages that could be fetched. The example queries below are built from the documented syntax and are marked "untested".

## 1. Do any Gundam-specific public APIs exist? Who runs them, are they maintained, how complete are they?

### Takeaway
There's only one Gundam-specific public API aimed at mobile suits: the unofficial, anonymous **Gundam API at gundam-api.pages.dev**. It's read-only, needs no key, takes its data from fan wikis, has no published source, license or record count, and its `/api/series` endpoint is still "coming soon". Every other "Gundam API" project found covers adjacent data (Gunpla model kits, Gundam Card Game cards) or is a dead hobby project. None of them is a trustworthy primary source for mobile-suit specs.

### Cited Findings
**Gundam API (gundam-api.pages.dev)**: the best Gundam-specific candidate
- Base URL is `https://gundam-api.pages.dev/api`. Endpoints are `/api/gundams`, `/api/gundams/{ids|wikiNames}`, `/api/characters`, `/api/characters/{ids|wikiNames}`, and `/api/series` (listed as "coming soon") — [Gundam API docs](https://gundam-api.pages.dev/)
- "All API endpoints are read-only and currently support GET requests only." No authentication or rate limits are documented — [Gundam API docs](https://gundam-api.pages.dev/)
- The data covers Gundams (mobile suits), characters and series, "sourced from fan wikis". Endpoints accept a "wikiName", which suggests keys map to wiki page names — [Gundam API docs](https://gundam-api.pages.dev/)
- The source isn't public: "The source code will be made open source once the codebase has been tidied up." The site names no operator, license, record count or update date. It's built on the Starlight docs framework (v0.35.2) — [Gundam API docs](https://gundam-api.pages.dev/)
- Example query (untested): `GET https://gundam-api.pages.dev/api/gundams/RX-78-2_Gundam` and `GET https://gundam-api.pages.dev/api/gundams`

**Other "Gundam API" projects (adjacent or defunct)**
- **zuhairajamt/GundamAPI**: Gunpla plastic-model data (HG to PG grades) plus Gundam film info. Node/Express + MySQL with JWT tokens (`/api/user/token`, expiring after 2000 s). Deployed at `project2gundamapi.herokuapp.com`. The repo has 1 commit, 1 star, 0 forks and no stated license — [GitHub](https://github.com/zuhairajamt/GundamAPI)
- **brianlin345/gunplaAPI**: "API containing information on HG Gunpla model kits" (model kits, not in-universe mobile-suit specs) — [GitHub](https://github.com/brianlin345/gunplaAPI)
- **yzRobo/gcg-api / gcgapi.com**: "Free, unofficial data + REST API for the Gundam Card Game (Bandai GCG). Weekly-refreshed, metadata-only. Not affiliated with Bandai." — [GitHub](https://github.com/yzRobo/gcg-api); [gcgapi.com](https://gcgapi.com/). The ApiTCG org also hosts TCG APIs — [GitHub ApiTCG](https://github.com/apitcg)
- A Hex package named `gundam` (v0.1.1) shows up in searches — [hexdocs](https://hexdocs.pm/gundam/api-reference.html). What it does wasn't checked (see Gaps).
- Searching GitHub for "gundam api" mostly returns unrelated repos: a private game server for *Federation vs. Zeon DX* ([inada-s/gdxsv](https://github.com/inada-s/gdxsv)), a fan "robotics" concept repo ([Gundam-Robotics-Systems](https://github.com/Gundam-Robotics-Systems/Mobile-Suite-X-00)) and [Frankoropeza/gundammx](https://github.com/Frankoropeza/gundammx).

### Inferences
- Gundam API (pages.dev) runs on Cloudflare Pages, judging by the domain, so it's probably cheap to keep running. But it has a single anonymous maintainer, no license and unpublished source. Treat it as **low-to-medium trust**: good for prototyping or for cross-checking wiki page names, not as the system of record. Because it's "sourced from fan wikis", its data inherits the Gundam Fandom wiki's CC BY-SA obligations even though the API states no license.
- The zuhairajamt GundamAPI is almost certainly dead. Heroku shut down free dynos in Nov 2022 (from general knowledge, not verified this session), and the repo has 1 commit. Exclude it.
- The Gunpla and card-game APIs could feed later features (e.g., "kits of this suit", "cards featuring this suit"), but they don't answer the core need: model number, pilot, manufacturer, height, weight, armaments, first appearance.

### Gaps
- Couldn't live-test `gundam-api.pages.dev/api/gundams` (blocked by the sandbox proxy), so record counts, field names, whether it's live as of Oct 2026, and data freshness are all unverified.
- No RapidAPI listing for a Gundam mobile-suit API turned up. RapidAPI wasn't searched directly.
- What the hexdocs `gundam` package does is unknown. The name may be a coincidence (e.g., an unrelated Elixir/Gleam library).
- Didn't confirm whether `project2gundamapi.herokuapp.com` still responds.

## 2. MediaWiki APIs of Gundam wikis (Gundam Wiki on Fandom, MAHQ, Japanese wikis, Wikipedia): what can be queried, rate limits, license, terms

### Takeaway
The **Gundam Wiki on Fandom** (`https://gundam.fandom.com/api.php`) is the richest structured source of mobile-suit data reachable through an API. It's a standard MediaWiki Action API with no key required. You can list pages by category, fetch page wikitext and parse the infobox templates (model number, manufacturer, height, weight, armaments, pilots, first appearance). Its text is CC BY-SA, and the documented rate limits are vague. **MAHQ** (mahq.net) is the most authoritative-feeling English mecha database and is organized by timeline, but it has **no API, RSS or JSON** and is privately copyrighted, so it's a crawl-only source. **Wikipedia's API** is reliable and well documented, but it covers few individual mobile suits, and Wikimedia brought in tighter anonymous rate limits in March–April 2026.

### Cited Findings
**Gundam Wiki (Fandom)**
- Fandom wikis expose the MediaWiki API, and community forum threads discuss it and its rate limits — [Fandom Community: "Mediawiki API"](https://community.fandom.com/f/p/4400000000003417046); [Fandom Community: "api ratelimit"](https://community.fandom.com/f/p/4400000000003546349); [Fandom Dev Wiki: "What is the Api rate limit?"](https://dev.fandom.com/f/p/3312799962890578193) (this page returned HTTP 402 on fetch, so its content couldn't be read)
- Fandom's text license is published at fandom.com/licensing. A Hacker News thread discusses that page, quoting it as beginning "Except where otherwise permitted, the text on..." — [Fandom Licensing](https://www.fandom.com/licensing); [HN discussion](https://news.ycombinator.com/item?id=43529416) (neither page could be fetched: 402 and 419)
- Fandom content is generally under CC BY-SA, and the community pages explain reuse obligations — [Fandom Community: The CC-BY-SA License and You](https://community.fandom.com/wiki/User_blog:Semanticdrifter/The_CC-BY-SA_License_and_You); [Fandom Community: Copyright](https://community.fandom.com/wiki/Copyright); Wikimedia Commons keeps a page on reusing Fandom files — [Commons:Fandom files](https://commons.wikimedia.org/wiki/Commons:Fandom_files)
- Third-party marketplaces resell "Fandom Wiki API" wrappers, which shows people commonly scrape Fandom programmatically — [parse.bot Fandom Wiki API](https://parse.bot/marketplace/9cb4e345-1b9f-45e0-a0b5-ec0469d3b071/wikia-org-api); [oanor Fandom API](https://www.oanor.com/api/fandom-api)
- Example queries (untested, standard MediaWiki syntax):
  - Site stats and license: `https://gundam.fandom.com/api.php?action=query&meta=siteinfo&siprop=general|statistics|rightsinfo&format=json`
  - Mobile suits in a category: `https://gundam.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:<category name>&cmlimit=500&format=json`
  - Infobox wikitext for one suit: `https://gundam.fandom.com/api.php?action=parse&page=RX-78-2_Gundam&prop=wikitext&format=json&formatversion=2`

**MAHQ (Mecha Anime HQ)**
- MAHQ groups Gundam content by timeline: Universal Century and Regild Century; Alternate UC; Future Century, After Colony, After War, Correct Century; Cosmic Era, Anno Domini, Advanced Generation, Post Disaster, Ad Stella; and Build Fighters/Build Divers. Its sections are Animation & Live Action, Variations (MSV), Manga & Novels, and Games — [MAHQ Gundam main](https://www.mahq.net/gundammain/)
- No API, RSS or JSON export was found. The page is marked "Original content ©2000 to by Accidental Pilot, Inc.", and the fetched page showed an update date of Feb 6, 2022 — [MAHQ Gundam main](https://www.mahq.net/gundammain/)
- MAHQ still adds recent series pages, e.g., *Mobile Suit Gundam U.C. ENGAGE* and *Moon Gundam* — [MAHQ U.C. ENGAGE](https://www.mahq.net/ucengage/); [MAHQ Moon Gundam](https://www.mahq.net/moongundam/)

**Wikipedia / Wikimedia Action API**
- Wikimedia announced new global API rate limits: "early March 2026" brought low limits on anonymous API requests from outside Toolforge/WMCS and on browser-based requests, and "early April 2026" brought higher limits for identified traffic. You can get higher limits with session-cookie or OAuth 2.0 authentication, a bot flag, running on Toolforge/WMCS, or Wikimedia Enterprise. Developers must "provide a meaningful User-Agent". The stated reason is that unidentified requests make up "around 33%" of traffic — [wikitech-l announcement](https://www.mail-archive.com/wikitech-l@lists.wikimedia.org/msg97202.html)
- Official documentation for the rate limits, etiquette and usage guidelines: [Wikimedia APIs/Rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits); [API:Etiquette](https://www.mediawiki.org/wiki/API:Etiquette); [WMF API Usage Guidelines](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines); [API Policy Update 2024](https://meta.wikimedia.org/wiki/API_Policy_Update_2024)
- English Wikipedia has standalone articles for only a few individual mobile suits, e.g., "Gundam (fictional robot)" and "Zaku" — [Wikipedia: Gundam (fictional robot)](https://en.wikipedia.org/wiki/Gundam_(fictional_robot)); [Wikipedia: Zaku](https://en.wikipedia.org/wiki/Zaku). It covers series in depth, including episode lists and games — [List of Mobile Suit Gundam episodes](https://en.wikipedia.org/wiki/List_of_Mobile_Suit_Gundam_episodes); [Mobile Suit Gundam](https://en.wikipedia.org/wiki/Mobile_Suit_Gundam)

### Inferences
- For mobile-suit specs, the Fandom Gundam Wiki API is the most practical **free, programmatic** source. Parse the infobox templates in each suit's wikitext. Plan for CC BY-SA attribution and share-alike on any text you republish, and send a descriptive User-Agent. Bulk-sync on a schedule and cache, rather than calling it live per visitor.
- MAHQ is probably the most trusted English reference for model numbers and specs. Since it has no API and is privately copyrighted, use it for manual verification or a polite, permission-seeking crawl, not as an automated feed.
- Wikipedia is best for series and universe-level summaries (series, films, OVAs, air dates), not for per-suit data. The new 2026 anonymous rate limits mean a server-side integration should identify itself with a User-Agent, or ideally OAuth.

### Gaps
- I couldn't read the Gundam Fandom wiki's actual category names, infobox template name and parameters, article count, or license string. The proxy blocked them, Fandom returned 402, and WebFetch refused the built URLs.
- Fandom's exact API rate limits and API terms couldn't be confirmed. The three forum threads couldn't be read. As I recall it (unverified), Fandom publishes no fixed number, throttles abusive clients, and licenses text under CC BY-SA 3.0 (some wikis use other versions). Verify all three before relying on them.
- Japanese Gundam wikis (e.g., the wikiwiki.jp or Seesaa fan wikis, and the ja.wikipedia "ガンダムシリーズ" articles) weren't researched because of the tool budget. Whether they have an API and what their license is remain open.
- The exact numeric Wikimedia rate limits (requests/sec for anonymous vs. identified clients) weren't retrieved. mediawiki.org was cache-only.

## 3. Wikidata (SPARQL / REST): how well it models Gundam series and individual mobile suits

### Takeaway
Wikidata has good coverage of Gundam **series and works**: separate items for many TV series and OVAs, plus a concept item for "mobile suit" and an item for the Gundam robot. Coverage of **individual mobile suits** appears thin and mostly limited to suits with Wikipedia articles. I couldn't verify mecha-specific properties or item counts this session. The data is CC0, which makes it the cleanest-licensed backbone for the series and universe layer, but not for per-suit specs.

### Cited Findings
- Concept item "mobile suit": Q838559 — [Wikidata Q838559](https://www.wikidata.org/wiki/Q838559)
- Robot item "Gundam": Q1141551 — [Wikidata Q1141551](https://www.wikidata.org/wiki/Q1141551)
- Series and OVA items exist, e.g., *MS IGLOO* Q2065243, *0080: War in the Pocket* Q2466311, *Gundam 00* Q696062, *Gundam Wing* Q711148 — [Q2065243](https://www.wikidata.org/wiki/Q2065243); [Q2466311](https://www.wikidata.org/wiki/Q2466311); [Q696062](https://www.wikidata.org/wiki/Q696062); [Q711148](https://www.wikidata.org/wiki/Q711148)
- No Wikidata property for a "Gundam Wiki ID" or "MAHQ ID" turned up in search (the search returned only unrelated results) — [search results incl. Wikipedia: Wikidata](https://en.wikipedia.org/wiki/Wikidata)
- Wikidata Query Service traffic is covered by the Wikimedia rate-limit regime above (identified User-Agent required; tighter anonymous limits from March 2026) — [wikitech-l announcement](https://www.mail-archive.com/wikitech-l@lists.wikimedia.org/msg97202.html)
- Example SPARQL (untested) at `https://query.wikidata.org/sparql`. It lists items that are instances of a subclass of "mobile suit", or linked to it, with English labels:
  `SELECT ?ms ?msLabel WHERE { ?ms wdt:P31/wdt:P279* wd:Q838559 . SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ja". } }`

### Inferences
- Wikidata works well as a CC0 spine for **series, films, OVAs, studios and dates**. It can also hold cross-IDs (e.g., AniList, MAL and ANN IDs on series items) that join the other APIs together. It isn't a viable source for mobile-suit specs (height, weight, armaments).
- Wikidata usually has items only for notable suits with Wikipedia articles, so expect individual mobile-suit items in the tens, not the hundreds or thousands. This is a hypothesis to check with the SPARQL count above.

### Gaps
- The statements on Q838559 and Q1141551 couldn't be read (wikidata.org was cache-only), so the actual modeling (instance of, from narrative universe P1080, height/mass properties, pilot, manufacturer) and the item count are **unverified**.
- Whether Wikidata has properties for fictional-mecha specs (as opposed to the generic height P2048 and mass P2067) is unconfirmed.

## 4. General anime APIs (AniList, Jikan, Kitsu, AniDB, ANN Encyclopedia, TMDB, Shikimori, Annict): limits, auth, terms, Gundam coverage, character/mecha data

### Takeaway
All of these are good for the **series/film/OVA layer** (titles, dates, studios, staff, synopses, images, and human characters with voice actors). **None models mecha or mobile suits as entities.** For a free web app, AniList (90 req/min, free commercial use under $150/month revenue, no storage or hoarding allowed) and the ANN Encyclopedia (1 req/s, attribution and link required) have the clearest terms. Jikan is unofficial and inherits MyAnimeList's ToS. AniDB has the strictest rules (registered client, 1 page per 2 s, heavy caching mandatory).

### Cited Findings
**AniList (GraphQL)**
- Rate limit: "90 requests per minute" normally, 30/min in a temporary "degraded state", plus a burst limiter. Response headers are `X-RateLimit-Limit/Remaining/Reset` and `Retry-After`. Requests for higher limits aren't currently being accepted — [AniList docs: Rate Limiting](https://docs.anilist.co/guide/rate-limiting)
- Terms: free for commercial apps "operating at less than $150 of revenue per month", with a commercial license needed above that. "Using the AniList API as a backup or data storage service is strictly prohibited." "Hoarding or mass collection of data" is prohibited. Use in "competing noncomplementary services" such as anime trackers needs authorization — [AniList Terms of Use](https://anilist.gitbook.io/anilist-apiv2-docs/docs/guide/terms-of-use)
- Endpoint (general knowledge, consistent with the docs domain): `POST https://graphql.anilist.co`. No key needed for public reads. Example query (untested): `{ Page(perPage:50){ media(search:"Gundam", type:ANIME){ id title{romaji english native} format startDate{year} studios{nodes{name}} characters{nodes{name{full}}} } } }`

**Jikan (unofficial MyAnimeList)**
- An "Unofficial MyAnimeList REST API". v4 has anime, manga, people and characters endpoints, and v3 is discontinued — [Jikan v4 docs](https://docs.api.jikan.moe/); [jikan-rest GitHub](https://github.com/jikan-me/jikan-rest)
- "Jikan is not affiliated with MyAnimeList.net… You are responsible for the usage of this API. Please be respectful towards MyAnimeList's Terms Of Service." Read-only, with no authenticated requests — [jikan-rest GitHub](https://github.com/jikan-me/jikan-rest)
- The project announced v4 on Patreon — [Jikan v4.0 Official Release](https://www.patreon.com/jikan/posts/jikan-v4-0-60604773)

**Kitsu (JSON:API)**
- Base `https://kitsu.io/api/edge`. Most GETs need no auth (OAuth 2.0 for writes and user data). It has anime, manga, episodes, characters, staff and categories, and paginates with `page[limit]` (max 20) — [Kitsu API docs](https://hummingbird-me.github.io/api-docs/); [Apiary docs](https://kitsu.docs.apiary.io/)
- Example (untested): `GET https://kitsu.io/api/edge/anime?filter[text]=gundam&page[limit]=20`

**AniDB HTTP API**
- Base `http://api.anidb.net:9001/httpapi`. A registered client is required (`client`, `clientver`, `protover=1`). "You should not request more than one page every two seconds". "Heavy local caching" is mandatory, and systematic downloading leads to bans — [AniDB HTTP API Definition](https://wiki.anidb.net/HTTP_API_Definition)
- The anime endpoint (`request=anime&aid=`) returns titles in many languages, related anime, creators, the full character cast with voice actors, episodes and tags — [AniDB HTTP API Definition](https://wiki.anidb.net/HTTP_API_Definition)
- People hit bans in practice — [AniDB forum: HTTP API Banned](https://anidb.net/post421893); [FileBot: AniDB client limits and bans](https://www.filebot.net/forums/viewtopic.php?t=12048); [AniDB Policies](https://anidb.net/policy)

**Anime News Network Encyclopedia API**
- Endpoints: `https://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=<id>` (details), `reports.xml` (lists), and `nodelay.api.xml` for bursts. You can search by `title=~name` and paginate with `nskip`/`nlist` — [ANN Encyclopedia API](https://www.animenewsnetwork.com/encyclopedia/api.php)
- "rate-limited to 1 request per second per IP address". The nodelay endpoint allows 5 requests per 5 s, then returns 503 — [ANN Encyclopedia API](https://www.animenewsnetwork.com/encyclopedia/api.php)
- Terms: "List Anime News Network as the source of the data" and "Include a link to the relevant Encyclopedia entry" — [ANN Encyclopedia API](https://www.animenewsnetwork.com/encyclopedia/api.php)
- Example (untested): `https://cdn.animenewsnetwork.com/encyclopedia/api.xml?title=~gundam`

**TMDB**
- TMDB has a public API with published terms. Developers ask about commercial pricing and rate limits on its forums — [TMDB API Terms of Use](https://www.themoviedb.org/api-terms-of-use) (blocked by robots.txt for the fetcher); [TMDB Talk: API rate limit (2025)](https://www.themoviedb.org/talk/686cff2fb5eabfc4219a459e); [TMDB Talk: commercial usage pricing](https://www.themoviedb.org/talk/622b91d0d236e60045f62782)
- Third-party profile: "community-built movie, TV, and people metadata catalog with a free REST API" — [api-evangelist/tmdb](https://github.com/api-evangelist/tmdb)

**Shikimori / Annict**
- Shikimori has a public API (docs at shikimori.one/api/doc) with wrappers in several languages — [Shikimori API Node wrapper](https://github.com/LennyLizowzskiy/Shikimori-API-Node); [Go package](https://pkg.go.dev/github.com/SevereCloud/shikimori); [Rust crate](https://docs.rs/shikimori-api/latest/shikimori_api/)
- There's also a cross-ID mapping project linking anime IDs across services — [nattadasu/animeApi](https://github.com/nattadasu/animeApi)

### Inferences
- Use AniList (or Kitsu, which has the simplest keyless REST) as the free source for **series metadata, cover art and human characters/pilots**. AniList's "no backup/data storage" and "no hoarding" clauses clash with mirroring its data into the app's own database. Calling it live with short-term caching is the safer reading of those terms.
- ANN's attribute-and-link terms are easy to meet, and its staff and company credits are strong. It's a good free "trust anchor" for series facts like studio, director, mechanical designers and air dates.
- AniDB's registration, 2-second throttle and ban risk make it a poor fit for a live web app. Use it only for an occasional, cached import if at all.
- Jikan is convenient, but it's an unofficial MAL scraper whose ToS exposure falls on the app developer. Rank it below AniList and Kitsu.
- No general anime API holds mobile-suit specs. Model number, height, weight, armaments and manufacturer have to come from the Gundam wikis or MAHQ.

### Gaps
- Jikan's exact rate limits and cache duration weren't retrieved (the docs page rendered only metadata, and freeapihub returned 403). As I recall it (unverified), the limits are 3 req/s and 60 req/min with about 24 h server cache.
- TMDB's current API terms (non-commercial vs. commercial, attribution, the "~50 req/s" figure) couldn't be fetched (blocked by robots.txt).
- Kitsu's rate limits, and whether it's still maintained in 2026, weren't confirmed.
- Shikimori's rate limits (as I recall it: 5 rps / 90 rpm, User-Agent required, unverified) and Annict's API (Japanese; needs an OAuth or personal access token; REST v1 and GraphQL) weren't confirmed from primary docs.
- Gundam-specific data quality (e.g., whether every UC OVA, compilation film and *Witch from Mercury* entry exists, and how franchise relations are linked) wasn't sampled in any of these APIs because live calls were blocked.

## 5. Official sources: does Bandai Namco / Sunrise (gundam-official.com, gundam.info) expose a public API or structured data feed?

### Takeaway
I found no evidence of any public API or structured data feed from Bandai Namco Filmworks / Sunrise. The official presence is websites and social accounts. The only "Gundam" APIs near official data are unofficial ones, notably the Gundam Card Game API, which explicitly says it's "not affiliated with Bandai".

### Cited Findings
- A search for an official gundam.info API or data feed returned only social accounts (Facebook and X), RSS aggregator listings, and unofficial projects — [Gundam.Info NA Facebook](https://www.facebook.com/GundamInfoNA/); [Gundam.Info Asia Facebook](https://www.facebook.com/gundam.info.en/); [GUNDAM NA Official on X](https://x.com/GundamInfoNA?lang=en); [Feedspot: Gundam RSS feeds](https://rss.feedspot.com/gundam_rss_feeds/)
- Unofficial derived data: "Free, unofficial data + REST API for the Gundam Card Game (Bandai GCG)… Not affiliated with Bandai." — [yzRobo/gcg-api](https://github.com/yzRobo/gcg-api); [gcgapi.com](https://gcgapi.com/)

### Inferences
- The official sites are the most authoritative source for canonical names and spellings and recent series. But with no API they're reference and verification sources only. Crawling them raises copyright and ToS concerns that need separate review (another researcher is covering crawlable sites).
- **Overall free-source ranking for Docking Bay (my synthesis):**
  1. **Gundam Wiki on Fandom, via the MediaWiki API.** Best per-mobile-suit coverage across all universes, free and keyless. CC BY-SA attribution and share-alike apply. Medium-high trust; it's community edited, so cross-check against MAHQ.
  2. **Wikidata + Wikipedia APIs.** CC0 (Wikidata) and CC BY-SA (Wikipedia) data for the universe/series/film/OVA layer and cross-IDs. High reliability and governance, but thin per-suit coverage, and the 2026 rate limits require an identified User-Agent or OAuth.
  3. **AniList GraphQL, with ANN Encyclopedia as the attribution-friendly backup.** Series metadata, images and human characters/pilots. Free for apps under $150/month revenue, no storage or hoarding allowed.
  - Watch-list: **Gundam API (gundam-api.pages.dev)**. It's the only Gundam-specific mobile-suit API, but it's anonymous, unlicensed, its source is unpublished and its live status is unverified. Use it only for prototyping, or once it publishes source and a license.
  - **MAHQ** is the most trusted reference for specs, but as a crawl/verification source (no API).

### Gaps
- gundam-official.com and gundam.info weren't fetched directly to check for sitemaps, JSON-LD/schema.org markup or embedded JSON. Whether they have a usable sitemap or structured markup is unknown.
- No official statement on fan-site data reuse or API access from Bandai Namco Filmworks was found.
