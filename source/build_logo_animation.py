"""Sembang logo loop: a small repeating corner animation built from the traced S emblem.

Matches the motion language of the site's corner symbols (Lottie, 30 fps, 100-frame
loop, cubic-bezier(.7,0,.3,1) stretch-and-return). One keyframe table drives both
outputs, so the self-playing SVG and the Lottie JSON move identically:

  logo_animation/sembang_logo_loop.svg   CSS-animated SVG, works as a plain <img>
  logo_animation/sembang_logo_loop.json  Lottie (lottie-web / bodymovin 5.x)

Motion, per loop: rest → squash → hop with a tilt → star twinkles at the top →
land with a squash → settle. The highlight glints wink out on take-off and pop back
one by one after landing.
"""
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'logo_animation'
DESIGN = '03_cream_raspberry'          # raspberry outline, cream faces: reads best on the site's cream

FPS, FRAMES, SIZE = 30, 100, 512
SCALE, CENTRE = 118, (256, 286)        # logo units → canvas px; sits low to leave headroom for the hop
INK, FACE = '#EF4C7A', '#FBFACF'       # logo raspberry / cream (overridable via CSS variables in the SVG)

# Eases as CSS cubic-bezier control points, applied from a keyframe to the next one.
SITE = (.7, 0, .3, 1)                  # the site's own symbol ease
SMOOTH = (.45, 0, .55, 1)
OUT_ = (.2, .7, .3, 1)                 # fast start, soft stop
IN_ = (.55, 0, .9, .45)                # gather speed into the landing
POP = (.3, 1.6, .5, 1)                 # overshoot

# frame, (dx, dy), (sx, sy) in %, rotation in degrees, ease to the next key
BODY = [
    (0,  (0, 0),   (100, 100), 0,  SMOOTH),
    (12, (0, 0),   (100, 100), 0,  SMOOTH),
    (20, (0, 0),   (110, 89),  0,  OUT_),       # anticipation squash
    (34, (0, -40), (95, 106),  -5, SMOOTH),     # launch, stretched and tilted
    (44, (0, -44), (100, 100), -3, IN_),        # hang at the top
    (54, (0, 0),   (111, 90),  0,  SITE),       # land
    (64, (0, 0),   (97, 103),  0,  SMOOTH),     # rebound
    (72, (0, 0),   (100, 100), 0,  SMOOTH),
    (100, (0, 0),  (100, 100), 0,  SMOOTH),
]
STAR = [
    (0,  (0, 0), (100, 100), 0,   SMOOTH),
    (32, (0, 0), (100, 100), 0,   IN_),
    (38, (0, 0), (35, 35),   -30, POP),         # twinkle: shrink and turn...
    (48, (0, 0), (100, 100), 0,   SMOOTH),      # ...then spring back
    (100, (0, 0), (100, 100), 0,  SMOOTH),
]

def glint(back):
    """A highlight that winks out on take-off and pops back at frame `back`."""
    return [
        (0,         (0, 0), (100, 100), 0, SMOOTH),
        (18,        (0, 0), (100, 100), 0, IN_),
        (24,        (0, 0), (0, 0),     0, SMOOTH),
        (back,      (0, 0), (0, 0),     0, POP),
        (back + 10, (0, 0), (100, 100), 0, SMOOTH),
        (100,       (0, 0), (100, 100), 0, SMOOTH),
    ]

# ------------------------------------------------------------------ geometry ---
def load_paths():
    """Return [(points, fill)] in canvas px. Order: outline, bubble face, star face, 4 highlights."""
    svg = ET.parse(ROOT / 'source' / f'{DESIGN}.svg').getroot()
    paths = []
    for el in svg:
        nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', el.get('d'))]
        pts = [(round(CENTRE[0] + x*SCALE, 2), round(CENTRE[1] + y*SCALE, 2)) for x, y in zip(nums[::2], nums[1::2])]
        paths.append((pts, el.get('fill').lower()))
    assert len(paths) == 7, len(paths)
    return paths

def bounds(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def centre_of(pts):
    x0, y0, x1, y1 = bounds(pts)
    return round((x0 + x1)/2, 2), round((y0 + y1)/2, 2)

def inside(pts, box):
    x, y = centre_of(pts)
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]

# ----------------------------------------------------------------- SVG (CSS) ---
def css_transform(key, pivot):
    _, (dx, dy), (sx, sy), r, _ = key
    px, py = pivot
    return (f'translate({px + dx:g}px,{py + dy:g}px) rotate({r:g}deg) '
            f'scale({sx/100:g},{sy/100:g}) translate({-px:g}px,{-py:g}px)')

