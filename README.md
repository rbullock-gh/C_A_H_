# Columbia Animal Hospital — website

A modern, mobile-first site for **Columbia Animal Hospital**, the companion animal practice
at 1409 Hwy 98E in Columbia, Mississippi, caring for the dogs and cats of Columbia and
Foxworth since 1975.

Sixteen pages of static HTML, one stylesheet, one small script. No framework, no npm, no
runtime dependencies. Python is used at build time only, from the standard library.

## See it now

`demo/columbia-animal-hospital-preview.html` is a **single self-contained file** — the
stylesheet, the script, both fonts and every image inlined. Double-click it and the whole
site opens, all sixteen pages, with working navigation. No server, no assets folder, nothing
to install. Email it, drop it in a shared folder, or open it on a phone.

It is labelled as a preview so a forwarded copy is never mistaken for the live site, and the
map is a static panel — a live map needs a real page.

```bash
python3 tools/build-demo.py     # rebuild it after any change
```

## Run it locally

```bash
python3 -m http.server 8000     # then open http://localhost:8000
```

## Validate before you ship

```bash
python3 tools/check.py --browser
```

Structured data, FAQ schema/page parity, missing files, SVG well-formedness, tag balance,
alt text, heading order, broken anchors, title and description lengths, and address and
phone consistency across every page. With `--browser` it also renders each page in Chromium
and checks horizontal overflow at 390/820/1440px, that every image actually decodes, WCAG
2.5.8 tap-target sizes at 390px, and that nothing stays invisible with JavaScript off.

Exits non-zero on failure, so it drops straight into CI or a pre-commit hook.

## Before you deploy

**Start with [`docs/LAUNCH-CHECKLIST.md`](docs/LAUNCH-CHECKLIST.md).** Three items there are
blockers:

| Blocker | Why |
|---|---|
| **Dr. Wallace Carson's status** | The old site has a live bio page for a fourth veterinarian the brief does not list. He is not published here until someone confirms whether he still practises. |
| **How to reach the on-call vet** | The practice says an on-call veterinarian is available after hours but never says how to reach one. Closing that gap is the most useful content change available. |
| **Saturday's opening time** | The official site says 8:00 AM; two aggregators say 7:30 AM. Confirm, then correct the listings. |

Two things also ship as placeholders:

| What | Why | Where |
|---|---|---|
| **Photography** | Every image host was blocked by the build environment's network policy, so no real photograph could be obtained. Rather than substitute stock, every slot is a labelled placeholder at the real dimensions. | [`docs/PHOTO-CHECKLIST.md`](docs/PHOTO-CHECKLIST.md) |
| **The logo** | No logo file could be obtained either. `tools/make-brand.py` draws a paw mark in the brand green and generates the favicons and share card from it. | [`docs/BRAND-AND-ASSETS.md`](docs/BRAND-AND-ASSETS.md) |

Everything factual on the site is sourced and recorded in
[`docs/CONTENT-SOURCES.md`](docs/CONTENT-SOURCES.md) — with its source, a confidence level,
the items that still need confirming, and the claims deliberately left off. **Nothing was
invented.**

## How it is built

Pages are composed from `src/` by `tools/build.py` and written as plain HTML at the repo
root. The output is ordinary static files that any host will serve.

There is a build step for one reason: **the address, the phone number and the hours appear
on all sixteen pages, and local search ranking depends on them matching character for
character.** Hand-maintaining them is how they drift. `src/data.json` is the single source of
truth, and `check.py` fails the build if any page deviates.

```
src/
  data.json             Every business fact — address, phone, hours, service area
  layout.html           The page shell: head, metadata, header/footer slots
  partials/             header, footer, icon sprite, call bar, service sidebar
  pages/                One file per page; JSON front matter sets title and meta
    services/           The nine service pages
tools/
  build.py              Composes src/ into the pages below. No dependencies
  check.py              Validates everything; --browser adds a render pass
  build-demo.py         Bundles the whole site into one shareable file
  make-brand.py         Mark, favicons, touch icon, share card
  make-placeholders.py  Photo placeholders at the real dimensions
  apply-photos.sh       Swaps placeholders for real photos in one command
  set-domain.sh         Points every absolute URL at the live domain
assets/
  css/styles.css        Design system — brand tokens at the top
  js/main.js            Nav, scroll reveal, open/closed indicator, deferred map
  fonts/                Fraunces and Inter, latin subset, self-hosted
  img/                  Placeholders, mark, share card
docs/                   Launch checklist, photo checklist, brand notes, sources
index.html … services/  The built site. Generated — edit src/, not these
```

```bash
python3 tools/build.py          # rebuild every page
```

## Pages

Home · About · Our Veterinarians · Services · FAQ · Contact & Directions, plus a page for
each of the nine services: Surgery, Dental Care, Digital Radiography, Heartworm Testing,
Dermatology, Reproductive Services, Grooming, Boarding and Microchipping. And a 404.

The home page runs land → understand the practice → see the services → see why → meet the
doctors → know what happens in an emergency → find us → call. Calling is reachable from the
sticky header on desktop, a fixed bar on mobile, and every major section.

## Notes on the implementation

- **No framework.** One stylesheet, one script of about 170 lines. Fast by default, and any
  web developer can maintain it.
- **Progressive enhancement.** Every page works with JavaScript disabled — the FAQ uses
  native `<details>`, the navigation degrades to plain links, and the scroll-reveal blocks
  have a no-JS rule so the page never renders blank. `check.py` enforces that last one.
- **Accessible.** Skip link, landmarks, one `h1` per page with a clean heading order,
  visible focus rings, `aria` on the nav toggle and current-page links, alt text on every
  image, tap targets that clear WCAG 2.5.8, full `prefers-reduced-motion` support, and every
  color pair measured for contrast.
- **Self-hosted fonts.** 115 kB for both variable faces, latin subset, preloaded. No
  third-party connection on the critical path.
- **Local SEO.** `VeterinaryCare`/`LocalBusiness` with opening hours and area served,
  `Service` on each service page, `FAQPage`, and `BreadcrumbList` — plus town names worked
  into headings and alt text rather than stuffed. No `aggregateRating`: the practice's
  Facebook rating belongs to a third party and is not first-party review markup.
- **Honest about emergencies.** The site says an on-call veterinarian is available after
  hours, and says plainly that this is not a 24-hour emergency hospital.
- **Responsive.** No horizontal overflow at 320, 390, 820 or 1440px.
