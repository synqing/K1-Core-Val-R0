import bpy, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "J1_GT-USB-7005A.blend"))
m = bpy.data.materials.get("MAT_vendor_reference")
b = m.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.365, 0.425, 0.510, 1.0)
b.inputs["Roughness"].default_value = 0.68
lt = bpy.data.objects.get("CAVITY_FILL")
lt.location = (-5, -24, 3.2); lt.data.size = 22.0; lt.data.size_y = 22.0*0.65
lt.data.energy = 7.5 * (22.0*22.0*0.65) * 3.141592653589793
bpy.ops.wm.save_mainfile(filepath=os.path.join(HERE, "J1_GT-USB-7005A.blend"))
print("BLEND SAVED with corrected reference clay + cavity fill", flush=True)
sc = bpy.context.scene; sc.cycles.samples = 256
cam = sc.camera
ref = bpy.data.objects.get("REF_vendor_STEP_GT-USB-7005A")
if ref: ref.hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("J1_"): o.hide_render = False
    if o.name.startswith("PCB_REF"): o.hide_render = False
def shot(loc, aim, path, lens, res, ortho=None):
    cam.location = loc
    d = (Vector(aim)-Vector(loc)).normalized()
    cam.rotation_euler = d.to_track_quat('-Z','Y' if abs(d.z)<0.999 else 'Z').to_euler()
    cam.data.type = 'ORTHO' if ortho else 'PERSP'
    if ortho: cam.data.ortho_scale = ortho
    cam.data.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(HERE, path)
    bpy.ops.render.render(write_still=True); print("  ->", path, flush=True)
shot((-18,-24,13), (0,-0.5,-0.3), "render_05_on_1p60mm_board.png", 70, (2200,1500))
shot((-40,0.15,-0.40), (0,0.15,-0.40), "render_06_side_board_sink_ortho.png", 70, (2000,900), ortho=17.0)
shot((0,-40,-0.40), (0,0,-0.40), "render_07_front_elevation_ortho.png", 70, (1700,1200), ortho=15.0)
print("DONE2", flush=True)
