#!/usr/bin/env python3
"""Generates every animated SVG used by the profile README.

    python scripts/build.py

No dependencies. Everything is hand-drawn SVG + CSS/SMIL animation, so the
README needs no third-party image services to render.
"""
import html
import pathlib
import random
import textwrap

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"

# palette -------------------------------------------------------------------
BG, PANEL, LINE = "#0a0d0c", "#0f1412", "#1e2824"
DIM, MID, TEXT = "#5d6d66", "#93a19a", "#e6ede9"
AMBER, GREEN, RED = "#ffb21a", "#35e08a", "#ff5a5f"
BLUE, PURPLE, GREY = "#5ab0ff", "#b08cff", "#6b7a73"

FONT = ("ui-monospace,'SF Mono','Cascadia Mono','JetBrains Mono',Menlo,"
        "Consolas,'Liberation Mono',monospace")
LANG_COLOR = {"Python": AMBER, "TypeScript": BLUE, "Dart": GREEN,
              "JavaScript": PURPLE, "HTML": RED, "Other": GREY}

# bytes of code per language across the public repos (GitHub linguist snapshot)
LANG_BYTES = {"Dart": 859454, "TypeScript": 791046, "Python": 581084,
              "JavaScript": 392700, "HTML": 132493, "Other": 78155}

