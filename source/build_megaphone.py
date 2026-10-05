"""Sembang pistol-grip megaphone: lathe-turned horn, wrapped S emblem, gold trim."""
import re
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Polygon, box
from props_common import Props, rounded_rect, place, rotation_about, ROOT

COLOURS = {
    'Raspberry': [239, 76, 122],        # Sembang raspberry #EF4C7A
    'Cream': [251, 250, 207],           # Sembang cream #FBFACF
    'Cream_Edge': [240, 228, 172],      # emblem outline, a touch deeper than the horn
    'Gold': [214, 171, 92],
    'Raspberry_Deep': [150, 30, 72],    # vent slots
}
props = Props('megaphone', COLOURS)
SEGMENTS = 120

# ------------------------------------------------------------------- lathe ---
def smooth(poly, radius, close=None):
    """Round convex corners (opening) and, optionally, concave ones (closing)."""
    poly = poly.buffer(-radius, quad_segs=10).buffer(radius, quad_segs=10)
    if close:
        poly = poly.buffer(close, quad_segs=10).buffer(-close, quad_segs=10)
    return poly

def lathe(points, radius=.03, close=.02, name='part'):
    """Revolve a profile given as (x, r) points about the X axis into a closed solid."""
    shape = Polygon(points)
    assert shape.is_valid, name
    both = shape.union(affinity.scale(shape, 1, -1, origin=(0, 0)))   # mirror: rounds axis-side corners away
    both = smooth(both, radius, close)
    xmin, _, xmax, rmax = both.bounds
    half = both.intersection(box(xmin - 1, 0, xmax + 1, rmax + 1))
    if half.geom_type != 'Polygon':
        half = max(half.geoms, key=lambda g: g.area)
    ring = np.array(half.simplify(.0025).exterior.coords)[:-1]
    ring[:, 1] = np.where(np.abs(ring[:, 1]) < 1e-9, 0, ring[:, 1])
    phi = np.linspace(0, 2*np.pi, SEGMENTS, endpoint=False)
    verts = np.array([[x, r*np.cos(p), r*np.sin(p)] for x, r in ring for p in phi])
    n = len(ring)
    faces = []
    for i in range(n):
        i1 = (i + 1) % n
        for j in range(SEGMENTS):
            j1 = (j + 1) % SEGMENTS
            a, b, c, d = i*SEGMENTS + j, i*SEGMENTS + j1, i1*SEGMENTS + j1, i1*SEGMENTS + j
            faces += [[a, b, c], [a, c, d]]
    mesh = trimesh.Trimesh(verts, faces, process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    if mesh.volume < 0:
        mesh.invert()
    mesh.fix_normals()
    return mesh

def add_lathe(name, colour, points, rough=.3, metallic=0, **kw):
    props.add(lathe(points, name=name, **kw), name, colour, rough, metallic)

# ------------------------------------------------------------- horn profile ---
X_COLLAR, X_BELL, X_LIP = -1.28, 1.72, 2.40
R_THROAT, R_MOUTH = .93, 1.95
def horn_r(x):
    t = np.clip((np.asarray(x, float) - X_COLLAR) / (X_LIP - X_COLLAR), 0, None)
    return R_THROAT + (R_MOUTH - R_THROAT) * t**1.7
def horn_slope(x, h=1e-4):
    return (horn_r(x + h) - horn_r(x - h)) / (2*h)

# Cream wall of the horn (thin shell, outside visible from collar to the bell ring)
xs = np.linspace(X_COLLAR, X_BELL + .02, 70)
shell = [(x, horn_r(x)) for x in xs] + [(x, horn_r(x) - .06) for x in xs[::-1]]
add_lathe('Horn_Body', 'Cream', shell, .32, 0, radius=.02, close=.0)

# Raspberry bell: inner liner, floor behind the driver, and the rolled lip
XF = -.20
xo = np.linspace(XF, X_LIP - .02, 90)
blend = np.clip((xo - 1.64) / .10, 0, 1); blend = blend*blend*(3 - 2*blend)
bulge = .09 * np.exp(-((xo - 2.24) / .13)**2)
outer = [(x, horn_r(x) - .055 + b*(.055 + g)) for x, b, g in zip(xo, blend, bulge)]
xi = np.linspace(XF + .12, X_LIP - .02, 90)
inner = [(x, horn_r(x) - .17) for x in xi[::-1]]
bell = [(XF, 0)] + outer + [(X_LIP, horn_r(X_LIP) * .985 - .02), (X_LIP, horn_r(X_LIP) - .15)] + inner + [(XF + .12, 0)]
add_lathe('Bell_Liner', 'Raspberry', bell, .24, 0, radius=.025, close=.015)

# Driver tube and gold button inside the bell
add_lathe('Driver_Tube', 'Cream', [(-.10, 0), (-.10, .52), (1.45, .52), (1.45, 0)], .3, 0, radius=.12, close=.0)
add_lathe('Button_Ring', 'Gold', [(1.40, 0), (1.40, .41), (1.52, .41), (1.52, 0)], .26, .4, radius=.05, close=.0)
add_lathe('Button_Cap', 'Gold', [(1.48, 0), (1.48, .31), (1.63, .31), (1.63, 0)], .22, .4, radius=.07, close=.0)

# Rear cap: two soft steps, vents on the end face
rear = [(-2.55, 0), (-2.55, .78), (-1.85, .78), (-1.85, .94), (X_COLLAR + .03, .94), (X_COLLAR + .03, 0)]
add_lathe('Rear_Cap', 'Raspberry', rear, .22, 0, radius=.2, close=.05)
slot_rows = np.linspace(-.40, .40, 7)
to_rear = (trimesh.transformations.translation_matrix([-2.555, 0, 0])
           @ trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))   # slot thickness (Z) -> along X
