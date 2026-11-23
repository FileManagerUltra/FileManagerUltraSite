#!/usr/bin/env python3
"""Build a throwaway demo home directory used for website screenshots and the demo video.

Usage: make_demo_data.py <target-dir>   (the directory is wiped and recreated)
Needs Pillow and ffmpeg (libmp3lame, libx264) for the playable demo media.
"""
import math
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

if len(sys.argv) != 2:
    sys.exit(__doc__)
home = Path(sys.argv[1]).resolve()
if home.exists():
    shutil.rmtree(home)
home.mkdir(parents=True)
rng = random.Random(7)
NOW = time.time()


def put(path, text="", days_ago=0.0):
    p = home / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text) if isinstance(text, str) else p.write_bytes(text)
    t = NOW - days_ago * 86400
    os.utime(p, (t, t))
    return p


def art(seed, size):
    r = random.Random(seed)
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    c1 = [r.randint(20, 120) for _ in range(3)]
    c2 = [r.randint(120, 255) for _ in range(3)]
    for y in range(h):
        k = y / h
        row = tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3))
        for x in range(w):
            px[x, y] = row
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(14):
        cx, cy, rad = r.randint(0, w), r.randint(0, h), r.randint(60, 260)
        col = tuple(r.randint(0, 255) for _ in range(3)) + (r.randint(50, 130),)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
    for i in range(0, w, 8):
        y = h * 0.78 + math.sin(i / 90 + seed) * 40
        d.rectangle([i, y, i + 8, h], fill=(10, 20, 30, 150))
    return img


def picture(name, seed, size=(1280, 853), days_ago=1.0):
    img = art(seed, size)
    p = home / "Pictures" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, quality=88)
    t = NOW - days_ago * 86400
    os.utime(p, (t, t))


# --- Pictures -----------------------------------------------------------------
for i, n in enumerate(["sunrise", "harbour", "forest-path", "city-night", "dunes", "glacier",
                       "market", "lighthouse", "canyon", "meadow", "old-bridge", "storm"]):
    picture(f"{n}.jpg", i + 3, days_ago=2 + i * 3)

# --- Documents ----------------------------------------------------------------
put("Documents/README.md", """# Trip planning

A short **overview** of the *Iceland* trip, with a checklist and a budget.

## Checklist

- [x] Book flights
- [x] Rent a 4x4
- [ ] Reserve guesthouses
  - [ ] Reykjavik
  - [ ] Vik

## Budget

| Item        | Cost (EUR) | Notes            |
|-------------|-----------:|------------------|
| Flights     |        640 | Return, 2 people |
| Car rental  |        910 | 10 days          |
| Guesthouses |       1200 | Estimated        |

## Route script

```rust
fn route() -> Vec<&'static str> {
    vec!["Reykjavik", "Vik", "Hofn", "Akureyri"]
}
```

> Tip: pack warm layers even in summer.

See also [the packing list](packing.md).
""", 3)
put("Documents/packing.md", "# Packing list\n\n- Rain jacket\n- Wool socks\n- Camera\n", 9)
put("Documents/budget-2026.csv", "month,income,spend\n" + "\n".join(
    f"{m},{3000 + rng.randint(0, 400)},{2100 + rng.randint(0, 600)}" for m in
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]) + "\n", 20)
put("Documents/notes.txt", "Remember to renew the passport.\nCall the landlord.\n", 12)
# The old placeholder used these random bytes; drawing them keeps the rest of the home unchanged.
for _ in range(40000):
    rng.getrandbits(8)


