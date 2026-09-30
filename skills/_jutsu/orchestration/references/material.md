# Material: harvest, images, type

The site is made of the client's real material or it is a template with a name on it. This
reference is how bunshin gathers that material, looks at it, and turns it into assets, with the
evidence kept at every step.

**Harvest only what the client owns and agreed to use, for their own site.** Their profile,
their current site, their documents. Never another business's photos, never a stock look-alike
passed off as theirs.

## Harvest

Everything lands in `.bunshin/harvest/`: the files, a `sources.json` that maps each file to its
origin URL and date, a `facts.md` of what the material actually states, and a `missing.md` of
what it does not.

### A public social profile, logged out

- A logged-out profile page shows only the latest posts (about twelve on 2026-09-30), but **each post page** (`/p/<code>/` on
  Instagram) carries a large version of the image and its caption, in its `og:image` and
  `og:description` meta tags (observed on 2026-09-30: `_jutsu/VERSIONS.md`, Orchestration). List the post URLs from the profile, then open the posts.
- Carousels: advance with an in-page click, `page.evaluate(() => document.querySelector(<next>).click())`.
  A tool-level click waits up to thirty seconds whenever a login overlay covers the page.
- Batch five or six posts per browser call: a single long call was killed after about thirty
  minutes in the measured run (Playwright MCP, 2026-09-30). Accumulate the results in a page global (`window.__all`), then write them to disk in
  one call (Playwright MCP: `browser_evaluate` with `filename`). Download the image URLs with
  `curl` in parallel afterwards.
- An authenticated API answers 401 without a session: do not log in with anyone's account.

### A current site, documents, a brief

Fetch the pages and keep the text. Documents: extract the text, keep the file. The brief:
copy it verbatim into `facts.md` as the first source.

### See it before you use it

Contact sheets, labelled, then read them with the file-reading tool. This is where the client's
real style shows (grounds, light, objects, framing), and where the reflex look of the category
gets ruled out.

```bash
magick montage -label '%f' .bunshin/harvest/img/*.jpg -tile 6x -geometry 320x320+6+6 .bunshin/harvest/sheet-%02d.png
```

**Palette by evidence.** Sample the key images and read the counts; a site's colours can come
from the client's own photographs rather than from a mood word.

```bash
magick <image> -resize 200x200 -colors 6 -format %c histogram:info:-
```

**Facts from the captions.** Places, collaborations, work done, names of products, services or
works, dates. Each fact keeps its source. These are what makes the site credible without inventing
anything; what is not there goes into `missing.md` (prices, testimonials, numbers, legal
details) and stays generic on the page.

## Images

- **Trim the frames social apps add:** `magick in.jpg -fuzz 12% -trim +repage out.jpg`.
- **Crop out what sells nothing:** hands, watches, price tags, a stranger in the background.
- **Web formats:** WebP for photographs by default. On phone photographs, AVIF came out heavier
  than WebP at matching quality in the run this pipeline comes from; measure before adding it.
- **Provenance on every raster.** With Impeccable: `<dir>/scripts/impeccable embed-prompt <file>
  --prompt "<origin>"` on each one, then `<dir>/scripts/impeccable embed-prompt --scan <every
  folder the site's rasters ship from>` (for example `src/assets public`) must report zero
  missing. Without it: every file in `sources.json`.

### Geometric cutouts from the real photograph

A round object seen square-on (a record, a coin, a clock face, a lens) can become a cutout, and a
cutout is only acceptable when its edge is the object's own edge. Never a disc stamped over a
scene: that is decoration pretending to be a subject.

Fit the object's real outline, then cut slightly inside it:

