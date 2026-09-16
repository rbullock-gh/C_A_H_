# Photo checklist

No photograph of Columbia Animal Hospital could be obtained during the build. Every image
host — the practice's own site, its Facebook page, Yelp, and every directory carrying photos —
is blocked by this environment's network policy.

Rather than substitute stock photography, which is exactly what visitors scroll past and which
the brief rules out, every slot began as a labelled placeholder at the real dimensions. The
client has since supplied the three doctors at work, the team at the sign, and the animals on
the service cards. The rooms, the building and the everyday-care shots are still placeholders,
and **they are the largest single upgrade left in this project.**

`python3 tools/photos.py list` prints what is filled and what is not. That command is the
live answer; the shot list below is the brief for taking the photographs.

**The five `gallery-*` slots have no section on the site at the moment.** The interior gallery
on the home page was five labelled placeholders in a row, which said nothing about this
practice, so it has been taken out. The slots and their placeholders are kept: photograph the
reception, an exam room, the treatment area and a boarding run, and the section goes back in
with something worth showing.

## How to swap them in

Save each photo into `incoming/` using the slot's name and your own extension —
`hero-care.jpg`, `svc-surgery.png`, `why-exam.webp` — then:

```bash
python3 tools/photos.py list      # what each slot needs, and what is still missing
python3 tools/photos.py import    # process everything in incoming/
```

Each photo is rotated per its EXIF orientation, cropped from the centre to the slot's exact
aspect ratio, resized to the slot's dimensions, encoded as WebP, and every reference in
`src/` is rewritten. A 4000×3000 phone photo becomes a correctly-sized 17 kB image rather
than a six-megabyte one that also shifts the layout, because the markup declares the
placeholder's width and height and cropping keeps those honest.

To record a credit, put a `.txt` file of the same name beside the photo — `hero-care.txt` —
containing the photographer, source and licence. It is carried into
[`PHOTO-CREDITS.md`](PHOTO-CREDITS.md).

## Studio photographs on a white background

A photograph shot on a white sweep looks like a box pasted onto the page when it sits
against a coloured ground. Cut the background away instead, so the subject stands on the
design's own colour:

```bash
pip install "rembg[cpu]"
python3 tools/cutout.py incoming/hero-care.png
python3 tools/photos.py import
```

`cutout.py` uses the isnet-general-use model with alpha matting — settings that held up on
the three-dog hero, where a plain threshold key leaves a white fringe on the black dog's
ear. It trims to the subject's bounding box so no empty margin is carried around.

**Always check a cut-out against a dark ground before trusting it.** A white fringe is
invisible on white and obvious on forest green.

Two things to expect. A subject cropped by the original frame — the hero dogs are cut at
chest level — keeps that flat edge, so anchor it to the bottom of a section where the edge
reads as a baseline rather than a crop, or dissolve the last few percent into the ground
behind. And transparency costs bytes: the hero is 208 kB with alpha against 161 kB flattened.

## Stock photography

Licensed stock is approved for the general care and service slots. **Unsplash**, **Pexels**
and **Pixabay** all license for commercial use without requiring attribution.

Two rules:

1. **Never use stock for `about-hospital` or `contact-building`.** Those slots show this
   practice's own building on Highway 98 East. A photograph of a different clinic presented
   as theirs misrepresents the business, and a first-time client who cannot recognise the
   building from the road is worse off than one who saw no photograph at all. A phone
   snapshot of the real building beats the best stock image in existence here.
2. **Keep it consistent.** Stock pulled from several photographers at several exposures
   looks exactly like what it is. Pick images that share a light quality and a colour cast,
   and prefer warm, unstaged, domestic-feeling frames over glossy studio work — the whole
   positioning of this practice is *hometown*, not corporate.

Avoid: pets in party hats, veterinarians with folded arms and perfect teeth, aggressively
blue-filtered clinical interiors, and anything with visible non-US signage or branding.

## Shooting notes

