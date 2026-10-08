# Crawlable Websites for a Gundam Universe / Series / Mobile Suit Dataset (as of Oct 2026)

Research method note: Direct HTTP access (curl) from the research sandbox was blocked by the egress proxy (CONNECT 403 for every candidate domain), and the fetch tool could only open URLs that had surfaced in search results. As a result, **no robots.txt file could be fetched verbatim** for any candidate site. Several Fandom pages returned **HTTP 402** to the fetch tool, and wikiwiki.jp and mechatalk.net returned **HTTP 403**. These response codes are recorded as observations below. They may reflect anti-bot policy on those sites or limits of the fetch tool, and the coordinator should not treat them as confirmed site policy.

## Q1: Which candidate sites exist, and how reliable, well-sourced and structured is each?

### Takeaway
The three strongest crawl targets for structured mobile-suit data are:
1. **MAHQ (mahq.net)**: a long-running, editor-curated (not crowd-edited) WordPress site. Every unit page carries a consistent "General and Technical Data" spec block, with clean `mahq.net/<model-number>/` URLs.
2. **The Gundam Wiki (gundam.fandom.com)**: the largest English crowd-sourced wiki, with about 8,456 articles, all universes covered and a CC BY-SA text license. Fandom also offers XML database dumps.
3. **Wikipedia (EN/JA)**: suitable for series and timeline-level data, available via official dumps. JA Wikipedia also keeps per-timeline mobile weapon list pages.

