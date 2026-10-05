"""Film clapperboard: striped hinged clapper arm, rounded slate and lettered face."""
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from shapely.affinity import translate
from shapely.geometry import Polygon, box
from props_common import Props, rounded_rect, place, rotation_about, ROOT

COLOURS = {
    'Slate_Raspberry': [239, 76, 122],     # Sembang raspberry #EF4C7A
    'Slate_Face': [226, 62, 108],          # slightly deeper raspberry for the lettered plate
    'Clapper_Raspberry': [199, 46, 92],    # deeper raspberry for the sticks
    'Stripe_Cream': [251, 250, 207],       # Sembang cream #FBFACF
    'Hinge_Blush': [249, 191, 197],        # Sembang blush #F9BFC5
    'Rivet_Cream': [251, 250, 207],
}
props = Props('clapperboard', COLOURS)

W = 4.4            # slate width
BODY_H = 2.9       # slate height
STICK_H = .39      # clapper stick height
YT = .62           # top of slate
ARM_ANGLE = np.radians(11)
STICK_Z, BODY_Z, HINGE_Z = .15, .12, .19

# ---------------------------------------------------------------- slate body
props.solid(rounded_rect(-W/2, YT-BODY_H, W/2, YT, .2, 'bottom'), -BODY_Z, BODY_Z, .05,
            'Slate_Body', 'Slate_Raspberry', .5, 0, depth_radius=.05)

# ------------------------------------------------- lettered face (textured)
INSET = .09
FX0, FX1 = -W/2 + INSET, W/2 - INSET
FY0, FY1 = YT - BODY_H + INSET, YT - .05
FW, FH = FX1 - FX0, FY1 - FY0
TW = 2048
TH = round(TW * FH / FW)
SCALE = W / 340                       # reference artwork: 340 px wide slate

def px(ix, iy):
    """Reference-artwork pixel (slate spans x 105-445, y 228-450) -> texture pixel."""
    x = -W/2 + (ix - 105) * SCALE
    y = YT - (iy - 228) * SCALE
    return (x - FX0) / FW * TW, (FY1 - y) / FH * TH

def unit(pixels):
    return pixels * SCALE / FW * TW   # reference pixels -> texture pixels

face = Image.new('RGB', (TW, TH), tuple(COLOURS['Slate_Face']))
# very soft vertical sheen so the slate does not read as a flat fill
sheen = np.linspace(1.03, .98, TH)[:, None, None] * np.ones((TH, TW, 3))
face = Image.fromarray(np.clip(np.asarray(face) * sheen, 0, 255).astype('uint8'))
draw = ImageDraw.Draw(face)
CHALK = (251, 250, 207)
LINE = (251, 250, 207)

def font(file, cap_px):
    return ImageFont.truetype(f'C:/Windows/Fonts/{file}', round(unit(cap_px) / .716))

def line(x0, y0, x1, y1, width=1.7):
    (ax, ay), (bx, by) = px(x0, y0), px(x1, y1)
    draw.line([(ax, ay), (bx, by)], fill=LINE, width=round(unit(width)))

draw.text(px(275, 264), 'STUDIO', font=font('arialbd.ttf', 17.5), fill=CHALK, anchor='ms')
LEFT, RIGHT = 120, 430
for y in (277, 335, 360, 385, 411, 437):
    line(LEFT, y, RIGHT, y)
for x in (232, 315):
    line(x, 277, x, 335)
for text, cx in (('SCENE', 176), ('TAKE', 273.5), ('ROLL', 371)):
    draw.text(px(cx, 299), text, font=font('arialbi.ttf', 11.5), fill=CHALK, anchor='ms')
for text, y in (('DATE', 360), ('PROD.CO.', 385), ('DIRECTOR', 411), ('CAMERAMAN', 437)):
    draw.text(px(LEFT + 3, y - 5), text, font=font('arialbi.ttf', 9.6), fill=CHALK, anchor='ls')
