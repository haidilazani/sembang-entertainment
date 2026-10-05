"""Trace the supplied artwork into bevelled, double-sided, material-coloured meshes."""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import trimesh
from pygltflib import GLTF2
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'models'
OUT.mkdir(exist_ok=True)
PALETTE = {'raspberry': [239,76,122], 'cream': [251,250,207], 'blush': [249,191,197]}
ART = np.array(Image.open(ROOT / 'Copy of studio sembang.png').convert('RGB'))
SPECS = [
    ('01_raspberry_cream', (298,410,555,690), 'raspberry', 'cream', 'cream'),
    ('02_blush_raspberry', (665,414,925,695), 'blush', 'raspberry', 'cream'),
    ('03_cream_raspberry', (1040,413,1300,690), 'cream', 'raspberry', 'raspberry'),
    ('04_raspberry_cream', (1408,415,1665,695), 'raspberry', 'cream', 'cream'),
]

def contours(mask, minimum=15):
    cs,_ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return sorted([c[:,0,:] for c in cs if cv2.contourArea(c)>minimum], key=lambda c: cv2.contourArea(c), reverse=True)

def polygon(points, centre, scale):
    p = gaussian_filter1d(points.astype(float), 1.05, axis=0, mode='wrap')
    p = (p-centre)*[scale,-scale]
    shape=Polygon(p).simplify(scale*.16, preserve_topology=True)
    assert shape.is_valid
    return orient(shape, sign=1)

def material(name):
    return PBRMaterial(name=name, baseColorFactor=PALETTE[name]+[255], metallicFactor=0,
        roughnessFactor=.48, doubleSided=False)

def flat(poly, z):
    verts, faces=trimesh.creation.triangulate_polygon(poly, engine='earcut')
    return trimesh.Trimesh(np.column_stack([verts,np.full(len(verts),z)]),faces,process=False)

def roundover_normals(mesh, poly, low, high, radius, depth_radius):
    """Analytical profile normals keep flat caps flat and rounded shoulders smooth."""
    from shapely import points, shortest_line, get_point, get_coordinates
    xy=mesh.vertices[:,:2]
    targets=points(xy)
    nearest=get_coordinates(get_point(shortest_line(targets,poly.boundary),1))
    outward=nearest-xy
    lengths=np.linalg.norm(outward,axis=1)
    on_edge=lengths<1e-7
    if on_edge.any():
        inner_boundary=poly.buffer(-.0001).boundary
        inside=get_coordinates(get_point(shortest_line(points(xy[on_edge]),inner_boundary),1))
        outward[on_edge]=xy[on_edge]-inside
    outward/=np.maximum(np.linalg.norm(outward,axis=1,keepdims=True),1e-12)
    centre=(low+high)/2
    midhalf=(high-low)/2-depth_radius
    dz=mesh.vertices[:,2]-centre
    sine=np.clip((abs(dz)-midhalf)/depth_radius,0,1)
    sine[np.isclose(abs(dz),(high-low)/2,atol=1e-7)]=1
    radial=np.sqrt(1-sine*sine)/radius
    vertical=np.sign(dz)*sine/depth_radius
    normals=np.column_stack([outward*radial[:,None],vertical])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    mesh.vertex_normals=normals

