# Brand and assets

## Colour

White-led and editorial, with near-black sections for drama and two warm accents so it never
reads cold or clinical. Ratios are against `--warm-white` (`#FCFBF9`) unless stated.

| Token | Value | On white | Use |
|---|---|---|---|
| `--ink` | `#15151A` | 18.2:1 | Headings, primary buttons |
| `--body` | `#3D3D45` | 10.8:1 | Body copy |
| `--muted` | `#6B6B74` | 5.3:1 | Captions and meta |
| `--charcoal` | `#1E1E23` | — | Dark section ground; white on it is 16.6:1 |
| `--charcoal-soft` | `#2B2B32` | — | Raised surface on dark |
| `--on-dark` | `#EDEAE5` | 13.8:1 on charcoal | Body copy on dark |
| `--on-dark-muted` | `#A8A8B0` | 7.0:1 on charcoal | Meta on dark |
| `--gray-50` | `#F6F4F1` | — | Alternating band |
| `--line` | `#E6E2DC` | — | Hairlines and card borders |
| `--line-strong` | `#8E8A83` | 3.0:1 | Form borders and real UI boundaries |

### Both accents are mid-tones, so both need several tokens

| Token | Value | On white | Verdict |
|---|---|---|---|
| `--amber` | `#C77B2B` | 3.3:1 | **Fill only.** White on it is also 3.3:1 and **fails** — amber buttons take *dark* text, where the ratio is 5.5:1 |
| `--amber-deep` | `#A8641F` | 4.7:1 | Small text, links and eyebrows on white |
| `--amber-glow` | `#E0A458` | 7.6:1 on charcoal | The accent on dark sections |
| `--amber-soft` | `#F6E8D6` | — | Tint surface behind icons |
| `--green` | `#4F7D6B` | 4.7:1 | Fill, and white on it is 4.7:1 — this one *can* take white text |
| `--green-deep` | `#3F6B5A` | 6.1:1 | Hover and small text |
| `--green-glow` | `#8FB8A6` | 7.6:1 on charcoal | The accent on dark |
| `--green-soft` | `#E8F0EC` | — | Tint surface |

The amber row is the trap worth remembering. A mid-tone accent that looks fine as a fill will
fail the moment you put white text on it, and finding that out after the build means touching
every button. Measure first. The formula:

```python
def lum(h):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
```

AA needs 4.5:1 for body text, 3:1 for large text (18.66px bold or 24px) and for UI boundaries.

## Type

| Role | Face | Why |
|---|---|---|
| Display | **Newsreader** (variable, 200–700, optical sizing) | A warm editorial serif. It carries the premium, established feel the brief asked for without the fashion-magazine coldness of a high-contrast Didone, and it is not the serif every template reaches for |
| Body and UI | **Inter** | Neutral and legible at small sizes; it does not compete with the headings |

Headings sit at weight 400 rather than bold. At the sizes used here the serif already has
presence, and letting it stay light is most of what separates *expensive* from *loud*.

Both faces are **self-hosted** in `assets/fonts/`, latin subset only, as variable WOFF2 —
about 180 kB for the pair. That keeps a third-party connection off the critical path and means
the site still works if Google Fonts is blocked. Both are preloaded in the `<head>`.

Sizes come from a fluid scale (`--step--2` to `--step-9`) interpolating between 390px and
1600px, so there are no font-size breakpoints to maintain.

## The mark

The site uses **the practice's own logo**: a sitting dog in silhouette with a cat cut out of
it in negative space. It was read off the sign on Highway 98 East in the team photograph the
client supplied, thresholded, and traced to a vector path with `potrace`. The cat is a hole in
the dog, so the path carries `fill-rule="evenodd"` — do not drop that attribute or the cat
disappears.

It sits on a near-black rounded tile, which is how the sign itself presents it.

```bash
pip install cairosvg
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

**This is a trace, not the original artwork.** It is faithful enough to use and crisp at every
size the site needs, but whoever fabricated the sign will hold a real vector file. If the
practice can get it, replace `LOGO_PATH` in `tools/make-brand.py` with the real path data and
re-run — everything else regenerates from that one value.

## Editing the common things## Editing the common things

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
