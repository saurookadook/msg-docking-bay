# Paid APIs and Data-Licensing Options for Mobile Suit Gundam Data (as of Oct 2026)

## 1. Are there any paid Gundam-specific APIs (RapidAPI, APILayer, other marketplaces)?

### Takeaway
I found no paid, Gundam-specific API on RapidAPI, APILayer or any other marketplace, and no commercial vendor sells mobile-suit-level data. The only Gundam-specific APIs I found are free fan projects that pull from fan wikis or scrape retailer sites. None has a clear license.

### Cited Findings
- A search for "Gundam API RapidAPI mobile suits" returned no RapidAPI or marketplace listing. The only Gundam API results were a fan-made "Gundam API" at gundam-api.pages.dev and a GitHub project, gunplaAPI. — [Search results: gundam-api.pages.dev](https://gundam-api.pages.dev/); [brianlin345/gunplaAPI on GitHub](https://github.com/brianlin345/gunplaAPI)
- gundam-api.pages.dev calls itself a "free public", "read-only" API with endpoints for Gundams (mobile suits) and Characters. A Series endpoint is marked "coming soon". Its data is "sourced from fan wikis". The site names no publisher and gives no license or terms. It says the source code "will be made open source once the codebase has been tidied up." — [Gundam API docs](https://gundam-api.pages.dev/)
- gunplaAPI on GitHub is described as an "API containing information on HG Gunpla model kits", meaning it covers High Grade kits only. — [GitHub: brianlin345/gunplaAPI](https://github.com/brianlin345/gunplaAPI)
- The only paid offerings that mention Gunpla are pay-per-use scrapers on Apify that crawl HobbyLink Japan (see Q4). They are not Gundam data APIs and are not official. — [Apify HLJ scraper](https://apify.com/jungle_synthesizer/hobbylinkjapan-anime-figure-gunpla-catalog-scraper/api)
- Ximilar, a visual-AI vendor, added Gundam (a trading card game) to its collectibles recognition system in 2025. It identifies cards, not mobile suit specs. — [Ximilar blog](https://www.ximilar.com/blog/2025-additions-to-collectibles-recognition-system/)

### Inferences
- There is no paid Gundam API to buy. Any source with mecha-level data (model number, pilot, height, weight, armaments) traces back to fan wikis such as the Gundam Wiki on Fandom or MAHQ, or to official sites that publish no API.
- The fan APIs are free but have no license and no named maintainer. That makes them weak "trusted" sources: the report writer should treat them as derivatives of Fandom wiki content, with the CC BY-SA obligations that come with it (see Q2) and an unknown maintenance outlook.

### Gaps
- I could not browse RapidAPI or APILayer directly; the conclusion rests on search results. A small, hidden Gundam listing could exist, but none turned up in search.
- I could not confirm whether gunplaAPI is still maintained or what license it uses.

## 2. Paid tiers of general entertainment/anime metadata APIs: price, Gundam coverage depth, terms, commercial use

### Takeaway
Every general metadata provider covers Gundam only at the title level: series, films, OVAs, episodes, cast/staff and, for games, game titles. None models mobile suits as entities. Prices run from free under revenue thresholds (TheTVDB, Simkl, IGDB) to $150,000 a year (IMDb). For a hobby or fan app, the free and low tiers already cover the series-level data, so paying buys nothing mecha-specific.

### Cited Findings
**TheTVDB**
- Tiered by company revenue: under $50k/yr is free but requires "attribution with a direct link to TheTVDB.com"; $50k–$250k/yr is $1,000/yr; $250k–$1M/yr is $10,000/yr; $1M+ is "contact sales". The page footer is © 2026. — [TheTVDB API information](https://www.thetvdb.com/api-information)
- "Our API is available for both commercial projects and to individual developers." It offers "significant discounts" to free and open-source projects. — [TheTVDB API information](https://www.thetvdb.com/api-information)
- TheTVDB is a community-driven TV and movie metadata database founded in 2006 that covers series, movies, people, artwork and awards. — [thetvdb/v4-api on GitHub](https://github.com/thetvdb/v4-api)
- Separately, TheTVDB introduced a paid end-user subscription model for v4, which affected Kodi add-ons. — [KodiTips](https://koditips.com/tvdb-paid-subscription-kodi/); [TheTVDB subscribe page](https://thetvdb.com/subscribe)

**TMDB (The Movie Database)**
- TMDB hosts forum threads titled "Commercial usage pricing", "Commercial License" and "What is the price of commercial API?", so a separate commercial track exists. TMDB's robots.txt blocked me from fetching them. — [TMDB Talk: Commercial usage pricing](https://www.themoviedb.org/talk/622b91d0d236e60045f62782); [TMDB Talk: Commercial License](https://www.themoviedb.org/talk/5d6e51969ae61300130b0a50?language=en-US)
- A third-party post claims "The TMDB API is generally free, for both commercial and non-commercial use." This is not a primary source and conflicts with the existence of the commercial-license threads above. — [Threads post](https://www.threads.com/@itslazyvar/post/CvpyooOyaGk)
- API Evangelist's profile describes TMDB as a "community-built movie, TV, and people metadata catalog with a free REST API used by streaming apps, recommendation engines, second-screen experiences, fan sites". — [api-evangelist/tmdb](https://github.com/api-evangelist/tmdb)

**IMDb (via AWS Data Exchange / AWS Marketplace)**
- "IMDb Essential Metadata for Movies/TV/OTT (API)" costs **$150,000 upfront for a 12-month term**, plus metered overage of $0.00000093 per 100 bytes of response. The listing says "Final price subject to specific licensed use case" and "Refunds are not offered". — [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-wdqq4hg3bcbws)
- Contents: 9M+ titles, 12M+ names, essential metadata for movies, TV, OTT and video games, ratings from 1B votes, alternate titles and release dates. It is a GraphQL API delivered through AWS Data Exchange. The licensing contact is imdb-licensing@imdb.com. — [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-wdqq4hg3bcbws); [IMDb Developer](https://developer.imdb.com/)

**Trakt**
- A blog post reports that in early August 2026, creating new API applications started to require a $4.99/month VIP subscription, and some developers' existing API apps "disappeared". — [ETTAYEB blog](https://ettayeb.fr/en/selfhosted/trakt-api-paywall-selfhosted-media/); corroborated by [tuliprox GitHub issue #853](https://github.com/euzu/tuliprox/issues/853)
- VIP renewals moved to a new standard rate on June 12, 2025, roughly doubling prices. Earlier in 2025 Trakt also tightened free-user limits. — [AlternativeTo (May 2025)](https://alternativeto.net/news/2025/5/trakt-announces-all-vip-renewals-will-switch-to-a-new-standard-rate-doubling-prices/); [Trakt forums](https://forums.trakt.tv/t/upcoming-vip-renewal-pricing-changes-effective-june-12-2025/56649); [AlternativeTo (Feb 2025)](https://alternativeto.net/news/2025/2/trakt-tv-has-set-stricter-limits-for-free-users-and-raised-vip-subscription-prices-by-100-/)
- A Trakt forum thread asks about commercial use on the free plan, so the commercial terms are not obvious. I did not fetch the thread. — [Trakt forums](https://forums.trakt.tv/t/asking-about-api-commercial-uses-on-free-plan/99367)

**Simkl**
- Free for non-commercial projects and for commercial apps earning under $150/month. Above that, "you must obtain a commercial license before continuing to use the API." No price is published. — [Simkl API rules](https://api.simkl.org/api-rules)
- Attribution rules: "Wherever Simkl data appears in your app, link back to the Simkl page for that specific item." Limits are 10 GET/sec and 1 POST/sec. Exceeding them leads to suspension "without warning, no appeal." — [Simkl API rules](https://api.simkl.org/api-rules)

**AniDB**
- AniDB's API requires client registration, and its forum has several threads on clients being banned from the API. Its HTTP API is documented on the AniDB wiki. AniDB's policy page returned a 403, so I could not quote its commercial-use rules. — [AniDB forum: API Client Banned](https://anidb.net/forum/thread/51988); [AniDB HTTP API Definition](https://wiki.anidb.net/HTTP_API_Definition); [AniDB Policies](https://anidb.net/policy)

**IGDB (Twitch), for Gundam video games**
- After Twitch acquired IGDB (September 2019), an IGDB representative said in a 2019–2020 thread that commercial use was fine under the single free tier, and that a policy update on commercial specifics would follow. — [Twitch Developer Forums](https://discuss.dev.twitch.com/t/commercial-use-of-igdb-api/23567); [TechCrunch](https://techcrunch.com/2019/09/17/twitch-acquires-gaming-database-site-igdb-to-improve-its-search-and-discovery-features)

**Fandom (the Gundam Wiki)**
- Fandom's licensing page reads: "Except where otherwise permitted, the text on..." (snippet only). Fandom wiki text is generally CC BY-SA. — [Fandom Licensing (HN discussion quoting it)](https://news.ycombinator.com/item?id=43529416); [fandom.com/licensing](https://www.fandom.com/licensing) (fetch returned HTTP 402)
- The Gundam Wiki uses official screenshots and scans under a "Fair use" template (for example `{{Fair use|tv-screenshot}}`) and requires verifiable official sources. So images on the wiki are not CC-licensed; they are hosted under a fair-use rationale. — [Gundam Wiki: Image Policy](https://gundam.fandom.com/wiki/Gundam_Wiki:Image_Policy); [Gundam Wiki: Copyrights](https://gundam.fandom.com/wiki/Gundam_Wiki:Copyrights)

### Inferences
- **Coverage depth:** TheTVDB, TMDB, IMDb, Trakt, Simkl and AniDB all model shows, films, episodes and people (voice cast and staff), with AniDB covering anime only. None of them has "mecha" or "mobile suit" entities. They are useful for the "universes / series / films / OVAs" layer, such as Universal Century series lists, air dates and posters, but not for suit specs.
- **IMDb at $150k/yr** is out of scale for a fan app and adds nothing Gundam-specific.
- **TheTVDB** is the most transparent paid option. A personal or fan project under $50k revenue pays $0 with attribution. Only past $50k revenue does it cost $1,000/yr.
- **Trakt** now effectively charges a developer $4.99/mo to hold an API app. It is a tracking and social service, not a deep metadata source, so it adds little here.
- **IGDB** remains the default for Gundam game titles. It is free, and paid tiers were not mentioned in the sources I found.
- **Fandom** text is reusable commercially under CC BY-SA, with attribution and share-alike obligations. Its images belong to Sotsu/Sunrise and cannot be re-licensed by Fandom. I found no evidence of a paid Fandom data-licensing product for third-party developers.

### Gaps
- **Gracenote/Nielsen:** I did not research pricing in this pass. Gracenote is an enterprise B2B video metadata vendor with quote-based pricing, but I found no source on its Gundam coverage or pricing, so the report should treat it as "enterprise, quote only, unverified".
- **TMDB commercial price:** I could not fetch the TMDB threads (robots.txt) or confirm a current figure or contact route. The sources conflict on whether commercial use needs a paid license.
- **AniDB commercial terms:** the policy page returned a 403.
- **Current IGDB terms (2026):** the API docs page returned a 403, so I could not confirm whether commercial use now requires a partnership agreement.
- **Fandom commercial data licensing:** the licensing page returned HTTP 402, so I could not verify whether Fandom sells any data or enterprise product.

## 3. Is there an official licensing route for Gundam data or imagery (Bandai Namco Filmworks / Sunrise, Gundam.info, GUNPLA database)? What are the IP considerations?

### Takeaway
I found no official partner API or data-licensing program for Gundam data, on Gundam.info, the Bandai Hobby site or Premium Bandai. Rights management moved inside Bandai Namco Filmworks on April 1, 2026, so any official image or spec licensing would now be negotiated directly with BNFW. The official copyright notice is "©SOTSU・SUNRISE".

### Cited Findings
- In October 2025, Anime News Network reported that "Bandai Namco Filmworks, Sotsu Reorganize to Combine Gundam Units." — [ANN, 2025-10-20](https://www.animenewsnetwork.com/news/2025-10-20/bandai-namco-filmworks-sotsu-reorganize-to-combine-gundam-units/.230119) (page returned 403; headline only)
- "Starting April 1, 2026, BNFW will absorb all Gundam-related planning, production, and copyright management from Sotsu, creating a unified strategic business group." — [Anime Rave on X](https://x.com/AniRave/status/2019359081778024595)
- "SOTSU's Gundam-related business will be integrated into Bandai Namco Filmworks starting April 2026… [SOTSU] will focus on advertising tasks going forward." — [Manga Mogura RE on X](https://x.com/MangaMoguraRE/status/2019347697342255544)
- Sunrise studio has been merged into Bandai Namco Filmworks. — [Cartoon Brew](https://www.cartoonbrew.com/business/sunrise-bandai-namco-gundam-cowboy-bebop-215458.html); [Wikipedia: Bandai Namco Filmworks](https://en.wikipedia.org/wiki/Bandai_Namco_Filmworks)
- Gundam.info (the "GUNDAM Official Website") is the official news and portal site; searches turned up no developer API or data-licensing page. — [GUNDAM Official Website](https://en.gundam.info/)
- Other official Gundam sites, such as Gundam Factory Yokohama and Gundam Challenge, publish "Terms of service" and "Agreement for use / Copyright / Disclaimer" pages that govern reuse of their content. — [Gundam Factory ToS](https://gundam-factory.net/en/agreement/); [Gundam Challenge agreement](https://gundam-challenge.com/en/agreement/index.html)
- Bandai Namco's group-level Terms of Use govern reuse of content on its sites. — [Bandai Namco Holdings Terms of Use](https://www.bandainamco.co.jp/en/terms/index.html)
- The Gundam Wiki itself relies on a fair-use rationale (not a license) to host official screenshots and scans. — [Gundam Wiki: Image Policy](https://gundam.fandom.com/wiki/Gundam_Wiki:Image_Policy)

### Inferences
- **No data API exists to license.** Official mobile suit "profiles" (spec sheets on Gundam.info and series sites) are editorial web content, not a feed. Anything sold as "official Gundam data" would be a bespoke license negotiated with BNFW's Gundam rights group. That is realistic for commercial partners such as game studios or toy makers, not for a fan web app.
- **IP considerations for a fan app:**
  - Factual specs (model number, height, weight, pilot) are facts, which are generally not copyrightable on their own. Compiling and presenting them in your own words is lower risk than copying text verbatim.
  - Official artwork and screenshots are copyrighted (©SOTSU・SUNRISE, now administered by BNFW). Hosting them relies on fair use, as the Fandom wiki does, and that risk grows if the app is monetized.
  - The "Gundam" name and logos are trademarks. The app name "Mobile Suit Gundam: Docking Bay" uses the franchise's full title, which could draw trademark scrutiny if it is ever commercialized. A disclaimer such as "unofficial fan project, not affiliated with Bandai Namco Filmworks / Sotsu / Sunrise" is advisable.
  - Safer image strategies: link to or embed from official pages instead of rehosting, use user-uploaded Gunpla photos, or use no images at the start.

### Gaps
- I could not fetch en.gundam.info's terms page (the permission request timed out), so I cannot quote its exact reproduction and linking clauses.
- I found no public BNFW licensing contact or form specifically for Gundam IP. The Bandai Namco group terms exist, but I found no dedicated licensing portal.
- I did not find any Bandai Hobby or Premium Bandai developer or affiliate API. If Premium Bandai has an affiliate program, I found no source for it.
- I found no published Bandai Namco fan-works guideline (二次創作ガイドライン) specific to Gundam in this pass.

## 4. Are there hobby/Gunpla data providers with APIs that map kits to mobile suits?

### Takeaway
No official Gunpla catalog API exists from Bandai Hobby, HobbyLink Japan (HLJ) or others. The paid options are third-party scrapers on Apify that extract HLJ product listings for a per-record fee. They return product fields (name, series, scale, JAN barcode, price) but no structured link from kit to mobile suit, and scraping HLJ may breach HLJ's terms.

### Cited Findings
- "HobbyLink Japan Anime Figure & Gunpla Catalog Scraper" on Apify, by the community developer BowTiedRaccoon: "names, prices in JPY, release status, manufacturer, series, scale, JAN barcodes, and image URLs". Pricing is **$2.00 per 1,000 records**. It is a third-party scraper, not an official HLJ API, with about 3 users and 135 runs. It supports backfill, weekly new-release tracking and pre-order monitoring. — [Apify listing](https://apify.com/jungle_synthesizer/hobbylinkjapan-anime-figure-gunpla-catalog-scraper/api)
- Other Apify scrapers cover the same ground: "HobbyLink Japan Gunpla & Figure Price + Stock Data API" (jpmarketdata) and "HobbyLink Japan Scraper – Gunpla, Anime Figures & Model Kits API" (lulzasaur). — [Apify jpmarketdata](https://apify.com/jpmarketdata/hlj-hobby-market-checker/api); [Apify lulzasaur](https://apify.com/lulzasaur/hlj-scraper/api/python)
- A free GitHub project, gunplaAPI, covers HG kits only. — [GitHub: gunplaAPI](https://github.com/brianlin345/gunplaAPI)

### Inferences
- Kit-to-mobile-suit mapping would have to be built in-house, by matching kit names such as "HG 1/144 RX-78-2 Gundam" against the model numbers in the app's suit database. Model numbers like RX-78-2 and MS-06S appear in kit names, so the matching is feasible.
- The JAN barcode from the scrapers is a useful stable product key.
- Paying $2 per 1,000 records for low-adoption scrapers adds legal risk (scraping HLJ) and maintenance risk (the scrapers break when HLJ's site changes). A Gunpla feature is a later-phase concern anyway.

### Gaps
- I did not find whether HLJ runs an affiliate program with a product feed.
- I found no Bandai Hobby (bandai-hobby.net) or Gunpla.info API. The Bandai Spirits hobby catalog appears to be web-only, but I did not confirm this with a primary source.
- I did not verify pricing for the jpmarketdata and lulzasaur actors.

## 5. Overall: is any paid API worth paying for this use case compared with free options?

### Takeaway
No paid API is worth paying for at launch. No paid product offers mobile-suit-level Gundam data. The series, film and OVA layer is covered for free or at no cost under revenue thresholds by TheTVDB (free under $50k with attribution), Simkl (free under $150/mo revenue), IGDB (free) and TMDB (free tier). Paid tiers only matter if the app later earns significant revenue: TheTVDB at $1,000/yr from $50k revenue, Simkl's unpublished commercial license past $150/mo.

### Cited Findings
- TheTVDB: $0 under $50k revenue with attribution; $1,000/yr at $50k–$250k. — [TheTVDB API information](https://www.thetvdb.com/api-information)
- Simkl: free under $150/month revenue; commercial license above that. — [Simkl API rules](https://api.simkl.org/api-rules)
- IMDb: $150,000/yr. — [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-wdqq4hg3bcbws)
- Trakt: $4.99/mo VIP now needed to create API apps (August 2026). — [ETTAYEB](https://ettayeb.fr/en/selfhosted/trakt-api-paywall-selfhosted-media/)
- The only Gundam-specific APIs found are free, fan-run and sourced from fan wikis. — [Gundam API](https://gundam-api.pages.dev/)
- Paid Gunpla data is available only through Apify scrapers at about $2 per 1,000 records. — [Apify](https://apify.com/jungle_synthesizer/hobbylinkjapan-anime-figure-gunpla-catalog-scraper/api)

### Inferences
- Suggested ranking of the paid and paid-tier options for this app (for the report writer's "top 3" synthesis):
  1. **TheTVDB.** It has transparent pricing, is effectively free for a fan app, includes commercial terms and has good anime series and episode coverage. Use it for the series layer.
  2. **Simkl.** It is anime-friendly and free under a low revenue threshold, but its attribution and rate-limit rules are strict and the commercial license price is unpublished.
  3. **IGDB (free) for the games layer.** If a paid choice is required for this slot, it would be the Apify HLJ scrapers for Gunpla, which carry heavy caveats.
  - Not recommended: IMDb (cost), Trakt (newly paywalled API and little metadata depth), Gracenote (enterprise only, unverified).
- Mobile suit data, the core of the app, will come from free or crawlable sources: Fandom's Gundam Wiki text under CC BY-SA, MAHQ, or Gundam.info pages read manually. Those are covered by other researchers. The real "cost" is license compliance (CC BY-SA attribution and share-alike) and image rights, not API fees.
- An official BNFW license is the only route to clean rights for images and specs. It is a bespoke negotiation with no public program, and is realistic only if the app becomes a commercial product.

### Gaps
- I found no public price or program for an official BNFW data or image license.
- I did not verify Gracenote and TMDB commercial pricing (see Q2 gaps).
