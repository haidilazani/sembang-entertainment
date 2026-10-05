SEMBANG — UNBRANDED DIGITAL CINEMA CAMERA

Open “Sembang Camera Preview.html” in a browser to rotate the camera and
replace its screen content. No installation or network connection is needed
for the model, logo, image/video preview, or GLB download.

FILES
Cinema_Camera.glb — camera and lens, with a neutral screen placeholder
Cinema_Camera.obj + Cinema_Camera.mtl — editable OBJ version
Screen_Content.png — companion screen texture referenced by the OBJ MTL
screen_placeholder.png — original 1600 × 900 placeholder image
Cinema_Camera_Sembang_Screen.glb — example with the Sembang logo on the LCD
manifest.json — dimensions, named parts and screen configuration
preview_*.png — model preview images

Keep the OBJ, MTL and all companion PNG files in the same folder.
The GLB embeds its materials and screen texture in one file.

DESIGN
An original simplified model inspired by the compact Sony FX3 body layout:
flat top, graphite shell, hand grip, mounting sockets, accessory shoe,
cooling slots, control dials, rear buttons, and side-opening LCD.
Includes an unbranded stepped lens with ribbed zoom/focus rings, mount,
filter rim and stylized coated optical glass. There are no Sony logos,
manufacturer markings or manufacturer textures on the model.
This is a visual asset, not an exact engineering or mechanical replica.

SCREEN
Mesh: Screen_Placeholder
Material: Screen_Content
Parent node: LCD_Assembly
UV range: 0–1 across the entire screen
Aspect ratio: 16:9
Display dimensions: 0.075 × 0.0421875 metres

The screen is a separate two-triangle surface. Assign an image, video or
render-target texture to its material in your 3D application or engine.
The default GLB uses an unlit material to keep screen colours consistent.
The LCD housing and bezel are separate from the display surface.
The display assembly is positioned open, facing forward. Its separate
parent node can be transformed in a 3D editor; it has no baked animation.

PREVIEW CONTROLS
Choose image or video — load a local file onto the screen, fitted without
stretching. PNG/JPG/WebP and browser-supported videos work.
Use Sembang logo — apply the supplied cream/raspberry S-and-star artwork.
Live camera feed — display a device camera on the model's LCD after you
explicitly allow browser camera access. No audio is requested.
Stop live feed — stop the camera and restore the placeholder.
Save model with current screen — download a customized GLB containing
the current image. Video and live-camera sources are captured as one still.
Download original GLB — get the neutral placeholder model.

The live feed exists in the running preview, not inside the static model.
It does not perform recognition, QR decoding or 3D scanning. To use a live
scene/background in another app, connect that app's camera or render texture
to Screen_Content. No image or video is uploaded by this preview.

If your browser disallows a device camera from a local HTML file, serve the
package root locally:
  python3 -m http.server 8080
Then open:
  http://localhost:8080/Sembang%20Camera%20Preview.html
Camera access requires browser permission and a supported device/browser.

GEOMETRY
Units: metres. Y is up; the lens and open screen face +Z.
The body is approximately 0.13 metres wide; the open LCD extends to the left.
The model contains 78 named meshes and approximately 71,000 triangles.
The display is intentionally an open plane. Other parts are individually
closed meshes. Assembled parts overlap; the model is intended for rendering
and interactive use, not as a boolean-unioned object for 3D printing.

REBUILD
  python3 -m venv .venv
  .venv/bin/pip install -r source/requirements.txt
  .venv/bin/python source/build_camera.py
  npm ci --prefix preview/vendor
  .venv/bin/python source/build_camera_preview.py
The texture-generation script uses the macOS Arial font path; change it
to a local TrueType font path when rebuilding on another operating system.

VALIDATION
GLB/OBJ geometry, display UVs and the customized GLB were checked.
The preview was tested for image and video replacement, logo placement,
rotation, download, customized export, and mobile layout.
Live-camera start/stop was tested using a synthetic browser test device;
your physical camera was not accessed during testing.

DESIGN REFERENCE
Sony's official FX3 specifications and product imagery were consulted for
the compact body proportions and side-opening screen layout:
https://www.sony.com/electronics/support/camcorders-and-video-cameras-interchangeable-lens-camcorders/ilme-fx3/specifications
