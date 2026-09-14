# Brand and assets

## Colour

Every color on this site was measured before it was used. The ratios below are against
`--cream` (`#FAF7F1`), the page ground, unless stated otherwise.

| Token | Value | On cream | Use |
|---|---|---|---|
| `--ink` | `#18261F` | 14.7:1 | Headings |
| `--body` | `#3D4A43` | 8.7:1 | Body copy |
| `--muted` | `#5E6E65` | 5.0:1 | Captions, meta |
| `--forest` | `#1E4034` | 10.7:1 | Primary brand; white on it is 11.4:1 |
| `--forest-deep` | `#143026` | 13.3:1 | Darkest surface; white on it is 14.2:1 |
| `--forest-soft` | `#2C5344` | — | Raised surface on dark grounds |
| `--clay` | `#A8512E` | 5.1:1 | Call-to-action fill; white on it is 5.4:1 |
| `--clay-deep` | `#8E4527` | 6.5:1 | CTA hover, small link text |
| `--cream-deep` | `#F0E9DC` | — | Alternating section band |
| `--sage-pale` | `#DCE6DC` | — | Tint surface. **Never a text color** |
| `--tan-pale` | `#EFE4D3` | — | Mat behind framed photographs |

### The two mid-tones need three tokens each

Sage and tan are mid-tones. A single value cannot serve as a fill, as large text on a light
ground, and as small text on a light ground — the numbers simply do not allow it:

| Colour | Value | On cream | Verdict |
|---|---|---|---|
| `--sage` | `#7E9C88` | **2.8:1** | **Fill only.** Never text on light. 4.7:1 on `--forest-deep`, so it is fine as text on dark |
| `--sage-deep` | `#557463` | 4.8:1 | Large text and icons on light |
| `--sage-text` | `#456052` | 6.4:1 | Small text on light |
| `--tan` | `#C7A57E` | **2.2:1** | **Fill only.** 6.2:1 on `--forest-deep` — this is why the tan accents live on the dark bands |
| `--tan-deep` | `#96714A` | 4.1:1 | **Large text and icons only** |

This is the trap worth remembering: a dark or saturated brand color usually works as one
token; a mid-tone will not, and finding that out after the build means touching every
component. Run the numbers first.

Re-check any new color before using it:

```python
def lum(h):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
```

AA needs 4.5:1 for body text, 3:1 for large text (18.66px bold or 24px) and for UI
boundaries.

## Type

| Role | Face | Why |
|---|---|---|
| Display | **Fraunces** | A variable serif with warmth and a little character. It reads as a practice with a history rather than a chain, which is the whole positioning. Set with `SOFT 20` and `WONK 0` — the expressive end of its axes is a step too far for a medical business |
| Body and UI | **Inter** | Neutral, legible at small sizes, and it does not compete with the headings |

Both are **self-hosted** in `assets/fonts/`, latin subset only, as variable WOFF2 — 115 kB
for the pair. That removes a third-party connection from the critical path and means the
site keeps working if Google Fonts is blocked or slow. They are preloaded in the `<head>`.

Sizes come from a fluid scale (`--step--1` to `--step-7`) that interpolates between 390px
and 1440px, so there are no font-size breakpoints to maintain.

## The mark

**No logo file for the practice could be obtained** — every image host was blocked. So
`tools/make-brand.py` draws a paw mark in the brand green and generates everything from it:

```bash
python3 tools/make-brand.py
```

| Output | Size | Used for |
|---|---|---|
| `assets/img/logo-mark.svg` | 96×96 | Header and footer |
| `assets/favicon/favicon.svg` | 96×96 | Modern browsers |
| `assets/favicon/favicon-32.png` | 32×32 | Fallback |
| `assets/favicon/apple-touch-icon.png` | 180×180 | iOS home screen |
| `assets/favicon/icon-192.png`, `icon-512.png` | — | Web manifest |
| `assets/img/og-image.png` | 1200×630 | Link previews |
| `assets/img/logo-mark.png` | 256×256 | Schema `logo` |

**If the practice has real artwork, use it.** Replace these outputs and delete the script
rather than trying to match it — and note that the artwork should drive the surface colors,
not the other way round. The header here is light because the clinic name is set in dark
forest type; a reversed logo would allow a dark header instead. On a dark ground, put real
artwork on a light plate rather than recolouring it. Recolouring is altering someone's brand.

## Editing the common things

| Change | Where |
|---|---|
| Phone number | `contact.phoneDisplay`, `phoneLink` and `phoneRaw` in `src/data.json` |
| Address | `contact.*` in `src/data.json`, plus the literal `1409 Hwy 98E` in the footer partial and the JSON-LD blocks |
| Hours | `hours` in `src/data.json`, the `openingHoursSpecification` in the home page JSON-LD, and `SCHEDULE` in `assets/js/main.js` (the open/closed indicator) |
| Brand colors | The token block at the top of `assets/css/styles.css` — read the mid-tone note above first |
| Navigation | `src/partials/header.html` and `src/partials/footer.html` |
| A service's copy | `src/pages/services/<slug>.html` |
| An FAQ answer | `src/pages/faq.html` — keep the visible `<summary>` and the JSON-LD `name` **identical**; `check.py` fails the build otherwise, because Google requires the answer to be visible on the page |

Run `python3 tools/build.py` after any change, then `python3 tools/check.py --browser`.
