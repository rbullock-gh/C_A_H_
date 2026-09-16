# Launch checklist

Work top to bottom. Items 1–3 are blockers: the site should not replace the current
one until they are done.

---

## 0. Verify the building photograph — BLOCKER

> **It is now in two places.** The same photograph fills `about-hospital` on the home page and the
> About page, and `contact-building` at the foot of the Contact page. The Contact slot is the one
> whose whole job is letting a first-time client recognise the building from the road, so if this
> is the wrong building it does not merely decorate badly — it sends people to the wrong place.

The exterior photograph on the home page and the About page was supplied by the client and
placed at their explicit direction. **It has not been verified as this practice.**

What the evidence says:

| | In the photograph | Columbia Animal Hospital, Columbia MS |
|---|---|---|
| Phone on the sign | **903-234-0869** | **601-736-3041** |
| Area code | 903 — East Texas | 601 — Mississippi |
| Logo on the sign | A single dog, white on green | A dog with a cat in negative space, white on black |

Both signs were read at high magnification. The practice's own sign is visible in the team
photograph and reads 601-736-3041, so the comparison is direct rather than inferred. There are
at least six unrelated practices called Columbia Animal Hospital, which is exactly how a mix-up
like this happens.

**Before launch, do one of two things:**

1. Confirm the photograph really is the Highway 98 East building — in which case delete this
   section and nothing else changes; or
2. Replace it. Drop a photograph of the real building into `incoming/about-hospital.jpg` and
   run `python3 tools/photos.py import`. A phone snapshot from the road on a bright day is
   entirely good enough.

Why it matters more than it looks: this is the image a first-time client matches against when
they are looking for the turning. If it shows the wrong building, they drive past.

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
  `src/pages/team.html`, add a card to the home page grid, and add a `Person`
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

## 3a. The proposal is ready to send

`docs/proposal/columbia-animal-hospital-proposal.html` is complete: **$3,500 once, and $75 a
month only if they want it looked after**, prepared by Ryan Bullock, (769) 313-6636,
ryanbullock09@gmail.com. Nothing is left blank and the draft notice is gone.

The price is one payment rather than a subscription because the research says their current site
almost certainly costs them nothing. It sits on `vetsourcecms.com`, and Vetsource takes its
revenue on pharmacy margin — no enrolment fee, no monthly service charge, no cancellation fee on
the core program, and a $499/month client app given away to the same customers. A monthly bill
would therefore be a **new** expense against a free incumbent, while a one-time purchase is a
single decision. The published vet-specific comparable is VIN's eVetSites at $109–$169 a month
with no setup fee, which also caps what any recurring charge can credibly be.
There are two documents, because they do different jobs:

| File | Pages | For |
|---|---|---|
| `Columbia-Animal-Hospital-One-Sheet.pdf` | 2 | What gets left on the desk. One sheet, printed both sides, about ninety seconds of reading. |
| `Columbia-Animal-Hospital-Website-Proposal.pdf` | 13 | The proof, for the reply that says "send me something". With a stranger its length is part of the argument. |
| `Visit-Brief.pdf` | 5 | **The sender's own brief — never goes to the practice.** The pitch, the facts, the price, how to answer "it's out of our budget", the questions to ask and the findings to keep in reserve. It says so across the top of page one, in case it ends up in the same stack as the others. |

Both are generated from the HTML beside them — edit that and run `node tools/proposal-pdf.mjs`,
so the two can never drift apart. Print the one-sheet **in colour**: the dark masthead and the
amber card carrying the recommended price both die in greyscale.

## 3b. Decide what "Request an Appointment" should do

The site now leads with a **Request an Appointment** call to action, in the header, the hero,
the footer, the mobile bar and every service page. Right now every one of them lands on
`request-appointment.html`, which explains how booking works and puts the phone number front
and centre.

**There is deliberately no form.** The practice publishes no booking system and no email
address, so a form would have nowhere to send — and a form that silently goes nowhere costs
you the appointment *and* the client's trust. If you want one:

1. Pick somewhere for it to go — a practice email address, or a form service that emails you.
2. Add the form to `src/pages/request-appointment.html` with a real `action`, and mark which
   fields are required.
3. Test it end to end, from a phone, before it goes live. Then keep the phone number where it
   is: most people will still call.

## 3c. Collect real testimonials

