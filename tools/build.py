# Builds the ledei/ledei GitHub profile README from profile.json.
# Every section is a card image (HTML in an SVG foreignObject, fonts and portrait embedded) so the
# design survives GitHub stripping CSS; each card is wrapped in a real link.
#
#   python3 tools/build.py        then commit README.md, assets/ and profile.json
#
# Needs Google Chrome (to measure each card's height). Set CHROME=/path/to/chrome if it lives elsewhere.
import base64, html, json, os, re, subprocess, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
OUT = os.path.join(TOOLS, '.out')  # previews and the canvas artboard, not committed
sys.path.insert(0, TOOLS)
import sprites as sp

P = json.load(open(os.path.join(REPO, 'profile.json')))
JOB = P.get('job')  # set "job": null when between jobs; the job card and job mentions drop out
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(REPO, 'assets'), exist_ok=True)

W = 880
GAP = 4  # cards share one paragraph on GitHub, so only the <br> line gap is left
BG, PANEL, PANEL2, BORDER, SHADOW = '#1F1D2B', '#2A2840', '#3A3557', '#0F0E17', '#121119'
CREAM, MUTED, PINK, PEACH, LAV, TEAL = '#F1E9DA', '#B8B0C8', '#E8A0BF', '#F4B183', '#A49AD9', '#7FB8B0'
e = html.escape
EMAIL = P['links']['email']
MAILTO, LINKEDIN = f'mailto:{EMAIL}', P['links']['linkedin']
PROFILE = f"https://github.com/{P['links']['github']}"
REPOS = f'{PROFILE}?tab=repositories'

# lofi recolour of the sprites
remap = {sp.INK: CREAM, sp.CLAY: PINK, sp.BUTTER: PEACH, sp.TEAL: TEAL, sp.SAGE: LAV,
         sp.WOOD: '#8B84B5', '#E9B8A4': PEACH, '#D9C9A0': BG}
for k, (rows, cols) in list(sp.S.items()):
    sp.S[k] = (rows, {c: remap.get(v, v) for c, v in cols.items()})
sp.S['f1dark'] = (sp.S['f1'][0], dict(sp.S['f1'][1], k=BG, o=BG, b=PANEL, y=PINK, g=PEACH))

def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
FONT_FILES = {'Pixelify Sans': 'pixelify.woff2', 'Silkscreen': 'silkscreen.woff2', 'VT323': 'vt323.woff2'}
portrait = b64(os.path.join(REPO, 'assets', 'portrait.png'))

def box(fill, shadow=True):
    s = f'background:{fill};box-shadow:0 -4px 0 0 {BORDER},0 4px 0 0 {BORDER},-4px 0 0 0 {BORDER},4px 0 0 0 {BORDER}'
    return s + (f',8px 10px 0 0 {SHADOW};' if shadow else ';')
LABEL = "font-family:'Silkscreen',monospace;font-size:13px;"
H2 = 'margin:0;font-size:40px;font-weight:700;'
FONT = f"color:{CREAM};font-family:'Pixelify Sans',monospace;"

def sv(name, scale):
    return sp.svg(name, scale).replace('></rect>', '/>').replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)

def stars():
    pts = [(40, 30, PEACH), (180, 70, CREAM), (330, 24, LAV), (610, 40, CREAM), (760, 90, PINK), (520, 110, LAV), (820, 160, CREAM)]
    return ''.join(f'<div class="tw" style="position:absolute;left:{x}px;top:{y}px;width:4px;height:4px;background:{c};animation-delay:{i * 0.37:.2f}s;animation-duration:{1.8 + (i % 3) * 0.7:.1f}s"></div>' for i, (x, y, c) in enumerate(pts))

def moon():
    rows = ["..mmm.", ".mm...", "mm....", "mm....", "mm....", ".mm...", "..mmm."]
    r = ''.join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{PEACH}"/>' for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == 'm')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="42" viewBox="0 0 6 7" shape-rendering="crispEdges" style="position:absolute;right:32px;top:28px">{r}</svg>'

def press(label, color):
    return f'<div style="{LABEL}color:{color};display:flex;align-items:center;gap:8px;white-space:nowrap">{label}<span style="display:inline-block;width:0;height:0;border-top:6px solid transparent;border-bottom:6px solid transparent;border-left:8px solid {color}"></span></div>'

