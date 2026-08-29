# fast fix-up: reopen the built .blend, correct the reference clay colour and
# the cavity fill, then re-render only the frames those two affect.
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "J1_GT-USB-7005A.blend"))
m = bpy.data.materials.get("MAT_vendor_reference")
if m:
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.365, 0.425, 0.510, 1.0)
    b.inputs["Roughness"].default_value = 0.68
    print("reference clay ->", b.inputs["Base Color"].default_value[:])
lt = bpy.data.objects.get("CAVITY_FILL")
if lt:
    lt.location = (-5, -24, 3.2); lt.data.size = 22.0; lt.data.size_y = 22.0*0.65
    lt.data.energy = 7.5 * (22.0*22.0*0.65) * 3.141592653589793
    print("cavity fill ->", lt.data.energy)
sc = bpy.context.scene
sc.cycles.samples = 256
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.012
cam = sc.camera
def shot(loc, aim, path, lens, res, ortho=None):
    cam.location = loc
    d = (Vector(aim)-Vector(loc)).normalized()
    cam.rotation_euler = d.to_track_quat('-Z', 'Y' if abs(d.z) < 0.999 else 'Z').to_euler()
    cam.data.type = 'ORTHO' if ortho else 'PERSP'
    if ortho: cam.data.ortho_scale = ortho
    cam.data.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(HERE, path)
    bpy.ops.render.render(write_still=True); print("  ->", path)
mine = [o for o in bpy.data.objects if o.name.startswith("J1_")]
ref  = bpy.data.objects.get("REF_vendor_STEP_GT-USB-7005A")
for o in bpy.data.objects:
    if o.name.startswith("PCB_REF"): o.hide_render = True
for o in mine: o.hide_render = False
if ref: ref.hide_render = True
shot((-17,-27,12), (0,-0.8,-0.25), "render_01_hero.png", 70, (2200,1500))
shot((0,-40,-0.40), (0,0,-0.40), "render_02_mating_face.png", 100, (1700,1700))
for which in ("mine","ref"):
    for o in mine: o.hide_render = (which != "mine")
    if ref: ref.hide_render = (which != "ref")
    shot((0,0.15,40), (0,0.15,0), f"verify_top_{which}.png", 70, (1500,1300), ortho=13.5)
    shot((0,-40,-0.40), (0,0,-0.40), f"verify_front_{which}.png", 70, (1500,900), ortho=13.5)
print("REFRESH DONE")
