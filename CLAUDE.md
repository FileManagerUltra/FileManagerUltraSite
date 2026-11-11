# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The project rules, layout and media-regeneration steps live in AGENTS.md and apply here in full:

@AGENTS.md

## Notes not covered in AGENTS.md

- **No build, lint or tests.** Preview by opening `index.html` directly, or serve it with `python3 -m http.server` from the repo root to test relative URLs the way Pages serves them.
- **Deployment** (`.github/workflows/pages.yml`) runs on every push to `main` and copies only the top-level `*.html` pages, `CNAME` and `assets/` into the Pages artifact. Anything else the live site needs has to be under `assets/`; `tools/` and `context/` are never published.
- **Theme switching uses two mechanisms together:**
  - CSS: colour tokens on `:root` in `assets/style.css`, overridden under `@media (prefers-color-scheme: dark)` with `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`. A new token needs a value in all three places.
  - Images: `assets/theme.js` forces the theme on screenshots by rewriting the `media` attribute of every `<picture><source media="(prefers-color-scheme: …)">`. Theme-aware screenshots must use that pattern: a `<source>` with a `prefers-color-scheme` media query plus a fallback `<img>`. Single-variant images, like the accent shots, just leave out the `<source>`.
- **Lightbox:** `assets/lightbox.js` makes every `figure picture img` click-to-enlarge in a `<dialog>`. Put screenshots inside `<figure><picture>` to get this; images outside that structure won't zoom.
- **Screenshot files:** `assets/screens/<name>-dark.webp` / `<name>-light.webp` at 1440×900. Declare `width`/`height` on the `<img>` so the layout doesn't shift while images load.
- **Pages:** `index.html`, `features.html` and `install.html` each carry their own copy of the header, nav and footer, so change all three together. The header `<nav>` links pages and marks the current one with `aria-current="page"`. `features.html` has its own `.subnav` linking its section `id`s. When you add or rename a section, update that nav, and the legacy-anchor map in `index.html` if an old anchor moved.
- **Before writing product copy**, check `context/product-readme.md`, `context/product-changelog.md` and `context/install.md`. `context/style-guide.md` and `context/architecture.md` describe the app's own UI and code, not this site.
