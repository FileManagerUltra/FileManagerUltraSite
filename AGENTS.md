# AGENTS.md: FileManagerUltraSite

Marketing/documentation website for **FileManagerUltra** (app repo: `FileManagerUltra/FileManagerUltra`, local checkout `/home/remko/code/FileManagerUltra`), published with GitHub Pages from this repo (`FileManagerUltra/FileManagerUltraSite`).

## Product in one paragraph

A cross-platform (Linux, macOS, Windows) multi-pane file manager written in Rust with a native `eframe`/egui UI (no Electron, no webview). Unlimited split panes, local/SMB/SFTP behind one `Vfs`, drag & drop (Ctrl = copy, Shift = move), background jobs with progress/conflicts/cancel, trash with undo, terminal panes, a Media pane (audio/video, subtitles, DVD images, equalizer, audiobooks), rich Markdown/image/log previews, Git status and diff view, dark/light themes. Beta, Apache 2.0 licensed. Product copy, feature list, install steps and architecture live in `context/` (snapshots copied from the app repo; refresh them when the product changes).

## Layout

```text
index.html            landing page: hero, demo video, feature cards, Media teaser, download
features.html         screenshot sections: previews & Git, Media, terminal & AI, SFTP/SMB, themes
install.html          per-OS install, ffmpeg for video, project status
roadmap.html          planned work: next release, now, next, later
assets/               shared CSS/JS/images (no build step, no JS framework, relative URLs only)
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
5. **Don't invent features.** Claims must match `context/product-readme.md` and the app's `CHANGELOG.md`. Status is "beta" (latest release 0.2.1, shown on `install.html#status`); keep it in sync with the app's README and tags. Features that are only in the changelog's `[Unreleased]` section get a `<span class="tag">Next release</span>` until they ship. Download links point to the GitHub Releases page.
6. Product name comes from the app's brand (`FileManagerUltra`); keep it in one place in templates where practical.
7. Never commit large raw recordings; commit only the final optimised video/screenshots.

## Keeping the roadmap current

`roadmap.html` is the public roadmap. Its sources are the app's `ROADMAP.md` (snapshot in `context/product-roadmap.md`), `docs/roadmap.md` ("Current focus") and the `[Unreleased]` section of `CHANGELOG.md`. The app's `ROADMAP.md` can lag behind, so check it against the changelog: drop anything that has shipped, and don't add plans that appear in none of those files.

Update it:

- **With every release** (the "Site for release X" commit): move what shipped out of the page, refill *Ready for the next release* from the new `[Unreleased]` section (or remove that section when it is empty), and review *Now*.
- **Whenever the app's `ROADMAP.md` or `docs/roadmap.md` changes**: copy `ROADMAP.md` to `context/product-roadmap.md` and update the page to match.
- Each time, set the "Last updated" `<time>` near the top of the page to the date of the update, and say which release it follows.

## Regenerating media

```sh
# in the app repo
CARGO_TARGET_DIR=target/agent-site cargo build --release -p fm-app
# here
python3 tools/make_demo_data.py /dev/shm/home      # fake home dir (needs Pillow and ffmpeg)
```

Capture runs the release binary under `Xvfb` with `HOME=/dev/shm/home` and `XDG_*` pointed inside it, driven by `xdotool`, recorded with `ffmpeg -f x11grab`. (No root needed: `apt-get download xvfb xdotool …` and `dpkg -x` into a temp dir, then add it to `PATH`/`LD_LIBRARY_PATH`.)

## Before you finish

Open `index.html`, `features.html`, `install.html` and `roadmap.html` locally, check dark and light, narrow (360 px) and wide widths, and that every link/asset resolves. Commit with the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.

## Extra media notes

- `tools/demo_sftp_server.py` (asyncssh, user/password `demo`, port 2222) serves fake data for the SFTP screenshots.
- The demo video (`assets/video/demo.{mp4,webm}`, `poster.webp`, `demo.vtt`) is a scripted xdotool + `ffmpeg -f x11grab` capture of the real app (workspaces: build Code/Ops/Media layouts, save each via Workspace ▸ Save Workspace, restart the app, then record Workspace ▸ Open saved); keep it at 1280 px wide and around 1–2 MB. Put `PS1='demo $ '` in the demo HOME's `.bashrc` and `.bash_profile` so terminals do not leak the real user and host.
- Keep the demo home at `/dev/shm/home`: the folder tree shows the siblings of every ancestor, and `/tmp` is full of real user/session names. `/dev/shm` is empty and its siblings are device nodes.
- The header, nav and footer are repeated in each HTML page (no templates); change all four pages together. `index.html` has a tiny inline script that forwards old one-page anchors (`#install`, `#screenshots`, …) to the new pages.
- Screenshot `<picture>` sources intentionally alternate: most match the page theme, every other one shows the opposite theme so readers see both (this is stated in the Features intro).
- Capture gotchas: there is no window manager, so call `xdotool windowfocus --sync <win>` before typing; egui repaints only on input, so nudge the pointer before each capture; resizing the window afterwards leaves a stale GL surface, so set `[window_geometry] size = [1440.0, 900.0]` in `$XDG_CONFIG_HOME/filemanagerultra/prefs.toml` before launch (and `check_updates = false`). Set the theme with `theme = "dark"` there, or toggle Ctrl+Shift+T and then nudge the pointer.
- Media scenes: seed `$XDG_CONFIG_HOME/filemanagerultra/media-queue.json` (mode 600; `paths`, `index`, `position`, `groups` for playlist folders, `items` for audiobook positions) instead of building the playlist by hand. Give the app a private `XDG_RUNTIME_DIR` and a `~/.asoundrc` with `pcm.!default { type null }` so demo audio never reaches real speakers; the null sink drains faster than real time, so pause right after Play. Stop only the instance you started (track its PID), never `pkill` by name: the user may be running the app.
- `assets/theme.js` powers the Auto/Light/Dark toggle (swaps `data-theme` and the `<picture>` source media).
