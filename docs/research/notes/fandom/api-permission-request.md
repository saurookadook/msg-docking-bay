# Draft: API permission request to Fandom

- **To:** support@fandom.com (the contact the Terms of Use list)
- **Status:** Draft. Not sent yet.
- **Before sending:** confirm the bracketed items.

---

**Subject:** Request for written permission: low-rate, read-only API access to The Gundam Wiki
(gundam.fandom.com)

Hello Fandom Support,

I'm building **msg-docking-bay**, a [non-commercial] fan project: a browsable, source-attributed catalog of
Gundam mobile suits and the series they appear in. The code is at
https://github.com/saurookadook/msg-docking-bay. The Gundam Wiki is by far the best-sourced reference for
this, and I'd like to use it properly.

Your Terms of Use (revised December 19, 2025) require express written permission for any automated access to
the Services. I'm writing to ask for that permission for the narrow, read-only use described below. If you'd
rather I use a different channel, or if a policy already covers this, please point me to it.

**What I'd like to do**

- **Read-only `api.php` requests to gundam.fandom.com only.** No HTML page scraping, no login, no edits.
  - `action=query&list=recentchanges` (main namespace) to find pages changed since the last run.
  - `action=query&prop=revisions` (batches of up to 50 titles) to fetch the current wikitext and revision ID
    of changed mobile-weapon pages.
  - `action=ask` (Semantic MediaWiki) on `[[Category:Mobile Weapons]]` for the infobox properties.
- **Volume and rate:**
  - The initial load is about 100 requests in total.
  - After that, one sync run a week of roughly 10–30 requests.
  - All requests are serial: one at a time, at most one per second, with backoff on errors and on any
    `Retry-After`.
- **Identification:** every request sends the User-Agent
  `msg-docking-bay-ingest/<version> (+https://github.com/saurookadook/msg-docking-bay) httpx/<version>`. You
  can reach me at the address I'm writing from.
- **What is stored and shown:**
  - Factual fields only, such as model number, height, weight, pilots, manufacturer and appearances. Each is
    stored with a link to the source article, its revision ID, and the CC BY-SA license notice, in line with
    your licensing page.
  - No images or other media, and no copied article prose.
  - Visitors to the app are served from my own database, never by live calls to Fandom.
- **No AI or machine-learning training.** The content is not used to train or fine-tune any AI or ML system.
- **No circumvention.** The client will never try to get past Cloudflare challenges or any other access
  control. If you'd like it to stop or slow down, I'll do so immediately.

**Until I hear back**

I'll work only from the "current pages" database dump on Special:Statistics. The latest dump I can see is
dated August 26, 2025. **Could you also generate a fresh dump of gundam.fandom.com?** I understand requests
are limited to one every seven days.

For transparency: on October 31, 2026, while checking feasibility, I sent about 20 slow, identified,
read-only requests to `gundam.fandom.com/api.php`. I then read your Terms of Use and stopped. I have made
no automated requests since, and I won't make any without your permission.

If you grant permission, I'm happy to accept any conditions you set, such as a different rate, specific
endpoints, a required User-Agent format, or a bot account. I'll keep a record of your reply alongside the
project's documentation.

Thank you for your time.

Best regards,
Andy Maskiell
[Optional: GitHub @saurookadook]