def bevel(poly, low, high, radius, color, name, depth_radius=None, segments=16):
    """Closed solid with smooth elliptical roundovers and planar caps."""
    depth_radius=radius if depth_radius is None else depth_radius
    poly=poly.simplify(1e-5, preserve_topology=True)
    inset=poly.buffer(-radius, quad_segs=4)
    assert inset.geom_type=='Polygon' and len(inset.interiors)==0
    parts=[]
    middle=trimesh.creation.extrude_polygon(poly, height=high-low-2*depth_radius, engine='earcut')
    middle.apply_translation([0,0,low+depth_radius])
    # Keep the middle walls; replace caps with bevel rings.
    middle.update_faces(abs(middle.face_normals[:,2])<.5)
    parts.append(middle)
    for side in [-1,1]:
        anchor = high-depth_radius if side==1 else low+depth_radius
        previous=poly
        previous_z=anchor
        for theta in np.linspace(0,np.pi/2,segments+1)[1:]:
            amount=radius*(1-np.cos(theta))
            inner=poly.buffer(-amount, quad_segs=4).simplify(1e-5, preserve_topology=True)
            z=anchor+side*depth_radius*np.sin(theta)
            ring=previous.difference(inner)
            verts,faces=trimesh.creation.triangulate_polygon(ring,engine='earcut')
            # Ring triangulation only has boundary vertices.
            from shapely import points, distance
            is_inner=distance(points(verts),inner.boundary)<1e-8
            zs=np.where(is_inner,z,previous_z)
            parts.append(trimesh.Trimesh(np.column_stack([verts,zs]),faces,process=False))
            previous,previous_z=inner,z
        parts.append(flat(previous,high if side==1 else low))
    mesh=trimesh.util.concatenate(parts)
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    # GEOS may insert a collinear boundary point during ring subtraction.
    # Split its neighbouring triangle so both surfaces share the same edge.
    for attempt in range(100):
        counts=np.bincount(mesh.edges_unique_inverse)
        boundary=mesh.edges_unique[counts==1]
        if not len(boundary): break
        candidates=np.unique(boundary)
        split=False
        for a,b in boundary:
            va,vb=mesh.vertices[[a,b]]
            delta=vb-va
            ts=(mesh.vertices[candidates]-va)@delta/(delta@delta)
            distances=np.linalg.norm(mesh.vertices[candidates]-(va+ts[:,None]*delta),axis=1)
            choices=candidates[(ts>1e-5)&(ts<1-1e-5)&(distances<1e-7)]
            if not len(choices): continue
            mid=choices[0]
            indices=np.flatnonzero(np.any(mesh.faces==a,axis=1)&np.any(mesh.faces==b,axis=1))
            if len(indices)!=1: continue
            fi=indices[0]
            tri=list(mesh.faces[fi])
            for j in range(3):
                u,v,w=tri[j],tri[(j+1)%3],tri[(j+2)%3]
                if {u,v}=={a,b}: break
            faces=np.delete(mesh.faces,fi,axis=0)
            mesh.faces=np.vstack([faces,[u,mid,w],[mid,v,w]])
            split=True
            break
        if not split: break
    mesh.fix_normals(multibody=True)
    
    if not mesh.is_watertight:
        edges=mesh.edges_unique[np.bincount(mesh.edges_unique_inverse)!=2]
        print(name, 'bad edges',len(edges),mesh.vertices[edges[:10]],flush=True)
    assert mesh.is_watertight, name
    assert mesh.is_winding_consistent and mesh.volume>0, name
    mesh.visual=TextureVisuals(material=material(color))
    mesh.metadata['name']=name
    roundover_normals(mesh,poly,low,high,radius,depth_radius)
    return mesh