def css_keyframes(name, keys, pivot):
    rows = [f'{k[0]/FRAMES*100:g}%{{transform:{css_transform(k, pivot)};'
            f'animation-timing-function:cubic-bezier({",".join(f"{v:g}" for v in k[4])})}}' for k in keys]
    return f'@keyframes {name}{{{"".join(rows)}}}'

def svg_path(pts):
    return 'M' + 'L'.join(f'{x:g},{y:g}' for x, y in pts) + 'Z'

# -------------------------------------------------------------------- Lottie ---
def ease(e):
    return {'o': {'x': e[0], 'y': e[1]}, 'i': {'x': e[2], 'y': e[3]}}

def track(keys, value):
    out = []
    for i, k in enumerate(keys):
        kf = {'t': k[0], 's': value(k)}
        if i < len(keys) - 1:
            kf.update(ease(k[4]))
        out.append(kf)
    return {'a': 1, 'k': out}

def lottie_transform(keys, pivot, group=False):
    px, py = pivot
    tr = {
        'p': track(keys, lambda k: [px + k[1][0], py + k[1][1]] + ([] if group else [0])),
        'a': {'a': 0, 'k': [px, py] + ([] if group else [0])},
        's': track(keys, lambda k: list(k[2]) + ([] if group else [100])),
        'r': track(keys, lambda k: [k[3]]),
        'o': {'a': 0, 'k': 100},
    }
    if group:
        tr.update(ty='tr', sk={'a': 0, 'k': 0}, sa={'a': 0, 'k': 0}, nm='Transform')
    return tr

def static_tr():
    return {'ty': 'tr', 'p': {'a': 0, 'k': [0, 0]}, 'a': {'a': 0, 'k': [0, 0]}, 's': {'a': 0, 'k': [100, 100]},
            'r': {'a': 0, 'k': 0}, 'o': {'a': 0, 'k': 100}, 'sk': {'a': 0, 'k': 0}, 'sa': {'a': 0, 'k': 0}, 'nm': 'Transform'}

def rgba(hexcolor):
    return [round(int(hexcolor[i:i+2], 16)/255, 4) for i in (1, 3, 5)] + [1]

def shape_group(name, pts, colour, tr=None):
    """One filled path in its own group, so its fill never leaks onto sibling paths."""
    n = len(pts)
    return {'ty': 'gr', 'nm': name, 'it': [
        {'ty': 'sh', 'nm': 'Path', 'ks': {'a': 0, 'k': {'i': [[0, 0]]*n, 'o': [[0, 0]]*n, 'v': [list(p) for p in pts], 'c': True}}},
        {'ty': 'fl', 'nm': 'Fill', 'c': {'a': 0, 'k': rgba(colour)}, 'o': {'a': 0, 'k': 100}, 'r': 1, 'bm': 0},
        tr or static_tr()]}