def form_pdf():
    """A one-page fillable PDF form (text fields, a list, checkboxes and a signature field)."""
    W, H = 595, 842
    text = []

    def t(x, y, size, s, bold=False):
        s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        text.append(f"BT /{'F2' if bold else 'F1'} {size} Tf {x} {y} Td ({s}) Tj ET")

    t(56, 770, 20, "Community Garden Plot Application", True)
    t(56, 748, 10, "Greenfield Allotments, season 2027. Return by 31 January.")
    text.append("0.2 0.45 0.3 RG 2 w 56 736 m 539 736 l S 0 G 0.6 w")
    fields = []  # (name, kind, rect, extra)
    y = 700
    for label, name in [("Full name", "name"), ("Street and number", "street"),
                        ("Postcode and town", "town"), ("Email", "email"), ("Phone", "phone")]:
        t(56, y + 26, 10, label)
        fields.append((name, "Tx", (56, y, 539, y + 22)))
        y -= 52
    t(56, y + 26, 10, "Plot size")
    fields.append(("plot", "Ch", (56, y, 260, y + 22)))
    t(300, y + 26, 10, "Preferred start date")
    fields.append(("start", "Tx", (300, y, 539, y + 22)))
    y -= 52
    t(56, y + 26, 11, "Interests", True)
    for i, (label, name) in enumerate([("Vegetables", "veg"), ("Flowers", "flowers"),
                                      ("Fruit trees", "fruit"), ("Beekeeping", "bees")]):
        x = 56 + i * 122
        fields.append((name, "Btn", (x, y, x + 14, y + 14)))
        text.append(f"0.55 0.6 0.58 RG 0.96 0.98 0.96 rg {x} {y} 14 14 re B 0 g")
        t(x + 22, y + 3, 10, label)
    y -= 50
    t(56, y + 26, 10, "Anything we should know")
    fields.append(("notes", "TxM", (56, y - 40, 539, y + 22)))
    y -= 80
    fields.append(("agree", "Btn", (56, y, 70, y + 14)))
    text.append(f"0.55 0.6 0.58 RG 0.96 0.98 0.96 rg 56 {y} 14 14 re B 0 g")
    t(78, y + 3, 10, "I have read the garden rules and will keep my plot tidy.")
    y -= 110
    t(56, y + 70, 10, "Signature")
    fields.append(("signature", "Sig", (56, y, 300, y + 60)))
    t(330, y + 70, 10, "Date")
    fields.append(("date", "Tx", (330, y + 38, 539, y + 60)))
    t(56, 60, 8, "Demo form made for FileManagerUltra screenshots. Not a real organisation.")

    for _, kind, (x1, y1, x2, y2) in fields:  # field frames, for viewers that skip /MK
        if kind != "Btn":
            text.append(f"0.55 0.6 0.58 RG 0.96 0.98 0.96 rg {x1} {y1} {x2 - x1} {y2 - y1} re B 0 g")
    objs = {}
    objs[1] = "<< /Type /Catalog /Pages 2 0 R /AcroForm 5 0 R >>"
    objs[2] = "<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    fonts = "<< /F1 6 0 R /F2 7 0 R /Helv 6 0 R /ZaDb 8 0 R >>"
    objs[6] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objs[7] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    objs[8] = "<< /Type /Font /Subtype /Type1 /BaseFont /ZapfDingbats >>"
    on = "q 0 g BT /ZaDb 12 Tf 1.5 2.5 Td (4) Tj ET Q"
    objs[9] = f"<< /Type /XObject /Subtype /Form /BBox [0 0 14 14] /Resources << /Font {fonts} >> /Length {len(on)} >>\nstream\n{on}\nendstream"
    objs[10] = "<< /Type /XObject /Subtype /Form /BBox [0 0 14 14] /Length 0 >>\nstream\n\nendstream"
    annots = []
    n = 11
    for name, kind, (x1, y1, x2, y2) in fields:
        common = (f"/Type /Annot /Subtype /Widget /P 3 0 R /T ({name}) /F 4 /Rect [{x1} {y1} {x2} {y2}] "
                  "/MK << /BC [0.55 0.6 0.58] /BG [0.96 0.98 0.96] >> /BS << /W 1 /S /S >>")
        if kind == "Tx":
            d = f"<< {common} /FT /Tx /DA (/Helv 11 Tf 0 g) >>"
        elif kind == "TxM":
            d = f"<< {common} /FT /Tx /Ff 4096 /DA (/Helv 10 Tf 0 g) >>"
        elif kind == "Ch":
            d = (f"<< {common} /FT /Ch /Ff 131072 /DA (/Helv 11 Tf 0 g) "
                 "/Opt [(Half plot, 50 m2) (Full plot, 100 m2) (Raised bed) (Shared greenhouse bench)] >>")
        elif kind == "Btn":
            d = (f"<< {common} /FT /Btn /V /Off /AS /Off /DA (/ZaDb 0 Tf 0 g) "
                 "/AP << /N << /Yes 9 0 R /Off 10 0 R >> >> >>")
        else:
            d = f"<< {common} /FT /Sig >>"
        objs[n] = d
        annots.append(f"{n} 0 R")
        n += 1
    stream = "\n".join(text)
    objs[4] = f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"
    objs[3] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Contents 4 0 R "
               f"/Resources << /Font {fonts} >> /Annots [{' '.join(annots)}] >>")
    objs[5] = (f"<< /Fields [{' '.join(annots)}] /NeedAppearances true "
               f"/DR << /Font {fonts} >> /DA (/Helv 0 Tf 0 g) >>")
    out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for k in sorted(objs):
        offsets[k] = len(out)
        out += f"{k} 0 obj\n{objs[k]}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {n}\n0000000000 65535 f \n".encode()
    for k in range(1, n):
        out += f"{offsets[k]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


