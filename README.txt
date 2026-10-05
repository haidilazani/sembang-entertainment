SEMBANG ENTERTAINMENT — 3D LOGO COLLECTION

Open “Sembang 3D Preview.html” in Chrome, Safari, or Edge to rotate and
compare all four designs. It works offline, without installation or a server.
Drag a model to orbit, scroll to zoom, or use the Front / Back / Edge buttons.

FILES
models/01_raspberry_cream — first logo, from the left of the source PNG
models/02_blush_raspberry — second logo
models/03_cream_raspberry — third logo
models/04_raspberry_cream — fourth logo

Each folder contains:
  .glb — geometry and colour materials in one portable file
  .obj + .mtl — editable geometry with companion colour materials
Keep each OBJ and its MTL together when importing into your 3D application.

DESIGN
Each design was independently traced from “Copy of studio sembang.png”.
Only the S, star, outline and four highlight strokes are retained.
The circle backgrounds and surrounding presentation text are removed.
Designs 1 and 4 have the same palette but retain their separate traced shapes.

These are solid emblems with broad, smoothly rounded depth edges, matching
front/back colour details, and a contrasting band following the curved sides.
The revised profile uses 16 segments per rounded shoulder and explicit smooth
normals in both GLB and OBJ. The S/star faces have softer rounded rims too.
The reverse side naturally shows a mirrored S when the object is flipped.
The original raster contours are lightly smoothed to remove pixel stair steps.

Original sampled sRGB palette:
  Raspberry #EF4C7A
  Cream     #FBFACF
  Blush     #F9BFC5
GLB material colours are converted to linear RGB as required by glTF.
Materials are opaque, nonmetallic, with a satin finish. Colours and outlines
exist on both faces and side walls; their apparent brightness still depends
on the lighting in the application where the model is viewed.

IMPORT / EDIT
Y is up; the front faces +Z. The model origin is at the centre.
Height is approximately 3 units and total depth is 0.640 units.
glTF uses metres; scale the model to the size required in your project.
Each model contains 14 named, individually closed mesh components:
outline body, side band, S/star faces, and four accents on each side.
Components intentionally overlap to create the assembled emblem. The files
are suitable for rendering and animation; they are not boolean-unioned
single-material print meshes. No animation is baked into the exports.

SOURCE / PREVIEWS
source/*.svg — traced vector artwork for each design
source/build_models.py — reproducible mesh-generation script
source/build_preview.py — offline-viewer build script
source/requirements.txt — Python dependency versions
preview/*.png — front, perspective, back, edge and dark-background views

To rebuild in the original workspace:
  .venv/bin/python source/build_models.py
  .venv/bin/python source/build_preview.py
To install the viewer build dependencies in a fresh copy, run:
  npm ci --prefix preview/vendor
The preview build uses Three.js and esbuild from preview/vendor/node_modules.

VALIDATION
All 56 mesh components checked for watertightness and consistent winding.
The offline viewer was checked in Chrome for loading, front/back/edge views,
auto rotation, GLB download, and mobile layout without JavaScript errors.