Gundam Unofficial (Mark Simmons's translations of the official MS Encyclopedia / *Mobile Suit Illustrated*) is the most authoritative English source for specs. However, it is a static translation archive with limited coverage. The official Gundam site appears to be a JS-rendered app with no confirmed public MS database.

### Cited Findings

**MAHQ (Mecha Anime Headquarters)**
- MAHQ unit pages use the URL pattern `mahq.net/[mobile-suit-designation]/` (e.g., `https://www.mahq.net/rx-78-2/`). The site runs on **WordPress** (meta-generator tag). Gundam content is indexed at `mahq.net/gundammain/`, with series navigation split alphabetically (Series A–F, G–L, M–S, T–Z). — [MAHQ RX-78-2 page](https://www.mahq.net/rx-78-2/)
- Each unit page has a structured "General and Technical Data" block. Its fields are model number, code name, unit type, manufacturer, operator, rollout/deployment dates, dimensions (e.g., "head height 18.0 meters"), weight, armor materials, powerplant, performance, equipment, fixed/optional armaments and pilot(s). The page also has "Technical and Historical Notes" (narrative) and "Miscellaneous Information" (designers, first appearance) sections. The data is a formatted label/value list rather than an HTML table. — [MAHQ RX-78-2 page](https://www.mahq.net/rx-78-2/)
- The footer reads "Original content ©2000 to by Accidental Pilot, Inc." No Gundam Officials or Master Archive citations appeared on the sampled page. — [MAHQ RX-78-2 page](https://www.mahq.net/rx-78-2/)
- MAHQ is current. It has a page for the 2025 series *Mobile Suit Gundam GQuuuuuuX* (`https://www.mahq.net/gundamgquuuuuux/`). — [MAHQ GQuuuuuuX](https://www.mahq.net/gundamgquuuuuux/)
- Legacy `.htm` URLs still appear in search results (e.g., `http://mahq.net/mecha/gundam/doublefake/amx-003s.htm`). This indicates a migration from a static-HTML structure (`/mecha/gundam/<series>/<model>.htm`) to WordPress slugs. — [MAHQ legacy URL](http://mahq.net/mecha/gundam/doublefake/amx-003s.htm)
- MAHQ has an associated forum community on Mecha Talk (e.g., the "MAHQ agenda" thread). — [Mecha Talk: MAHQ agenda](https://mechatalk.net/viewtopic.php?t=16584) (the page returned 403 to the fetch tool, so its content was not verified)

**The Gundam Wiki (gundam.fandom.com)**
- The wiki reports "8,456 articles since January 9, 2005". It is organized by Series, Timelines, Factions, Characters, Mobile Weapons, Technology and Locations, and covers the AU series (G Gundam, IBO, Witch from Mercury, etc.). — [The Gundam Wiki main page](https://gundam.fandom.com/wiki/The_Gundam_Wiki)
- It positions itself as "a resource center… interested in the contribution of official information." It runs an "Improvement Drive" with "Proper citation" as an aim and a "fact checking channel". It draws from the official English subsite, official social accounts, and Gundam.Info announcements. — [The Gundam Wiki main page](https://gundam.fandom.com/wiki/The_Gundam_Wiki)
- A separate **Japanese Gundam Wiki on Fandom** exists (`gundam.fandom.com/ja/`). It has list pages such as "ガンダムシリーズの登場モビルスーツ一覧" and per-series categories (e.g., "カテゴリ:機動戦士Zガンダムの登場モビルスーツ"). — [JA Fandom MS list](https://gundam.fandom.com/ja/wiki/%E3%82%AC%E3%83%B3%E3%83%80%E3%83%A0%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%81%AE%E3%83%A2%E3%83%93%E3%83%AB%E3%82%B9%E3%83%BC%E3%83%84%E4%B8%80%E8%A6%A7); [JA Fandom Z Gundam category](https://gundam.fandom.com/ja/wiki/%E3%82%AB%E3%83%86%E3%82%B4%E3%83%AA:%E6%A9%9F%E5%8B%95%E6%88%A6%E5%A3%ABZ%E3%82%AC%E3%83%B3%E3%83%80%E3%83%A0%E3%81%AE%E7%99%BB%E5%A0%B4%E3%83%A2%E3%83%93%E3%83%AB%E3%82%B9%E3%83%BC%E3%83%84)

**Gundam Unofficial (gundamunofficial.com, Mark Simmons)**
- The "Mobile Suit Catalog" is "based on the 2015 edition" of Kadokawa's *Mobile Suit Illustrated* (the official MS Encyclopedia), which the translator calls "the closest thing to a comprehensive official guide to the Gundam universe". Entries include affiliation, model number and official English name, specs (height, weight, power output, sensor range, armor), armaments and pilots. — [Gundam Unofficial: Mobile Suit Catalog](https://www.gundamunofficial.com/mscatalog.html)
- The catalog is sectioned into Universal Century (36+ subseries), Experimental & Event Movie, Another Century (AUs) and Game Variation, with anchor IDs like `#uc01` and `#ac23`. It follows the official book's inclusion criteria ("setting art from the official filmed works produced by Sunrise, and the semi-official works derived from them"). — [Gundam Unofficial: Mobile Suit Catalog](https://www.gundamunofficial.com/mscatalog.html)
- The archive also hosts a translation of the 1992 *New MS Encyclopedia Ver. 3.0* plus Entertainment Bible / Data Collection material. It is marked "© 1992 Sotsu • Sunrise", and the translator says it is incomplete (missing F90/F91 machines and some background articles). — [Gundam Unofficial: MS Encyclopedia archive](https://www.gundamunofficial.com/archive/msencyclopedia.html)

**Official sites (gundam-official.com / gundam.info)**
- `en.gundam.info/terms-of-service.html` now 302-redirects to `https://en.gundam-official.com/`, meaning GUNDAM.INFO has been folded into gundam-official.com. — observed redirect via [en.gundam.info ToS URL](https://en.gundam.info/terms-of-service.html)
- Fetching `https://en.gundam-official.com/` returned only an HTML shell (viewport metadata, no content), which is consistent with a client-side-rendered app. — [GUNDAM Official (EN)](https://en.gundam-official.com/)

**Wikipedia (EN / JA)**
- EN Wikipedia has a "Database download" page for full dumps, and Wikimedia publishes dump licensing at dumps.wikimedia.org/legal.html. Ready-made parsed dumps exist on Hugging Face (`wikimedia/wikipedia`). — [Wikipedia:Database download](https://en.wikipedia.org/wiki/Wikipedia:Database_download); [Wikimedia dumps legal](https://dumps.wikimedia.org/legal.html); [HF wikimedia/wikipedia](https://huggingface.co/datasets/wikimedia/wikipedia)
- JA Wikipedia keeps aggregate list pages such as "ガンダムシリーズの登場機動兵器一覧" (list of mobile weapons in the Gundam series) and "宇宙世紀の登場機動兵器一覧" (UC mobile weapons list). — [JA WP: Gundam series mobile weapons list](https://ja.wikipedia.org/wiki/%E3%82%AC%E3%83%B3%E3%83%80%E3%83%A0%E3%82%B7%E3%83%AA%E3%83%BC%E3%82%BA%E3%81%AE%E7%99%BB%E5%A0%B4%E6%A9%9F%E5%8B%95%E5%85%B5%E5%99%A8%E4%B8%80%E8%A6%A7); [JA WP: UC mobile weapons list](https://ja.wikipedia.org/wiki/%E5%AE%87%E5%AE%99%E4%B8%96%E7%B4%80%E3%81%AE%E7%99%BB%E5%A0%B4%E6%A9%9F%E5%8B%95%E5%85%B5%E5%99%A8%E4%B8%80%E8%A6%A7)
- EN Wikipedia has a per-series article for nearly every entry (e.g., GQuuuuuuX, The Witch from Mercury, MS IGLOO, Twilight AXIS, Requiem for Vengeance) and a few mecha articles (e.g., "Zaku", "Gundam (fictional robot)"). — [EN WP: GQuuuuuuX](https://en.wikipedia.org/wiki/Mobile_Suit_Gundam_GQuuuuuuX); [EN WP: Zaku](https://en.wikipedia.org/wiki/Zaku); [EN WP: Gundam (fictional robot)](https://en.wikipedia.org/wiki/Gundam_(fictional_robot))

**Japanese wikis**
- wikiwiki.jp hosts a general "機動戦士ガンダム Wiki*" (`wikiwiki.jp/gundam/`) and several game-specific wikis with mobile suit pages (e.g., `wikiwiki.jp/gundammsvs/` for "ガンダムオールモビルスーツVS", and `wikiwiki.jp/ps3-gundam/` for Gundam Senki). — [wikiwiki.jp/gundam](https://wikiwiki.jp/gundam/); [wikiwiki.jp/gundammsvs](https://wikiwiki.jp/gundammsvs/%E3%83%A2%E3%83%93%E3%83%AB%E3%82%B9%E3%83%BC%E3%83%84); [wikiwiki.jp/ps3-gundam](https://wikiwiki.jp/ps3-gundam/%E9%80%A3%E9%82%A6%E8%BB%8D%E3%83%A2%E3%83%93%E3%83%AB%E3%82%B9%E3%83%BC%E3%83%84)
- アニヲタWiki(仮) on atwiki has Gundam MS articles (e.g., "ガンダムタイプ・モビルスーツ"). — [Aniwota Wiki](https://w.atwiki.jp/aniwotawiki/pages/54843.html)

**Gunpla / other fan databases**
- Dalong.net is a "Gunpla Review Database" that catalogs **model kits**, not in-universe mobile suits. Its catalogs are split by line (e.g., Old Gunplas, Club G/Premium Bandai, ETC), with URL patterns like `/reviews/<line>/<line>_cata_e.htm`. — [Dalong.net review index](https://www.dalong.net/reviews/index_e.htm); [Dalong Old Gunplas](https://www.dalong.net/reviews/old/old_cata_e.htm); [Dalong Club G](https://www.dalong.net/reviews/cg/cg_cata_e.htm)
- **mobilesuit.dev** is a newer unofficial site. It describes itself as an "interactive development-tree database of 3,812 Gundam mobile suits across 14 timelines", covering UC, nine AUs, meta series (Build, SD) and crossovers. Its Gunpla section lists ~3,950–3,987 kits across 1,384 mobile suits (grade, scale, list price, release date, box art). The operator is not identified (contact@mobilesuit.dev), and the site states no data sources, API or license. — [mobilesuit.dev mobile suits](https://www.mobilesuit.dev/mobile-suit); [mobilesuit.dev gunpla](https://www.mobilesuit.dev/gunpla)

### Inferences
- **Reliability ranking (inferred):**
  1. Gundam Unofficial is a direct translation of official Kadokawa/Sunrise reference books, so it has the highest per-entry reliability but limited coverage and no recent updates.
  2. MAHQ is single-editor curated, consistent and long-running, though it does not cite sources on its pages.
  3. The Gundam Wiki has the broadest coverage but variable quality, as is usual for crowd-edited wikis. Its stated citation drive implies uneven sourcing.
  4. Wikipedia is reliable for series-level facts (air dates, staff, studios) but thin on individual mobile suits.
- MAHQ's fixed spec labels make it the easiest site to parse into a normalized schema with regex or label/value pairs. The Gundam Wiki's MediaWiki infobox templates can be parsed from wikitext (via dumps or the API) rather than HTML.
- mobilesuit.dev already models development trees and timelines similar to the Docking Bay concept. Because its provenance and license are unknown, it is better treated as a design reference than a data source.

### Gaps
- Exact mobile suit counts per site could not be confirmed (MAHQ total units, Gundam Wiki "Mobile Weapons" category size, and wikiwiki.jp size) because index pages could not be fetched.
- Whether Gundam Wiki mecha articles consistently cite *Gundam Officials*, *Gundam Perfect Files* or *Master Archive* was not verified on individual pages (Fandom pages returned 402 to the fetch tool).
- Whether gundam-official.com currently has a public "MS"/mobile weapons database was not confirmed. The site appears to be JS-rendered, and searches surfaced no such section.
- Pixiv Encyclopedia (dic.pixiv.net), the ANN Encyclopedia mecha coverage, Gunpla 101, the Bandai Hobby site and Mechabay could not be evaluated within the tool budget. The ANN Encyclopedia was only seen as a company page ([ANN: Bandai Namco Filmworks](https://www.animenewsnetwork.com/encyclopedia/company.php?id=22618)).
- No Reddit r/Gundam discussions of MAHQ versus Gundam Wiki reliability were returned by search.

## Q2: What do robots.txt, terms of service and content licenses permit? Are database dumps available?

### Takeaway
Fandom (the Gundam Wiki) and Wikipedia are the legally cleanest sources. Their text is CC BY-SA, which allows reuse with attribution and ShareAlike, and both publish official XML dumps that avoid crawling altogether. MAHQ, Gundam Unofficial, Dalong.net, the official sites and the JP wikis are effectively all-rights-reserved and would need permission or fact-only extraction. No robots.txt file could be retrieved in this session.

### Cited Findings
- Fandom community text is licensed **CC BY-SA 3.0**. Reusers must link the license, attribute (link the article, a stable copy, or list authors) and apply ShareAlike to derivatives. **Images and videos are not necessarily CC BY-SA**, and some communities use alternate licenses (mostly CC BY-NC). — [Fandom Help:Licensing](https://community.fandom.com/wiki/Help:Licensing)
- **Fandom database dumps** are available from each wiki's `Special:Statistics` page in two forms: current pages only, or pages with full history. They are 7z-compressed MediaWiki XML and exclude "private user information or images". Admins can request a new dump via "Send request", and non-admins via Special:Contact. A new dump "can only be requested once every seven days". As of Feb 2024, the page noted dumps "are taking longer to generate than usual" due to an open engineering ticket. — [Fandom Help:Database download](https://community.fandom.com/wiki/Help:Database_download)
- Fandom's Terms of Use and a community thread titled "Am I allowed to scrape Fandom Data?" exist, but both returned **HTTP 402** to the fetch tool, so their contents were not verified. — [Fandom Terms of Use](https://www.fandom.com/terms-of-use); [Fandom community: Am I allowed to scrape Fandom Data?](https://community.fandom.com/f/p/4400000000002575935)
- HTTP 402 is the status code Cloudflare's "Pay Per Crawl" uses. Cloudflare began blocking AI crawlers by default and launched Pay Per Crawl in July 2025, then launched "AI Crawl Control" in Aug 2025. — [MediaPost, 07/01/2025](https://www.mediapost.com/publications/article/407093/cloudflare-blocks-ai-content-scrapers-across-24-o.html); [Cloudflare AI Crawl Control changelog](https://developers.cloudflare.com/changelog/2025-08-27-ai-crawl-control-launch); [Cloudflare blog](https://blog.cloudflare.com/introducing-ai-crawl-control/)
- A Fandom community post titled "BROKEN robots.txt" exists, suggesting past issues with Fandom's robots.txt. Its content was not fetched. — [Fandom community post](https://community.fandom.com/f/p/2913406835228674125)
- Wikimedia publishes dump license terms at dumps.wikimedia.org/legal.html. The page was cache-only and could not be fetched. — [Wikimedia dumps legal](https://dumps.wikimedia.org/legal.html)
- MAHQ: "Original content ©2000 to by Accidental Pilot, Inc." (all rights reserved by default; no open license stated). — [MAHQ RX-78-2](https://www.mahq.net/rx-78-2/)
- Gundam Unofficial's MS Encyclopedia translation carries "© 1992 Sotsu • Sunrise" (the underlying content is copyrighted official material). — [Gundam Unofficial MS Encyclopedia](https://www.gundamunofficial.com/archive/msencyclopedia.html)
- mobilesuit.dev: "Gundam and all related marks are trademarks of Sotsu and Sunrise; this is an unofficial fan-made reference." No data license is given. — [mobilesuit.dev](https://www.mobilesuit.dev/mobile-suit)

### Inferences
- The 402 responses from Fandom pages suggest Fandom sits behind Cloudflare AI-crawler controls (Pay Per Crawl / AI Crawl Control). A plain HTTP crawler with a non-browser user agent may be blocked or asked to pay. This is a strong reason to use the **Special:Statistics XML dump** or the MediaWiki API (`/api.php`) with a descriptive user agent rather than HTML crawling. This should be verified by loading gundam.fandom.com/robots.txt and the ToS in a normal browser.
- CC BY-SA ShareAlike applies to any **text** copied from Fandom or Wikipedia. Spec facts themselves (height, weight, model number) are generally treated as uncopyrightable facts, but prose descriptions would trigger ShareAlike. A practical approach is to store only factual fields plus a source link and attribution per record. (This is a general legal inference, not legal advice.)
- MAHQ and Gundam Unofficial are small, personally run sites. Bulk crawling them without permission is ethically and legally riskier than using Fandom or Wikipedia. Asking the owners (Accidental Pilot / Mark Simmons) for permission, or using them only for manual verification, is the safer route.
- Bandai Namco Filmworks / Sotsu / Sunrise own the IP. Official-site content, including images, should not be scraped into a redistributed dataset.

### Gaps
- No robots.txt could be retrieved for **any** site (gundam.fandom.com, mahq.net, gundam-official.com, wikiwiki.jp, dic.pixiv.net, animenewsnetwork.com, dalong.net, etc.). All direct fetches were blocked by the sandbox proxy or required URL provenance. These must be checked manually.
- The scraping clauses in the Fandom Terms of Use and the gundam-official.com ToS were not retrievable (402 for Fandom; the official ToS URL redirected to a JS shell).
- No terms pages were found for wikiwiki.jp (returned 403), Pixiv Encyclopedia or Dalong.net.

## Q3: What practical crawling concerns exist (anti-bot measures, JS rendering, rate limits, sitemaps, URL patterns)?

### Takeaway
MAHQ is the easiest site to crawl directly: server-rendered WordPress, predictable `/<model-number>/` slugs and series index pages. WordPress sites usually expose `wp-sitemap.xml` and the `/wp-json/` REST API, but neither was confirmed. Fandom and Wikipedia should be ingested via dumps or the API rather than crawled. The official Gundam site is client-rendered and would need a headless browser. wikiwiki.jp and mechatalk.net returned 403 to automated fetches.

### Cited Findings
- MAHQ is built on WordPress, with series indexes at `/gundammain/` and alphabetical series menus. Unit URLs follow `mahq.net/<designation>/`. — [MAHQ RX-78-2](https://www.mahq.net/rx-78-2/)
- Old MAHQ static URLs (`/mecha/gundam/<series>/<model>.htm`) still resolve or appear in indexes, and a third-party project scraped the old index at `https://www.mahq.net/mecha/gundam/index.htm`. — [MAHQ legacy URL](http://mahq.net/mecha/gundam/doublefake/amx-003s.htm); [Askannz/gundam-stable-diffusion](https://github.com/Askannz/gundam-stable-diffusion)
- Fandom XML dumps exclude images, can be refreshed at most weekly, and have had generation delays (Feb 2024 notice). — [Fandom Help:Database download](https://community.fandom.com/wiki/Help:Database_download)
- Fandom pages (Terms of Use, community posts) returned **HTTP 402**, while the Gundam Wiki main page and help pages did load. This suggests the blocking is selective or rate-based. — observed during fetches of [fandom.com/terms-of-use](https://www.fandom.com/terms-of-use) and [community.fandom.com post](https://community.fandom.com/f/p/4400000000002575935)
- Cloudflare's default AI-crawler blocking (since July 2025) and 402 Pay Per Crawl responses affect sites that opt in. — [AlternativeTo news, July 2025](https://alternativeto.net/news/2025/7/cloudflare-blocks-ai-crawlers-by-default-and-launches-pay-per-crawl-for-publishers); [Crawlora, 2026](https://crawlora.net/blog/cloudflare-ai-crawler-block-2026)
- `en.gundam-official.com` served an empty HTML shell to a non-JS fetcher (client-side rendering). — [GUNDAM Official (EN)](https://en.gundam-official.com/)
- wikiwiki.jp (`/gundam/`) and mechatalk.net returned **HTTP 403** to the fetch tool. — [wikiwiki.jp/gundam](https://wikiwiki.jp/gundam/); [Mecha Talk](https://mechatalk.net/viewtopic.php?t=16584)
- Gundam Unofficial's catalog is a single long HTML page with section anchors (`#uc01`, `#ac23`), which is easy to fetch in one request. — [Gundam Unofficial catalog](https://www.gundamunofficial.com/mscatalog.html)

### Inferences
- **Recommended ingestion strategy (inferred):**
  1. Gundam Wiki: request or download the Special:Statistics "current pages" XML dump, then parse mobile-weapon infobox templates with `mwparserfromhell`. For delta updates, use the MediaWiki API (`api.php?action=query&list=categorymembers` on the mobile weapons categories) with a contact-bearing user agent and ~1 req/s.
  2. Wikipedia: use dumps or the API for series and timeline metadata.
  3. MAHQ: crawl `/gundammain/` series index pages, then unit pages politely (cache, 1 request every few seconds), ideally after contacting the owner. Check `/wp-sitemap.xml` and `/wp-json/wp/v2/pages` first, since they may list all unit pages in one place.
- Images from any of these sites should not be hot-linked or redistributed. Fandom dumps exclude them, and image licenses differ from text licenses.
- The JP wikis (wikiwiki.jp, atwiki) appear to block automated fetches and have unclear licensing. They are better used as manual cross-references for Japanese names.

### Gaps
- No sitemap URLs were confirmed for any site, and no Crawl-delay values were found, because robots.txt could not be fetched.
- Whether MAHQ uses Cloudflare or any rate limiting was not determined. The fetch succeeded without obstruction.
- Whether the Gundam Wiki uses a consistent Portable Infobox template (and its field names) for all mobile weapons was not verified.

## Q4: Are there existing open-source scrapers or datasets built from these sites?

### Takeaway
No open, structured, spec-level Gundam mobile suit dataset (CSV/JSON of model number, pilot, height and so on) turned up. The datasets that exist are image datasets scraped from MAHQ for ML, Gunpla kit datasets, and a Gundam Card Game API.

### Cited Findings
- **Askannz/gundam-stable-diffusion** fine-tuned Stable Diffusion on mecha images scraped from MAHQ's Gundam index (`mahq.net/mecha/gundam/index.htm`). The scraper code is not included and no license is stated. — [GitHub: Askannz/gundam-stable-diffusion](https://github.com/Askannz/gundam-stable-diffusion)
- The resulting captioned image dataset is on Hugging Face as **Gazoche/gundam-captioned** (BLIP-assisted color captions). — [HF: Gazoche/gundam-captioned](https://huggingface.co/datasets/Gazoche/gundam-captioned)
- **Kaggle "Gunpla Dataset" (marzho)** covers HG, RG, MG, PG and SD model kits. Row count, fields, license and source were not visible in the fetched metadata. — [Kaggle: Gunpla Dataset](https://www.kaggle.com/datasets/marzho/gunpla-dataset)
- **yzRobo/gcg-api** offers "free, unofficial data + REST API for the Gundam Card Game (Bandai GCG). Weekly-refreshed, metadata-only. Not affiliated with Bandai." — [GitHub: yzRobo/gcg-api](https://github.com/yzRobo/gcg-api)
- **nugujeyong/GANdam** generates new Gundam designs with WGAN-GP (an image-only project). — [GitHub: GANdam](https://github.com/nugujeyong/GANdam)
- **mobilesuit.dev** aggregates 3,812 mobile suits across 14 timelines plus ~3,950 kits, but publishes no dataset, API or source attribution. — [mobilesuit.dev](https://www.mobilesuit.dev/mobile-suit)

### Inferences
- MAHQ is the de facto scrape source in existing projects, which supports its reputation as the most consistently structured Gundam mecha catalog.
- The lack of a public spec-level dataset is an opportunity: building one from the Fandom dump (CC BY-SA) and publishing it under CC BY-SA would be legally clean. The gcg-api project could supply card-game metadata that cross-links mobile suit names.

### Gaps
- No search results showed GitHub scrapers specifically targeting the Gundam Wiki (Fandom) infoboxes. A more targeted GitHub code search (e.g., "gundam.fandom.com" in code) was not run within budget.
- No Kaggle or Hugging Face tabular dataset of mobile suit specifications was found.
