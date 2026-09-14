# Photo checklist

No photograph of Columbia Animal Hospital could be obtained. Every image host — the
practice's own site, its Facebook page, Yelp, and every directory carrying photos — is
blocked by this environment's network policy.

Rather than substitute stock photography, which is exactly what visitors scroll past and
which the brief rules out, every slot is a labelled placeholder at the real dimensions.
**Real photographs are the largest single upgrade left in this project.**

## How to swap them in

Save each photo into `assets/img/` using the placeholder's basename and your own
extension — `vet-loper.jpg`, `svc-surgery.webp` — then run:

```bash
./tools/apply-photos.sh
```

Every reference is rewritten, the placeholder is deleted and the site rebuilds. Run it as
often as photos arrive; it only touches slots that now have a real file.

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
| `hero-care.svg` | 1800×1100 | plain | Veterinarian examining a dog, warm natural light | `index.html` |
| `closer-community.svg` | 1800×900 | plain | Owner with their dog outside the hospital | `about.html`, `index.html` |
| `why-exam.svg` | 1200×900 | labelled | Technician holding a cat during an exam | `index.html`, `services.html` |
| `about-hospital.svg` | 1200×900 | labelled | Exterior of the hospital on Hwy 98E, signage visible | `about.html` |
| `about-history.svg` | 1000×1200 | labelled | Older photograph of the practice, or the building today | `about.html` |
| `vet-loper.svg` | 800×1000 | labelled | Dr. Janelle Loper — portrait, chest up | `index.html`, `veterinarians.html` |
| `vet-sanford.svg` | 800×1000 | labelled | Dr. Pat Sanford — portrait, chest up | `index.html`, `veterinarians.html` |
| `vet-williams.svg` | 800×1000 | labelled | Dr. Bridgett Williams — portrait, chest up | `index.html`, `veterinarians.html` |
| `svc-surgery.svg` | 1200×800 | labelled | Surgical suite, prepped and clean | `services/surgery.html` |
| `svc-dental-care.svg` | 1200×800 | labelled | Dental cleaning in progress, or a dog's teeth | `services/dental-care.html` |
| `svc-digital-radiography.svg` | 1200×800 | labelled | Digital x-ray image on a monitor | `services/digital-radiography.html` |
| `svc-heartworm-testing.svg` | 1200×800 | labelled | Blood draw or in-house test being run | `services/heartworm-testing.html` |
| `svc-dermatology.svg` | 1200×800 | labelled | Skin or ear examination close up | `services/dermatology.html` |
| `svc-grooming.svg` | 1200×800 | labelled | Groomer working with a dog on the table | `services/grooming.html` |
| `svc-boarding.svg` | 1200×800 | labelled | Clean boarding run, or a dog on its daily walk | `services/boarding.html` |
| `svc-microchipping.svg` | 1200×800 | labelled | Scanner being passed over a pet's shoulders | `services/microchipping.html` |
| `svc-reproductive-services.svg` | 1200×800 | labelled | Puppies or a nursing mother, calm setting | `services/reproductive-services.html` |
| `contact-building.svg` | 1400×900 | labelled | The building and car park from the road | `contact.html` |

## Priority

If only a few photographs can be taken, take these five:

1. **`hero-care`** — the first thing every visitor sees.
2. **`vet-loper`, `vet-sanford`, `vet-williams`** — faces build more trust than any
   amount of copy, and they are the reason someone chooses one practice over another.
3. **`contact-building`** — so a first-time client recognizes the building from the road.