# effects: plain CSS animations inside the SVG, which GitHub plays in <img>.
# Content is visible by default; animations only hide it briefly, so a frozen frame still shows everything.
INTRO = P['intro'].replace('{at_job}', f" at {JOB['company']}" if JOB else '')
TYPE_START, TYPE_STEP = 0.6, 0.035
TYPE_END = TYPE_START + len(INTRO) * TYPE_STEP
def typed(text):
    return ''.join(f'<span class="ty" style="animation-duration:{TYPE_START + i * TYPE_STEP:.3f}s">{e(ch)}</span>' for i, ch in enumerate(text))
EFFECTS = f'''
@keyframes tw{{0%,100%{{opacity:.9}}50%{{opacity:.12}}}}
.tw{{animation:tw 2.4s steps(2) infinite}}
@keyframes hide{{from,to{{opacity:0}}}}
.ty{{animation:hide 1s steps(1)}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.cur{{animation:blink 1s steps(1) infinite}}
.car{{animation:hide {TYPE_END:.2f}s steps(1),blink 1s steps(1) {TYPE_END:.2f}s infinite}}
@keyframes ride{{0%{{transform:translateX(0)}}50%{{transform:translateX(32px)}}100%{{transform:translateX(0)}}}}
@keyframes hop{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
.bmx{{display:inline-block;animation:ride 3s steps(8) infinite}}
.bmx>span{{display:inline-block;animation:hop .5s steps(1) infinite}}
@keyframes row{{from{{opacity:0;transform:translateX(-12px)}}}}
.row{{animation:row .45s steps(3) backwards}}
@keyframes drive{{0%{{transform:translateX(-120px)}}65%,100%{{transform:translateX(900px)}}}}
.drive{{position:absolute;left:0;bottom:8px;animation:drive 5s steps(70) infinite}}
@media (prefers-reduced-motion: reduce){{
.tw,.cur,.bmx,.bmx>span,.ty,.row,.car{{animation:none}}
.drive{{animation:none;transform:translateX(700px)}}
}}'''

def render_rows(lines, reveal=False):
    # reveal: lines appear one after another, like a terminal printing
    rows = []
    for n, line in enumerate(lines, 1):
        toks = ''.join(f'<span class="cur" style="display:inline-block;width:11px;height:20px;margin-left:4px;vertical-align:-3px;background:{PINK}"></span>' if t is None
                       else f'<span style="color:{col}">{e(t)}</span>' for t, col in line)
        style = 'display:flex;white-space:pre'
        rows.append(f'<div class="row" style="animation-delay:{0.4 + n * 0.32:.2f}s;{style}">{toks}</div>' if reveal else f'<div style="{style}">{toks}</div>')
    return ''.join(rows)

def window(title, body_html):
    return (f'<div style="{box(PANEL, False)}"><div style="display:flex;align-items:center;gap:10px;padding:10px 16px;background:{PANEL2}">'
            f'<div style="width:12px;height:12px;background:{PINK}"></div><div style="width:12px;height:12px;background:{PEACH}"></div><div style="width:12px;height:12px;background:{TEAL}"></div>'
            f'<div style="{LABEL}color:{MUTED};margin-left:10px">{e(title)}</div></div>'
            f'<div style="padding:16px 20px 18px;font-family:\'VT323\',monospace;font-size:25px;line-height:1.3">{body_html}</div></div>')

# About: a terminal session built from profile.json
def terminal():
    prompt = [(f"{P['handle']}@profile", TEAL), (':', MUTED), ('~', LAV), ('$ ', MUTED)]
    pad = max(len(k) for k in P['stack']) + 2
    lines = [[*prompt, ('whoami', CREAM)], [(f"{P['name']} · {P['role'].lower()}", PEACH)], [*prompt, ('cat stack.txt', CREAM)]]
    lines += [[(k.ljust(pad), LAV), (', '.join(v), CREAM)] for k, v in P['stack'].items()]
    lines += [[*prompt, (None, CREAM)]]
    return window(f"{P['handle']}@profile: ~", render_rows(lines, reveal=True))

PORTRAIT_IMG = f'<img src="data:image/png;base64,{portrait}" width="256" height="256" style="display:block;image-rendering:pixelated"/>'
stats = [('Class', P['role']), ('Guild', f"{JOB['company']}, since {JOB['since']}" if JOB else 'Open to new quests'),
         ('Home', P['home']), ('Languages', P['languages'])]
stack_flat = ', '.join(x for v in P['stack'].values() for x in v)

