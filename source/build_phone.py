"""Original burgundy flagship-phone mockup with a blank, UV-mapped display."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import box
from PIL import Image
from pygltflib import GLTF2
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial
from build_models import bevel, PALETTE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'phone'
OUT.mkdir(exist_ok=True)

COLOURS = {
    'Cherry_Red_Titanium': [103, 21, 35],
    'Burgundy_Glass': [86, 12, 27],
    'Polished_Burgundy': [130, 31, 49],
    'Dark_Metal': [28, 25, 28],
    'Lens_Glass': [20, 36, 46],
    'Lens_Reflection': [50, 91, 106],
    'Sensor_Black': [6, 8, 11],
    'Matte_Gray_Screen': [128, 132, 134],
    'Speaker_Black': [17, 18, 19],
}
PALETTE.update(COLOURS)

scene = trimesh.Scene()
metadata = []

def material(name, rough=.4, metallic=0):
    return PBRMaterial(name=name, baseColorFactor=COLOURS[name] + [255],
                       roughnessFactor=rough, metallicFactor=metallic)

def add(mesh, name, colour, rough=.4, metallic=0):
    if name != 'Screen_Placeholder':
        mesh.visual = TextureVisuals(material=material(colour, rough, metallic))
    assert np.isfinite(mesh.vertices).all(), name
    if name != 'Screen_Placeholder':
        assert mesh.is_watertight and mesh.is_winding_consistent, name
    # Construction values are millimetres; exported GLB uses metres.
    normals = mesh.vertex_normals.copy()
    mesh.apply_scale(.001)
    mesh.vertex_normals = normals
    scene.add_geometry(mesh, geom_name=name, node_name=name)
    metadata.append({'name': name, 'triangles': len(mesh.faces), 'closed': bool(mesh.is_watertight)})

def rounded(name, size, centre, colour, radius, rough=.4, metallic=0, transform=None):
    width, height, depth = size
    radius = min(radius, width*.22, height*.22)
    shape = box(-width/2, -height/2, width/2, height/2).buffer(-radius).buffer(radius, quad_segs=10)
    mesh = bevel(shape, -depth/2, depth/2, min(radius*.65, depth*.28), colour, name,
                 depth_radius=min(radius*.65, depth*.38), segments=10)
    if transform is not None:
        mesh.apply_transform(transform)
    mesh.apply_translation(centre)
    add(mesh, name, colour, rough, metallic)

def disc(name, radius, depth, centre, colour, rough=.4, metallic=0, sections=96):
    mesh = trimesh.creation.cylinder(radius=radius, height=depth, sections=sections)
    mesh.apply_translation(centre)
    add(mesh, name, colour, rough, metallic)

def torus(name, major, minor, centre, colour, rough=.3, metallic=.7):
    mesh = trimesh.creation.torus(major_radius=major, minor_radius=minor, major_sections=96, minor_sections=16)
    mesh.apply_translation(centre)
    add(mesh, name, colour, rough, metallic)

# Unbranded 6.9-inch-class flagship body: soft radii, an exposed titanium rim,
# and separate satin back glass. +Z is display/front, -Z is camera/back.
rounded('Titanium_Frame', (78.2, 165.5, 8.25), (0, 0, 0), 'Cherry_Red_Titanium', 10.4, .36, .80)
rounded('Front_Bezel', (76.8, 164.0, .32), (0, 0, 4.11), 'Dark_Metal', 9.5, .28, .55)
rounded('Rear_Bezel', (76.8, 164.0, .28), (0, 0, -4.10), 'Dark_Metal', 9.5, .30, .55)
rounded('Burgundy_Back_Glass', (75.5, 162.6, .42), (0, 0, -4.27), 'Burgundy_Glass', 9.2, .24, .15)

# A completely flat neutral-gray placeholder, with full 0–1 UV coverage for UI drop-ins.
w, h = 74.45, 160.10
screen = trimesh.Trimesh(vertices=[[-w/2,-h/2,4.31],[w/2,-h/2,4.31],[w/2,h/2,4.31],[-w/2,h/2,4.31]],
                        faces=[[0,1,2],[0,2,3]], process=False)
screen_image = Image.new('RGB', (1024, 2200), tuple(COLOURS['Matte_Gray_Screen']))
screen_image.save(OUT/'Matte_Gray_Screen.png')
screen_material = PBRMaterial(name='Matte_Gray_Screen', baseColorFactor=[255,255,255,255],
                              baseColorTexture=screen_image, roughnessFactor=.68, metallicFactor=0)
screen.visual = TextureVisuals(uv=np.array([[0,0],[1,0],[1,1],[0,1]],float), material=screen_material)
add(screen, 'Screen_Placeholder', 'Matte_Gray_Screen', .68, 0)

# Top-left camera island and three independent lens modules. It intentionally has no text or logo.
rounded('Camera_Island', (35.0, 43.0, 2.40), (-18.0, 56.0, -5.30), 'Polished_Burgundy', 7.8, .30, .67)
rounded('Camera_Island_Inset', (31.9, 39.9, .28), (-18.0, 56.0, -6.54), 'Burgundy_Glass', 6.8, .23, .20)
lens_positions = [(-25.2, 65.4), (-25.2, 49.8), (-9.8, 58.0)]
for index, (x, y) in enumerate(lens_positions, 1):
    disc('Camera_%d_Outer_Rim' % index, 9.05, .96, (x, y, -6.85), 'Dark_Metal', .22, .70)
    torus('Camera_%d_Polished_Ring' % index, 7.82, .64, (x, y, -7.43), 'Polished_Burgundy', .22, .83)
    disc('Camera_%d_Lens_Glass' % index, 7.05, .40, (x, y, -7.56), 'Lens_Glass', .08, .52)
    disc('Camera_%d_Optical_Core' % index, 4.22, .45, (x, y, -7.79), 'Sensor_Black', .18, .35)
    reflection = trimesh.creation.uv_sphere(radius=1, count=[24,48])
    reflection.apply_scale([2.8, 1.8, .22]); reflection.apply_translation((x-1.25,y+1.15,-8.03))
    add(reflection, 'Camera_%d_Glass_Reflection' % index, 'Lens_Reflection', .11, .58)

disc('Camera_Flash_Rim', 4.1, .54, (-9.2, 70.0, -6.78), 'Dark_Metal', .30, .55)
disc('Camera_Flash_Diffuser', 3.35, .22, (-9.2, 70.0, -7.16), 'Matte_Gray_Screen', .52, .05)
disc('Camera_LiDAR', 2.55, .44, (-9.0, 45.9, -6.76), 'Sensor_Black', .24, .45)

# Physical details around the burgundy frame: mute control, buttons, USB-C recess and grilles.
x_axis = trimesh.transformations.rotation_matrix(np.pi/2, [0,1,0])
rounded('Action_Button', (4.2, 13.0, 1.15), (-39.45, 44.0, 0), 'Cherry_Red_Titanium', 1.7, .34, .75, x_axis)
rounded('Volume_Up', (3.4, 20.5, .98), (-39.41, 12.0, 0), 'Cherry_Red_Titanium', 1.45, .34, .75, x_axis)
rounded('Volume_Down', (3.4, 20.5, .98), (-39.41, -13.2, 0), 'Cherry_Red_Titanium', 1.45, .34, .75, x_axis)
rounded('Capture_Button', (3.5, 31.0, 1.06), (39.43, 8.0, 0), 'Cherry_Red_Titanium', 1.45, .34, .75, x_axis)

y_axis = trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0])
rounded('USB_C_Recess', (14.6, 2.7, 1.0), (0, -82.68, 0), 'Speaker_Black', .9, .74, 0, y_axis)
for side in [-1, 1]:
    for number in range(5):
        x = side * (13.0 + number*3.05)
        mesh = trimesh.creation.cylinder(radius=.58, height=.92, sections=18)
        mesh.apply_transform(y_axis); mesh.apply_translation((x, -82.62, 0))
        add(mesh, 'Bottom_Grille_%s_%d' % ('L' if side < 0 else 'R', number+1), 'Speaker_Black', .7, 0)

# Small bottom antenna divisions and a single clean top microphone.
for x in [-26.0, 26.0]:
    rounded('Antenna_Divider_'+str(x), (1.15, 2.4, 8.32), (x, -81.0, 0), 'Dark_Metal', .3, .55, .15)
disc('Top_Microphone', 1.05, .18, (10.5, 82.6, 0), 'Speaker_Black', .68, 0)

# Export materials in glTF's linear colour space, retaining names for DCC editing.
gltf = GLTF2().load_from_bytes(scene.export(file_type='glb', include_normals=True))
for item in gltf.materials:
    rgb = np.array(COLOURS[item.name]) / 255
    linear = np.where(rgb <= .04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
    item.pbrMetallicRoughness.baseColorFactor = linear.tolist() + [1]
(OUT/'Burgundy_Flagship_Phone.glb').write_bytes(b''.join(gltf.save_to_bytes()))
obj, resources = trimesh.exchange.obj.export_obj(scene, include_normals=True, include_color=False,
                                                   include_texture=True, return_texture=True,
                                                   mtl_name='Burgundy_Flagship_Phone.mtl')
(OUT/'Burgundy_Flagship_Phone.obj').write_text(obj)
for name, data in resources.items():
    (OUT/name).write_bytes(data if isinstance(data, bytes) else data.encode())

manifest = {
    'name': 'Original unbranded burgundy flagship phone mockup',
    'file': 'Burgundy_Flagship_Phone.glb', 'units': 'metres',
    'screen': {'node':'Screen_Placeholder','material':'Matte_Gray_Screen','uv':[0,0,1,1],
               'aspect_ratio':'19.5:9','size_m':[w*.001,h*.001], 'default':'neutral matte gray'},
    'branding':'none', 'components':metadata, 'bounds':scene.bounds.tolist(),
    'triangles':sum(len(mesh.faces) for mesh in scene.geometry.values())
}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps({key:value for key,value in manifest.items() if key != 'components'}, indent=2))
