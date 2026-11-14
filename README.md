# World Top 10

A daily briefing of the 10 most important world stories, written by a Claude cloud routine every morning at 8:00 AM Hong Kong time.

**Read it:** https://giovan-a11y.github.io/world-news/ (on iPhone: open in Safari → Share → Add to Home Screen).

## How it works

| File | What it is |
|---|---|
| `briefings/YYYY-MM-DD.md` | One briefing per day, written by the routine. |
| `template.html` | The page layout, styles and script. `/*DATA*/[]` is filled in by the build. |
| `build.py` | Turns every briefing into HTML and inlines them all into `index.html`, so the page is one self-contained file (same idea as the A350 Atlas offline build). |
| `index.html` | The built page that GitHub Pages serves. Don't edit it by hand. |
| `sw.js`, `manifest.webmanifest`, `icon-*.png` | Let the page install to the Home Screen and open offline with the last copy it saw. |
| `make_icons.py` | Draws the icons (standard library only). |

Rebuild after changing a briefing or the template:

```
python3 build.py
```