def quest_row(i, q):
    color = PEACH if q.get('current') else TEAL if q.get('tag') else LAV
    right = press('Visit', PEACH) if q.get('url') else (f'<div style="{LABEL}color:{color};white-space:nowrap">★ {e(q["tag"])}</div>' if q.get('tag') else '<div></div>')
    return f'''
<div class="row" style="animation-delay:{0.3 + i * 0.25:.2f}s;display:grid;grid-template-columns:196px 170px 1fr auto;align-items:center;gap:16px">
  <div style="display:flex;align-items:center;gap:10px;white-space:nowrap;{LABEL}font-size:12px;color:{MUTED}"><div style="width:12px;height:12px;background:{color};box-shadow:0 0 0 3px {BORDER}"></div>{e(q['when'])}</div>
  <div style="font-size:20px;font-weight:700;white-space:nowrap">{e(q['where'])}</div>
  <div style="font-size:16px;color:{MUTED};white-space:nowrap">{e(q['what'])}</div>
  {right}
</div>'''

# (key, alt text, link or None, fill, padding, inner html)
CARDS = [
('hero', f"{P['name']}, {P['role'].lower()}{' at ' + JOB['company'] if JOB else ''} in {P['home']}. {INTRO}", None, BG, '40px 32px 32px', f'''
{stars()}{moon()}
<div style="display:flex;flex-direction:column;gap:36px">
<div style="display:flex;align-items:center;gap:36px">
  <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:22px">
    <div style="display:flex;align-items:center;gap:12px;{LABEL}font-size:15px;color:{PINK}">{sv('game', 3)}Player 1 has entered<span class="cur" style="display:inline-block;width:8px;height:14px;background:{PINK}"></span></div>
    <div style="font-size:92px;line-height:.95;font-weight:700;text-shadow:5px 5px 0 #3D3A5C">{'<br/>'.join(e(w) for w in P['name'].split(' ', 1))}</div>
    <div style="position:relative;padding:20px 24px 30px;{box(PANEL)}">
      <div style="font-size:21px;line-height:1.4">{typed(INTRO)}</div>
      <div class="car" style="position:absolute;right:18px;bottom:10px;width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-top:10px solid {PINK}"></div>
    </div>
  </div>
  <div style="width:276px;flex:none;display:flex;flex-direction:column;gap:18px">
    <div style="padding:10px;{box(LAV)}">{PORTRAIT_IMG}</div>
    <div style="{LABEL}color:{MUTED};text-align:center">{e(P['first_name'])} · {e(P['home'].split(',')[0])}</div>
  </div>
</div>
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px">
  {''.join(f'<div style="padding:16px;{box(PANEL, False)}display:flex;flex-direction:column;gap:8px"><div style="{LABEL}font-size:12px;color:{PINK}">{a}</div><div style="font-size:18px;font-weight:500;line-height:1.3">{e(b)}</div></div>' for a, b in stats)}
</div>
</div>'''),
('about', f"About, as a terminal: whoami prints {P['name']}, {P['role'].lower()}. Stack: {stack_flat}.", None, BG, '32px', f'''
<div style="display:flex;flex-direction:column;gap:22px">
  <div style="{H2}display:flex;align-items:flex-end;gap:16px">About{sv('code', 4)}</div>
  {terminal()}
</div>'''),
*([('quest', f"Current quest: {JOB['title'].lower()} at {JOB['company']}, {JOB['period']}", JOB.get('url'), PANEL2, '32px', f'''
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px">
  <div style="display:flex;flex-direction:column;gap:14px"><div style="{LABEL}color:{PEACH}">Current quest · {e(JOB['period'])}</div><div style="font-size:38px;line-height:1.05;font-weight:700">{e(JOB['title'])} at {e(JOB['company'])}</div></div>
  <div style="display:flex;flex-direction:column;gap:14px;font-size:19px;line-height:1.5">{''.join(f'<div>{e(t)}</div>' for t in JOB['text'])}</div>
</div>''')] if JOB else []),
('log', 'Quest log', None, BG, '28px 32px', f'''
<div style="{H2}display:flex;align-items:flex-end;gap:16px">Quest log<span class="bmx"><span>{sv('bmx', 4)}</span></span></div>'''),
# one save-slot card per quest, so any row can be a link (give it a "url" in profile.json)
*[(f'q{i}', f"{q['where']}, {q['when']}: {q['what']}", q.get('url'), PANEL, '18px 24px', quest_row(i, q)) for i, q in enumerate(P['quest_log'])],
('talk', f"Let's talk: email {EMAIL}", MAILTO, PEACH, '36px 32px', f'''
<div style="color:{BG};display:flex;flex-direction:column;gap:18px">
  <div style="font-size:64px;line-height:1;font-weight:700">Let's talk</div>
  <div style="font-size:20px;line-height:1.5">Questions, ideas or just want to say hej? My inbox is open.</div>
  <div style="display:flex;justify-content:space-between;align-items:center;gap:16px"><div style="{LABEL}font-size:15px">{e(EMAIL)}</div>{press('Press to email', BG)}</div>
  <div style="position:relative;height:44px;margin:4px -32px -36px;overflow:hidden;border-top:4px dotted rgba(31,29,43,.35)"><span class="drive">{sv('f1dark', 4)}</span></div>
</div>'''),
]