put("Documents/garden-plot-application.pdf", form_pdf(), 2)


def orders_csv():
    """A few thousand orders, with long notes for the Record panel."""
    r = random.Random(23)
    cities = ["Amsterdam", "Utrecht", "Groningen", "Leiden", "Haarlem", "Delft", "Zwolle", "Breda",
              "Arnhem", "Maastricht", "Eindhoven", "Nijmegen"]
    first = ["Anna", "Bram", "Carmen", "Daan", "Eva", "Finn", "Gwen", "Hugo", "Iris", "Jasper", "Kim",
             "Lars", "Mila", "Noah", "Olga", "Pim", "Rosa", "Sven", "Tess", "Vince"]
    last = ["Bakker", "de Vries", "Jansen", "Visser", "Smit", "Meijer", "Mulder", "Bos", "Dekker",
            "Peters", "Hendriks", "van Dijk"]
    products = [("Desk lamp", 39.95), ("Notebook A5", 4.50), ("Fountain pen", 24.00),
                ("Monitor arm", 89.00), ("Ergonomic chair", 249.00), ("USB-C hub", 34.99),
                ("Standing desk", 459.00), ("Cable tray", 17.50), ("Desk mat", 21.00),
                ("Webcam", 69.00), ("Headset", 79.95), ("Plant pot", 12.95)]
    statuses = ["delivered"] * 6 + ["shipped"] * 2 + ["processing", "returned", "cancelled"]
    notes = ["", "", "", "Leave at the back door if nobody answers.",
             "Gift: please leave out the invoice and add a card that says Happy birthday.",
             "Customer asked to combine this with the previous order to save on shipping costs.",
             "Box arrived with a dented corner; the product itself was fine, customer kept it.",
             "Deliver after 17:00 on weekdays. Third floor, the bell on the left does not work, call instead."]
    rows = ["order_id,date,customer,city,product,qty,unit_price,total,status,notes"]
    t0 = time.mktime((2026, 1, 1, 9, 0, 0, 0, 0, -1))
    for i in range(4000):
        when = time.strftime("%Y-%m-%d", time.localtime(t0 + i * 1.9 * 3600))
        name = f"{r.choice(first)} {r.choice(last)}"
        prod, price = r.choice(products)
        qty = r.choice([1, 1, 1, 2, 2, 3, 4, 10])
        note = r.choice(notes)
        if "," in note:
            note = '"' + note + '"'
        rows.append(f"{10421 + i},{when},{name},{r.choice(cities)},{prod},{qty},{price:.2f},"
                    f"{qty * price:.2f},{r.choice(statuses)},{note}")
    return "\n".join(rows) + "\n"