BASE_CSS = f"""
text{{font-family:{FONT}}}
@keyframes on{{from{{opacity:0}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def esc(s):
    return html.escape(s, quote=True)


def mono(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    """Monospace text with a pinned advance width so layout survives font fallback."""
    w = round(len(s) * size * 0.6, 1)
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" textLength="{w}" lengthAdjust="spacingAndGlyphs" {extra}>'
            f'{esc(s)}</text>')


def tw(s, size):
    return len(s) * size * 0.6


def svg(w, h, body, css="", defs="", label="", pad=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
            f'width="{w + 2 * pad}" height="{h + 2 * pad}" role="img" aria-label="{esc(label)}">'
            f'<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n')


def tri(x, y, s=5, fill=GREEN):
    return f'<path d="M{x},{y - s} l{s},{s * 1.7} h{-2 * s} z" fill="{fill}"/>'


def candles(n, x0, x1, y0, y1, seed, cls="cd", step=0.035, start=0.0, drift=0.9, revert=0.0):
    """A seeded random-walk candlestick series. Decorative, not data."""
    rnd = random.Random(seed)
    p, rows = 100.0, []
    for _ in range(n):
        o = p
        c = o + rnd.gauss(drift, 6) - revert * (o - 100)
        hi, lo = max(o, c) + rnd.random() * 5, min(o, c) - rnd.random() * 5
        rows.append((o, c, hi, lo))
        p = c
    top, bot = max(r[2] for r in rows), min(r[3] for r in rows)

    def Y(v):
        return round(y1 - (v - bot) / (top - bot) * (y1 - y0), 1)

    pitch = (x1 - x0) / n
    bw = max(3, round(pitch * 0.56, 1))
    out = []
    for i, (o, c, hi, lo) in enumerate(rows):
        cx = round(x0 + pitch * (i + 0.5), 1)
        col = GREEN if c >= o else RED
        ya, yb = sorted((Y(o), Y(c)))
        out.append(
            f'<g class="{cls}" style="animation-delay:{start + i * step:.2f}s">'
            f'<line x1="{cx}" x2="{cx}" y1="{Y(hi)}" y2="{Y(lo)}" stroke="{col}" stroke-width="1.4"/>'
            f'<rect x="{cx - bw / 2:.1f}" y="{ya}" width="{bw}" height="{max(2, yb - ya):.1f}" '
            f'fill="{col}" rx="1"/></g>')
    last = (round(x0 + pitch * (n - 0.5), 1), Y(rows[-1][1]))
    return "".join(out), last


# hero ------------------------------------------------------------------------
GLYPH = {
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "H": "10001 10001 10001 11111 10001 10001 10001",
}
PHRASES = [
    "running 20 paper-trading bots on free GitHub Actions compute",
    "training a GPT-style decoder from scratch in PyTorch",
    "measuring how LLMs answer the same question in a different dialect",
    "shipping apps in Flutter, Next.js, Electron and React Native",
    "dictating code with Whisper running on a local GPU",
]


def hero():
    W, H = 1200, 420
    # LED matrix: which (col,row) cells are lit
    lit, col = set(), 0
    for ch in "YUVANSH SHAH":
        if ch == " ":
            col += 3
            continue
        for r, row in enumerate(GLYPH[ch].split()):
            for c, bit in enumerate(row):
                if bit == "1":
                    lit.add((col + c, r))
        col += 6
    cols = col - 1
    pitch, rad = 15, 5.2
    bx = (W - (cols - 1) * pitch) / 2
    by = 92

    off = "".join(
        f'<circle cx="{bx + c * pitch:.1f}" cy="{by + r * pitch}" r="{rad}"/>'
        for c in range(-2, cols + 2) for r in range(-1, 8) if (c, r) not in lit)
    by_col = {}
    for c, r in sorted(lit):
        by_col.setdefault(c, []).append(r)
    on = "".join(
        f'<g class="led" style="animation-delay:{0.25 + c * 0.022:.2f}s">' + "".join(
            f'<circle cx="{bx + c * pitch:.1f}" cy="{by + r * pitch}" r="{rad}"/>' for r in rows)
        + "</g>" for c, rows in by_col.items())
    clip = "".join(f'<circle cx="{bx + c * pitch:.1f}" cy="{by + r * pitch}" r="{rad}"/>'
                   for c, r in sorted(lit))

    # top bar
    bar = (f'<rect x="20" y="13" width="34" height="20" rx="3" fill="{AMBER}"/>'
           + mono(37, 28, "YS", 14, BG, 700, "middle")
           + mono(64, 28, "TERMINAL", 14, TEXT, 700))
    x = 170
    for key, name in (("F1", "ABOUT"), ("F2", "LISTINGS"), ("F3", "RESEARCH"), ("F4", "STACK")):
        bar += mono(x, 28, key, 13, AMBER) + mono(x + 22, 28, name, 13, DIM)
        x += 22 + tw(name, 13) + 26
    bar += (f'<circle class="dot" cx="{W - 150}" cy="23" r="4.5" fill="{GREEN}"/>'
            + mono(W - 24, 28, "SESSION OPEN", 13, GREEN, 700, "end")
            + f'<line x1="0" x2="{W}" y1="46" y2="46" stroke="{LINE}"/>')

    # typed line
    size, cw, tx, ty = 22, 22 * 0.6, 118, 258
    slot = 5.2
    total = slot * len(PHRASES)
    typed, clips = mono(92, ty, ">", size, AMBER, 700), ""
    for i, p in enumerate(PHRASES):
        n = len(p)
        t0, dt = i * slot + 0.3, min(0.04, 2.0 / n)
        kt, wv = [0.0], [0.0]
        for k in range(1, n + 1):
            kt.append((t0 + k * dt) / total)
            wv.append(k * cw)
        kt.append((i * slot + slot - 0.2) / total)
        wv.append(0.0)
        keys = ";".join(f"{t:.5f}" for t in kt)
        anim = (f'dur="{total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{keys}"')
        base = n * cw if i == 0 else 0
        clips += (f'<clipPath id="ty{i}"><rect x="{tx}" y="{ty - 24}" width="{base:.1f}" height="34">'
                  f'<animate attributeName="width" {anim} values="{";".join(f"{v:.1f}" for v in wv)}"/>'
                  f'</rect></clipPath>')
        typed += (f'<g clip-path="url(#ty{i})">{mono(tx, ty, p, size, TEXT)}</g>'
                  f'<rect class="cur" x="{tx + base + 3:.1f}" y="{ty - 19}" width="12" height="24" fill="{AMBER}">'
                  f'<animate attributeName="x" {anim} values="{";".join(f"{tx + v + 3:.1f}" if v else "-99" for v in wv)}"/>'
                  f'</rect>')

    cds, (lx, ly) = candles(62, 40, 1110, 282, 368, seed=11, start=0.9, drift=0.4, revert=0.18)
    chart = (f'<g opacity=".5">{cds}</g>'
             f'<line x1="40" x2="{W - 40}" y1="{ly}" y2="{ly}" stroke="{AMBER}" stroke-width="1" '
             f'stroke-dasharray="3 6" opacity=".45"/>'
             f'<circle class="dot" cx="{lx}" cy="{ly}" r="5" fill="{AMBER}"/>'
             f'<rect x="{W - 78}" y="{ly - 10}" width="44" height="20" rx="3" fill="{AMBER}"/>'
             + mono(W - 56, ly + 4.5, "LAST", 12, BG, 700, "middle"))

    # footer strip
    cells = [("LISTED", "9 public repos"), ("MAIN STACK", "Python / TypeScript / Dart"),
             ("ON GITHUB SINCE", "2024")]
    strip = f'<line x1="0" x2="{W}" y1="382" y2="382" stroke="{LINE}"/>'
    x = 40
    for k, v in cells:
        strip += mono(x, 406, k, 13, DIM) + mono(x + tw(k, 13) + 12, 406, v, 13, TEXT, 700)
        x += tw(k, 13) + tw(v, 13) + 60
    strip += mono(W - 40, 406, "github.com/Yuvansh-Shah", 13, AMBER, 400, "end")

    css = f"""
