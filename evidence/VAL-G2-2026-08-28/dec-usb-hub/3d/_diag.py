import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("jb", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "j1_build.py"))
# don't exec (it runs main); replicate minimal pieces instead
from mathutils import Vector
def clean():
    for c in (bpy.data.objects, bpy.data.meshes): 
        for x in list(c): c.remove(x, do_unlink=True)
clean()
Zo = -0.400
def Z(sy): return sy + Zo
def rrect(hw,hh,r,seg=20):
    cx,cz=hw-r,hh-r; pts=[]
    for ox,oz,a0 in ((cx,cz,0.0),(-cx,cz,math.pi/2),(-cx,-cz,math.pi),(cx,-cz,3*math.pi/2)):
        for i in range(seg+1):
            t=a0+(math.pi/2)*i/seg; pts.append((ox+r*math.cos(t), oz+r*math.sin(t)))
    return pts
def tube(outer,inner,y0,y1):
    bm=bmesh.new(); n=len(outer)
    O0=[bm.verts.new((p[0],y0,p[1])) for p in outer]; O1=[bm.verts.new((p[0],y1,p[1])) for p in outer]
    I0=[bm.verts.new((p[0],y0,p[1])) for p in inner]; I1=[bm.verts.new((p[0],y1,p[1])) for p in inner]
    for i in range(n):
        j=(i+1)%n
        bm.faces.new((O0[i],O0[j],O1[j],O1[i])); bm.faces.new((I1[i],I1[j],I0[j],I0[i]))
        bm.faces.new((O0[j],O0[i],I0[i],I0[j])); bm.faces.new((O1[i],O1[j],I1[j],I1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); return bm
outer=[(x,Z(z)) for x,z in rrect(4.375,1.480,1.15)]
inner=[(x,Z(z)) for x,z in rrect(4.175,1.280,0.95)]
bm=tube(outer,inner,-5.0,1.7); me=bpy.data.meshes.new("shell"); bm.to_mesh(me); bm.free()
sh=bpy.data.objects.new("shell",me); bpy.context.scene.collection.objects.link(sh)
def zmax(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
    v=max(vv.co.z for vv in m.vertices); e.to_mesh_clear(); return round(v,4)
print("shell only zmax", zmax(sh))
DEPTH,WALL=0.075,0.200; rx,ry,rz=0.46,0.78,0.30
z_out=1.480+Zo
helpers=[]
for tag,zc,op in (("cut", z_out+(rz-DEPTH), 'DIFFERENCE'),("add", z_out+(rz-DEPTH)-WALL,'UNION')):
    b=bmesh.new(); bmesh.ops.create_uvsphere(b,u_segments=28,v_segments=16,radius=1.0)
    bmesh.ops.scale(b,vec=Vector((rx,ry,rz)),verts=b.verts[:])
    bmesh.ops.translate(b,vec=Vector((2.55,-3.05,zc)),verts=b.verts[:])
    bmesh.ops.recalc_face_normals(b,faces=b.faces[:])
    m2=bpy.data.meshes.new(tag); b.to_mesh(m2); b.free()
    o=bpy.data.objects.new("_"+tag,m2); bpy.context.scene.collection.objects.link(o)
    print("  ",tag,"zc",round(zc,4),"span",round(zc-rz,4),round(zc+rz,4))
    helpers.append((o,op))
for o,op in helpers:
    if op=='UNION':
        mo=sh.modifiers.new("add",'BOOLEAN'); mo.operation='UNION'; mo.object=o; mo.solver='EXACT'
print("after UNION zmax", zmax(sh))
for o,op in helpers:
    if op=='DIFFERENCE':
        mo=sh.modifiers.new("cut",'BOOLEAN'); mo.operation='DIFFERENCE'; mo.object=o; mo.solver='EXACT'
print("after DIFF  zmax", zmax(sh))
print("modifier stack:", [(m.name,m.operation) for m in sh.modifiers])
