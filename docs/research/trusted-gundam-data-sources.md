# Wiki APIs Anchor Docking Bay's Mobile Suits

Three sources should feed Docking Bay. First is **the Gundam Wiki on Fandom**, read through its free MediaWiki API and XML dumps, which supplies the mobile suits themselves. Second is **Wikidata plus Wikipedia**, read through Wikimedia's free APIs and dumps, which supplies universes, series, films and the cross-IDs that join everything together. Third is **MAHQ (mahq.net)**, a crawl-only, editor-curated spec database, which serves as a verification layer and should be used only with its owner's permission. The paid tier puts nothing in the top three. No marketplace sells a Gundam mobile-suit API, and every paid metadata service (TheTVDB, Simkl, IMDb) describes only series and films, which the free APIs already cover. This is where your priority order and trustworthiness pull apart. Read strictly, the order would hand slot three to AniList's free GraphQL API, which has no mecha entities at all. Meanwhile the most trusted spec references (MAHQ, Mark Simmons's translations of the official mobile suit encyclopedias, and the official Gundam site) have no API. The one Gundam-specific API, gundam-api.pages.dev, sits in the top tier but ranks lowest on trust: it is anonymous, unlicensed and sourced from the same fan wikis. The real cost of this stack is compliance, not fees: CC BY-SA attribution and share-alike on wiki text, images that can only be hosted under fair use, and Wikimedia's tighter 2026 rate limits. Every endpoint, rate limit and robots.txt described here comes from documentation, not live calls, because the research sandbox's network proxy blocked direct requests. A one-day verification spike should come before any build.

## The Gundam Wiki API, Wikimedia data and MAHQ form the top three

The ranking below follows your order wherever the order produces a useful source, and departs from it in exactly one place, which the table and the paragraphs after it explain.

| Rank | Source | Access tier | What it supplies to Docking Bay | Trust |
|---|---|---|---|---|
| 1 | Gundam Wiki (gundam.fandom.com) | Free public API (MediaWiki Action API) plus XML dumps | Per-suit specs, versions, pilots and appearances across every timeline | Medium-high: written sourcing and canon policies, but crowd-edited |
| 2 | Wikidata + Wikipedia | Free public APIs (SPARQL, Action API) plus dumps | Works, timelines, air dates, studios and cross-IDs | High for works; thin on individual suits |
| 3 | MAHQ (mahq.net) | Crawl only, with permission | A uniform spec block per unit, used to cross-check rank 1 | Medium-high: curated since 2000, but uncited |

