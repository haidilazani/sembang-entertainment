"""Cream folded envelope with an organic raspberry wax seal and traced logo."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from shapely.geometry import Polygon,box
from pygltflib import GLTF2
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial
from build_models import bevel,PALETTE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'envelope'
OUT.mkdir(exist_ok=True)
PALETTE.update(paper=[247,240,215],paper_fold=[244,236,209],paper_flap=[251,245,224])
scene=trimesh.Scene()
seal_scene=trimesh.Scene()

def add(mesh,name,seal=False):
    assert mesh.is_watertight and mesh.is_winding_consistent,name
    assert np.isfinite(mesh.vertices).all(),name
    scene.add_geometry(mesh,geom_name=name,node_name=name)
    if seal:
        normals=mesh.vertex_normals.copy()
        copy=mesh.copy()
        copy.apply_translation([0,.38,-.19])
        copy.vertex_normals=normals
        seal_scene.add_geometry(copy,geom_name=name,node_name=name)

def paper(poly,low,high,color,name,radius=.016):
    poly=poly.buffer(-.04,quad_segs=10).buffer(.04,quad_segs=10)
    m=bevel(poly,low,high,radius,color,name,depth_radius=min((high-low)*.43,.022),segments=10)
    m.visual.material.roughnessFactor=.92
    add(m,name)

body=box(-3.2,-2.1,3.2,2.1).buffer(-.08).buffer(.08,quad_segs=16)
paper(body,-.075,.045,'paper','Envelope_body',.025)
paper(Polygon([(-3.18,2.07),(.30,-.02),(-3.18,-2.07)]),.04,.084,'paper_fold','Left_fold')
paper(Polygon([(3.18,2.07),(-.30,-.02),(3.18,-2.07)]),.04,.084,'paper_fold','Right_fold')
paper(Polygon([(-3.17,-2.08),(3.17,-2.08),(3.17,-1.92),(.13,.30),(-.13,.30),(-3.17,-1.92)]),.073,.119,'paper','Bottom_fold')
paper(Polygon([(-3.17,2.08),(3.17,2.08),(3.17,1.96),(.13,-.43),(-.13,-.43),(-3.17,1.96)]),.120,.176,'paper_flap','Closing_flap',.019)

# A pressed wax puddle: subtly uneven perimeter, raised rim and flat stamp bed.
count=224
theta=np.arange(count)*2*np.pi/count
edge=.765*(1+.025*np.sin(5*theta+.4)+.017*np.sin(9*theta-1.1)+.012*np.cos(13*theta+.8))
radial=np.linspace(.04,1,32)
verts=[[0,-.38,.19+.08]]
for rho in radial:
    # Outer wax curls up around the stamped, level central field.
    rim=.063*np.exp(-((rho-.87)/.105)**2)
    rolloff=.095*np.clip((rho-.94)/.06,0,1)**1.4
    height=.08+rim-rolloff
    wobble=(.009*np.sin(6*theta+.5)+.006*np.sin(11*theta))*np.clip((rho-.67)/.33,0,1)
    verts.extend(np.column_stack([edge*rho*np.cos(theta),-.38+edge*rho*np.sin(theta),.19+height+wobble]))
faces=[]
for j in range(count):faces.append([0,1+j,1+(j+1)%count])
for ring in range(len(radial)-1):
    for j in range(count):
        a=1+ring*count+j;b=1+ring*count+(j+1)%count;c=b+count;d=a+count
        faces.extend([[a,b,c],[a,c,d]])
bottom_start=len(verts)
verts.extend(np.column_stack([edge*np.cos(theta),-.38+edge*np.sin(theta),np.full(count,.176)]))
top_start=1+(len(radial)-1)*count
for j in range(count):
    a=top_start+j;b=top_start+(j+1)%count;c=bottom_start+(j+1)%count;d=bottom_start+j
    faces.extend([[a,c,b],[a,d,c]])
centre=len(verts);verts.append([0,-.38,.176])
for j in range(count):faces.append([centre,bottom_start+(j+1)%count,bottom_start+j])
wax=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
wax.fix_normals()
wax.visual=TextureVisuals(material=PBRMaterial(name='raspberry',baseColorFactor=PALETTE['raspberry']+[255],roughnessFactor=.32,metallicFactor=0))
add(wax,'Raspberry_wax_seal',True)

# The SVG paths were independently traced from the source PNG, design 03.
svg=ET.parse(ROOT/'source/03_cream_raspberry.svg').getroot()
paths=list(svg)
for i,node in enumerate(paths[1:]):
    numbers=np.array([float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',node.attrib['d'])]).reshape(-1,2)
    numbers*=np.array([.31,-.31])
    numbers[:,1]-=.38
    p=Polygon(numbers)
    color='cream' if i<2 else 'raspberry'
    low,high=(.267,.306) if i<2 else (.303,.310)
    name=['Cream_S','Cream_star','Logo_highlight_1','Logo_highlight_2','Logo_highlight_3','Logo_highlight_4'][i]
    m=bevel(p,low,high,.009 if i<2 else .0018,color,name,depth_radius=.017 if i<2 else .003,segments=10)
    m.visual.material.roughnessFactor=.38
    add(m,name,True)

def export(s,slug):
    gltf=GLTF2().load_from_bytes(s.export(file_type='glb',include_normals=True))
    for mat in gltf.materials:
        rgb=np.array(PALETTE[mat.name])/255
        linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
        mat.pbrMetallicRoughness.baseColorFactor=linear.tolist()+[1]
    (OUT/f'{slug}.glb').write_bytes(b''.join(gltf.save_to_bytes()))
    obj,resources=trimesh.exchange.obj.export_obj(s,include_normals=True,include_color=False,include_texture=True,return_texture=True,mtl_name=f'{slug}.mtl')
    (OUT/f'{slug}.obj').write_text(obj)
    for name,data in resources.items():(OUT/name).write_bytes(data if isinstance(data,bytes) else data.encode())
    return dict(name=slug,components=len(s.geometry),triangles=sum(len(m.faces) for m in s.geometry.values()),bounds=s.bounds.tolist(),all_components_closed=all(m.is_watertight for m in s.geometry.values()))

manifest=[export(scene,'Sembang_Cream_Envelope'),export(seal_scene,'Sembang_Wax_Seal')]
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
