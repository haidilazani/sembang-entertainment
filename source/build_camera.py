"""Unbranded compact cinema camera with lens and a UV-mapped replaceable LCD."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import box
from PIL import Image,ImageDraw,ImageFont
from pygltflib import GLTF2
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
from build_models import bevel,PALETTE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'camera';OUT.mkdir(exist_ok=True)
COLORS={'Graphite_shell':[72,76,81],'Black_metal':[25,29,34],
 'Rubber':[20,23,27],'Dark_recess':[8,11,15],'Machined_metal':[141,150,160],
 'Red_record':[198,39,57],'Lens_glass':[20,47,60],'Lens_coating':[33,60,83],
 'Button_grey':[92,97,103],'Screen_Content':[255,255,255]}
PALETTE.update(COLORS)
scene=trimesh.Scene()
metadata=[]

def mat(color,rough=.45,metal=0):
 return PBRMaterial(name=color,baseColorFactor=COLORS[color]+[255],roughnessFactor=rough,metallicFactor=metal)

def add(m,name,color=None,rough=.45,metal=0,parent=None):
 if color:m.visual=TextureVisuals(material=mat(color,rough,metal))
 assert np.isfinite(m.vertices).all(),name
 if name!='Screen_Placeholder':assert m.is_watertight and m.is_winding_consistent,name
 # Model dimensions are authored in decimetres, exported in metres.
 normals=m.vertex_normals.copy();m.apply_scale(.1);m.vertex_normals=normals
 scene.add_geometry(m,geom_name=name,node_name=name,parent_node_name=parent)
 metadata.append({'name':name,'triangles':len(m.faces),'closed':bool(m.is_watertight)})

def rounded(name,size,centre,color,r=.025,rough=.5,metal=0,rotation=None,parent=None):
 w,h,d=size
 r=min(r,w*.22,h*.22)
 poly=box(-w/2,-h/2,w/2,h/2).buffer(-r).buffer(r,quad_segs=6)
 m=bevel(poly,-d/2,d/2,min(r*.7,d*.30),color,name,depth_radius=min(r*.7,d*.40),segments=6)
 if rotation is not None:m.apply_transform(rotation)
 m.apply_translation(centre)
 add(m,name,color,rough,metal,parent)

def cylinder(name,radius,depth,centre,color,axis='z',rough=.4,metal=0):
 m=trimesh.creation.cylinder(radius=radius,height=depth,sections=64)
 if axis=='y':m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]))
 if axis=='x':m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
 m.apply_translation(centre);add(m,name,color,rough,metal)

def ring(name,rmin,rmax,depth,centre,color,axis='z',rough=.35,metal=.5):
 # Small machined chamfers around an annular cross section.
 b=min(.009,depth*.20,(rmax-rmin)*.24)
 p=[[rmin,-depth/2+b],[rmin+b,-depth/2],[rmax-b,-depth/2],[rmax,-depth/2+b],
    [rmax,depth/2-b],[rmax-b,depth/2],[rmin+b,depth/2],[rmin,depth/2-b],[rmin,-depth/2+b]]
 m=trimesh.creation.revolve(np.array(p),sections=96)
 if axis=='y':m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]))
 if axis=='x':m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
 m.apply_translation(centre);m.fix_normals();add(m,name,color,rough,metal)

rounded('Camera_body',(1.30,.778,.59),(0,0,-.055),'Graphite_shell',.072,.56,.28)
rounded('Front_body_plate',(1.14,.69,.065),(-.045,-.012,.264),'Graphite_shell',.035,.48,.25)
rounded('Hand_grip',(.335,.715,.77),(.487,-.015,.019),'Rubber',.10,.88)
rounded('Grip_top_cap',(.33,.11,.51),(.484,.318,.079),'Graphite_shell',.032,.56,.25)
rounded('Grip_front_pad',(.22,.46,.035),(.486,-.083,.409),'Rubber',.040,.93)
rounded('Rear_control_plate',(.31,.59,.055),(.475,-.007,-.378),'Graphite_shell',.03,.56,.2)
rounded('Rear_LCD_recess',(.825,.49,.018),(-.18,-.03,-.359),'Dark_recess',.025,.70)
rounded('Rear_LCD_inner',(.75,.42,.014),(-.18,-.03,-.372),'Black_metal',.02,.63)

# Lens mount, stepped barrel, rubber focus and zoom rings, and coated glass.
cx,cy=-.155,-.018
ring('Lens_mount_flange',.298,.358,.042,(cx,cy,.318),'Machined_metal',metal=.82)
ring('Lens_mount_gasket',.292,.342,.025,(cx,cy,.347),'Rubber',metal=0)
ring('Lens_rear_barrel',.260,.333,.175,(cx,cy,.437),'Black_metal',rough=.34,metal=.40)
ring('Zoom_ring',.264,.371,.153,(cx,cy,.584),'Rubber',rough=.72,metal=0)
ring('Lens_middle_barrel',.266,.358,.106,(cx,cy,.712),'Black_metal',rough=.35,metal=.35)
ring('Focus_ring',.270,.383,.160,(cx,cy,.845),'Rubber',rough=.75,metal=0)
ring('Lens_front_barrel',.285,.376,.105,(cx,cy,.969),'Black_metal',rough=.31,metal=.55)
ring('Filter_rim',.308,.379,.034,(cx,cy,1.034),'Black_metal',rough=.28,metal=.64)
ring('Glass_retaining_ring',.288,.312,.022,(cx,cy,1.025),'Machined_metal',rough=.24,metal=.65)
ring('Inner_optical_ring',.183,.289,.050,(cx,cy,.995),'Dark_recess',rough=.35,metal=.1)
for tag,radius,z,depth in [('Zoom',.370,.584,.115),('Focus',.382,.845,.125)]:
 ribs=[]
 for a in np.linspace(0,2*np.pi,88,endpoint=False):
  rib=trimesh.creation.cylinder(radius=.0045,height=depth,sections=6)
  rib.apply_translation([cx+radius*np.cos(a),cy+radius*np.sin(a),z]);ribs.append(rib)
 add(trimesh.util.concatenate(ribs),tag+'_knurling','Rubber',.76)
glass=trimesh.creation.uv_sphere(radius=1,count=[32,64]);glass.apply_scale([.287,.287,.023]);glass.apply_translation([cx,cy,1.018]);add(glass,'Lens_front_glass','Lens_glass',.10,.62)
cylinder('Optical_inner_disc',.193,.009,(cx,cy,1.042),'Lens_coating',rough=.12,metal=.5)
ring('Optical_inner_reflection',.137,.144,.002,(cx,cy,1.049),'Lens_glass',rough=.1,metal=.6)

# Lens barrel switch details and one unmarked release button.
rounded('Lens_switch_base',(.048,.105,.115),(-.51,.015,.708),'Black_metal',.008,.5)
rounded('Lens_switch',(.055,.033,.048),(-.52,.035,.711),'Button_grey',.007,.6)
cylinder('Lens_release_button',.034,.027,(.243,-.162,.30),'Black_metal')

# Top controls, accessory shoe, sockets and record accents. No branding or lettering.
rounded('Top_deck',(.86,.043,.43),(-.145,.398,-.069),'Graphite_shell',.018,.52,.3)
for x,z in [(-.49,-.18),(.11,-.21),(-.45,.12)]:
 ring('Top_socket_'+str(x)+'_'+str(z),.022,.036,.012,(x,.429,z),'Machined_metal',axis='y',rough=.46,metal=.65)
 cylinder('Top_socket_well_'+str(x)+'_'+str(z),.023,.011,(x,.425,z),'Dark_recess',axis='y')
rounded('Accessory_shoe_base',(.235,.030,.21),(-.08,.434,-.065),'Dark_recess',.009,.5,.2)
for x in [-.184,.024]:rounded('Accessory_shoe_rail_'+str(x),(.025,.031,.225),(x,.455,-.065),'Machined_metal',.006,.3,.7)
cylinder('Top_control_dial',.084,.052,(.263,.422,-.157),'Black_metal',axis='y',rough=.48,metal=.2)
cylinder('Record_button_rim',.068,.033,(.476,.396,.08),'Black_metal',axis='y')
cylinder('Record_button',.047,.022,(.476,.420,.08),'Red_record',axis='y',rough=.38)
cylinder('Shutter_button',.049,.024,(.492,.38,.255),'Button_grey',axis='y',rough=.35,metal=.35)
for i,x in enumerate([-.32,-.16,.015]):cylinder('Top_function_button_'+str(i),.031,.019,(x,.427,.095),'Black_metal',axis='y',rough=.65)
rounded('Front_tally_light',(.043,.020,.012),(.335,.24,.302),'Red_record',.005,.28)
rounded('Rear_tally_light',(.038,.016,.012),(.22,.265,-.39),'Red_record',.004,.28)

# Rear controls with a thumb wheel and directional pad.
for i,(x,y) in enumerate([(.29,.24),(.48,.24),(.55,.10),(.55,-.27),(.30,-.27)]):
 cylinder('Rear_button_'+str(i),.030,.022,(x,y,-.413),'Black_metal',rough=.68)
ring('Rear_control_wheel',.065,.10,.026,(.424,-.095,-.421),'Black_metal',rough=.55,metal=.1)
cylinder('Rear_wheel_centre',.052,.031,(.424,-.095,-.434),'Button_grey',rough=.62)
for i,a in enumerate(np.arange(4)*np.pi/2):
 rounded('Wheel_direction_'+str(i),(.019,.009,.004),(.424+.081*np.cos(a),-.095+.081*np.sin(a),-.438),'Button_grey',.002,.6)
cylinder('Rear_joystick',.027,.040,(.328,.088,-.425),'Rubber',rough=.8)

# Cooling slots and port doors on the left side.
rot=trimesh.transformations.rotation_matrix(-np.pi/2,[0,1,0])
for i in range(9):rounded('Cooling_slot_'+str(i),(.24,.017,.008),(-.653,-.22+i*.045,-.10),'Dark_recess',.005,.9,rotation=rot)
rounded('Port_door',(.245,.23,.020),(-.662,.16,.09),'Rubber',.020,.86,rotation=rot)
rounded('Port_door_tab',(.035,.048,.014),(-.677,.08,.13),'Button_grey',.006,.7,rotation=rot)
rounded('Card_door',(.32,.43,.015),(.657,-.025,-.072),'Rubber',.018,.85,rotation=rot)
rounded('Base_plate',(.92,.019,.41),(-.06,-.397,-.041),'Black_metal',.018,.6,.3)
ring('Tripod_socket',.026,.044,.014,(-.12,-.412,-.04),'Machined_metal',axis='y',metal=.7)
cylinder('Tripod_socket_well',.027,.014,(-.12,-.415,-.04),'Dark_recess',axis='y')

# Side-opening monitor, held open and facing forward. A separate node can rotate.
rounded('LCD_hinge_bracket',(.060,.455,.092),(-.686,-.020,-.30),'Black_metal',.015,.53,.35)
cylinder('LCD_hinge_pin',.027,.445,(-.697,-.02,-.30),'Machined_metal',axis='y',rough=.35,metal=.6)
screen_centre=np.array([-1.137,-.020,-.30])
scene.graph.update(frame_to='LCD_Assembly',matrix=trimesh.transformations.translation_matrix(screen_centre*.1))
rounded('LCD_housing',(.846,.510,.054),(0,0,0),'Graphite_shell',.035,.54,.2,parent='LCD_Assembly')
rounded('LCD_bezel',(.807,.472,.018),(0,0,.033),'Dark_recess',.025,.63,parent='LCD_Assembly')
rounded('LCD_rear_cover',(.774,.433,.010),(0,0,-.032),'Black_metal',.024,.64,parent='LCD_Assembly')

# An ordinary UV quad is deliberate: it is easy to replace with logos/video/render textures.
w,h=.750,.421875
uv=np.array([[0,0],[1,0],[1,1],[0,1]],float)
screen=trimesh.Trimesh(vertices=[[-w/2,-h/2,.044],[w/2,-h/2,.044],[w/2,h/2,.044],[-w/2,h/2,.044]],faces=[[0,1,2],[0,2,3]],process=False)
image=Image.new('RGB',(1600,900),(17,26,36));draw=ImageDraw.Draw(image)
for x in range(0,1600,100):draw.line((x,0,x,900),fill=(26,39,51),width=2)
for y in range(0,900,100):draw.line((0,y,1600,y),fill=(26,39,51),width=2)
for x,y,sx,sy in [(110,100,1,1),(1490,100,-1,1),(110,800,1,-1),(1490,800,-1,-1)]:
 draw.line((x,y,x+sx*90,y),fill=(117,151,158),width=5);draw.line((x,y,x,y+sy*90),fill=(117,151,158),width=5)
font='/System/Library/Fonts/Supplemental/Arial.ttf'
draw.text((800,411),'YOUR CONTENT',font=ImageFont.truetype(font,68),anchor='mm',fill=(211,225,224))
draw.text((800,500),'LOGO  /  IMAGE  /  VIDEO',font=ImageFont.truetype(font,29),anchor='mm',fill=(127,155,163))
image.save(OUT/'screen_placeholder.png')
screen.visual=TextureVisuals(uv=uv,material=PBRMaterial(name='Screen_Content',baseColorFactor=[255,255,255,255],baseColorTexture=image,roughnessFactor=1,metallicFactor=0,doubleSided=False))
add(screen,'Screen_Placeholder',parent='LCD_Assembly')

gltf=GLTF2().load_from_bytes(scene.export(file_type='glb',include_normals=True))
for material in gltf.materials:
 if material.name=='Screen_Content':
  material.extensions={'KHR_materials_unlit':{}}
 else:
  c=np.array(COLORS[material.name])/255
  material.pbrMetallicRoughness.baseColorFactor=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4).tolist()+[1]
gltf.extensionsUsed=list(set((gltf.extensionsUsed or [])+['KHR_materials_unlit']))
(OUT/'Cinema_Camera.glb').write_bytes(b''.join(gltf.save_to_bytes()))
obj,resources=trimesh.exchange.obj.export_obj(scene,include_normals=True,include_color=False,include_texture=True,return_texture=True,mtl_name='Cinema_Camera.mtl')
(OUT/'Cinema_Camera.obj').write_text(obj)
for name,data in resources.items():(OUT/name).write_bytes(data if isinstance(data,bytes) else data.encode())
manifest={'name':'Unbranded compact cinema camera','file':'Cinema_Camera.glb','units':'metres','body_width_m':.13,
 'screen':{'node':'Screen_Placeholder','material':'Screen_Content','assembly_node':'LCD_Assembly','uv':[0,0,1,1],'aspect_ratio':'16:9','size_m':[.075,.0421875]},
 'components':metadata,'bounds':scene.bounds.tolist(),'triangles':sum(len(m.faces) for m in scene.geometry.values())}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k!='components'},indent=2));print(len(metadata),'named meshes')