**The Gundam Wiki is the rare case where the top tier and the top trust coincide.** It is the richest mobile-suit source reachable through an API. Its standard MediaWiki endpoint at `gundam.fandom.com/api.php` needs no key and can list pages by category and return each page's infobox wikitext ([Fandom Community](https://community.fandom.com/f/p/4400000000003417046)). It reports **8,456 articles since January 2005** and covers every timeline, from the Universal Century through IBO and The Witch from Mercury ([The Gundam Wiki](https://gundam.fandom.com/wiki/The_Gundam_Wiki)). It is also the only fan source found with a written sourcing policy tied to official material. That policy names Sunrise-licensed works as the most reliable sources, requires model kit manuals to be cited with release date and JAN number, and states that a topic with no reliable source "should not have an article" ([Gundam Wiki: Reliable Sources](https://gundam.fandom.com/wiki/Gundam_Wiki:Reliable_Sources)). Its canon policy keeps distinct versions as separate entities, so the 1979 RX-78-2, The Origin's RX-78-02 and the Yokohama 1:1 RX-78F00 each have their own page ([RX-78-02](https://gundam.fandom.com/wiki/RX-78-02_Gundam); [RX-78F00](https://gundam.fandom.com/wiki/RX-78F00_Gundam)). That split is the structure a careful data model needs. The weakness is open editing: the policies show intent, not page-level guarantees.

**Wikidata and Wikipedia take slot two for the layer above the suits.** Wikidata already has items for the mobile suit concept (Q838559), the Gundam robot (Q1141551) and individual works such as *MS IGLOO*, *War in the Pocket*, *Gundam 00* and *Gundam Wing* ([Q838559](https://www.wikidata.org/wiki/Q838559); [Q2065243](https://www.wikidata.org/wiki/Q2065243); [Q696062](https://www.wikidata.org/wiki/Q696062)). English Wikipedia has an article for nearly every series, including *GQuuuuuuX* ([Wikipedia: GQuuuuuuX](https://en.wikipedia.org/wiki/Mobile_Suit_Gundam_GQuuuuuuX)). It is not a spec source, though. Its article on the fictional robot gives only height and weight, citing a single archived Bandai USA page from 2008 ([Wikipedia: Gundam (fictional robot)](https://en.wikipedia.org/wiki/Gundam_(fictional_robot))).

**MAHQ takes slot three because the paid tier has nothing to offer for mobile suits.** Every MAHQ unit page carries the same "General and Technical Data" block: model number, unit type, manufacturer, operator, first deployment, dimensions, weight, armor, powerplant output, thrust, sensor range, armaments and pilots. Pages sit at predictable `mahq.net/<model-number>/` URLs on a WordPress site ([MAHQ: RX-78-2](https://www.mahq.net/rx-78-2/)), and the site is current through the 2025 series *GQuuuuuuX* ([MAHQ: GQuuuuuuX](https://www.mahq.net/gundamgquuuuuux/)). Existing projects already treat MAHQ as the de facto Gundam scrape target ([Askannz/gundam-stable-diffusion](https://github.com/Askannz/gundam-stable-diffusion)). It has two weaknesses. Its pages cite no sources, and it merges versions, listing "RX-78-2/RX-78-02" as one entry ([MAHQ: RX-78-2](https://www.mahq.net/rx-78-2/)). That makes it the right cross-check for rank 1, not a replacement for it.

**If you want the order applied strictly, slot three goes to AniList, backed by the Anime News Network (ANN) Encyclopedia.** Both are free, both have clear terms, and both are good for series metadata, cover art and human characters ([AniList docs](https://docs.anilist.co/guide/rate-limiting); [ANN Encyclopedia API](https://www.animenewsnetwork.com/encyclopedia/api.php)). Neither models mobile suits, so this choice trades away the app's core entity for tier purity. The recommendation is to use them as supporting sources for the series layer, not as a top-three pillar. Two other mismatches follow the same pattern. The official site, en.gundam-official.com, is the authority for the work list and release dates, but it is a client-rendered JavaScript app with no API ([gundam-official: series](https://en.gundam-official.com/series)). The only Gundam-specific API, gundam-api.pages.dev, offers read-only `/api/gundams` and `/api/characters` endpoints with no key, but it names no operator, license or record count, its source code is unpublished, and its `/api/series` endpoint is still "coming soon" ([Gundam API docs](https://gundam-api.pages.dev/)). Its data comes from fan wikis, so it adds a single point of failure between you and data you can read directly.

## Each tier covers a different layer of the data

### Free APIs: one good suit source, many series sources

Among the free APIs, mobile-suit data comes only from wiki sources. Every general anime API covers titles, staff and human characters and stops there.

| Source | Data layer | Access | Trust / fit |
|---|---|---|---|
| Gundam Wiki MediaWiki API | Mobile suits, versions, pilots, works | Keyless `api.php` | Best free suit source |
| Wikidata SPARQL / Wikipedia API | Works, timelines, cross-IDs | Keyless; identified User-Agent expected | High for works, thin for suits |
| AniList GraphQL | Series, art, characters, voice actors | Keyless reads, 90 req/min | Good series layer; terms forbid storing its data |
| ANN Encyclopedia API | Series, staff and company credits | Keyless XML, 1 req/s | Strong credits; easy attribution |
| Kitsu JSON:API | Series, episodes, characters | Keyless GETs, max 20 per page | Usable; 2026 maintenance unconfirmed |
| Jikan (unofficial MyAnimeList) | Series, characters | Keyless | MyAnimeList ToS risk falls on you |
| AniDB HTTP API | Series, cast, episodes | Registered client, 1 page per 2 s | Ban risk; poor fit for a live app |
| gundam-api.pages.dev | Suits, characters | Keyless, GET only | Low-medium: anonymous, unlicensed |

The table's sources are [Kitsu API docs](https://hummingbird-me.github.io/api-docs/), [jikan-rest](https://github.com/jikan-me/jikan-rest) and [AniDB HTTP API](https://wiki.anidb.net/HTTP_API_Definition), plus the citations above. The other "Gundam APIs" on GitHub cover adjacent data: High Grade Gunpla kits ([gunplaAPI](https://github.com/brianlin345/gunplaAPI)), a one-commit kit-and-film API on Heroku ([zuhairajamt/GundamAPI](https://github.com/zuhairajamt/GundamAPI)), and Gundam Card Game cards ([gcg-api](https://github.com/yzRobo/gcg-api)). They could feed later "kits of this suit" or "cards featuring this suit" features, but none holds in-universe specs. **No official Bandai Namco or Sunrise API or data feed was found**. The official presence consists of websites, social accounts and RSS listings ([Feedspot: Gundam RSS](https://rss.feedspot.com/gundam_rss_feeds/)).

### Paid APIs: money buys series metadata, never mecha specs

**There is no paid Gundam API to buy.** Searches found no RapidAPI or marketplace listing ([Gundam API](https://gundam-api.pages.dev/)), and every commercial metadata provider models shows, films, episodes and people rather than mecha.

| Option | What you pay | What you get | Verdict |
|---|---|---|---|
| TheTVDB | $0 under $50k/yr revenue with a link back; $1,000/yr at $50k–$250k | Series, episodes, artwork | Best paid-tier option; free for a fan app |
| Simkl | Free under $150/month revenue; unpublished license above | Anime-friendly series data | Strict attribution and suspension rules |
| TMDB | Free tier; commercial terms unclear | Films, TV, people | Sources conflict on commercial use |
| IMDb (AWS Data Exchange) | $150,000 upfront for 12 months | 9M+ titles | Out of scale; nothing Gundam-specific |
| Trakt | $4.99/month VIP to create API apps (Aug 2026) | Tracking, light metadata | Adds little |
| Apify HLJ scrapers | About $2 per 1,000 records | Gunpla product listings (JAN, price, scale) | Third-party scraping of HobbyLink Japan; later-phase only |
| Official BNFW license | Bespoke, no public program | Clean rights to specs and images | Only realistic if the app goes commercial |

The table's sources are [TheTVDB](https://www.thetvdb.com/api-information), [Simkl API rules](https://api.simkl.org/api-rules), [TMDB Talk](https://www.themoviedb.org/talk/622b91d0d236e60045f62782), [AWS Marketplace: IMDb](https://aws.amazon.com/marketplace/pp/prodview-wdqq4hg3bcbws), [ETTAYEB on Trakt](https://ettayeb.fr/en/selfhosted/trakt-api-paywall-selfhosted-media/) and [Apify](https://apify.com/jungle_synthesizer/hobbylinkjapan-anime-figure-gunpla-catalog-scraper/api). The one paid route that would change the trust picture is an official license. Gundam rights moved inside Bandai Namco Filmworks (BNFW) on April 1, 2026, when BNFW absorbed "all Gundam-related planning, production, and copyright management from Sotsu" ([Anime Rave](https://x.com/AniRave/status/2019359081778024595)). No public licensing program exists, so this is a negotiation for commercial partners, not a purchase. **At launch, nothing in this tier is worth paying for.** TheTVDB is the one to revisit if revenue ever passes its threshold.

### Crawlable sites: the most trusted spec references have no API

| Site | Strength | Structure | Rights |
|---|---|---|---|
| MAHQ | Curated, consistent spec blocks | Server-rendered WordPress, `/<model-number>/` slugs | ©2000 Accidental Pilot, Inc. |
| Gundam Unofficial (Mark Simmons) | Translation of the official *Mobile Suit Illustrated* (2015 edition) | One long page with anchors | Underlying content © Sotsu • Sunrise |
| Gundam Wiki HTML | Same as rank 1 | Use the dump or API instead | CC BY-SA text; returned HTTP 402 to fetches |
| Wikipedia (EN/JA) | Works; the JA site has per-timeline weapon lists | Official dumps | CC BY-SA |
| gundam-official.com | Authority on works and dates | Client-rendered app | Bandai Namco terms |
| wikiwiki.jp, atwiki | Japanese names, game data | Returned 403 to fetches | Unclear |
| mobilesuit.dev | 3,812 suits across 14 timelines, development trees | Unknown | No license or sources stated |

The table's sources are [MAHQ](https://www.mahq.net/rx-78-2/), [Gundam Unofficial catalog](https://www.gundamunofficial.com/mscatalog.html), [Gundam Unofficial MS Encyclopedia](https://www.gundamunofficial.com/archive/msencyclopedia.html), [JA Wikipedia weapons list](https://ja.wikipedia.org/wiki/%E3%82%AC%E3%83%B3%E3%83%80%E3%83%A0%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%81%AE%E7%99%BB%E5%A0%B4%E6%A9%9F%E5%8B%95%E5%85%B5%E5%99%A8%E4%B8%80%E8%A6%A7), [wikiwiki.jp](https://wikiwiki.jp/gundam/) and [mobilesuit.dev](https://www.mobilesuit.dev/mobile-suit). **Gundam Unofficial has the highest per-entry reliability of any source**, because it translates Kadokawa's official encyclopedia, which the translator calls "the closest thing to a comprehensive official guide" ([Gundam Unofficial](https://www.gundamunofficial.com/mscatalog.html)). The translated content is copyrighted official material, though, so use it for manual spot checks rather than ingestion. mobilesuit.dev already models development trees across timelines, much as Docking Bay plans to. With no stated provenance or license, it works as a design reference, not a data source. Sunrise's own order of authority puts animation first, then Tomino's novels, then Sunrise-supervised books, then approved materials such as kit manuals ([fan compilation of Sunrise statements](https://pastebin.com/LfFAeqSW)). Every fan site sits downstream of those primaries, and the Gundam Wiki is the only one that shows its citations.

## Share-alike text, fair-use images and 2026 rate limits set the rules

**Licensing, not pricing, is the binding constraint.** Fandom licenses community text under **CC BY-SA 3.0**. Reusers must link the license, attribute the article and apply share-alike to derivatives, and images and video are not necessarily covered ([Fandom Help: Licensing](https://community.fandom.com/wiki/Help:Licensing)). The Gundam Wiki hosts official screenshots and scans under a fair-use template, not a license, so **those images cannot be republished on the strength of the wiki's text license** ([Gundam Wiki: Image Policy](https://gundam.fandom.com/wiki/Gundam_Wiki:Image_Policy)). The same CC BY-SA obligations carry through to gundam-api.pages.dev, because its data is "sourced from fan wikis" even though it states no license ([Gundam API docs](https://gundam-api.pages.dev/)).

| Source | License / terms | Attribution duty | Rate limit |
|---|---|---|---|
| Gundam Wiki (Fandom) | CC BY-SA 3.0 text; images fair use | Link the license and the article; share-alike on derived text | No published number; dumps at most once every 7 days |
| Wikipedia | CC BY-SA | As above | Low anonymous limits since March 2026; higher for identified traffic |
| Wikidata | CC0 (confirm) | None required | Same Wikimedia regime |
| AniList | Free under $150/month revenue; no storage or hoarding | Not specified in fetched terms | 90 req/min (30 when degraded) |
| ANN Encyclopedia | Free | Name ANN and link each entry | 1 req/s per IP |
| TheTVDB | Free under $50k/yr | Direct link to TheTVDB.com | Not retrieved |
| Simkl | Free under $150/month | Link each item's Simkl page | 10 GET/s; suspension without appeal |
| MAHQ / Gundam Unofficial | All rights reserved | Ask permission | Unknown; be very polite |

The table's sources are [Fandom Help: Database download](https://community.fandom.com/wiki/Help:Database_download), [wikitech-l announcement](https://www.mail-archive.com/wikitech-l@lists.wikimedia.org/msg97202.html), [AniList Terms](https://anilist.gitbook.io/anilist-apiv2-docs/docs/guide/terms-of-use), [ANN Encyclopedia API](https://www.animenewsnetwork.com/encyclopedia/api.php), [TheTVDB](https://www.thetvdb.com/api-information) and [Simkl](https://api.simkl.org/api-rules). Three obligations shape the architecture.

**Wikimedia now penalises anonymous clients.** Low limits on unidentified API traffic arrived in early March 2026, with higher limits for identified traffic from April. Getting the higher tier means a meaningful User-Agent, OAuth 2.0, a bot flag or Wikimedia Enterprise. Wikimedia's stated reason is that unidentified requests made up about 33% of traffic ([wikitech-l](https://www.mail-archive.com/wikitech-l@lists.wikimedia.org/msg97202.html)).

**AniList's terms conflict with a local copy.** They forbid using the API "as a backup or data storage service" and ban "hoarding or mass collection of data". Use in competing non-complementary services such as anime trackers also needs authorization ([AniList Terms](https://anilist.gitbook.io/anilist-apiv2-docs/docs/guide/terms-of-use)). Docking Bay's favourites feature makes it tracker-adjacent, so store only AniList IDs and fetch details live with short caching. Facts you need to keep should be persisted from ANN or Wikidata instead.

**Fandom may block plain crawlers.** Fandom pages returned **HTTP 402** to the research fetcher. That is the status code of Cloudflare's Pay Per Crawl, which launched alongside default AI-crawler blocking in July 2025 ([MediaPost](https://www.mediapost.com/publications/article/407093/cloudflare-blocks-ai-content-scrapers-across-24-o.html); [Cloudflare blog](https://blog.cloudflare.com/introducing-ai-crawl-control/)). The connection is an inference, not confirmed Fandom policy, but it points to the official dump and API rather than HTML crawling.

**On IP**, factual specs such as height and model number are generally treated as uncopyrightable facts, while prose and artwork are not. Storing factual fields with a per-record source link, and writing descriptions in your own words, keeps share-alike confined to any text you copy (a general inference, not legal advice). The app name uses the franchise's full title. An "unofficial fan project, not affiliated with Bandai Namco Filmworks / Sotsu / Sunrise" disclaimer is prudent, and so is a launch with no rehosted official images.

## Store specs as sourced claims on versioned suits

Gundam has no single "true" spec sheet, and the data model should not pretend otherwise. Sunrise separates "official" setting information from "canon" story events, and ranks material by medium ([fan compilation](https://pastebin.com/LfFAeqSW)). The Gundam Wiki lets an animated adaptation override its non-animated source, so the 2021 *Hathaway* film supersedes the 1989 novel ([Gundam Wiki: Canon Policy](https://gundam.fandom.com/wiki/Gundam_Wiki:Canon_Policy)). Timelines alone are not a sufficient key, either. *GQuuuuuuX* is set in an alternate Universal Century where Zeon wins the One Year War ([Wikipedia: GQuuuuuuX](https://en.wikipedia.org/wiki/Mobile_Suit_Gundam_GQuuuuuuX)), and the Gundam Wiki's ten-timeline list ([Gundam Wiki: Timelines](https://gundam.fandom.com/wiki/Gundam_Wiki:Timelines)) shows no separate entries for newer settings. These facts call for a schema that separates the suit from its versions, and each value from its source.

| Entity | Key fields | Fed by |
|---|---|---|
| `continuity` | name, parent continuity (e.g., alternate UC under UC) | Gundam Wiki timelines, official site |
| `work` | title, type (TV/film/OVA/manga/game), continuity, dates, `wikidata_qid`, `anilist_id`, `ann_id` | Wikidata, Wikipedia, ANN |
| `mobile_suit` | canonical name, base model number, `fandom_title`, `mahq_slug` | Gundam Wiki |
| `suit_version` | suit, label (1979 TV / The Origin / 1:1 statue), originating work | Gundam Wiki version pages |
| `spec_claim` | version, field, value, unit, source, retrieved_at | Gundam Wiki infobox, MAHQ cross-check |
| `source` | kind (episode, book, kit manual with JAN, wiki revision, MAHQ page), citation, URL, license | All |
| `appearance`, `pilot` | version ↔ work, version ↔ character | Gundam Wiki, AniList (live) |
| `user_favourite` | user, entity type, entity ID | Docking Bay |

Each field needs a unit and a precise meaning, or unlike values get mixed together. MAHQ's 1,380 kW for the RX-78-2 is generator output, while the Gundam Wiki's 1.9 MW is the beam rifle's output. They measure different things and do not conflict ([MAHQ: RX-78-2](https://www.mahq.net/rx-78-2/); [Gundam Wiki: RX-78-2](https://gundam.fandom.com/wiki/RX-78-2_Gundam)). A good core field set is MAHQ's own: model number, unit type, manufacturer, operator, pilots, head and overall height, empty and gross weight, armor, generator output, thrust, sensor range, first deployment, and fixed and hand armaments. Model number, name, pilots and height are reliably present for major units. The engineering figures are often missing, and they are where official books diverge.

**Ingest in batches and serve from your own database; never call upstream per visitor.** Seed suits from the Gundam Wiki's "current pages" XML dump, requested from Special:Statistics. It arrives as 7z-compressed MediaWiki XML without images, and a new one can be requested at most weekly ([Fandom Help: Database download](https://community.fandom.com/wiki/Help:Database_download)). Parse the infobox templates with a wikitext parser such as `mwparserfromhell`, and keep each page's revision ID as the attribution anchor. Between dumps, pull changes through `api.php` category listings at about one request per second, with a contact-bearing User-Agent. Build the `work` and `continuity` tables from a Wikidata SPARQL pull, and enrich them with ANN credits, honoring its 1 req/s limit and per-entry link. Treat AniList as a live, cached enrichment rather than a store. Run MAHQ comparisons as an offline job after asking Accidental Pilot for permission, checking `wp-sitemap.xml` first so the crawl needs only one index request. Flag any field where MAHQ and the Gundam Wiki disagree for human review instead of picking a winner.

## Nothing here was tested live, so start with a verification spike

The research sandbox's network proxy refused direct connections to gundam-api.pages.dev and gundam.fandom.com. Fandom pages returned HTTP 402, wikidata.org and mediawiki.org were readable only from cache, and the fetch tool would not open hand-built API query URLs. **No endpoint was called, no robots.txt was read, and no record counts were measured.** Every example query is built from documented syntax. The checks below should run from a normal network before any code is committed.

| Unverified item | Why it matters | How to check |
|---|---|---|
| gundam-api.pages.dev is live, plus its fields and counts | Only Gundam-specific API | `GET /api/gundams` |
| Gundam Wiki infobox template name and parameters | Defines the parser | `api.php?action=parse&page=RX-78-2_Gundam&prop=wikitext` |
| Fandom rate limits, scraping clauses in its ToS, and robots.txt | Crawl legality and throttling | Read fandom.com/terms-of-use and gundam.fandom.com/robots.txt in a browser |
| The Gundam Wiki's own license string | Confirms CC BY-SA 3.0 on this wiki | `meta=siteinfo&siprop=rightsinfo` |
| Dump freshness (generation delays were noted in Feb 2024) | Seeding strategy | Special:Statistics |
| Wikidata modeling and count of individual suits; CC0 license | Size of the suit-level Wikidata layer | SPARQL count on Q838559 subclasses; Wikidata licensing page |
| Numeric Wikimedia limits for anonymous vs identified clients | Sync scheduling | Wikimedia APIs / Rate limits page |
| MAHQ robots.txt, sitemap and unit count | Crawl scope | `/robots.txt`, `/wp-sitemap.xml` |
| Exact MAHQ RX-78-2 thrust (fetched as 55,599 kg, possibly 55,500) | Example of transcription risk | View the page |
| TMDB commercial terms, IGDB 2026 terms, Kitsu maintenance | Secondary series sources | Primary docs |

Japanese sources (JA Wikipedia, wikiwiki.jp, atwiki, Pixiv Encyclopedia) were not researched in depth. They are likely closer to the primary Japanese reference books, and they are the obvious place to source Japanese names. Community reputation data (Reddit, Mecha Talk) could not be retrieved, so the trust ratings above rest on each site's published policies and the sampled pages, not on user consensus.

## Conclusion

The research turns the original question around. Trust in Gundam data does not come from an access tier. It comes from whether a source shows its citations back to official books and manuals, and only the Gundam Wiki does that at scale. Because no paid product holds mecha data, your priority order collapses into a choice between free wiki data, which carries share-alike obligations, and curated sites that have no API. That makes the share-alike decision an early architecture choice: anything derived from the Gundam Wiki, including the third-party gundam-api.pages.dev, carries CC BY-SA. Storing facts plus source links, rather than copied prose, keeps those obligations light.

The gap is also an opportunity. No open, structured, spec-level Gundam dataset exists today: the closest equivalents are image datasets scraped from MAHQ and Gunpla kit lists ([Gazoche/gundam-captioned](https://huggingface.co/datasets/Gazoche/gundam-captioned); [Kaggle Gunpla Dataset](https://www.kaggle.com/datasets/marzho/gunpla-dataset)). A versioned, source-attributed suit database built from the Gundam Wiki dump, published under CC BY-SA, would be legally clean. It could be Docking Bay's most durable contribution, beyond the app itself, and give the community a version-aware reference with sources shown for every value.
