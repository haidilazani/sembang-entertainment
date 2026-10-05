"""Raspberry clipboard: rounded board, loose cream sheets and a bent steel clip."""
import numpy as np
import trimesh
from PIL import Image
from scipy.ndimage import gaussian_filter
from shapely.geometry import Polygon
from props_common import Props, rounded_rect, place, rotation_about

COLOURS = {
    'Raspberry_Board': [239, 76, 122],     # Sembang raspberry #EF4C7A
    'Paper_Cream': [251, 250, 207],        # Sembang cream #FBFACF
    'Paper_Under': [241, 238, 190],
    'Clip_Cream': [251, 250, 207],
    'Clip_Blush': [249, 191, 197],         # Sembang blush #F9BFC5
    'Clip_Shadow': [150, 30, 72],
}
props = Props('clipboard', COLOURS)

BW, BH, BT = 3.6, 5.3, .10          # board width, height, thickness
TOP = BH / 2                         # y of the board's top edge
BOARD_Z = BT / 2
rng = np.random.default_rng(7)

# ------------------------------------------------ procedural board grain
TW, TH = 1024, round(1024 * BH / BW)
mottle = gaussian_filter(rng.normal(size=(TH, TW)), 38) * 14
fibre = gaussian_filter(rng.normal(size=(TH, TW)), (.7, 3.2)) * 7.5
fine = gaussian_filter(rng.normal(size=(TH, TW)), .8) * 3.2
flecks = (gaussian_filter(rng.random((TH, TW)), 1.1) > .575) * -9.0
tone = (mottle + fibre + fine + flecks)[..., None] * np.array([1.0, .62, .78])
base = np.array(COLOURS['Raspberry_Board'], float)
board_texture = base + tone
# cut board edges darken a touch towards the rim
yy, xx = np.mgrid[0:TH, 0:TW]
edge = np.minimum.reduce([xx, TW - 1 - xx, yy, TH - 1 - yy]) / TW
board_texture *= (1 - .17 * np.exp(-edge / .012))[..., None]
texture = Image.fromarray(np.clip(board_texture, 0, 255).astype('uint8'))
texture.save(props.out / 'Raspberry_Board.png')

# ----------------------------------------------------------------- the board
props.solid(rounded_rect(-BW/2, -BH/2, BW/2, BH/2, .2), -BOARD_Z, BOARD_Z, .028, 'Board_Panel',
            'Raspberry_Board', .72, 0, depth_radius=.034, texture=texture, planar_uv=True, segments=12)

# ------------------------------------------------------------ paper (2 sheets)
SHEET_W, SHEET_H = 3.1, 4.35
sheet_y1 = TOP - .6
under = rounded_rect(-SHEET_W/2, sheet_y1 - SHEET_H, SHEET_W/2, sheet_y1, .028)
props.solid(under, BOARD_Z - .002, BOARD_Z + .007, .003, 'Paper_Under_Sheet', 'Paper_Under', .94, 0,
            depth_radius=.0035, segments=6,
            matrix=rotation_about(np.radians(-.9), (0, sheet_y1)) @ trimesh.transformations.translation_matrix([.02, -.01, 0]))
top_sheet = rounded_rect(-SHEET_W/2, sheet_y1 - SHEET_H + .035, SHEET_W/2, sheet_y1, .028)
props.solid(top_sheet, BOARD_Z + .006, BOARD_Z + .0165, .003, 'Paper_Sheet', 'Paper_Cream', .92, 0,
            depth_radius=.0035, segments=6)

# ------------------------------------------------------------------ steel clip
CLIP_Z0, CLIP_Z1 = -BOARD_Z - .03, BOARD_Z + .095     # wraps over the top edge of the board
def clip_outline():
    pts = [(-.93, -.84), (.93, -.84), (.93, -.30), (.84, -.06), (.50, .10), (.34, .26),
           (.26, .31), (-.26, .31), (-.34, .26), (-.50, .10), (-.84, -.06), (-.93, -.30)]
    shape = Polygon(pts).buffer(-.07, quad_segs=12).buffer(.07, quad_segs=12)
    return shape.simplify(.002)

outline = clip_outline()
shift = trimesh.transformations.translation_matrix([0, TOP, 0])
props.solid(outline, CLIP_Z0, CLIP_Z1, .034, 'Clip_Body', 'Clip_Cream', .38, 0, depth_radius=.045, matrix=shift)

# raised lower jaw that presses on the paper, with a dark slit above the sheet
jaw = rounded_rect(-.93, -.84, .93, -.62, .06)
props.solid(jaw, CLIP_Z1 - .02, CLIP_Z1 + .05, .026, 'Clip_Jaw', 'Clip_Blush', .36, 0,
            depth_radius=.03, matrix=shift)
slit = rounded_rect(-.80, -.60, .80, -.575, .012)
props.solid(slit, CLIP_Z1 - .005, CLIP_Z1 + .012, .004, 'Clip_Slit', 'Clip_Shadow', .6, .1,
            depth_radius=.005, segments=6, matrix=shift)

# hanging eyelet: polished ring around a dark opening
ring = trimesh.creation.torus(major_radius=.135, minor_radius=.032, major_sections=64, minor_sections=16)
ring.apply_translation([0, TOP + .11, CLIP_Z1])
props.add(ring, 'Clip_Eyelet_Ring', 'Clip_Blush', .36, 0)
hole = trimesh.creation.cylinder(radius=.14, height=.012, sections=64)
hole.apply_translation([0, TOP + .11, CLIP_Z1 + .002])
props.add(hole, 'Clip_Eyelet_Opening', 'Clip_Shadow', .7, .1)

# rivets, front and back
for n, x in enumerate((-.60, .60), 1):
    for side, label in ((1, 'front'), (-1, 'back')):
        dome = trimesh.creation.uv_sphere(radius=.085, count=[18, 36])
        dome.apply_scale([1, 1, .5])
        z = CLIP_Z1 + .004 if side == 1 else CLIP_Z0 - .004
        dome.apply_translation([x, TOP - .30, z])
        props.add(dome, f'Clip_Rivet_{label}_{n}', 'Clip_Blush', .38, 0)

props.export('Sembang_Clipboard')
