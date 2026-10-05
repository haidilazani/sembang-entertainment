SEMBANG ENTERTAINMENT — LOGO LOOP

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