def main():
    manifest=[]
    for index,(slug,box,fill,trim,highlight) in enumerate(SPECS,1):
        x0,y0,x1,y1=box
        crop=ART[y0:y1,x0:x1]
        names=list(PALETTE)
        distances=np.linalg.norm(crop[:,:,None,:].astype(float)-np.array(list(PALETTE.values()))[None,None,:,:],axis=3)
        labels=distances.argmin(axis=2)
        mask=(labels==names.index(trim)) & (distances.min(axis=2)<60)
        outline=contours(mask,100)[0]
        solid=np.zeros(mask.shape,'uint8')
        cv2.fillPoly(solid,[outline],1)
        centre=(outline.min(axis=0)+outline.max(axis=0))/2
        scale=3.0/(outline[:,1].max()-outline[:,1].min())
        outer=polygon(outline,centre,scale)
        fills=contours((labels==names.index(fill)) & solid.astype(bool),100)
        # Only the two large enclosed colour fields are S and star.
        fills=fills[:2]
        assert len(fills)==2
        face_polys=[polygon(p,centre,scale) for p in fills]
        # Highlights are small isolated colour islands inside each face.
        faces_mask=np.zeros(mask.shape,'uint8')
        cv2.fillPoly(faces_mask,fills,1)
        accents=contours((labels==names.index(highlight)) & faces_mask.astype(bool),25)
        assert len(accents)==4,(slug,len(accents))
        accent_polys=[polygon(p,centre,scale) for p in accents]
        scene=trimesh.Scene()
        def add(mesh,name): scene.add_geometry(mesh,geom_name=name,node_name=name)
        body=bevel(outer,-.25,.25,.11,trim,'outline_body',depth_radius=.23)
        add(body,'outline_body')
        # Slice the same curved body for the colour band, so its side profile
        # follows the roundover instead of adding a separate square-edged slab.
        side_band=trimesh.intersections.slice_mesh_plane(body,[0,0,1],[0,0,-.115],cap=True,engine='earcut')
        side_band=trimesh.intersections.slice_mesh_plane(side_band,[0,0,-1],[0,0,.115],cap=True,engine='earcut')
        side_band.vertices[:,:2]*=1.0006
        side_band.fix_normals()
        assert side_band.is_watertight and side_band.is_winding_consistent
        side_band.visual=TextureVisuals(material=material(fill))
        roundover_normals(side_band,outer,-.25,.25,.11,.23)
        add(side_band,'colour_side_band')
        for side,label in [(1,'front'),(-1,'back')]:
            for p,part in zip(face_polys,['S','star']):
                a,b=sorted([side*.220,side*.310])
                add(bevel(p,a,b,.045,fill,f'{part}_{label}',depth_radius=.043),f'{part}_{label}')
            for i,p in enumerate(accent_polys,1):
                a,b=sorted([side*.306,side*.320])
                add(bevel(p,a,b,.005,highlight,f'highlight_{label}_{i}',depth_radius=.006,segments=8),f'highlight_{label}_{i}')
        folder=OUT/slug
        folder.mkdir(exist_ok=True)
        # PNG/OBJ swatches are sRGB. glTF material factors must be linear RGB.
        gltf=GLTF2().load_from_bytes(scene.export(file_type='glb',include_normals=True))
        for mat in gltf.materials:
            rgb=np.array(PALETTE[mat.name])/255.0
            linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
            mat.pbrMetallicRoughness.baseColorFactor=linear.tolist()+[1.0]
        glb=b''.join(gltf.save_to_bytes())
        (folder/f'{slug}.glb').write_bytes(glb)
        obj,resources=trimesh.exchange.obj.export_obj(scene,include_normals=True,include_color=False,include_texture=True,return_texture=True,mtl_name=f'{slug}.mtl')
        (folder/f'{slug}.obj').write_text(obj)
        for name,data in resources.items():
            (folder/name).write_bytes(data if isinstance(data,bytes) else data.encode())
        # Editable, precisely registered vector contours accompany the 3D source.
        def path(p):
            coords=np.array(p.exterior.coords)*[1,-1]
            return 'M '+' L '.join(f'{x:.5f},{y:.5f}' for x,y in coords)+' Z'
        def hexcolor(name): return '#'+''.join(f'{v:02x}' for v in PALETTE[name])
        paths=[(outer,trim)]+[(p,fill) for p in face_polys]+[(p,highlight) for p in accent_polys]
        svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.6 -1.6 3.2 3.2">'+''.join(f'<path d="{path(p)}" fill="{hexcolor(c)}"/>' for p,c in paths)+'</svg>'
        (ROOT/'source'/f'{slug}.svg').write_text(svg)
        record=dict(id=index,name=slug,fill=fill,outline=trim,highlight=highlight,
            file=f'models/{slug}/{slug}.glb',bounds=scene.bounds.tolist(),
            meshes=len(scene.geometry),triangles=sum(len(m.faces) for m in scene.geometry.values()),
            all_parts_watertight=all(m.is_watertight for m in scene.geometry.values()))
        manifest.append(record)
        print(json.dumps(record),flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