# top buttons, each its own linked image
BTNS = [('repos', 'Repos', CREAM, REPOS), ('linkedin', 'LinkedIn', LAV, LINKEDIN), ('hej', 'Say hej', PEACH, MAILTO)]
BW, BH = 212, 72  # README shows each at 24% width so all three fit one row on a phone

def card_div(key, fill, pad, inner, tag='div', href=None):
    h = f' href="{href}"' if href else ''
    return (f'<{tag}{h} id="c-{key}" style="display:block;width:{W}px;box-sizing:border-box;padding:4px 14px 14px 4px;text-decoration:none">'
            f'<div style="position:relative;padding:{pad};{box(fill)}{FONT}">{inner}</div></{tag}>')

def btn_div(label, fill, tag='div', href=None):
    h = f' href="{href}"' if href else ''
    return (f'<{tag}{h} style="display:flex;align-items:center;justify-content:center;width:{BW - 18}px;height:{BH - 18}px;margin:4px 14px 14px 4px;'
            f'{box(fill)}color:{BG};text-decoration:none;font-family:\'Silkscreen\',monospace;font-size:18px">{label}</{tag}>')

def font_faces(src):
    return ''.join(f"@font-face{{font-family:'{name}';{'font-weight:400 700;' if name == 'Pixelify Sans' else ''}src:url({src(file)}) format('woff2')}}" for name, file in FONT_FILES.items())
fonts = font_faces(lambda f: 'data:font/woff2;base64,' + b64(os.path.join(TOOLS, 'fonts', f)))

# measure every card in Chrome with the real fonts
XH = 'xmlns="http://www.w3.org/1999/xhtml" '
measure = os.path.join(OUT, 'measure.html')
open(measure, 'w').write(f'<!doctype html><html><head><meta charset="utf-8"/><style>{fonts}{EFFECTS}body{{margin:0;background:#0d1117}}</style></head><body>'
    + ''.join(card_div(k, f, p, i) for k, _, _, f, p, i in CARDS)
    + '<script>document.fonts.ready.then(()=>{document.title=JSON.stringify([...document.querySelectorAll("[id^=c-]")].map(e=>[e.id.slice(2),e.offsetHeight]))})</script></body></html>')
dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=3000', '--dump-dom', f'file://{measure}'],
                     capture_output=True, text=True, timeout=90).stdout
heights = dict(json.loads(html.unescape(re.search(r'<title>(.*?)</title>', dom).group(1))))

def svg_wrap(w, h, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{fonts}{EFFECTS}</style>'
            f'<foreignObject x="0" y="0" width="{w}" height="{h}"><div {XH}style="margin:0">{inner}</div></foreignObject></svg>')

# rewrite the card images, dropping ones that no longer exist (a removed quest, the job card)
keep = {f'card-{k}.svg' for k, *_ in CARDS} | {f'btn-{k}.svg' for k, *_ in BTNS}
for f in os.listdir(os.path.join(REPO, 'assets')):
    if re.match(r'(card|btn)-.*\.svg$', f) and f not in keep:
        os.remove(os.path.join(REPO, 'assets', f))
for k, _, _, f, p, i in CARDS:
    open(os.path.join(REPO, 'assets', f'card-{k}.svg'), 'w').write(svg_wrap(W, heights[k], card_div(k, f, p, i)))
for k, label, fill, _ in BTNS:
    open(os.path.join(REPO, 'assets', f'btn-{k}.svg'), 'w').write(svg_wrap(BW, BH, btn_div(label, fill)))

# README: no whitespace between the buttons, and all cards in one paragraph, so GitHub adds no extra margins
def img(src, alt, width):
    return f'<img src="{src}" width="{width}" alt="{e(alt)}" />'
