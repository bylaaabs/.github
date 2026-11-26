"""draw github.com/bylaaabs: the header, the buttons, the map of the open pieces and one card per repository.

reads map/repos.yml, the wordmarks from bylaaabs/brand and, from the github api, which repositories are
public, their latest release and the casks in the tap. writes profile/ in light and dark and the card list
between the repos markers of profile/README.md. fails when a public repository is not declared, so the
profile never falls behind the organisation.

    pip install -r map/requirements.txt
    python3 map/render.py          # set GITHUB_TOKEN to avoid the api rate limit
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html import escape
from io import BytesIO
from pathlib import Path

import yaml
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ORG = "bylaaabs"
SITE = "https://laaabs.com"
WORDMARKS = "https://raw.githubusercontent.com/bylaaabs/brand/main/generated/wordmarks.ts"
ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "profile"
README = OUT / "README.md"
FONT = ROOT / "fonts" / "Outfit.woff2"

# the brand tokens (bylaaabs/brand tokens/tokens.json); the greys are the white and black opacity ladders, flattened
CYAN = "#00b5e2"
THEMES = {
    "light": dict(fill="#ffffff", line="#e3e3e3", text="#0a0a0a", muted="#666666", faint="#9a9a9a",
                  live_bg="#00b5e2", live_bg_o=".12", live_text="#007ea0", work_bg="#0a0a0a", work_bg_o=".06",
                  led_work="#0a0a0a", button="#0a0a0a", button_text="#ffffff"),
    "dark": dict(fill="#111111", line="#272727", text="#ffffff", muted="#9a9a9a", faint="#666666",
                 live_bg="#00b5e2", live_bg_o=".16", live_text="#8fddf2", work_bg="#ffffff", work_bg_o=".06",
                 led_work="#ffffff", button="#ffffff", button_text="#0a0a0a"),
}
LIVE = {"alpha", "beta", "stable"}
GROUPS = [("tools", "tools"), ("apps", "apps"), ("alongside", "alongside"), ("project", "project")]


# github

def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def public_repos():
    """only ever asks for the public ones, so no private name reaches this script or its output."""
    names, page = set(), 1
    while True:
        batch = api(f"/orgs/{ORG}/repos?type=public&per_page=100&page={page}")
        names |= {r["name"] for r in batch if not r["archived"] and not r["private"]}
        if len(batch) < 100:
            return names
        page += 1


def latest_release(name):
    try:
        releases = api(f"/repos/{ORG}/{name}/releases?per_page=10")
    except urllib.error.HTTPError:
        return None
    return next((r for r in releases if not r["draft"]), None)


def casks():
    try:
        files = api(f"/repos/{ORG}/homebrew-tap/contents/Casks")
    except urllib.error.HTTPError:
        return []
    return [f["name"][:-3] for f in files if f["name"].endswith(".rb")]


# the brand

def wordmarks():
    """the paths of every wordmark, as bylaaabs/brand generates them for the webs."""
    with urllib.request.urlopen(WORDMARKS) as res:
        ts = res.read().decode()
    marks = {}
    for m in re.finditer(r"^  '?([a-z0-9-]+)'?: \{ viewBox: \[([^\]]+)\], letterHeight: ([\d.]+).*?paths: \[(.*?)\n  \] \},", ts, re.S | re.M):
        name, vb, lh, body = m.groups()
        paths = [dict(d=p.group(1), rule=p.group(2) or "evenodd", dot=bool(p.group(3)))
                 for p in re.finditer(r'\{ d: "([^"]+)"(?:, rule: "(\w+)")?(, dot: true)? \}', body)]
        marks[name] = dict(viewBox=[float(v) for v in vb.split(",")], letterHeight=float(lh), paths=paths)
    if "laaabs" not in marks:
        sys.exit("could not read the wordmarks from bylaaabs/brand")
    return marks


def mark(wm, x, y, height, color):
    """a wordmark whose letters are `height` tall, top left at x, y; the dot is always cyan. returns (svg, width)."""
    s = height / wm["letterHeight"]
    inner = "".join(f'<path d="{p["d"]}" fill="{CYAN if p["dot"] else color}" fill-rule="{p["rule"]}"/>' for p in wm["paths"])
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.6f})">{inner}</g>', wm["viewBox"][2] * s


class Type:
    """outfit, embedded as a subset and measured, so text is placed and trimmed to the pixel."""

    def __init__(self):
        self.data = FONT.read_bytes()
        self.face = ("@font-face{font-family:'Outfit';font-weight:500 700;"
                     f"src:url(data:font/woff2;base64,{base64.b64encode(self.data).decode()}) format('woff2')}}")
        self.cache = {}

    def _font(self, weight):
        if weight not in self.cache:
            f = TTFont(BytesIO(self.data))
            instantiateVariableFont(f, {"wght": weight}, inplace=True)
            self.cache[weight] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        return self.cache[weight]

    def width(self, text, size, weight=500, tracking=0.0):
        cmap, hmtx, upm = self._font(weight)
        units = sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text)
        return units * size / upm + tracking * len(text)

    def fit(self, text, size, room, weight=500):
        if self.width(text, size, weight) <= room:
            return text
        while text and self.width(text + "...", size, weight) > room:
            text = text[:-1]
        return text.rstrip(" ,-") + "..."


def svg(w, h, label, body, t, fonts=True):
    style = f"<style>{t.face}text{{font-family:'Outfit',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}}</style>" if fonts else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" '
            f'role="img" aria-label="{escape(label)}">{style}{body}</svg>\n')


def write(name, text):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def arrow_out(x, y, color, size=7):
    """the small north-east arrow that says the link leaves for somewhere else."""
    return (f'<path d="M{x} {y + size}L{x + size} {y}M{x + 2} {y}H{x + size}V{y + size - 2}" fill="none" stroke="{color}" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')


# the pieces

def header(marks, t):
    w, h = 640, 150
    for theme, c in THEMES.items():
        wm = marks["laaabs"]
        width = wm["viewBox"][2] * 64 / wm["letterHeight"]
        logo, _ = mark(wm, (w - width) / 2, 18, 64, c["text"])
        tb = marks["things-by-laaabs"]
        tw = tb["viewBox"][2] * 17 / tb["letterHeight"]
        tag, _ = mark(tb, (w - tw) / 2, 112, 17, c["muted"])
        write(f"header-{theme}.svg", svg(w, h, "laaabs. things by laaabs.", logo + tag, t, fonts=False))


BUTTONS = {
    "web": ("laaabs.com", True),
    "handbook": ("handbook", False),
    "brand": ("brand", False),
    "tap": ("homebrew tap", False),
    "contributing": ("how we work", True),
    "first-issue": ("good first issues", False),
    "security": ("report a vulnerability", False),
}


def buttons(t):
    for slug, (label, primary) in BUTTONS.items():
        size, pad, h = 15, 18, 40
        tw = t.width(label, size, 600)
        w = round(pad + tw + 12 + 8 + pad)
        for theme, c in THEMES.items():
            if primary:
                box = f'<rect width="{w}" height="{h}" rx="10" fill="{c["button"]}"/>'
                ink = c["button_text"]
            else:
                box = f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="9.25" fill="{c["fill"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
                ink = c["text"]
            body = (box + f'<text x="{pad}" y="25.5" font-size="{size}" font-weight="600" fill="{ink}">{escape(label)}</text>'
                    + arrow_out(pad + tw + 12, 16.5, ink))
            write(f"buttons/{slug}-{theme}.svg", svg(w, h, label, body, t))


def status_of(r, public, release):
    status, version = r.get("status"), r.get("version")
    if r["name"] in public and release:
        version = release["tag_name"].lstrip("v")
        if status == "building" and any(a["name"].endswith(".dmg") for a in release.get("assets", [])):
            status = "alpha"
    if version and status:
        version = re.sub(rf"-{status}(\.\d+)?$", "", version)
    return status, version


def pill(x_right, y, status, version, c, t):
    """the status pill of ui-web: a cyan wash and a lit led for the live ones, grey for the rest."""
    label = f"{status} {version}" if version else status
    size, h = 12, 24
    tw = t.width(label, size, 600, .6)
    w = 10 + 6 + 7 + tw + 10
    x = x_right - w
    live = status in LIVE
    bg, bo = (c["live_bg"], c["live_bg_o"]) if live else (c["work_bg"], c["work_bg_o"])
    ink = c["live_text"] if live else c["muted"]
    led = CYAN if live else c["led_work"]
    led_o = "1" if live else ".55"
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="6" fill="{bg}" fill-opacity="{bo}"/>'
            f'<circle cx="{x + 13:.1f}" cy="{y + h / 2}" r="3" fill="{led}" fill-opacity="{led_o}"/>'
            f'<text x="{x + 23:.1f}" y="{y + 16.5}" font-size="{size}" font-weight="600" letter-spacing=".6" fill="{ink}">{escape(label)}</text>')


def name_of(r, marks, x, y, height, color, t):
    """a product is its wordmark, never typed; a repository is its name in outfit 700, set as tight."""
    if r.get("product") and r["name"] in marks:
        return mark(marks[r["name"]], x, y, height, color)
    size = height / .86  # outfit 700 ascends to .86 em: the letters stand as tall as the wordmarks
    w = t.width(r["name"], size, 700, -.03 * size)
    return (f'<text x="{x}" y="{y + height:.2f}" font-size="{size:.2f}" font-weight="700" letter-spacing="{-.03 * size:.2f}" '
            f'fill="{color}">{escape(r["name"])}</text>'), w


def link_of(r, public):
    if r["name"] in public:
        return f"https://github.com/{ORG}/{r['name']}", "github"
    return f"{SITE}/{r['product']}s/{r['name']}", "laaabs.com"


def cards(repos, marks, public, releases, t):
    W, H, P = 440, 116, 22
    for old in (OUT / "cards").glob("*.svg"):
        old.unlink()
    cells = {}
    for r in repos:
        slug = r["name"].lstrip(".")
        status, version = status_of(r, public, releases.get(r["name"]))
        href, where = link_of(r, public)
        meta = list(r.get("stack", [])) + ([r["licence"]] if r.get("licence") else [])
        for theme, c in THEMES.items():
            body = f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="{c["fill"]}" stroke="{c["line"]}" stroke-width="1.5"/>'
            name, _ = name_of(r, marks, P, 24, 20, c["text"], t)
            body += name
            if status:
                body += pill(W - P, 22, status, version, c, t)
            what = t.fit(r["what"], 14, W - 2 * P)
            body += f'<text x="{P}" y="76" font-size="14" font-weight="500" fill="{c["muted"]}">{escape(what)}</text>'
            ww = t.width(where, 12, 500)
            right = W - P - 11
            body += f'<text x="{right - 6 - ww:.1f}" y="99" font-size="12" font-weight="500" fill="{c["faint"]}">{where}</text>'
            body += arrow_out(right, 90.5, c["faint"], 6)
            line = t.fit("  /  ".join(meta), 12, right - 6 - ww - P - 16)
            body += f'<text x="{P}" y="99" font-size="12" font-weight="500" fill="{c["faint"]}" xml:space="preserve">{escape(line)}</text>'
            write(f"cards/{slug}-{theme}.svg", svg(W, H, f"{r['name']}: {r['what']}", body, t))
        alt = f"{r['name']}: {r['what']}" + (f", {status}" if status else "")
        cells.setdefault(r["group"], []).append(
            f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="cards/{slug}-dark.svg">'
            f'<img src="cards/{slug}-light.svg" alt="{escape(alt)}" width="49%"></picture></a>')
    return cells


def the_map(repos, marks, public, tap, t):
    """the open pieces, in columns: what each one is built on sits to its left."""
    on_map = [r for r in repos if r.get("map")]
    by = {r["name"]: r for r in on_map}
    columns = ["brand", "kits", "tools", "install"]
    titles = {"brand": "the brand", "kits": "the kits", "tools": "the tools", "install": "install"}
    BW, BH, GX, GY, TOP, LEFT = 200, 48, 76, 14, 112, 2
    col = {c: [r for r in on_map if r["map"] == c] for c in columns}
    tallest = max(len(v) for v in col.values())
    span = tallest * BH + (tallest - 1) * GY
    pos = {}
    for i, c in enumerate(columns):
        members = col[c]
        x = LEFT + i * (BW + GX)
        if c == "install":
            # the tap sits level with the tools it ships
            ys = [pos[n][1] for n in tap if n in pos] or [TOP]
            for r in members:
                pos[r["name"]] = (x, (min(ys) + max(ys)) / 2)
            continue
        h = len(members) * BH + (len(members) - 1) * GY
        top = TOP + (span - h) / 2
        if c == "kits":
            top = TOP + (span - BH) / 2
        for j, r in enumerate(members):
            pos[r["name"]] = (x, top + j * (BH + GY * (3 if c == "kits" else 1)))
    width = LEFT * 2 + len(columns) * BW + (len(columns) - 1) * GX
    height = TOP + span + 86

    edges = []  # (d, dotted)
    for r in on_map:
        uses = list(r.get("uses", []))
        if r.get("casks"):
            uses += [n for n in tap if n in by]
        for dep in uses:
            (ax, ay), (bx, by_) = pos[dep], pos[r["name"]]
            if ax == bx:  # same column: straight down
                edges.append((f"M{ax + BW / 2} {ay + BH}V{by_ - 2}", False))
                continue
            x1, y1, x2, y2 = ax + BW, ay + BH / 2, bx - 2, by_ + BH / 2
            mx = (x1 + x2) / 2
            edges.append((f"M{x1} {y1}C{mx} {y1} {mx} {y2} {x2} {y2}", False))
        for src in r.get("cards", []):
            (ax, ay), (bx, by_) = pos[src], pos[r["name"]]
            x = ax + BW
            bulge = x + 26 + abs(by_ - ay) * .12
            edges.append((f"M{x} {ay + BH / 2}C{bulge} {ay + BH / 2} {bulge} {by_ + BH / 2} {x + 2} {by_ + BH / 2}", True))

    for theme, c in THEMES.items():
        body = (f'<defs><marker id="a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0 0L8 4L0 8z" fill="{c["faint"]}"/></marker></defs>')
        body += f'<text x="{LEFT}" y="44" font-size="26" font-weight="700" letter-spacing="-.78" fill="{c["text"]}">how the open pieces fit</text>'
        body += (f'<text x="{LEFT}" y="72" font-size="15" font-weight="500" fill="{c["muted"]}">'
                 "every tool is built on one design kit, the kit on the brand. redrawn every day from the repositories.</text>")
        for i, cname in enumerate(columns):
            body += (f'<text x="{LEFT + i * (BW + GX)}" y="{TOP - 16}" font-size="13" font-weight="600" letter-spacing="1.3" '
                     f'fill="{c["faint"]}">{titles[cname].upper()}</text>')
        for d, dotted in edges:
            dash = ' stroke-dasharray="2 5" stroke-linecap="round"' if dotted else ""
            body += f'<path d="{d}" fill="none" stroke="{c["faint"]}" stroke-width="1.5"{dash} marker-end="url(#a)"/>'
        for r in on_map:
            x, y = pos[r["name"]]
            dash = '' if r["name"] in public else ' stroke-dasharray="5 4"'
            stroke = c["muted"] if r["name"] in public else c["faint"]
            body += f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="12" fill="{c["fill"]}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
            _, nw = name_of(r, marks, 0, 0, 15, c["text"], t)
            name, _ = name_of(r, marks, x + (BW - nw) / 2, y + (BH - 15) / 2 - 1, 15, c["text"], t)
            body += name
        ly = height - 26
        body += (f'<g font-size="14" font-weight="500" fill="{c["muted"]}">'
                 f'<rect x="{LEFT}" y="{ly - 12}" width="26" height="16" rx="5" fill="none" stroke="{c["muted"]}" stroke-width="1.5"/>'
                 f'<text x="{LEFT + 36}" y="{ly + 1}">public</text>'
                 f'<rect x="{LEFT + 104}" y="{ly - 12}" width="26" height="16" rx="5" fill="none" stroke="{c["faint"]}" stroke-width="1.5" stroke-dasharray="5 4"/>'
                 f'<text x="{LEFT + 140}" y="{ly + 1}">opening soon</text>'
                 f'<path d="M{LEFT + 262} {ly - 4}H{LEFT + 296}" stroke="{c["faint"]}" stroke-width="1.5" marker-end="url(#a)"/>'
                 f'<text x="{LEFT + 308}" y="{ly + 1}">built on, shipped by</text>'
                 f'<path d="M{LEFT + 468} {ly - 4}H{LEFT + 502}" stroke="{c["faint"]}" stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round" marker-end="url(#a)"/>'
                 f'<text x="{LEFT + 514}" y="{ly + 1}">shows its card in</text></g>')
        write(f"map-{theme}.svg", svg(width, height, "the open repositories of laaabs. and how they depend on each other", body, t))


def main():
    spec = yaml.safe_load((ROOT / "repos.yml").read_text())
    repos, skip = spec["repos"], set(spec.get("skip", []))
    declared = {r["name"] for r in repos}
    public = public_repos()

    missing = sorted(public - declared - skip)
    if missing:
        sys.exit(f"public but not in map/repos.yml: {', '.join(missing)}. declare it, or add it to skip.")
    for r in repos:
        if r.get("group") not in dict(GROUPS):
            sys.exit(f"{r['name']}: group must be one of {', '.join(dict(GROUPS))}")
        for dep in r.get("uses", []) + r.get("cards", []):
            if dep not in declared:
                sys.exit(f"{r['name']} uses {dep}, which is not in map/repos.yml.")
        if r["name"] not in public and not r.get("product"):
            sys.exit(f"{r['name']} is not public and not a product: only products may be listed before they are public.")

    marks = wordmarks()
    t = Type()
    releases = {r["name"]: latest_release(r["name"]) for r in repos if r["name"] in public and r.get("product")}
    tap = casks() if "homebrew-tap" in public else []

    header(marks, t)
    buttons(t)
    cells = cards(repos, marks, public, releases, t)
    the_map(repos, marks, public, tap, t)

    blocks = "\n\n".join(f"#### {title}\n\n<p>\n" + "\n".join(cells[g]) + "\n</p>" for g, title in GROUPS if g in cells)
    readme = README.read_text()
    start, end = "<!-- repos:start -->", "<!-- repos:end -->"
    if start not in readme or end not in readme:
        sys.exit("profile/README.md has lost its repos markers")
    before, rest = readme.split(start, 1)
    README.write_text(before + start + "\n" + blocks + "\n" + end + rest.split(end, 1)[1])
    opened = sum(1 for r in repos if r["name"] in public)
    print(f"drew the profile: {len(repos)} cards, {opened} of them public, the map and the buttons")


if __name__ == "__main__":
    main()
