SEMBANG — CREAM ENVELOPE & RASPBERRY WAX SEAL

Open Sembang Envelope Preview.html in a browser to inspect the envelope.
Choose “Wax seal” for a close view of the separate stamp. Drag to rotate,
scroll to zoom, or use the front/back/edge and automatic rotation controls.
The preview is self-contained and works offline.

MODELS
Sembang_Cream_Envelope.glb — complete sealed envelope
Sembang_Cream_Envelope.obj + .mtl — complete model for editing
Sembang_Wax_Seal.glb — separate wax seal, centred for reuse
Sembang_Wax_Seal.obj + .mtl — separate seal for editing
Keep OBJ and MTL files together to retain the colours.

DESIGN
Cream paper with a plain reverse, overlapping side and bottom folds,
and a closed triangular flap. Paper edges are gently rounded.
The raspberry wax has an uneven perimeter and a raised pressed rim.
The cream S and star are traced from design 03 of the supplied PNG,
with raspberry highlight strokes. The emblem is raised on the wax surface.

COLOURS
Paper #F7F0D7, with subtle cream variations on folded panels.
Wax #EF4C7A. Raised logo #FBFACF. Logo accents #EF4C7A.
GLB materials use linear RGB factors converted from these sRGB values.
Paper has a matte finish; wax and the raised emblem have a satin finish.

MODEL DETAILS
Y is up; the decorated side faces +Z.
Envelope: 6.4 units wide × 4.2 units high, approximately 0.417 units deep.
Wax seal: approximately 1.54 units across, approximately 0.168 units deep.
glTF units are metres. Scale to the size required for your project.
The envelope has 12 named mesh components; the separate seal has seven.
Every component is closed and has consistent winding. Components overlap
as an assembled object; these are rendering/animation assets, not a
boolean-unioned print mesh. The envelope is closed and has no opening rig.

SOURCE
source/build_envelope.py — generates the models
source/build_models.py — shared rounded-mesh and colour helpers
source/03_cream_raspberry.svg — original traced logo contours
source/build_envelope_preview.py — generates the offline viewer
preview/vendor/envelope_viewer.js — interactive preview source

To rebuild from the package root with Python 3:
  python3 -m venv .venv
  .venv/bin/pip install -r source/requirements.txt
  .venv/bin/python source/build_envelope.py
  npm ci --prefix preview/vendor
  .venv/bin/python source/build_envelope_preview.py

VALIDATION
The GLB and OBJ exports were reimported to check geometry and materials.
The browser preview was checked for model switching, front/back/edge views,
rotation, GLB download, and mobile layout without JavaScript errors.