```python
# Circle cutout fitted to the object's own edge. Needs Pillow and numpy.
import numpy as np
from PIL import Image

def cutout(src, out, center=None, r_min=0.25, r_max=0.62, inset=0.015, rays=360):
    im = Image.open(src).convert("RGB")
    g = np.asarray(im.convert("L"), dtype=float)
    h, w = g.shape
    gy, gx = np.gradient(g)
    mag = np.hypot(gx, gy)
    if center is None:  # centroid of the bright side of an Otsu split: a light object on a darker ground
        hist = np.bincount(g.astype(np.uint8).ravel(), minlength=256).astype(float)
        p = hist / hist.sum(); om = np.cumsum(p); mu = np.cumsum(p * np.arange(256))
        t = np.nanargmax((mu[-1] * om - mu) ** 2 / (om * (1 - om) + 1e-12))
        ys, xs = np.nonzero(g > t)
        center = (xs.mean(), ys.mean())
    cx, cy = center
    side = min(w, h)
    pts = []
    for a in np.linspace(0, 2 * np.pi, rays, endpoint=False):
        rs = np.arange(int(side * r_min), int(side * r_max))
        x = (cx + rs * np.cos(a)).astype(int); y = (cy + rs * np.sin(a)).astype(int)
        ok = (x >= 0) & (x < w) & (y >= 0) & (y < h)
        if ok.sum() < 10:
            continue
        i = np.argmax(mag[y[ok], x[ok]])  # the strongest edge along the ray
        pts.append((x[ok][i], y[ok][i]))
    P = np.array(pts, dtype=float)
    for _ in range(3):  # least-squares circle, then drop the rays that hit something else
        A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
        b = (P ** 2).sum(1)
        (fx, fy, c), *_ = np.linalg.lstsq(A, b, rcond=None)
        r = np.sqrt(c + fx ** 2 + fy ** 2)
        res = np.abs(np.hypot(P[:, 0] - fx, P[:, 1] - fy) - r)
        P = P[res < max(2.0, 2.5 * np.median(res))]
    r *= 1 - inset
    yy, xx = np.mgrid[0:h, 0:w]  # alpha from each pixel's coverage: an antialiased edge
    d = np.hypot(xx + 0.5 - fx, yy + 0.5 - fy)
    mask = Image.fromarray((np.clip(r - d + 0.5, 0, 1) * 255).astype(np.uint8))
    rgba = im.copy(); rgba.putalpha(mask)
    box = (int(fx - r), int(fy - r), int(fx + r), int(fy + r))
    rgba.crop(box).save(out)
    return {"center": (round(fx), round(fy)), "radius": round(r), "rays_kept": len(P)}
```

- When the rim is cut by the frame, fit the inner well instead (narrow `r_min` / `r_max` to it)
  or pick another photograph; a flat side on a "circle" is worse than no cutout.
- When the object is not round (a tray, a box, a book), use a different image.
- **Check every cutout on a light and on a dark ground** before it ships: a halo of the old
  background shows on one of the two.

### Grain

Grain as a small tiled texture, applied per colour field as a `background-image`, never as a
fixed full-screen layer (that costs a repaint on every scroll frame):

```python
import numpy as np; from PIL import Image
rng = np.random.default_rng(7)
n = rng.random((256, 256))
a = np.zeros((256, 256, 4), dtype=np.uint8)
a[n > 0.985] = (0, 0, 0, 38); a[n < 0.015] = (255, 255, 255, 30)
Image.fromarray(a, "RGBA").save("grain.webp", lossless=True)
```

## Type, by evidence

A typeface chosen from a name in a list is a reflex. Choose it from rendered specimens.

1. **Specimens.** Write one throwaway HTML page with 20 or more candidates, each set in a real
   miniature of the layout: the colour field, the display line, the subtitle, a paragraph, in
   the project's languages and with its real words. Capture it (`shoot.mjs` serves any folder)
   and compare the captures, not the names.
2. **Rule out the reflexes** the `tells` module names for the display role, unless the visual
   thesis names the face and says why this one.
3. **In situation.** Take the two or three survivors into a second sheet: display and text
   faces together, at the real scale steps, on the real grounds. Choose there.
4. **Record the choice** in the direction contract with its one-line reason. Self-host or load
   it through the framework's font pipeline, with the subsets the languages need.
