"""Shaded catalogue renders of exported accessory STLs, for the gallery.

    blender --background --python tools/render_preview.py -- OUTDIR STL [STL ...]

The line-art previews (`ExportSVG` + `project_to_viewport`) draw every edge, so a B-rep solid with
59 faces looks crisp while a Blender-decorated part with 2318 faces becomes an unreadable black
hatch - exactly backwards, since the decorated parts are the ones worth looking at. This renders
shaded instead: form reads from light, not from edge count, so a mesh and a solid of the same part
are directly comparable.

One Blender launch renders the whole list; process startup dominates otherwise. Output is one
`<stl stem>.png` per input, RGBA on a transparent film so the same image sits correctly on the
gallery's light and dark themes.

Deterministic by construction: fixed camera direction, fixed sun angles, fixed sample count, no
randomness and nothing read from the clock. Same STL in, same bytes out.
"""

from __future__ import annotations

import sys
import time
from math import sqrt
from pathlib import Path

import bpy
from mathutils import Vector

RES = 600
SAMPLES = 16
MARGIN = 1.12  # bounding-box slack so nothing kisses the frame edge
VIEW = Vector((-1.0, -1.1, 0.72)).normalized()  # three-quarter, same for every part
BASE_GREY = (0.62, 0.62, 0.63, 1.0)


def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material() -> bpy.types.Material:
    """Mid-grey matte with a little specular - enough sheen to read a dome or a chamfer."""
    mat = bpy.data.materials.new("catalogue")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = BASE_GREY
    bsdf.inputs["Roughness"].default_value = 0.42
    for name, value in (("Specular IOR Level", 0.4), ("Metallic", 0.0)):
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
    return mat


def add_light(name: str, rotation, energy: float, angle: float = 0.5) -> None:
    light = bpy.data.lights.new(name, type="SUN")
    light.energy = energy
    light.angle = angle  # soft shadow terminator
    obj = bpy.data.objects.new(name, light)
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)


def setup_world() -> None:
    """Key / fill / rim. Sun lamps, so shading does not change with part size."""
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.06, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    bpy.context.scene.world = world
    # Sun energy is irradiance: a few W/m^2 is a full exposure. Keep the key well under 2 or the
    # mid-grey clips to white and every dome and chamfer disappears into a flat silhouette.
    add_light("key", (0.95, 0.0, -0.62), 1.45, 0.45)
    add_light("fill", (1.15, 0.0, 2.10), 0.42, 0.9)
    add_light("rim", (1.75, 0.0, 1.05), 0.75, 0.25)


def setup_render(out_dir: Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True  # works on both gallery themes
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"  # grey stays grey
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = SAMPLES
        for attr, value in (("use_shadows", True), ("use_raytracing", False)):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)
    out_dir.mkdir(parents=True, exist_ok=True)


def setup_camera() -> bpy.types.Object:
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"  # fits deterministically from the bounding box
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = VIEW.to_track_quat("Z", "Y")
    return cam


def frame(cam: bpy.types.Object, obj: bpy.types.Object) -> None:
    """Fit the ortho camera to the object's world bounding box along the camera's own axes, so a
    3 g lens cover and a 40 g side skin both fill their frame the same way."""
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8.0
    right = cam.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    up = cam.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
    half_w = max(abs((c - centre).dot(right)) for c in corners)
    half_h = max(abs((c - centre).dot(up)) for c in corners)
    cam.data.ortho_scale = 2.0 * max(half_w, half_h) * MARGIN
    radius = max((c - centre).length for c in corners)
    cam.location = centre + VIEW * (radius * 4.0 + 50.0)
    cam.data.clip_start = 0.1
    cam.data.clip_end = radius * 12.0 + 500.0


def render_one(path: Path, out_dir: Path, cam: bpy.types.Object, mat: bpy.types.Material) -> float:
    t0 = time.perf_counter()
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    fresh = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not fresh:
        print(f"SKIP {path.name}: nothing imported", flush=True)
        return 0.0
    for obj in fresh:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = fresh[0]
    if len(fresh) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if not obj.modifiers:  # keep hard edges hard, smooth the domes
        mod = obj.modifiers.new("edge_split", "EDGE_SPLIT")
        mod.split_angle = 0.61  # ~35 deg
    frame(cam, obj)
    bpy.context.scene.render.filepath = str(out_dir / f"{path.stem}.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(obj, do_unlink=True)
    return time.perf_counter() - t0


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) < 2:
        print("usage: blender --background --python tools/render_preview.py -- OUTDIR STL [STL ...]")
        return 2
    out_dir, stls = Path(argv[0]), [Path(p) for p in argv[1:]]
    clear_scene()
    setup_render(out_dir)
    setup_world()
    cam = setup_camera()
    mat = make_material()
    times = []
    for path in stls:
        if not path.is_file():
            print(f"SKIP {path}: missing", flush=True)
            continue
        dt = render_one(path, out_dir, cam, mat)
        if dt:
            times.append(dt)
            print(f"RENDER {path.stem} {dt:.2f}s", flush=True)
    if times:
        total = sum(times)
        print(f"DONE {len(times)} parts in {total:.1f}s "
              f"(mean {total / len(times):.2f}s, max {max(times):.2f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