.led{{animation:on .45s both}}
.cd{{animation:on .35s both}}
.dot{{animation:pulse 1.8s ease-in-out infinite}}
.cur{{animation:blink 1s steps(1) infinite}}
.sweep{{animation:sweep 6.5s ease-in-out 2.4s infinite}}
@keyframes sweep{{0%{{transform:translateX(-260px)}}38%,100%{{transform:translateX({W + 60}px)}}}}
"""
    defs = (f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
            f'<clipPath id="lit">{clip}</clipPath>'
            f'<filter id="glow" x="-10%" y="-60%" width="120%" height="220%">'
            f'<feGaussianBlur stdDeviation="5"/></filter>'
            f'<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".9"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r="1" fill="{LINE}"/></pattern>' + clips)
    body = (f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<rect y="46" width="{W}" height="336" fill="url(#grid)" opacity=".7"/>'
            f'{bar}'
            f'<g fill="#151b18">{off}</g>'
            f'<g fill="{AMBER}" filter="url(#glow)" opacity=".75">{on}</g>'
            f'<g fill="{AMBER}">{on}</g>'
            f'<g clip-path="url(#lit)"><rect class="sweep" x="0" y="{by - 12}" width="200" height="120" '
            f'fill="url(#sh)" style="transform:translateX(-260px)"/></g>'
            f'{typed}{chart}{strip}</g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{LINE}"/>')
    return svg(W, H, body, css, defs, "Yuvansh Shah. " + ". ".join(PHRASES))


# ticker ------------------------------------------------------------------------
TAPE = [("ALGO", "20 paper bots"), ("DBLM", "936 API calls"), ("RPLM", "GPT from scratch"),
        ("JQST", "Flutter + Firebase"), ("JQWB", "Next.js + Workers"), ("FLOW", "Whisper on GPU"),
        ("SATF", "adaptive mocks"), ("TTRB", "robot drills"), ("EYEC", "AI front desk")]


def ticker():
    W, H, size = 1200, 46, 15
    x, row = 0, ""
    for sym, note in TAPE:
        row += mono(x, 29, sym, size, AMBER, 700)
        x += tw(sym, size) + 12
        row += tri(x, 23.5, 5)
        x += 14
        row += mono(x, 29, note, size, TEXT)
        x += tw(note, size) + 22
        row += f'<rect x="{x:.1f}" y="21" width="5" height="5" fill="{DIM}"/>'
        x += 27
    L = round(x, 1)
    css = (f".tape{{animation:roll {L / 55:.1f}s linear infinite}}"
           f"@keyframes roll{{to{{transform:translateX(-{L}px)}}}}")
    defs = (f'<clipPath id="r"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
            f'<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{PANEL}"/>'
            f'<stop offset="1" stop-color="{PANEL}" stop-opacity="0"/></linearGradient>')
    body = (f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="{PANEL}"/>'
            f'<g class="tape"><g>{row}</g><g transform="translate({L})">{row}</g>'
            f'<g transform="translate({2 * L})">{row}</g></g>'
            f'<rect width="70" height="{H}" fill="url(#f)"/>'
            f'<rect x="{W - 70}" width="70" height="{H}" fill="url(#f)" '
            f'transform="rotate(180 {W - 35} {H / 2})"/></g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{LINE}"/>')
    return svg(W, H, body, css, defs, "Project ticker: " + ", ".join(f"{s} {n}" for s, n in TAPE))


# small pieces --------------------------------------------------------------------
def divider(label, note):
    W, H = 1200, 34
    lw = tw(label, 14)
    nw = tw(note, 13)
    body = (f'<rect x="2" y="12" width="9" height="9" fill="{AMBER}"/>'
            + mono(22, 22, label, 14, AMBER, 700)
            + f'<line x1="{34 + lw}" x2="{W - nw - 14}" y1="17" y2="17" stroke="{GREY}" '
              f'stroke-width="1" stroke-dasharray="2 5"/>'
            + mono(W - 2, 22, note, 13, GREY, 400, "end"))
    return svg(W, H, body, label=f"{label}: {note}")


def chips(x, y, tags, size=12):
    out = ""
    for t in tags:
        w = tw(t, size) + 20
        out += (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="23" rx="11.5" fill="none" stroke="{LINE}"/>'
                + mono(x + 10, y + 15.5, t, size, MID))
        x += w + 8
    return out


# card motifs: each draws inside a 152 x 120 box ------------------------------------
def m_dialect():
    def block(y, label, widths, col, cls):
        s = mono(0, y, label, 11, DIM)
        for i, w in enumerate(widths):
            s += (f'<rect class="{cls}" style="animation-delay:{i * 0.18:.2f}s" x="0" y="{y + 9 + i * 11}" '
                  f'width="{w}" height="6" rx="3" fill="{col}"/>')
        return s
    css = (".ba,.bb{transform-box:fill-box;transform-origin:left;animation:grow 6s ease-out infinite}"
           ".bb{animation-name:grow2}"
           "@keyframes grow{0%{transform:scaleX(0)}14%,88%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
           "@keyframes grow2{0%,22%{transform:scaleX(0)}36%,88%{transform:scaleX(1)}100%{transform:scaleX(0)}}")
    return (block(12, "STANDARD", [150, 132, 144, 96], AMBER, "ba")
            + block(76, "DIALECT", [150, 70], RED, "bb")), css


def m_gpt():
    s = ""
    xs = [i * 26 for i in range(6)]
    for i, x in enumerate(xs):
        last = i == 5
        s += (f'<rect class="tk" style="animation-delay:{i * 0.45:.2f}s" x="{x}" y="88" width="21" height="17" '
              f'rx="3" fill="{AMBER if last else "none"}" stroke="{AMBER if last else MID}" stroke-width="1.3"/>')
    for i, x in enumerate(xs[:5]):
        h = 20 + (5 - i) * 13
        s += (f'<path class="arc" style="animation-delay:{2.5 + (4 - i) * 0.12:.2f}s" pathLength="1" '
              f'd="M{xs[5] + 10.5},86 Q{(xs[5] + x) / 2 + 10.5},{86 - h} {x + 10.5},86" fill="none" '
              f'stroke="{AMBER}" stroke-width="1.3" opacity="{0.3 + i * 0.15:.2f}"/>')
    css = (".tk{animation:tk 6s steps(1) infinite both}"
           "@keyframes tk{0%{opacity:0}5%,100%{opacity:1}}"
           ".arc{stroke-dasharray:1;animation:arc 6s ease-out infinite both}"
           "@keyframes arc{0%{stroke-dashoffset:1}12%,100%{stroke-dashoffset:0}}")
    return s, css


def m_path():
    pts = [(14, 104), (46, 70), (80, 96), (112, 50), (138, 18)]
    s = (f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{LINE}" '
         f'stroke-width="3" stroke-dasharray="1 7" stroke-linecap="round"/>')
    for i, (x, y) in enumerate(pts):
        col = AMBER if i == 4 else GREEN
        s += (f'<circle cx="{x}" cy="{y}" r="10" fill="{PANEL}" stroke="{col}" stroke-width="1.6"/>'
              f'<circle class="nd" style="animation-delay:{i * 0.7:.1f}s" cx="{x}" cy="{y}" r="6" fill="{col}"/>')
    css = (".nd{transform-box:fill-box;transform-origin:center;animation:nd 7s ease-out infinite both}"
           "@keyframes nd{0%{transform:scale(0)}6%{transform:scale(1.35)}10%,100%{transform:scale(1)}}")
    return s, css


def m_chat():
    s = (f'<rect x=".7" y="6.7" width="150.6" height="108" rx="7" fill="none" stroke="{LINE}" stroke-width="1.4"/>'
         f'<line x1="1" x2="151" y1="25" y2="25" stroke="{LINE}" stroke-width="1.4"/>'
         + "".join(f'<circle cx="{13 + i * 11}" cy="16" r="3" fill="{c}"/>'
                   for i, c in enumerate((RED, AMBER, GREEN))))
    rows = [(12, 36, 82, MID), (74, 58, 66, AMBER), (12, 80, 104, MID)]
    for i, (x, y, w, col) in enumerate(rows):
        s += (f'<rect class="bub" style="animation-delay:{0.4 + i * 1.1:.1f}s" x="{x}" y="{y}" width="{w}" '
              f'height="15" rx="7.5" fill="{col}" opacity="{.9 if col == AMBER else .45}"/>')
    css = (".bub{transform-box:fill-box;transform-origin:left center;animation:bub 6s ease-out infinite both}"
           "@keyframes bub{0%{transform:scale(0)}6%,100%{transform:scale(1)}}")
    return s, css


def m_eye():
    s = (f'<g class="lid"><path d="M6,60 Q76,-4 146,60 Q76,124 6,60 Z" fill="none" stroke="{AMBER}" '
         f'stroke-width="1.8"/><g class="iris"><circle cx="76" cy="60" r="24" fill="none" stroke="{TEXT}" '
         f'stroke-width="1.5"/><circle cx="76" cy="60" r="10" fill="{AMBER}"/>'
         f'<circle cx="80" cy="56" r="3" fill="{TEXT}"/></g></g>')
    css = (".lid{transform-box:fill-box;transform-origin:center;animation:lid 5s ease-in-out infinite}"
           "@keyframes lid{0%,44%,52%,100%{transform:scaleY(1)}48%{transform:scaleY(.06)}}"
           ".iris{animation:look 5s ease-in-out infinite}"
           "@keyframes look{0%,100%{transform:translateX(0)}20%{transform:translateX(-13px)}"
           "70%{transform:translateX(13px)}}")
    return s, css


def m_pong():
    s = (f'<line x1="4" x2="148" y1="98" y2="98" stroke="{TEXT}" stroke-width="2" stroke-linecap="round"/>'
         f'<line x1="76" x2="76" y1="98" y2="82" stroke="{MID}" stroke-width="2"/>'
         f'<line x1="30" x2="22" y1="98" y2="116" stroke="{LINE}" stroke-width="2"/>'
         f'<line x1="122" x2="130" y1="98" y2="116" stroke="{LINE}" stroke-width="2"/>'
         f'<rect x="0" y="44" width="15" height="20" rx="3" fill="none" stroke="{AMBER}" stroke-width="1.6"/>'
         f'<circle cx="7.5" cy="54" r="2.5" fill="{AMBER}"/>'
         f'<g class="bat"><ellipse cx="143" cy="48" rx="5" ry="10" fill="{RED}"/>'
         f'<line x1="143" x2="143" y1="58" y2="68" stroke="{MID}" stroke-width="2.4"/></g>'
         f'<circle r="4.5" fill="{TEXT}"><animateMotion dur="2.6s" repeatCount="indefinite" '
         f'path="M17,52 Q72,-6 112,93 Q128,44 138,50 Q92,-4 42,93 Q28,48 17,52"/></circle>')
    css = (".bat{transform-box:fill-box;transform-origin:bottom;animation:bat 2.6s ease-in-out infinite}"
           "@keyframes bat{0%,30%,60%,100%{transform:rotate(0)}45%{transform:rotate(-22deg)}}")
    return s, css


def m_wave():
    hs = [14, 30, 46, 22, 38, 52, 26, 40, 18, 34, 12]
    s = "".join(
        f'<rect class="wv" style="animation-delay:-{i * 0.13:.2f}s" x="{4 + i * 13.4:.1f}" y="{36 - h / 2}" '
        f'width="6" height="{h}" rx="3" fill="{AMBER}"/>' for i, h in enumerate(hs))
    s += (f'<path d="M76,70 v12 m-5,-5 l5,5 l5,-5" fill="none" stroke="{DIM}" stroke-width="1.6" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    x = 4
    for i, w in enumerate((34, 22, 42, 26)):
        s += (f'<rect class="wd" style="animation-delay:{0.6 + i * 0.7:.1f}s" x="{x}" y="98" width="{w}" '
              f'height="9" rx="2" fill="{TEXT}"/>')
        x += w + 7
    css = (".wv{transform-box:fill-box;transform-origin:center;animation:wv 1.1s ease-in-out infinite alternate}"
           "@keyframes wv{from{transform:scaleY(.25)}to{transform:scaleY(1)}}"
           ".wd{animation:wd 5s steps(1) infinite both}@keyframes wd{0%{opacity:0}4%,100%{opacity:1}}")
    return s, css


def m_sheet():
    s, picks = "", [1, 3, 0, 2]
    for r in range(4):
        y = 16 + r * 29
        s += mono(2, y + 4.5, str(r + 1), 12, DIM)
        for c in range(4):
            x = 38 + c * 31
            s += f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{MID}" stroke-width="1.3"/>'
            if c == picks[r]:
                s += (f'<circle class="pk" style="animation-delay:{0.5 + r * 0.9:.1f}s" cx="{x}" cy="{y}" '
                      f'r="6" fill="{AMBER}"/>')
    css = (".pk{transform-box:fill-box;transform-origin:center;animation:pk 6.5s ease-out infinite both}"
           "@keyframes pk{0%{transform:scale(0)}5%{transform:scale(1.3)}8%,100%{transform:scale(1)}}")
    return s, css


CARDS = [
    ("dialect", "DBLM", "dialect-bias-llm", "Python", m_dialect,
     "52 questions asked twice, in Standard American English and in dialect, to 3 LLMs. "
     "Same meaning, shorter answers.", ["research", "llm-eval", "scipy"]),
    ("gpt", "RPLM", "research-paper-llm", "Python", m_gpt,
     "A GPT-style decoder built from scratch in PyTorch, trained on DBLP + arXiv paper metadata.",
     ["pytorch", "transformer", "from-scratch"]),
    ("jainquest", "JQST", "JainQuest", "Dart", m_path,
     "Mobile app for learning Jain philosophy through gamified lessons.",
     ["flutter", "firebase", "gemini"]),
    ("jainquest-web", "JQWB", "jainquest-web", "TypeScript", m_chat,
     "The web edition. Next.js and Firebase, with AI chat served through a Cloudflare Worker.",
     ["nextjs", "firebase", "workers"]),
    ("flowlite", "FLOW", "flowlite", "Python", m_wave,
     "Local Windows dictation. Whisper on the GPU, then a local LLM cleans up the transcript.",
     ["whisper", "ollama", "pyqt6"]),
    ("satforge", "SATF", "satforge", "TypeScript", m_sheet,
     "Offline Digital SAT trainer with adaptive and full-length mock exams.",
     ["electron", "react", "vite"]),
    ("tt-robot", "TTRB", "tt-robot-app", "TypeScript", m_pong,
     "Control app for a table-tennis training robot: drills, live sessions, stats.",
     ["expo", "react-native", "bluetooth"]),
    ("eye-care", "EYEC", "sadhana-eye-care", "TypeScript", m_eye,
     "Eye-clinic site with an AI assistant that answers questions and books appointments.",
     ["nextjs", "llm", "netlify"]),
]


def card(sym, name, lang, motif, desc, tags):
    W, H = 600, 236
    lines = textwrap.wrap(desc, 42)
    assert len(lines) <= 3, (name, lines)
    art, css = motif()
    lw = tw(lang, 13)
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
            + mono(28, 48, sym, 27, AMBER, 700) + tri(28 + tw(sym, 27) + 14, 37, 6)
            + f'<circle cx="{W - 34 - lw}" cy="38.5" r="4.5" fill="{LANG_COLOR[lang]}"/>'
            + mono(W - 26, 43, lang, 13, MID, 400, "end")
            + mono(28, 78, name, 17, TEXT, 700)
            + "".join(mono(28, 107 + i * 21, ln, 14.5, MID) for i, ln in enumerate(lines))
            + chips(28, 188, tags)
            + f'<g transform="translate(424 58)">{art}</g>')
    return svg(W, H, body, css, label=f"{name}: {desc}", pad=6)


BOTS = ["orb_breakout", "vwap_pullback", "vwap_reversion", "ema_crossover", "supertrend_intraday",
        "bb_squeeze", "macd_adx", "gap_and_go", "tv_rating_scalper", "rsi2_scalper", "connors_rsi2",
        "donchian_turtle", "ema_trend_swing", "bb_reversion_daily", "hourly_macd_swing",
        "tv_rating_swing", "momentum_rotation", "nifty_buy_hold", "crypto_supertrend",
        "external_signals"]


def feature():
    W, H = 1200, 268
    desc = ("An arena of 20 paper-trading bots on NSE. A cron ping wakes GitHub Actions every "
            "5 minutes in market hours, the engine runs every strategy, and the leaderboard "
            "commits itself back to the repo. The laptop can stay off.")
    lines = textwrap.wrap(desc, 57)
    assert len(lines) <= 4, lines
    cds, (lx, ly) = candles(30, 620, 930, 60, 214, seed=5, cls="fc", step=0.16, drift=1.6)
    rowh = 23
    lst = "".join(
        f'<rect x="970" y="{i * rowh + 5}" width="6" height="6" fill="{GREEN if i % 4 else AMBER}"/>'
        + mono(986, i * rowh + 13, b, 13, MID) for i, b in enumerate(BOTS))
    Lh = rowh * len(BOTS)
    css = (f".fc{{animation:fc 9s ease-out infinite both}}"
           f"@keyframes fc{{0%{{opacity:0}}3%,94%{{opacity:1}}100%{{opacity:0}}}}"
           f".roll{{animation:up 26s linear infinite}}@keyframes up{{to{{transform:translateY(-{Lh}px)}}}}"
           f".dot{{animation:pulse 1.8s ease-in-out infinite}}")
    defs = (f'<clipPath id="bots"><rect x="960" y="62" width="216" height="158"/></clipPath>'
            f'<linearGradient id="fd" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{PANEL}"/>'
            f'<stop offset=".18" stop-color="{PANEL}" stop-opacity="0"/>'
            f'<stop offset=".82" stop-color="{PANEL}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{PANEL}"/></linearGradient>')
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
            + mono(36, 60, "ALGO", 34, AMBER, 700) + tri(36 + tw("ALGO", 34) + 16, 46, 7)
            + mono(36 + tw("ALGO", 34) + 40, 58, "FEATURED LISTING", 12, DIM)
            + mono(36, 94, "algo-trading-platform", 19, TEXT, 700)
            + "".join(mono(36, 126 + i * 23, ln, 15.5, MID) for i, ln in enumerate(lines))
            + chips(36, 222, ["python", "github-actions", "paper-trading", "backtests"], 12.5)
            + f'<line x1="600" x2="600" y1="28" y2="{H - 28}" stroke="{LINE}"/>'
            + mono(620, 44, "NSE / 15m", 12, DIM)
            + cds
            + f'<circle class="dot" cx="{lx}" cy="{ly}" r="4" fill="{AMBER}"/>'
            + f'<line x1="946" x2="946" y1="28" y2="{H - 28}" stroke="{LINE}"/>'
            + mono(970, 44, "20 BOTS IN THE ARENA", 12, DIM)
            + f'<g clip-path="url(#bots)"><g transform="translate(0 62)"><g class="roll">{lst}'
              f'<g transform="translate(0 {Lh})">{lst}</g></g></g>'
              f'<rect x="960" y="62" width="216" height="158" fill="url(#fd)"/></g>'
            + f'<circle cx="{W - 34 - tw("Python", 13)}" cy="{H - 30.5}" r="4.5" fill="{AMBER}"/>'
            + mono(W - 26, H - 26, "Python", 13, MID, 400, "end"))
    return svg(W, H, body, css, defs, "algo-trading-platform: " + desc)


def allocation():
    W, H = 1200, 118
    total = sum(LANG_BYTES.values())
    x0, x1, gap = 2, W - 2, 4
    span = x1 - x0 - gap * (len(LANG_BYTES) - 1)
    x, bar, leg, lx = x0, "", "", 2
    for i, (lang, n) in enumerate(LANG_BYTES.items()):
        w = span * n / total
        col = LANG_COLOR[lang]
        bar += (f'<rect class="seg" style="animation-delay:{i * 0.12:.2f}s" x="{x:.1f}" y="14" '
                f'width="{w:.1f}" height="26" rx="4" fill="{col}"/>')
        x += w + gap
        pct = f"{100 * n / total:.1f}%"
        leg += (f'<rect x="{lx}" y="68" width="11" height="11" rx="2" fill="{col}"/>'
                + mono(lx + 20, 79, lang, 14.5, TEXT, 700)
                + mono(lx + 20, 100, pct, 13.5, MID))
        lx += (W - 4) / len(LANG_BYTES)
    css = (".seg{transform-box:fill-box;transform-origin:left;animation:seg 1s cubic-bezier(.2,.8,.2,1) both}"
           "@keyframes seg{from{transform:scaleX(0)}}")
    return svg(W, H, bar + leg, css, label="Language allocation: " + ", ".join(
        f"{k} {100 * v / total:.1f}%" for k, v in LANG_BYTES.items()))


def footer():
    W, H = 1200, 64
    d = ("M0,34 H430 l10,-6 l10,12 l10,-22 l12,30 l10,-18 l8,4 H740 l10,-8 l10,14 l10,-20 "
         "l12,24 l10,-12 l8,2 H1200")
    css = (".tr{stroke-dasharray:1;animation:tr 7s linear infinite}"
           "@keyframes tr{0%{stroke-dashoffset:1}70%,100%{stroke-dashoffset:0}}")
    body = (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
            f'<path class="tr" pathLength="1" d="{d}" fill="none" stroke="{AMBER}" stroke-width="1.5"/>'
            f'<rect x="{W / 2 - 78}" y="22" width="156" height="24" rx="12" fill="{BG}" stroke="{LINE}"/>'
            + mono(W / 2, 39, "END OF TAPE", 13, AMBER, 700, "middle"))
    return svg(W, H, body, css, label="End of tape")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "hero.svg": hero(), "ticker.svg": ticker(), "footer.svg": footer(),
        "div-listings.svg": divider("LISTINGS", "9 SYMBOLS / CLICK TO OPEN"),
        "div-allocation.svg": divider("ALLOCATION", "BYTES OF CODE / PUBLIC REPOS"),
        "card-algo.svg": feature(), "allocation.svg": allocation(),
    }
    for slug, sym, name, lang, motif, desc, tags in CARDS:
        files[f"card-{slug}.svg"] = card(sym, name, lang, motif, desc, tags)
    for name, data in files.items():
        (OUT / name).write_text(data, encoding="utf-8", newline="\n")
        print(f"{name:24} {len(data) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