for n, y in enumerate(slot_rows, 1):
    half = .80 * np.sqrt(max(.5**2 - y**2, 0))
    props.solid(rounded_rect(-half, y - .026, half, y + .026, .024), -.025, .025, .008, f'Rear_Vent_{n}',
                'Raspberry_Deep', .55, 0, depth_radius=.008, segments=6, matrix=to_rear)

# Gold trim rings at the collar and where the bell begins
def ring(name, xc, width, below, above):
    pts = [(xc - width/2, horn_r(xc - width/2) - below), (xc + width/2, horn_r(xc + width/2) - below),
           (xc + width/2, horn_r(xc + width/2) + above), (xc - width/2, horn_r(xc - width/2) + above)]
    add_lathe(name, 'Gold', pts, .26, .4, radius=.03, close=.0)
ring('Collar_Ring', X_COLLAR + .02, .17, .10, .05)
ring('Bell_Ring', X_BELL, .15, .13, .05)

# --------------------------------------------------- S emblem wrapped on horn ---
svg = ET.parse(ROOT / 'source/01_raspberry_cream.svg').getroot()
paths = list(svg)
LOGO_SCALE = .56
EMBLEM_X = .18

def logo_poly(node):
    numbers = np.array([float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', node.attrib['d'])]).reshape(-1, 2)
    return Polygon(numbers * [LOGO_SCALE, -LOGO_SCALE])        # SVG y is flipped; logo "up" is +Y

def wrap(mesh):
    """Bend a flat emblem (X along the horn, Y around it, Z out of the surface) onto the cone at +Z."""
    v = mesh.vertices.copy()
    c = 1 / np.sqrt(1 + horn_slope(EMBLEM_X)**2)
    x = EMBLEM_X + v[:, 0] * c
    r = horn_r(x)
    theta = np.pi/2 - v[:, 1] / r
    slope = horn_slope(x)
    n = np.column_stack([-slope, np.cos(theta), np.sin(theta)]) / np.sqrt(1 + slope**2)[:, None]
    surface = np.column_stack([x, r*np.cos(theta), r*np.sin(theta)])
    mesh.vertices = surface + v[:, 2:3] * n
    mesh.fix_normals()
    return mesh

def emblem(poly, low, high, radius, depth_radius, name, colour, rough=.3):
    from build_models import bevel
    flat = bevel(poly, low, high, radius, colour, name, depth_radius=depth_radius, segments=6)
    flat = flat.subdivide_to_size(.06)
    flat.merge_vertices()
    mesh = wrap(flat)
    assert mesh.is_watertight, name
    props.add(mesh, name, colour, rough, 0)

emblem(logo_poly(paths[0]), -.02, .035, .012, .018, 'Emblem_Outline', 'Cream_Edge', .34)
for n, node in enumerate(paths[1:3], 1):
    emblem(logo_poly(node), .03, .085, .018, .02, f'Emblem_{"S" if n == 1 else "Star"}', 'Raspberry', .24)
for n, node in enumerate(paths[3:], 1):
    emblem(logo_poly(node), .08, .094, .004, .005, f'Emblem_Highlight_{n}', 'Cream', .28)

# ------------------------------------------------------------- pistol grip ---
GRIP_PIVOT = np.array([-.40, -.55])
GRIP_MATRIX = rotation_about(np.radians(18), GRIP_PIVOT)
def grip(shape, low, high, radius, depth_radius, name, colour, rough=.3, metallic=0):
    props.solid(shape, low, high, radius, name, colour, rough, metallic, depth_radius=depth_radius,
                segments=10, matrix=GRIP_MATRIX @ trimesh.transformations.translation_matrix([*GRIP_PIVOT, 0]))

grip(rounded_rect(-.47, -2.35, .43, .15, .2), -.36, .36, .10, .14, 'Grip_Core', 'Raspberry', .26)
for side, label in ((1, 'Front'), (-1, 'Back')):
    lo, hi = sorted((side * .32, side * .42))
    grip(rounded_rect(-.34, -2.24, .35, .15, .17), lo, hi, .05, .04, f'Grip_Panel_{label}', 'Cream', .26)
    lo, hi = sorted((side * .395, side * .445))
    grip(rounded_rect(-.49, -2.20, .45, -2.12, .035), lo, hi, .012, .012, f'Grip_Band_{label}', 'Gold', .22, .4)
grip(rounded_rect(.05, -1.55, .72, -.62, .24), -.30, .30, .09, .12, 'Trigger_Housing', 'Raspberry', .26)
trigger = Polygon([(.20, -.84), (.58, -.84), (.70, -1.40), (.36, -1.42)]).buffer(-.06, quad_segs=8).buffer(.06, quad_segs=8)
grip(trigger, -.37, .37, .05, .06, 'Trigger', 'Gold', .22, .4)
for side, label in ((1, 'front'), (-1, 'back')):
    pin = trimesh.creation.uv_sphere(radius=.06, count=[14, 28])
    pin.apply_scale([1, 1, .55])
    pin.apply_translation([-.14, -.72, side * .415])
    place(pin, GRIP_MATRIX @ trimesh.transformations.translation_matrix([*GRIP_PIVOT, 0]))
    props.add(pin, f'Grip_Pin_{label}', 'Gold', .24, .4)

props.export('Sembang_Megaphone')
