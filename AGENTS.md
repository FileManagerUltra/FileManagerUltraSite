# AGENTS.md: FileManagerUltraSite

Marketing/documentation website for **FileManagerUltra** (app repo: `FileManagerUltra/FileManagerUltra`, local checkout `/home/remko/code/filemanager`), published with GitHub Pages from this repo (`FileManagerUltra/FileManagerUltraSite`).

## Product in one paragraph

A cross-platform (Linux, macOS, Windows) multi-pane file manager written in Rust with a native `eframe`/egui UI (no Electron, no webview). Unlimited split panes, local/SMB/SFTP behind one `Vfs`, drag & drop (Ctrl = copy, Shift = move), background jobs with progress/conflicts/cancel, trash with undo, terminal panes, rich Markdown/image/log previews, Git status and diff view, dark/light themes. Pre-alpha, MIT licensed. Product copy, feature list, install steps and architecture live in `context/` (snapshots copied from the app repo; refresh them when the product changes).

## Layout

```text
index.html, assets/   the static site (no build step, no JS framework, relative URLs only)
assets/screens/       screenshots (dark + light)
assets/video/         demo video (mp4 + webm) and poster
tools/                scripts that regenerate demo data, screenshots and video from the real app
context/              product docs copied from the app repo (read-only reference)
.github/workflows/    Pages deployment
```

## Rules

1. **Plain static HTML/CSS** with minimal vanilla JS. No bundlers, no CDNs, no trackers, no external fonts (self-host or system fonts); the site must work offline from a checkout.
2. **Relative URLs only**: the site is served from the custom domain `filemanagerultra.com` (set in `CNAME`), and may also be reached under `/FileManagerUltraSite/`.
3. **Screenshots come from the real app**, never mockups. Use `tools/make_demo_data.py` for a deterministic fake home directory (no personal data in any image), capture under Xvfb, and provide dark and light variants.
4. **Accessibility and speed**: alt text on every image, `<video>` with poster and captions/controls, `loading="lazy"` for below-the-fold images, WebP/optimised PNG, respect `prefers-color-scheme` and `prefers-reduced-motion`.
5. **Don't invent features.** Claims must match `context/product-readme.md` and the app's `CHANGELOG.md`. Status stays "pre-alpha" until the app says otherwise. Download links point to the GitHub Releases page.
6. Product name comes from the app's brand (`FileManagerUltra`); keep it in one place in templates where practical.
7. Never commit large raw recordings; commit only the final optimised video/screenshots.

## Regenerating media

```sh
# in the app repo
CARGO_TARGET_DIR=target/agent-site cargo build --release -p fm-app
# here
python3 tools/make_demo_data.py /tmp/fmdemo/home      # fake home dir (needs Pillow)
```

Capture runs the release binary under `Xvfb` with `HOME=/tmp/fmdemo/home` and `XDG_*` pointed inside it, driven by `xdotool`, recorded with `ffmpeg -f x11grab`. (No root needed: `apt-get download xvfb xdotool …` and `dpkg -x` into a temp dir, then add it to `PATH`/`LD_LIBRARY_PATH`.)

## Before you finish

Open `index.html` locally, check dark and light, narrow (360 px) and wide widths, and that every link/asset resolves. Commit with the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.

## Extra media notes

- `tools/demo_sftp_server.py` (asyncssh, user/password `demo`, port 2222) serves fake data for the SFTP screenshots.
- The demo video (`assets/video/demo.{mp4,webm}`, `poster.webp`, `demo.vtt`) is a scripted xdotool + `ffmpeg -f x11grab` capture of the real app (workspaces: build Code/Ops/Media layouts, save each via Workspace ▸ Save Workspace, restart the app, then record Workspace ▸ Open saved); keep it at 1280 px wide and around 1–2 MB. Put `PS1='demo $ '` in the demo HOME's `.bashrc` and `.bash_profile` so terminals do not leak the real user and host.
- `assets/theme.js` powers the Auto/Light/Dark toggle (swaps `data-theme` and the `<picture>` source media).