- **Real light, real rooms.** A phone photograph of the actual building beats a polished
  stock image of somewhere else, every time. Local is the whole point.
- **Get consent.** Ask owners before photographing their pets, and staff before
  photographing them.
- **Shoot wider than you need.** These slots crop to fixed ratios; leave room around the
  subject.
- **Keep it consistent.** One camera, similar light, similar treatment, so the site does
  not look assembled from several sources.
- **Two slots have no label on purpose** — they sit behind headline copy, where a label
  would ghost through the text and read as a bug. They still need real photographs.

## The shot list

| Slot | Size | Type | The shot | Used on |
|---|---|---|---|---|
| ~~`hero-care`~~ | 1536×1024 | **filled** | Three dogs on a white studio background — supplied by the client, in place as `hero-care.webp` | `index.html` |
| `closer-community.svg` | 1800×900 | plain | Owner with their dog outside the hospital | `about.html`, `index.html` |
| `why-exam.svg` | 1200×900 | labelled | Technician holding a cat during an exam | `index.html`, `services.html` |
| `about-hospital.svg` | 1200×900 | labelled | Exterior of the hospital on Hwy 98E, signage visible | `about.html` |
| `about-history.svg` | 1000×1200 | labelled | Older photograph of the practice, or the building today | `about.html` |
| ~~`vet-loper`~~ | 560×700 | **filled** | Dr. Janelle Loper listening to a corgi — supplied by the client | `index.html`, `team.html` |
| ~~`vet-sanford`~~ | 560×700 | **filled** | Dr. Pat Sanford listening to a puppy — supplied by the client | `index.html`, `team.html` |
| ~~`vet-williams`~~ | 560×700 | **filled** | Dr. Bridgett Williams holding a kitten — supplied by the client | `index.html`, `team.html` |
| ~~`svc-surgery`~~ | 1200×800 | **filled** | Surgical suite, prepped and clean — supplied by the client | `services/surgery.html` |
| ~~`svc-dental-care`~~ | 1200×800 | **filled** | Dental cleaning in progress, or a dog's teeth — supplied by the client | `services/dental-care.html` |
| ~~`svc-digital-radiography`~~ | 1200×800 | **filled** | Digital x-ray image on a monitor — supplied by the client | `services/digital-radiography.html` |
| ~~`svc-heartworm-testing`~~ | 1200×800 | **filled** | Blood draw or in-house test being run — supplied by the client | `services/heartworm-testing.html` |
| ~~`svc-dermatology`~~ | 1200×800 | **filled** | Skin or ear examination close up — supplied by the client | `services/dermatology.html` |
| ~~`svc-grooming`~~ | 1200×800 | **filled** | Groomer working with a dog on the table — supplied by the client | `services/grooming.html` |
| ~~`svc-boarding`~~ | 1200×800 | **filled** | Clean boarding run, or a dog on its daily walk — supplied by the client | `services/boarding.html` |
| ~~`svc-microchipping`~~ | 1200×800 | **filled** | Scanner being passed over a pet's shoulders — supplied by the client | `services/microchipping.html` |
| ~~`svc-reproductive-services`~~ | 1200×800 | **filled** | Puppies or a nursing mother, calm setting — supplied by the client | `services/reproductive-services.html` |
| `contact-building.svg` | 1400×900 | labelled | The building and car park from the road | `contact.html` |

## Priority

If only a few photographs can be taken, take these five:

1. ~~**`hero-care`**~~ — done. The client supplied the three-dog studio photograph.
2. ~~**`vet-loper`, `vet-sanford`, `vet-williams`**~~ — done. Each doctor at work, with a
   patient, which is better than the head-and-shoulders portrait originally asked for.
3. ~~**The nine service pages**~~ — done. The client supplied all nine.
4. **`contact-building`** — so a first-time client recognizes the building from the road. With the
   service pages filled, this is now the most valuable photograph left in the project, and the
   only one nobody but the practice can take.