# ---------------------------------------------------------------------- main ---
def main():
    paths = load_paths()
    (outline, _), (bubble, _), (star, _) = paths[:3]
    highlights = [p for p, _ in paths[3:]]
    star_box = bounds(star)
    star_glint = next(p for p in highlights if inside(p, star_box))
    s_glints = sorted((p for p in highlights if p is not star_glint), key=lambda p: centre_of(p)[1])  # top → bottom
    x0, y0, x1, y1 = bounds(outline)
    body_pivot = (round((x0 + x1)/2, 2), round(y1, 2))      # bottom centre: squash against the ground
    star_pivot = centre_of(star)
    glint_backs = [56, 60, 64]
    star_glint_back = 46

    # --- SVG ---------------------------------------------------------------
    anims = [css_keyframes('sb-body', BODY, body_pivot), css_keyframes('sb-star', STAR, star_pivot),
             css_keyframes('sb-glint-star', glint(star_glint_back), centre_of(star_glint))]
    anims += [css_keyframes(f'sb-glint-{i}', glint(b), centre_of(p)) for i, (p, b) in enumerate(zip(s_glints, glint_backs))]
    dur = f'{FRAMES/FPS:.4f}s'
    css = (
        '.ink{fill:var(--sembang-ink,%s)}.face{fill:var(--sembang-face,%s)}' % (INK, FACE)
        + 'g{transform-box:view-box;transform-origin:0 0;animation:%s infinite both}' % dur
        + '#body{animation-name:sb-body}#star{animation-name:sb-star}#glint-star{animation-name:sb-glint-star}'
        + ''.join(f'#glint-{i}{{animation-name:sb-glint-{i}}}' for i in range(len(s_glints)))
        + ''.join(anims)
        + '@media (prefers-reduced-motion:reduce){g{animation:none}}'
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" role="img" aria-label="Sembang Entertainment">'
        f'<style>{css}</style>'
        f'<g id="body">'
        f'<path class="ink" d="{svg_path(outline)}"/>'
        f'<path class="face" d="{svg_path(bubble)}"/>'
        f'<g id="star"><path class="face" d="{svg_path(star)}"/>'
        f'<g id="glint-star"><path class="ink" d="{svg_path(star_glint)}"/></g></g>'
        + ''.join(f'<g id="glint-{i}"><path class="ink" d="{svg_path(p)}"/></g>' for i, p in enumerate(s_glints))
        + '</g></svg>'
    )

    # --- Lottie ------------------------------------------------------------
    def glint_group(name, pts, back):
        return shape_group(name, pts, INK, lottie_transform(glint(back), centre_of(pts), group=True))
    star_group = {'ty': 'gr', 'nm': 'Star', 'it': [
        glint_group('Star Glint', star_glint, star_glint_back),
        shape_group('Star Face', star, FACE),
        lottie_transform(STAR, star_pivot, group=True)]}
    shapes = ([glint_group(f'S Glint {i + 1}', p, b) for i, (p, b) in reversed(list(enumerate(zip(s_glints, glint_backs))))]
              + [star_group, shape_group('Bubble Face', bubble, FACE), shape_group('Outline', outline, INK)])  # first = topmost
    lottie = {
        'v': '5.11.0', 'fr': FPS, 'ip': 0, 'op': FRAMES, 'w': SIZE, 'h': SIZE, 'nm': 'Sembang Logo Loop', 'ddd': 0,
        'assets': [], 'markers': [],
        'layers': [{'ddd': 0, 'ind': 1, 'ty': 4, 'nm': 'Sembang S', 'sr': 1, 'ao': 0, 'bm': 0,
                    'ks': lottie_transform(BODY, body_pivot), 'shapes': shapes, 'ip': 0, 'op': FRAMES, 'st': 0}],
    }

    lottie_json = json.dumps(lottie, separators=(',', ':'))
    OUT.mkdir(exist_ok=True)
    (OUT / 'sembang_logo_loop.svg').write_text(svg, encoding='utf-8')
    (OUT / 'sembang_logo_loop.json').write_text(lottie_json, encoding='utf-8')
    (OUT / 'README.txt').write_text(README, encoding='utf-8')
    (ROOT / PREVIEW).write_text(preview_html(svg, lottie_json), encoding='utf-8')
    with zipfile.ZipFile(ROOT / 'Sembang_Logo_Animation.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in [*sorted(OUT.iterdir()), ROOT / PREVIEW, Path(__file__), ROOT / 'source' / f'{DESIGN}.svg']:
            z.write(f, f.relative_to(ROOT).as_posix())
    print(f'svg {len(svg)//1024} KB, lottie {len(lottie_json)//1024} KB')

# ------------------------------------------------------------------- preview ---
PREVIEW = 'Sembang Logo Animation Preview.html'

def preview_html(svg, lottie_json):
    inline = svg.replace('<svg ', '<svg class="logo" ', 1)
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sembang — Logo loop</title><style>
*{box-sizing:border-box}body{margin:0;background:#f2f0ee;color:#392d31;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}header{padding:30px 4vw;display:flex;justify-content:space-between;border-bottom:1px solid #dcd7d3;font-size:11px;letter-spacing:2px;font-weight:650}header span:last-child{color:#9d6c7c}main{display:grid;grid-template-columns:300px 1fr;gap:30px;padding:44px 4vw 24px}aside{padding-top:26px}.eyebrow{font-size:10px;letter-spacing:2px;color:#b73d63;font-weight:700}h1{font-family:Georgia,serif;font-weight:400;font-size:49px;line-height:1.04;letter-spacing:-2px;margin:20px 0 22px}p{font-size:14px;line-height:1.8;color:#7f7479;margin:0 0 23px}.swatches{display:flex;flex-wrap:wrap;gap:10px 16px;font-size:11px;color:#7f7479;margin-bottom:35px}.swatches span{display:flex;align-items:center;gap:7px}.swatches i{width:14px;height:14px;border-radius:50%;border:1px solid #2b262833}button,a.download{font:inherit;cursor:pointer;border:1px solid #d3cbc8;border-radius:8px;background:transparent;padding:10px 14px;color:inherit;text-decoration:none}button:hover,a.download:hover{border-color:#b43b60}.download{display:block;width:100%;text-align:left;font-size:12px;margin:10px 0;padding:14px 16px}.download.primary{background:#2b2628;color:#fff;border-color:#2b2628}.tiny{font-size:11px;line-height:1.7;color:#9c9096}pre{font:11px/1.6 ui-monospace,Consolas,monospace;background:#e6e1dd;border-radius:8px;padding:12px 14px;white-space:pre-wrap;word-break:break-all;color:#5b4f54;margin:0 0 14px}.viewer{min-width:0;border:1px solid #dcd5d0;border-radius:18px;background:#e6e1dd;overflow:hidden}.viewerhead{display:flex;justify-content:space-between;align-items:center;padding:19px 23px}.tabs{display:flex;gap:6px}.tabs button{font-size:11px;border:0}.tabs .selected{background:#fbf9f7}.object-label{font-size:10px;letter-spacing:1px;color:#8d8085}.stage{height:540px;position:relative;overflow:hidden;background:#FEF5EB}.stage[hidden]{display:none!important}#corner .hero{position:absolute;left:6%;top:16%;right:6%;font-weight:800;letter-spacing:-.05em;line-height:.92;font-size:clamp(34px,6.4vw,84px);color:#EE4F78;text-transform:uppercase}#corner .hero small{display:block;font-size:13px;letter-spacing:0;font-weight:600;color:#5F729B;margin-top:22px;text-transform:none}#corner .logo{position:absolute;left:30px;bottom:30px;width:96px;height:96px}#close{display:grid;place-items:center}#close .logo{width:min(440px,80%);height:auto}.toolbar{display:flex;gap:7px;justify-content:center;align-items:center;padding:15px 15px 22px;flex-wrap:wrap}.toolbar button{font-size:11px;padding:9px 12px}.toolbar .active{background:#2b2628;border-color:#2b2628;color:#fff}.toolbar input{width:200px;accent-color:#b73d63}.toolbar output{font-size:11px;color:#8d8085;width:58px;font-variant-numeric:tabular-nums}footer{margin:0 4vw;padding:20px 0 25px;border-top:1px solid #dcd7d3;display:flex;justify-content:space-between;font-size:10px;color:#9c9096;line-height:1.8}@media(max-width:900px){main{grid-template-columns:1fr;padding-top:15px}aside{max-width:560px}h1{font-size:38px}.stage{height:420px}.download{display:inline-block;width:auto;margin-right:8px}.object-label{display:none}#corner .logo{left:16px;bottom:16px;width:64px;height:64px}}@media(max-width:500px){header{font-size:9px}.stage{height:320px}.toolbar input{width:140px}footer{display:block}footer span{display:block}}
</style></head><body>
<header><span>SEMBANG ENTERTAINMENT</span><span>LOGO LOOP</span></header>
<main><aside>
<div class="eyebrow">CORNER ANIMATION</div>
<h1>The S, on a loop.</h1>
<p>A small repeating mark for the bottom-left corner. It squashes, hops, twinkles its star at the top and lands with a bounce, then rests. It uses the site&rsquo;s 3.33&nbsp;s symbol rhythm and its stretch-and-return ease.</p>
<div class="swatches"><span><i style="background:#EF4C7A"></i>Raspberry</span><span><i style="background:#FBFACF"></i>Cream</span><span><i style="background:#FEF5EB"></i>Site background</span></div>
<a class="download primary" id="dl-svg" download="sembang_logo_loop.svg">Download animated SVG</a>
<a class="download" id="dl-json" download="sembang_logo_loop.json">Download Lottie JSON</a>
<p class="tiny" style="margin-top:22px">Drop-in, no library needed:</p>
<pre>&lt;img src="sembang_logo_loop.svg" alt="Sembang Entertainment"
     style="position:fixed;left:3rem;bottom:3rem;width:6rem"&gt;</pre>
<p class="tiny">Or with lottie-web, like the site&rsquo;s other corner symbols: load <b>sembang_logo_loop.json</b> as <code>animationData</code> with <code>loop: true</code>. The motion stops when the viewer prefers reduced motion (SVG version).</p>
</aside>
<section class="viewer"><div class="viewerhead"><div class="tabs"><button class="selected" data-view="corner">In place</button><button data-view="close">Close-up</button></div><span class="object-label">512 × 512 · 30 FPS · 100 FRAMES</span></div>
<div class="stage" id="corner"><div class="hero">We create<br>culture. Stories.<br>Impact.<small>Creative Media &amp; Marketing</small></div>''' + inline + '''</div>
<div class="stage" id="close" hidden>''' + inline + '''</div>
<div class="toolbar"><button id="play" class="active">Pause</button><button data-rate="0.25">¼×</button><button data-rate="0.5">½×</button><button data-rate="1" class="active">1×</button><input id="scrub" type="range" min="0" max="99" value="0" aria-label="Frame"><output id="frame">frame 0</output></div>
</section></main>
<footer><span>Built from source/''' + DESIGN + '''.svg by source/build_logo_animation.py</span><span>SVG and Lottie share one keyframe table</span></footer>
<script>
const SVG=''' + json.dumps(svg) + ''', LOTTIE=''' + json.dumps(lottie_json) + ''';
const url=(t,s)=>URL.createObjectURL(new Blob([s],{type:t}));
document.getElementById('dl-svg').href=url('image/svg+xml',SVG);
document.getElementById('dl-json').href=url('application/json',LOTTIE);
const LOOP=''' + f'{FRAMES/FPS*1000:.3f}' + ''', anims=()=>document.getAnimations();
let playing=true, rate=1;
const play=document.getElementById('play'), scrub=document.getElementById('scrub'), out=document.getElementById('frame');
play.onclick=()=>{playing=!playing; anims().forEach(a=>playing?a.play():a.pause()); play.textContent=playing?'Pause':'Play'; play.classList.toggle('active',playing)};
document.querySelectorAll('[data-rate]').forEach(b=>b.onclick=()=>{rate=+b.dataset.rate; anims().forEach(a=>a.playbackRate=rate); document.querySelectorAll('[data-rate]').forEach(x=>x.classList.toggle('active',x===b))});
scrub.oninput=()=>{if(playing)play.click(); const t=scrub.value/30*1000; anims().forEach(a=>a.currentTime=t)};
(function tick(){const a=anims()[0]; if(a&&playing){const f=Math.floor(((a.currentTime%LOOP)+LOOP)%LOOP/1000*30); scrub.value=f; out.textContent='frame '+f} else out.textContent='frame '+scrub.value; requestAnimationFrame(tick)})();
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('selected',x===b)); document.querySelectorAll('.stage').forEach(s=>s.hidden=s.id!==b.dataset.view); const t=scrub.value/30*1000; anims().forEach(a=>{a.playbackRate=rate; a.currentTime=t; playing?a.play():a.pause()})});
</script></body></html>'''

README = '''SEMBANG ENTERTAINMENT — LOGO LOOP

