SEMBANG — FILM CLAPPERBOARD

Open "Sembang Studio Props Preview.html" in a browser and choose "Clapperboard".
Drag to rotate, scroll to zoom, or use the Front / Back / Edge buttons.

MODELS
Sembang_Clapperboard.glb — complete model, textures embedded
Sembang_Clapperboard.obj + .mtl — editable model (keep the .png beside them)
Slate_Face.png — lettered slate face texture (editable; same UV layout)

DESIGN
Modelled from the supplied reference, recoloured in the Sembang raspberry and
cream palette: a raspberry slate with STUDIO, SCENE / TAKE /
ROLL boxes and DATE / PROD.CO. / DIRECTOR / CAMERAMAN rows, a raspberry-and-cream
striped fixed stick, and a striped clapper arm raised 11 degrees on a
blush hinge block with cream rivets on both sides.
Nothing is a sharp box: the slate has rounded lower corners and bevelled edges,
the sticks and arm have rounded ends and softly rolled edges, the hinge block is
rounded, and the stripes are slightly raised, soft-cornered inlays on both faces.
The lettering is a texture on a thin raised face plate (mesh Slate_Face), so it
can be changed by editing Slate_Face.png.

COLOURS
Raspberry #EF4C7A (slate), deeper raspberry #E23E6C (lettered plate) and
#C72E5C (sticks), cream #FBFACF (lettering, stripes, rivets), blush #F9BFC5
(hinge). All materials are satin and non-metallic. GLB colour factors are
linear RGB.

MODEL DETAILS
Y is up; the lettered side faces +Z. About 4.4 units wide and 4.4 units high
including the raised arm, 0.46 units deep at the hinge.
glTF units are metres; scale to the size you need.
37 named, individually closed mesh components that overlap as an assembled
object (rendering/animation assets, not a boolean-unioned print mesh).
The arm is its own set of meshes (Clapper_Arm_*) for easy animation.

SOURCE
source/build_clapperboard.py, source/props_common.py, source/build_props_preview.py
Rebuild: .venv\Scripts\python.exe source\build_clapperboard.py