The reviews section on the home page carries the practice's own mission statement and a link
to the Facebook page where clients already leave reviews. **No testimonial on this site was
written by us**, and the Facebook rating is deliberately absent from the structured data —
that is a third party's rating, not first-party review markup, and publishing it as the latter
is a policy violation.

To add real ones: collect them first-party with the client's permission, then paste into the
reviews section using this shape, which is what the styles already expect:

```html
<blockquote>Their words, unedited.</blockquote>
<cite>First name, and their pet's name — Columbia, MS</cite>
```

Use real names with permission. An invented quote is the fastest way to lose a client's trust,
and people local enough to be reading this will notice a name that does not exist.

### Twelve real reviews are now on the home page — and three things came with them

The practice's Google listing carries **303 reviews**. Twelve are on the site, copied verbatim
from the public listing into `src/reviews.json`, named by first name and last initial. Anything
Google had truncated behind a "More" link was left out rather than trimmed, because a shortened
quote stops being the reviewer's sentence. **Still outstanding: the star rating and the listing
URL**, so the page can say "4.x from 303" and link out. Ask the practice, or read it off Google
Maps in thirty seconds.

**Three things the reviews revealed that matter more than the quotes:**

1. **A client disputes the after-hours claim.** One reviewer writes that the practice "no longer
   help[s] with after hours emergency visits" and describes driving at 3am with a dog having a
   seizure. The review is old — edited about ten years ago — and the practice's own site still
   advertises an on-call veterinarian. **This site publishes that claim.** It is now blocker 2 and
   it is not merely "how do clients reach the on-call vet" any more; it is "is this still true."
2. **They take walk-ins, and the site never says so.** Four separate reviews mention it, two of
   them within the last eight months: "I can just walk in as needed", "saw us quickly even as a
   walk-in", "You don't need an appointment for basic stuff". For a practice whose nearest
   alternative is 22 miles away this is a real selling point, and it is nowhere on either site.
   Confirm it and it belongs on the home page.
3. **The front desk is the recurring criticism.** Several reviewers praise the doctors and
   complain about reception in the same breath. Nothing goes on the website about it, and it is
   not a thing to raise with whoever is at that desk — but the practice may not know, and it is
   worth an owner hearing once.

### What a search for existing reviews turned up

Every review host is blocked from this environment, so this is what search results carried,
not what the pages say. **Nothing found here is publishable.**

- **No Google rating or review count could be verified at all.** Two scraper sites gave
  contradictory figures — 4.7 and 5.0 — and the one with the higher figure never showed the
  address or phone, so it may not even be this practice.
- **Not one review anywhere carried both a reviewer's name and a date.** Several fragments
  surfaced, one of them naming Dr. Sanford and Dr. Loper and so almost certainly genuine, but
  anonymous, undated and second-hand is not a testimonial.
- The Facebook figure this project recorded earlier — **94% recommend across 37 reviews** —
  came back identically across several differently-worded searches, each time attached to the
  right address and phone. It is still unconfirmed by us, and Facebook Recommendations is
  yes/no, so there is no star rating to show.
- The name collision is vicious here. The first search of the session returned praise for a
  "Dr. Bartlett", who belongs to Columbia Animal Hospital in **Pennsylvania**. That practice
  also owns the generic `demandforce.com/b/columbiaanimalhospital` slug. **Check the phone
  number on anything before believing it.**

**Two questions to the client settle this in a minute**, and either answer beats any amount of
searching: *do you manage a Google Business Profile, and what does it say today?* and *what
does Facebook show for recommendations?*

### If the client wants Google reviews on the page

The only legitimate route is the Google Places API, and its constraints shape the design:

- **Five reviews, maximum**, and Google picks which five. More needs the Business Profile
  APIs, which only the profile's owner can authorize.
- **The review text may not be stored.** Google's Maps Platform terms permit caching the Place
  ID indefinitely and coordinates for 30 days, and nothing else — so review text and author
  names cannot go into a JSON file, a CMS, or the page's structured data. They have to be
  fetched live on each view.
- **Attribution is mandatory**: author name, avatar, and a link to their Google Maps profile,
  plus the "Powered by Google" mark on any page showing Places data without a map.
- **It will not put stars in search results.** Google treats a business's own reviews of
  itself as self-serving and does not show review rich results for them. That is the same
  reason there is no `aggregateRating` in this site's structured data, and
  `tools/check.py` fails the build if one appears.