md = ['<!-- Generated from profile.json by tools/build.py, do not edit by hand. -->\n']
md.append('<p align="right">' + ''.join(f'<a href="{href}">{img(f"assets/btn-{k}.svg", label, "24%")}</a>' for k, label, _, href in BTNS) + '</p>\n')
rows = [f'<a href="{href or PROFILE}">{img(f"assets/card-{k}.svg", alt, "100%")}</a>' for k, alt, href, *_ in CARDS]  # unlinked cards open the profile, not the raw SVG
md.append('<p align="center">\n' + '<br />\n'.join(rows) + '\n</p>\n')
md.append('<p align="center"><sub>Thanks for visiting · Game saved</sub></p>\n')
text = [f"### {P['name']}\n", INTRO + '\n',
        ' · '.join(f'**{a}** {b}' for a, b in stats) + '\n',
        '**Stack:** ' + ' · '.join(f"{k} {', '.join(v)}" for k, v in P['stack'].items()) + '\n']
if JOB:
    text.append(f"**Current quest: {JOB['title'].lower()} at {JOB['company']}** ({JOB['period']}). " + ' '.join(JOB['text']) + '\n')
text.append('**Quest log**\n' + '\n'.join(f"- {q['when']} · {q['where']} · {q['what']}" for q in P['quest_log']) + '\n')
md.append('<details>\n<summary>Text version</summary>\n\n' + '\n'.join(text) + '\n</details>\n')
open(os.path.join(REPO, 'README.md'), 'w').write('\n'.join(md))

# Claude canvas artboard: the same cards and buttons as real links on GitHub's dark page.
# The /_blob ids are files uploaded to that canvas; only needed when updating the canvas.
CANVAS_FONTS = {'pixelify.woff2': '7f4c89fd355131fc990e117927ce6c39', 'silkscreen.woff2': 'f2be33cf2adfea471e84f215ce3065e5', 'vt323.woff2': 'd48fe36bb6d009ad42dbdb71366e5b9a'}
CANVAS_PORTRAIT_BLOB = '69bb2fc2d9aca403d0345e370cce96b7'
CANVAS_PORTRAIT = ('<canvas ref="{{photoRef}}" width="256" height="256" role="img" aria-label="Pixel-art portrait" '
                   'style="display:block;width:256px;height:256px;image-rendering:pixelated;background:#9FC7C4"></canvas>')
cards = ''.join(card_div(k, f, p, i.replace(PORTRAIT_IMG, CANVAS_PORTRAIT), 'a', href or PROFILE) for k, _, href, f, p, i in CARDS)
buttons = ''.join(btn_div(label, fill, 'a', href) for _, label, fill, href in BTNS)
total = BH + sum(heights.values()) + GAP * (len(CARDS) + 1) + 120
open(os.path.join(OUT, 'Main.dc.html'), 'w').write(f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{e(P['name'])}, GitHub profile</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
{font_faces(lambda f: '/_blob/' + CANVAS_FONTS[f])}
{EFFECTS}
body{{margin:0;background:#0d1117}}
a{{color:{PINK}}}a:hover{{color:{PEACH}}}
</style>
</helmet>
<div style="width: {W}px; background: #0d1117; display: flex; flex-direction: column; gap: {GAP}px; padding-bottom: 24px">
<div style="display: flex; justify-content: flex-end">{buttons}</div>
{cards}
<p style="margin: 0; text-align: center; color: #8b949e; font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 12px">Thanks for visiting · Game saved</p>
<details style="margin: 0 16px; color: #c9d1d9; font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 14px"><summary>Text version</summary><p>Plain-text copy of the profile for screen readers and search.</p></details>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{total}}}}}'>
class Component extends DCLogic {{
componentDidMount() {{
fetch('/_blob/{CANVAS_PORTRAIT_BLOB}')
.then((r) => r.blob())
.then((b) => createImageBitmap(b))
.then((bmp) => {{ this.photo = bmp; this.drawPhoto(); }})
.catch(() => {{}});
}}
drawPhoto() {{
if (!this.photo || !this.photoEl) return;
const c = this.photoEl;
const ctx = c.getContext('2d');
ctx.imageSmoothingEnabled = false;
ctx.drawImage(this.photo, 0, 0, c.width, c.height);
}}
renderVals() {{
if (!this.photoRef) this.photoRef = (el) => {{ this.photoEl = el; this.drawPhoto(); }};
return {{ photoRef: this.photoRef }};
}}
}}
</script>
</body>
</html>
''')
print('Built', len(CARDS), 'cards. Commit README.md, assets/ and profile.json.', {k: heights[k] for k, *_ in CARDS})