face.save(props.out / 'Slate_Face.png')

props.solid(rounded_rect(FX0, FY0, FX1, FY1, .09), BODY_Z - .004, BODY_Z + .012, .006,
            'Slate_Face', 'Slate_Face', .62, 0, depth_radius=.006, segments=6,
            texture=face, planar_uv=True)

# ------------------------------------------------------------- clapper sticks
FIXED_Y0 = YT - .03
PIVOT = np.array([-W/2 + .30, FIXED_Y0 + STICK_H + .012])
ARM_MATRIX = trimesh.transformations.translation_matrix([*PIVOT, 0]) @ rotation_about(ARM_ANGLE, (0, 0))
ARM_X0, ARM_X1 = -.28, W - .30

def stripes(x_start, x_end, y0, y1, slant):
    """Parallelogram stripes clipped to a margin inside the stick."""
    period, width = .54, .27
    clip = box(x_start, y0 + .05, x_end, y1 - .05)
    out = []
    for i in range(-2, 12):
        x = x_start + i * period
        shape = Polygon([(x, y0), (x + width, y0), (x + width + slant, y1), (x + slant, y1)])
        shape = shape.intersection(clip).buffer(-.012, quad_segs=4).buffer(.012, quad_segs=4)
        if shape.geom_type == 'Polygon' and shape.area > .012:
            out.append(shape)
    return out

def add_stick(prefix, outline, shapes, matrix=None):
    props.solid(outline, -STICK_Z, STICK_Z, .04, f'{prefix}_Stick', 'Clapper_Raspberry', .46, 0,
                depth_radius=.05, matrix=matrix)
    for n, shape in enumerate(shapes, 1):
        for side, label in ((1, 'front'), (-1, 'back')):
            lo, hi = sorted((side * (STICK_Z - .004), side * (STICK_Z + .012)))
            props.solid(shape, lo, hi, .004, f'{prefix}_Stripe_{label}_{n}', 'Stripe_Cream', .42, 0,
                        depth_radius=.005, segments=6, matrix=matrix)

add_stick('Fixed', rounded_rect(-W/2, FIXED_Y0, W/2, FIXED_Y0 + STICK_H, .075),
          stripes(-W/2 + .88, W/2 - .10, FIXED_Y0, FIXED_Y0 + STICK_H, .21))
add_stick('Clapper_Arm', rounded_rect(ARM_X0, 0, ARM_X1, STICK_H, .075),
          stripes(.66, ARM_X1 - .10, 0, STICK_H, -.21), ARM_MATRIX)

# --------------------------------------------------------------------- hinge
def arm_top_y(x):
    top_left = (ARM_MATRIX @ [ARM_X0, STICK_H, 0, 1])[:2]
    return top_left[1] + (x - top_left[0]) * np.tan(ARM_ANGLE)

HX0, HX1 = -W/2 - .01, -W/2 + .84
hinge = Polygon([(HX0, FIXED_Y0), (HX1, FIXED_Y0), (HX1, arm_top_y(HX1) + .02), (HX0, arm_top_y(HX0) + .02)])
hinge = hinge.buffer(-.07, quad_segs=10).buffer(.07, quad_segs=10)
props.solid(hinge, -HINGE_Z, HINGE_Z, .04, 'Hinge_Block', 'Hinge_Blush', .42, 0, depth_radius=.05)
for n, (dx, dy) in enumerate(((.25, .66), (.62, .24)), 1):
    for side, label in ((1, 'front'), (-1, 'back')):
        dome = trimesh.creation.uv_sphere(radius=.075, count=[18, 36])
        dome.apply_scale([1, 1, .55])
        dome.apply_translation([HX0 + dx, FIXED_Y0 + dy, side * HINGE_Z])
        props.add(dome, f'Hinge_Rivet_{label}_{n}', 'Rivet_Cream', .34, 0)

props.export('Sembang_Clapperboard')