put("Documents/orders-2026.csv", orders_csv(), 1)
put("Documents/archive-2025.zip", bytes(rng.getrandbits(8) for _ in range(250000)), 200)

# --- Logs ---------------------------------------------------------------------
levels = ["INFO"] * 8 + ["WARN"] * 2 + ["ERROR"]
msgs = ["request handled", "cache refreshed", "connection pool resized", "slow query detected",
        "upstream timeout", "user signed in", "job scheduled", "disk usage at 81%"]
lines = []
start = NOW - 3 * 3600
for i in range(400):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start + i * 27))
    lines.append(f"{ts} {rng.choice(levels):5} api: {rng.choice(msgs)} id={rng.randint(1000, 9999)}")
put("Projects/api-server/logs/server.log", "\n".join(lines) + "\n", 0.01)

# --- Projects: a git repo with local modifications ------------------------------
repo = home / "Projects" / "webshop"
(repo / "src").mkdir(parents=True)
put("Projects/webshop/src/main.rs", """use std::collections::HashMap;

fn total(prices: &HashMap<String, u32>) -> u32 {
    prices.values().sum()
}

fn main() {
    let mut cart = HashMap::new();
    cart.insert("book".to_string(), 12);
    cart.insert("pen".to_string(), 2);
    println!("total: {}", total(&cart));
}
""", 5)
put("Projects/webshop/src/lib.rs", "pub fn greet() -> &'static str {\n    \"hello\"\n}\n", 5)
put("Projects/webshop/README.md", "# webshop\n\nA tiny demo shop.\n", 5)
put("Projects/webshop/Cargo.toml", '[package]\nname = "webshop"\nversion = "0.1.0"\nedition = "2021"\n', 5)
git_env = {**os.environ, "GIT_AUTHOR_NAME": "Demo", "GIT_AUTHOR_EMAIL": "demo@example.com",
           "GIT_COMMITTER_NAME": "Demo", "GIT_COMMITTER_EMAIL": "demo@example.com",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


def git(*a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, env=git_env, capture_output=True)


git("init", "-q", "-b", "main")
git("add", ".")
git("commit", "-q", "-m", "Initial commit")
put("Projects/webshop/src/main.rs", """use std::collections::HashMap;

/// Sum of all line items, with a 10% discount over 50.
fn total(prices: &HashMap<String, u32>) -> u32 {
    let sum: u32 = prices.values().sum();
    if sum > 50 { sum * 9 / 10 } else { sum }
}

fn main() {
    let mut cart = HashMap::new();
    cart.insert("book".to_string(), 12);
    cart.insert("pen".to_string(), 2);
    cart.insert("lamp".to_string(), 45);
    println!("total: {}", total(&cart));
}
""", 0.02)
put("Projects/webshop/src/checkout.rs", "pub fn pay() {}\n", 0.01)
put("Projects/webshop/README.md", "# webshop\n\nA tiny demo shop.\n\n## Usage\n\n`cargo run`\n", 0.02)

put("Projects/api-server/Cargo.toml", '[package]\nname = "api-server"\nversion = "0.3.2"\n', 30)
put("Projects/api-server/src/main.rs", "fn main() {\n    println!(\"listening\");\n}\n", 30)
put("Projects/dotfiles/vimrc", "set number\nsyntax on\n", 100)

# --- Misc ---------------------------------------------------------------------
for i in range(1, 9):
    put(f"Downloads/installer-{i}.deb", bytes(rng.getrandbits(8) for _ in range(30000 * i)), i * 2)
(home / "Desktop").mkdir()
(home / "Public").mkdir()
for rc in (".bashrc", ".bash_profile"):
    put(rc, "PS1='demo $ '\n", 30)

# --- Sync: Photos and an older backup of it in Backup/Photos ----------------------
# Synchronize Folders screenshots compare these two. Their own random generator keeps
# the rest of the demo home byte-for-byte the same.
srng = random.Random(11)


def photo_pair(album, names, days_ago, both=True, size=None):
    for name in names:
        n = size or srng.randint(900_000, 3_400_000)
        data = srng.randbytes(n)
        put(f"Photos/{album}/{name}", data, days_ago)
        if both:
            put(f"Backup/Photos/{album}/{name}", data, days_ago)


photo_pair("2025 Summer Lake", [f"IMG_{i}.jpg" for i in range(1001, 1015)], 120)
photo_pair("Family", [f"IMG_{i:04d}.jpg" for i in range(801, 810)], 60)
photo_pair("2026 Iceland", [f"IMG_{i}.jpg" for i in range(2201, 2211)], 30)
photo_pair("2026 Iceland", [f"IMG_{i}.jpg" for i in range(2211, 2225)], 3, both=False)  # new
photo_pair("Screenshots", [f"Screenshot 2026-11-{d:02d}.png" for d in (2, 9, 14)], 2, both=False)
for name in ("IMG_2203-edit.jpg", "IMG_2207-edit.jpg", "IMG_2215-edit.jpg"):  # edited on both sides
    put(f"Backup/Photos/2026 Iceland/Edited/{name}", srng.randbytes(srng.randint(1_500_000, 2_500_000)), 20)
    put(f"Photos/2026 Iceland/Edited/{name}", srng.randbytes(srng.randint(1_500_000, 2_500_000)), 1)
put("Backup/Photos/Family/IMG_0803.jpg", srng.randbytes(1_800_000), 10)  # newer in the backup
put("Backup/Photos/Family/IMG_0805 (1).jpg", srng.randbytes(2_100_000), 58)  # only in the backup
for i in range(1, 7):  # a folder that was removed from Photos
    put(f"Backup/Photos/Old phone/DSC_{i:04d}.jpg", srng.randbytes(srng.randint(600_000, 1_400_000)), 400)
put("Photos/2026 Iceland/Thumbs.db", srng.randbytes(24_000), 3)
put("Photos/Family/.DS_Store", srng.randbytes(6_148), 60)

# --- Media: real, playable files generated with ffmpeg ---------------------------
# Invented artists, albums and books; the audio is synthesised chords and the
# video is an ffmpeg test source, so nothing here is copyrighted or personal.
tmp = home / ".cache" / "demo-build"
tmp.mkdir(parents=True)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def cover(name, seed):
    p = tmp / f"{name}.jpg"
    art(seed, (600, 600)).save(p, quality=88)
    return p


def tone(seed, seconds):
    """aevalsrc expression: a slowly pulsing three-note chord, different per seed."""
    r = random.Random(seed)
    root = r.choice([110, 123.5, 130.8, 146.8, 164.8])
    notes = [root, root * r.choice([1.25, 1.2]), root * 1.5, root * 2]
    parts = [f"0.12*sin(2*PI*{f:.2f}*t)*(0.6+0.4*sin(2*PI*{0.1 + i * 0.07:.2f}*t))"
             for i, f in enumerate(notes)]
    return f"aevalsrc='{'+'.join(parts)}':s=44100:d={seconds}"


def stamp(p, days_ago):
    t = NOW - days_ago * 86400
    os.utime(p, (t, t))


def track(path, seed, seconds, tags, art_seed, days_ago, codec=("-c:a", "libmp3lame", "-b:a", "96k")):
    p = home / path
    p.parent.mkdir(parents=True, exist_ok=True)
    meta = [x for k, v in tags.items() for x in ("-metadata", f"{k}={v}")]
    ffmpeg("-f", "lavfi", "-i", tone(seed, seconds), "-i", str(cover(f"c{art_seed}", art_seed)),
           "-map", "0:a", "-map", "1:v", *codec, "-c:v", "mjpeg", "-disposition:v", "attached_pic",
           "-id3v2_version", "3", *meta, str(p))
    stamp(p, days_ago)


albums = [
    ("Northern Lights Ensemble", "Tidal Hours", 2024, 21,
     [("First Light", 192), ("Saltwater", 241), ("Harbour Bells", 207), ("Low Tide", 263), ("Lanterns", 228)]),
    ("Mira Okafor", "Paper Satellites", 2025, 34,
     [("Orbit", 215), ("Static Bloom", 186), ("Signal Fire", 249), ("Homeward", 232)]),
]
for artist, album, year, seed, songs in albums:
    for n, (title, secs) in enumerate(songs, 1):
        track(f"Music/{artist}/{album}/{n:02d} {title}.mp3", seed + n, secs,
              {"title": title, "artist": artist, "album": album, "date": year, "track": n,
               "genre": "Ambient"}, seed, 40 + n)

# An .m4b audiobook with chapters.
book = home / "Audio Books" / "Elin Varga - The Lighthouse Keeper.m4b"
book.parent.mkdir(parents=True)
chapters = ["Opening", "The Keeper", "Fog", "A Letter", "The Storm", "Morning"]
ch_len = 7 * 60 * 1000
meta = tmp / "chapters.txt"
meta.write_text(";FFMETADATA1\ntitle=The Lighthouse Keeper\nartist=Elin Varga\nalbum=The Lighthouse Keeper\n"
                "genre=Audiobook\n" + "".join(
                    f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={i * ch_len}\nEND={(i + 1) * ch_len}\ntitle={c}\n"
                    for i, c in enumerate(chapters)))
ffmpeg("-f", "lavfi", "-i", tone(91, len(chapters) * ch_len // 1000), "-i", str(meta),
       "-i", str(cover("book", 91)), "-map", "0:a", "-map", "2:v", "-map_metadata", "1",
       "-map_chapters", "1", "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-c:v", "mjpeg",
       "-disposition:v", "attached_pic", "-f", "mp4", str(book))
stamp(book, 15)

# A folder audiobook of mp3 chapters (recognised from the "Chapter…" names).
for n in range(1, 6):
    track(f"Audio Books/Tomas Lind - Wind Over Water/Chapter {n:02d}.mp3", 70 + n, 300 + n * 17,
          {"title": f"Chapter {n}", "artist": "Tomas Lind", "album": "Wind Over Water", "track": n,
           "genre": "Audiobook"}, 77, 25, codec=("-c:a", "libmp3lame", "-b:a", "48k", "-ac", "1"))


def video(path, seconds, source, days_ago, seed):
    p = home / path
    p.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg("-f", "lavfi", "-t", str(seconds), "-i", f"{source}:s=1280x720:r=25", "-f", "lavfi", "-i", tone(seed, seconds),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-metadata", f"title={p.stem}", str(p))
    stamp(p, days_ago)
    return p


v = video("Videos/Fractal Zoom.mp4", 90, "mandelbrot=end_scale=0.01:end_pts=2250", 4, 55)
subs = [(2, 7, "We start with the whole Mandelbrot set."), (8, 14, "Every point is tested: does it stay bounded?"),
        (15, 21, "The colours show how quickly points escape."), (22, 28, "Zooming in, the edge never gets simpler."),
        (31, 37, "Small copies of the whole set appear."), (40, 46, "There is always more detail to find.")]
(v.parent / "Fractal Zoom.en.srt").write_text("".join(
    f"{i}\n00:00:{a:02d},000 --> 00:00:{b:02d},000\n{text}\n\n" for i, (a, b, text) in enumerate(subs, 1)))
video("Videos/Colour Gradients.mp4", 45, "gradients=speed=0.02:n=4:seed=5", 11, 63)
video("Downloads/holiday-video.mp4", 20, "gradients=speed=0.05:seed=9", 6, 12)
shutil.rmtree(tmp)
print(f"demo home ready: {home}")
