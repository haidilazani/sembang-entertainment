BURGUNDY FLAGSHIP PHONE — ORIGINAL UNBRANDED 3D MOCKUP

Open “Sembang Phone Preview.html” to inspect the model under soft studio
lighting. The default perspective leads with the triple-camera back; use
Front or Screen for the flat display and Back for an orthographic rear view.
The preview runs offline and supports screen-image replacement.

FILES
Burgundy_Flagship_Phone.glb — self-contained render-ready model
Burgundy_Flagship_Phone.obj + .mtl — editable model with materials
Burgundy_Flagship_Phone_Custom_Screen.glb — example custom-screen export
manifest.json — editable screen and geometry information
preview_*.png — studio preview views

Keep the OBJ, MTL, and companion texture files together after moving them.

DESIGN
This is an original, unbranded modern flagship-phone mockup. It has a matte
cherry-red titanium frame, frosted burgundy back glass, raised triple-camera
island, coated lens glass, physical side buttons, USB-C recess, speaker
grilles, antenna divisions and a plain flat display. It contains no Apple
logo, Apple product marks, manufacturer logo, brand name, or text marking.
It is suitable for product visualization and UI layout work; it is not an
exact engineering replica of a current or future commercial device.

SCREEN PLACEHOLDER
Mesh: Screen_Placeholder
Material: Matte_Gray_Screen
UV range: 0–1 across the full screen surface
Aspect ratio: 19.5:9
Display dimensions: 0.07445 × 0.16010 metres
Default: neutral solid matte gray, with no artwork or UI

Assign a render, image or UI texture to Matte_Gray_Screen in a DCC tool or
engine. The screen is a separate two-triangle plane, deliberately kept flat
for reliable texture drop-in. In the offline preview, choose a PNG/JPG/WebP
file and select “Save GLB with screen image” to create a separate copy with
your image embedded. The source image remains on your device.

GEOMETRY
Units: metres. The phone is approximately 0.078 metres wide × 0.166 metres
high × 0.008 metres thick before camera protrusions. +Z is the display side;
the camera island is on -Z. The model contains individually named parts for
the frame, glass, camera island, three lens stacks, flash, sensor, controls,
ports and screen. The screen plane is intentionally open; all other parts are
closed, overlapping assembled meshes designed for rendering, animation and
interactive use rather than a boolean-unioned print mesh.

MATERIALS
Cherry_Red_Titanium — matte metallic frame
Burgundy_Glass — frosted back glass
Polished_Burgundy — camera island and lens-ring accents
Lens_Glass / Lens_Reflection — layered coated optics
Matte_Gray_Screen — neutral editable screen placeholder

VALIDATION
The exported GLB and OBJ were checked for geometry, materials, named screen
surface, full display UV coverage and 19.5:9 dimensions. The browser preview
was checked for perspective/front/back/screen views, screen-image replacement,
customized GLB export, rotation and mobile layout.

REBUILD
  python3 -m venv .venv
  .venv/bin/pip install -r source/requirements.txt
  .venv/bin/python source/build_phone.py
  npm ci --prefix preview/vendor
  .venv/bin/python source/build_phone_preview.py