- It needs a Google Cloud project with billing enabled. One clinic's traffic sits inside the
  free monthly allowance, but the key cannot be issued without a card on file.

Given all of that, **first-party collection is the better trade**: real names, real dates, no
terms exposure, no bill, and the practice owns the words.

## 4. Point the site at its domain

Everything absolute — canonical tags, Open Graph, Twitter cards, JSON-LD, sitemap, robots —
comes from one value:

```bash
./tools/set-domain.sh https://www.columbiaanimalhospital.net
```

Then re-scrape the link preview at <https://developers.facebook.com/tools/debug/>; previews
cache hard.

## 5. Replace the placeholder photography

Twenty-four slots hold real photographs now — all nine service pages, the three doctors at work,
the animals on the service cards, the exam-room shot and the team at the sign. Eight are still
labelled placeholders, and `python3 tools/photos.py list` prints which is which at any moment.

**Of the eight, five belong to the interior gallery that is currently off the home page**, so the
ones that actually matter are `contact-building`, `closer-community` and `about-history` — and all
three are photographs of this practice's own building and people, which is exactly why nobody else
can supply them. See
[`PHOTO-CHECKLIST.md`](PHOTO-CHECKLIST.md) for the shot list, then drop files into
`incoming/` named after their slot and run:

```bash
python3 tools/photos.py list      # what each slot needs
python3 tools/photos.py import    # crop, resize, encode, rewrite references
```

Licensed stock is approved for the general care and service slots. It is **not** appropriate
for `about-hospital` or `contact-building` — those show this practice's own building, and a
stock photograph of another clinic presented as theirs misrepresents the business. Leave
those two on placeholders until someone photographs the building; a phone will do.

Record where every stock image came from and under what licence. `tools/photos.py` carries a
`.txt` sidecar into [`PHOTO-CREDITS.md`](PHOTO-CREDITS.md) for you. Unsplash, Pexels and
Pixabay all permit commercial use without attribution — keep the record regardless, because a
licence you cannot evidence is a licence you do not have.

## 5b. Get consent for the staff photographs, and a photograph of the building

The team photograph on the home page and the Our Team page shows around a dozen identifiable
people, and each doctor now appears in a working photograph of their own — Dr. Sanford with a
puppy, Dr. Loper with a corgi, Dr. Williams with a kitten. **Confirm every one of them is
happy to appear on the website** before it goes live. People leave jobs, and a website is more
public than a noticeboard.

The client photographs also carry pets that belong to somebody. Where an animal is
recognisable to its owner — the corgi and the puppy on the exam tables, rather than the studio
portraits on the service cards — confirm the owner is happy too.

There is still **no photograph of the building**. The exterior shot supplied during the build
was a different Columbia Animal Hospital — its sign reads 903-234-0869, an East Texas number,
with a different logo. It is not on the site. A phone snapshot of the real building on
Highway 98 East, taken from the road on a bright day, is all that is needed, and it matters:
it is what a first-time client matches against when they are looking for the turning.

## 6. Supply the original logo artwork, if it exists

The mark on the site is **the practice's own dog-and-cat silhouette**, traced from the sign in
the team photograph. It is unmistakably their logo and it renders cleanly from 32px up.

But it is traced from a photograph of a sign, not from original artwork. **If the practice has
the original file** — whoever made the sign will have one, in some vector format — use that
instead: put it in place of `assets/img/logo-mark.svg`, update `LOGO_PATH` in
`tools/make-brand.py`, and re-run it to regenerate the favicons, touch icon and share card.
See [`BRAND-AND-ASSETS.md`](BRAND-AND-ASSETS.md).

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
| Searches surface the **Pennsylvania** practice's review pages | Demandforce, GeniusVets | Nothing to fix directly — one more reason to build up the Google profile, which does carry the right address |
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
| `/AboutUs/DrPatSanford.aspx` | `/team.html#dr-pat-sanford` |
| `/AboutUs/DrJanelleLoper.aspx` | `/team.html#dr-janelle-loper` |
| `/AboutUs/DrBridgettWilliams.aspx` | `/team.html#dr-bridgett-williams` |
| `/AboutUs/DrWallaceCarson.aspx` | `/team.html` (or his own block, after item 1) |
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
