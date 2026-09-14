# Launch checklist

Work top to bottom. Items 1–3 are blockers: the site should not replace the current
one until they are done.

---

## 1. Confirm Dr. Wallace Carson's status — BLOCKER

The existing site has a live, indexed bio page for **Dr. Wallace Carson**
(`/AboutUs/DrWallaceCarson.aspx`): Mississippi State undergraduate, DVM from Auburn
University College of Veterinary Medicine in 1974, with the practice since 1975. The brief
that commissioned this site lists only Loper, Sanford and Williams.

No obituary and no retirement announcement could be found, and no evidence that he is
currently practicing beyond that page and some stale directory entries. **He is not
published on this site**, because publishing a veterinarian who has retired — or worse — is
a far more damaging error than a page with three doctors instead of four.

**Ask the practice.** Then either:

- *Still practicing* → add him. Copy the pattern of any existing doctor block in
  `src/pages/veterinarians.html`, add a card to the home page grid, and add a `Person`
  entry to the `employee` array in the home page JSON-LD and to `mainEntity` on the
  veterinarians page.
- *Retired* → consider a line in the About page history. Fifty years is worth saying.
- *Neither* → leave as is, and take the old bio page down when the site is replaced.

## 2. Say how to reach the on-call vet — BLOCKER

The practice publishes *that* an on-call veterinarian is available after hours, but
**nowhere does it say how to reach one**. No second number, no answering service, no
instruction. This site tells people to call (601) 736-3041, the only published number, and
warns them not to drive over assuming someone is there.

Find out what actually happens when that number rings at 9pm on a Sunday, then make the
after-hours copy say exactly that. It is on the home page (`#emergency`), the contact page,
the FAQ and the footer — all four are in `src/`. This is the single most useful improvement
available to this website.

## 3. Confirm the Saturday opening time — BLOCKER

The official site, the Facebook page and three directories say **8:00 AM**. Pawlicy and
GeniusVets say 7:30 AM. This site uses **8:00 AM**, in `src/data.json` under `hours` and in
the `openingHoursSpecification` the build generates from it.

Confirm it, then correct whichever listings are wrong. A visitor who arrives at 7:30 to a
locked door does not come back.

---

## 4. Point the site at its domain

Everything absolute — canonical tags, Open Graph, Twitter cards, JSON-LD, sitemap, robots —
comes from one value:

```bash
./tools/set-domain.sh https://www.columbiaanimalhospital.net
```

Then re-scrape the link preview at <https://developers.facebook.com/tools/debug/>; previews
cache hard.

## 5. Replace the placeholder photography

Every image is a labelled placeholder. Real photographs are the largest single upgrade left
in this project — see [`PHOTO-CHECKLIST.md`](PHOTO-CHECKLIST.md) for the shot list, then:

```bash
./tools/apply-photos.sh
```

## 6. Supply a real logo, if one exists

No logo file could be obtained, so `tools/make-brand.py` draws a paw mark in the brand green
and generates the favicons and share card from it. If the practice has real artwork, replace
the outputs and delete that script rather than trying to match it. See
[`BRAND-AND-ASSETS.md`](BRAND-AND-ASSETS.md).

## 7. Clean up the listings

These directly affect map rankings and are quick wins:

| Problem | Where | Fix |
|---|---|---|
| Wrong street number **1498** | Marion County Development Partnership | Claim the listing, correct to 1409 |
| Street written as **Old Hwy 98 E** | US Companies | Correct or request removal |
| Saturday shown as **7:30 AM** | Pawlicy, GeniusVets | Correct to 8:00 AM once confirmed |
| Two Yelp pages for one business | Yelp | Merge |
| A Yelp listing under **CARSON WALLACE DR** at the same address | Yelp | Merge or remove |
| An unclaimed Facebook place page | Facebook | Merge into the real page |
| Site indexed at both `columbiaanimalhospital.net` and `columbiaanimalhospital.vetsourcecms.com` | Old host | Redirect the CMS subdomain, or have it de-indexed |
| `Boarding.aspx` and `DrBridgettWilliams.aspx` indexed over **http** | Old host | Force HTTPS sitewide |

Pick one way of writing the address and use it **character for character** everywhere — the
site, the Google Business Profile, and every directory. This site uses `1409 Hwy 98E`, the
current site's own form. `tools/check.py` fails the build if any page deviates.

> The Google Business Profile matters more than the website for showing up in the map pack.
> Claim it, match the address exactly, set the hours, and add photos.

## 8. Redirect the old URLs

The old site's pages are indexed. When it is replaced, 301 each one so the ranking carries
over:

| Old | New |
|---|---|
| `/` and `/Home.aspx` | `/` |
| `/ContactUs.aspx` | `/contact.html` |
| `/FAQs.aspx` | `/faq.html` |
| `/AboutUs/DrPatSanford.aspx` | `/veterinarians.html#dr-pat-sanford` |
| `/AboutUs/DrJanelleLoper.aspx` | `/veterinarians.html#dr-janelle-loper` |
| `/AboutUs/DrBridgettWilliams.aspx` | `/veterinarians.html#dr-bridgett-williams` |
| `/AboutUs/DrWallaceCarson.aspx` | `/veterinarians.html` (or his own block, after item 1) |
| `/OurServices/Surgery.aspx` | `/services/surgery.html` |
| `/OurServices/DentalCare.aspx` | `/services/dental-care.html` |
| `/OurServices/Dermatology.aspx` | `/services/dermatology.html` |
| `/OurServices/DigitalRadiography.aspx` | `/services/digital-radiography.html` |
| `/OurServices/Grooming.aspx` | `/services/grooming.html` |
| `/OurServices/HeartwormTesting.aspx` | `/services/heartworm-testing.html` |
| `/OurServices/Microchipping.aspx` | `/services/microchipping.html` |
| `/OurServices/ReproductiveServices.aspx` | `/services/reproductive-services.html` |
| `/OurServices/Boarding.aspx` | `/services/boarding.html` |

## 9. Optional, once confirmed

- **Online pharmacy.** A store may exist at `columbiaanimalhospital.myvetstoreonline.pharmacy`,
  but a second source found no pharmacy link for this practice and flagged a similar URL
  belonging to a *different* business. Confirm the correct address before linking it.
- **Microchip brand.** One source says Avid. Confirm before naming it.
- **Payment methods and CareCredit.** Only evidenced on third-party listings, never on the
  practice's own site.
- **Reviews.** The Facebook page shows a 94% recommendation rate across 37 reviews. That is
  a third party's rating and is deliberately absent from this site's structured data. If the
  practice wants testimonials, collect them first-party, with permission, and add them with
  real names.

## 10. Before you publish

```bash
python3 tools/build.py            # regenerate every page from src/
python3 tools/check.py --browser  # must exit 0
python3 tools/build-demo.py       # refresh the shareable preview
```

`check.py` verifies structured data, FAQ schema/page parity, missing files, SVG
well-formedness, tag balance, alt text, heading order, broken anchors, title and description
lengths, address and phone consistency across all sixteen pages, and — with `--browser` —
horizontal overflow at 390/820/1440px, image decoding, WCAG tap-target sizes, and that
nothing stays invisible when JavaScript is off.
