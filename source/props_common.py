"""Shared helpers for the studio-prop builds (clapperboard, clipboard)."""
from pathlib import Path
import json
import numpy as np
import trimesh
from PIL import Image
from pygltflib import GLTF2
from shapely.geometry import Polygon, box
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial
from build_models import bevel, PALETTE

ROOT = Path(__file__).resolve().parents[1]


def rounded_rect(x0, y0, x1, y1, radius, corners='all'):
    """Rounded rectangle polygon. corners='bottom' leaves the top corners square."""
    shape = box(x0, y0, x1, y1).buffer(-radius, quad_segs=14).buffer(radius, quad_segs=14)
    if corners == 'bottom':
        shape = shape.union(box(x0, (y0 + y1) / 2, x1, y1))
    return shape


def srgb_to_linear(rgb):
    rgb = np.asarray(rgb, float) / 255
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


class Props:
    """Collects closed, named, material-coloured components and exports them."""

    def __init__(self, folder, colours):
        self.out = ROOT / folder
        self.out.mkdir(exist_ok=True)
        self.colours = colours
        PALETTE.update(colours)
        self.scene = trimesh.Scene()
        self.rough = {}
        self.metal = {}

    def material(self, colour, rough, metallic, texture=None):
        return PBRMaterial(name=colour, baseColorFactor=[255, 255, 255, 255] if texture is not None
                           else list(self.colours[colour]) + [255],
                           baseColorTexture=texture, roughnessFactor=rough, metallicFactor=metallic)

    def add(self, mesh, name, colour, rough=.5, metallic=0, texture=None, uv=None):
        assert np.isfinite(mesh.vertices).all(), name
        assert mesh.is_watertight and mesh.is_winding_consistent, name
        normals = mesh.vertex_normals.copy()
        mesh.visual = TextureVisuals(uv=uv, material=self.material(colour, rough, metallic, texture))
        mesh.vertex_normals = normals
        self.scene.add_geometry(mesh, geom_name=name, node_name=name)
        return mesh

    def solid(self, poly, low, high, radius, name, colour, rough=.5, metallic=0,
              depth_radius=None, segments=10, matrix=None, texture=None, planar_uv=False):
        mesh = bevel(poly, low, high, radius, colour, name, depth_radius=depth_radius, segments=segments)
        if matrix is not None:
            place(mesh, matrix)
        uv = None
        if planar_uv:
            x0, y0, x1, y1 = poly.bounds
            uv = np.column_stack([(mesh.vertices[:, 0] - x0) / (x1 - x0), (mesh.vertices[:, 1] - y0) / (y1 - y0)])
        return self.add(mesh, name, colour, rough, metallic, texture, uv)

    def export(self, slug):
        gltf = GLTF2().load_from_bytes(self.scene.export(file_type='glb', include_normals=True))
        for mat in gltf.materials:
            if mat.pbrMetallicRoughness.baseColorTexture is None:
                mat.pbrMetallicRoughness.baseColorFactor = srgb_to_linear(self.colours[mat.name]).tolist() + [1]
        (self.out / f'{slug}.glb').write_bytes(b''.join(gltf.save_to_bytes()))
        obj, resources = trimesh.exchange.obj.export_obj(
            self.scene, include_normals=True, include_color=False, include_texture=True,
            return_texture=True, mtl_name=f'{slug}.mtl')
        (self.out / f'{slug}.obj').write_text(obj)
        for name, data in resources.items():
            (self.out / name).write_bytes(data if isinstance(data, bytes) else data.encode())
        record = dict(name=slug, components=len(self.scene.geometry),
                      triangles=sum(len(m.faces) for m in self.scene.geometry.values()),
                      bounds=self.scene.bounds.tolist(),
                      all_components_closed=all(m.is_watertight for m in self.scene.geometry.values()),
                      parts=sorted(self.scene.geometry))
        (self.out / 'manifest.json').write_text(json.dumps(record, indent=2))
        print(json.dumps({k: v for k, v in record.items() if k != 'parts'}, indent=2))
        return record


def place(mesh, matrix):
    """Apply a rigid transform and carry the analytic vertex normals along with it."""
    normals = mesh.vertex_normals.copy() @ np.asarray(matrix)[:3, :3].T
    mesh.apply_transform(matrix)
    mesh.vertex_normals = normals
    return mesh


def rotation_about(angle, point):
    """Z-axis rotation about a point in the XY plane."""
    return trimesh.transformations.rotation_matrix(angle, [0, 0, 1], [point[0], point[1], 0])
