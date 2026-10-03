# Image rights for Docking Bay

_Last updated: 2026-10-03. This is background research, not legal advice._

## Decision (current)

**For now, Docking Bay will use mobile suit images from the Gundam Wiki (gundam.fandom.com) while the app is completely free and non-commercial.**

**Stop condition:** If the app ever has any of the following, it must **stop using Gundam Wiki images** and switch to one of the alternatives below before the change goes live:

- advertising of any kind
- donations or tip jars (e.g., Ko-fi, Buy Me a Coffee, GitHub Sponsors)
- a Patreon or similar membership
- a paid subscription, paid tier, or paywalled features
- affiliate links (e.g., to Gunpla shops such as HobbyLink Japan, Amazon or Premium Bandai)
- sponsorships, sponsored content, or merchandise sales
- any other way the app or its operator earns money from the app

This decision accepts some risk. Keeping the app free helps a fair-use argument but **does not grant permission** to use the images (see below). The realistic exposure is a takedown request from the rights holder. That request might go to the hosting provider, which could take the whole site offline.

### Guardrails while the decision is in effect

- **Keep images swappable.** Store each image's original source URL, its origin (e.g. `source: "gundam-wiki"`) and its key in our storage on every record, so that all wiki images can be found and removed or replaced in one pass.
- **Use web resolution only.** Show thumbnails or modest sizes, not full-resolution scans.
- **Credit the rights holder.** Show the copyright notice (e.g., "© SOTSU・SUNRISE", or the notice the official site uses for that work). Also link back to the Gundam Wiki page the image came from.
- **Add an "unofficial" disclaimer.** State that the app is an unofficial fan project and not affiliated with or endorsed by Bandai Namco Filmworks, Sunrise or Sotsu. "Gundam" is a trademark.
- **Have a takedown process ready.** Publish a contact address and remove images promptly on request.
- **Host our own copies (decided 2026-10-03).** Images are copied to our own storage and served from a CDN or similar service. We do not hotlink from Fandom's servers. This means we are clearly responsible for the copies, so a takedown has to remove the file from storage and also clear it from the CDN's cache.
- **Re-check this decision** whenever a monetization feature is proposed (the stop condition above).

## Why being free doesn't make it safe

- **The Gundam Wiki doesn't own the images.** Its [Copyrights page](https://gundam.fandom.com/wiki/Gundam_Wiki:Copyrights) says all images "are copyrighted by their parent company and/or the artist(s)." The wiki uses them under US fair use. It allows visitors to download them only "for personal use, as long as they are not used for profit."
- **The CC BY-SA license covers the wiki's text, not its images.** See the wiki's [Image Policy](https://gundam.fandom.com/wiki/Gundam_Wiki:Image_Policy).
- **The rights holder is Bandai Namco Filmworks.** It absorbed Gundam planning, production and copyright management from Sotsu on April 1, 2026 ([ANN](https://www.animenewsnetwork.com/news/2025-10-20/bandai-namco-filmworks-sotsu-reorganize-to-combine-gundam-units/.230119)).
- **Using the images means making our own fair use argument.** Courts judge fair use case by case, on four factors. Being non-commercial helps one of them. Two factors work against us:
  - we would copy whole images
  - we would use them for the same purpose as the official art: showing what a suit looks like
- **There is no official fan-works guideline for Gundam.** Some franchises publish guidelines that grant permission for fan works. A 2026 Japanese roundup of these guidelines lists none for Gundam, Sunrise or Bandai Namco ([posfie](https://posfie.com/@s1yu/p/nlIzjqg)).

## Alternative image sources (safest first)

These are the fallbacks if the stop condition is triggered. Some can also be used alongside the wiki images now.

1. **Embed from official channels.** Show official trailers from the GUNDAM.INFO YouTube channel, or posts from official social accounts, using each platform's own player. The platforms' terms allow embedding, and the rights holder chose to publish there.
2. **Link out instead of hosting.** Link each suit page to its Gundam Wiki page, the official work page on gundam-official.com, or the Bandai Hobby kit page for visuals.
3. **Let users upload Gunpla photos.** Photos of kits are still based on copyrighted designs, but fans share them widely and the rights holder generally tolerates it. Two requirements:
   - our terms require uploaders to grant us a license to show their photos
   - we register a DMCA agent with the US Copyright Office (small fee) and take photos down promptly when asked; that protects us from liability for what users upload
4. **Use Wikimedia Commons photos of real-world statues** (Odaiba, Yokohama, Shanghai) under their Creative Commons licenses, e.g. [Category:Gundam Odaiba](https://commons.wikimedia.org/wiki/Category:Gundam_Odaiba). Check each file. The statues are copyrighted artworks, and Japan's rule allowing photos of public artworks ("freedom of panorama") is narrow, so some of these files may get deleted.
5. **Buy editorial stock photos** (e.g., [Getty Images](https://www.gettyimages.com/photos/gundam-statue-japan)) of statues and events. These cost money, and editorial licenses restrict how the photos can be used.
6. **Get an official license from Bandai Namco Filmworks.** This is the only clean route to official artwork, but there is no public licensing program. It would be a direct negotiation, realistically only worth it if the app goes commercial.

**There is no freely licensed source of official Gundam artwork.**

**Recommended long-term approach:** text-first suit pages, plus official embeds and links to official pages, plus user-uploaded kit photos handled through a DMCA process.

## Related

- [Trusted Gundam data sources](./trusted-gundam-data-sources.md): the licensing and attribution obligations for each data source