A small, repeating animation of the S emblem for the bottom-left corner of the site,
in the same spirit as the site's existing corner symbols.

Open "Sembang Logo Animation Preview.html" (project root) to see it in place,
in close-up, slowed down, or frame by frame. It works offline.

FILES
sembang_logo_loop.svg   Self-playing animated SVG (CSS keyframes inside the file).
                        No JavaScript or library needed; works as a plain <img>.
sembang_logo_loop.json  The same animation as Lottie, for lottie-web / bodymovin.

TIMING
512 x 512 canvas, 30 fps, 100 frames = 3.33 s per loop, repeating forever. This is
the same length and ease (cubic-bezier(.7,0,.3,1)) as the site's own symbols.

  frames  0-12   rest
         12-20   squash (anticipation)
         20-44   hop up with a slight tilt; highlight glints wink out
         32-48   star twinkles: shrinks, turns, springs back
         44-54   fall and land with a squash
         54-72   rebound and settle; glints pop back one by one
         72-100  rest

USE — plain image (simplest)
  <img src="sembang_logo_loop.svg" alt="Sembang Entertainment"
       style="position:fixed;left:3rem;bottom:3rem;width:6rem">

USE — inline SVG (lets you recolour)
  Paste the file's <svg> into the page, then set CSS variables on any parent:
    --sembang-ink:  outline, S and highlights   (default #EF4C7A)
    --sembang-face: bubble and star faces       (default #FBFACF)
  Note: CSS ids/keyframes inside are prefixed "sb-"; use one inline copy per page,
  or the <img> form for several copies.

USE — Lottie
  lottie.loadAnimation({ container, renderer: 'svg', loop: true, autoplay: true,
                         animationData: <contents of sembang_logo_loop.json> });
  The site's symbol styles force "fill: currentColor !important" on every child
  (for example .Dot_dot). Don't reuse those classes for this logo, or both colours
  will flatten into one and the S will disappear.

ACCESSIBILITY
The SVG stops animating and shows the resting logo when the visitor has
"reduce motion" turned on. For Lottie, check
matchMedia('(prefers-reduced-motion: reduce)') and call goToAndStop(0, true).

REBUILD
  .venv/Scripts/python source/build_logo_animation.py   (Windows)
  .venv/bin/python source/build_logo_animation.py       (macOS / Linux)
Motion lives in the BODY / STAR / glint() keyframe tables at the top of the
script. DESIGN picks which traced logo colourway to animate.
'''

if __name__ == '__main__':
    main()
