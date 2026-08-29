# ---------------------------------------------------------------------------
#  J1  -  G-Switch GT-USB-7005A  (LCSC C5250872)
#  USB Type-C 24P receptacle, horizontal, board-sink 1.9 / CH 0.4, L=10.30 mm
#
#  Parametric Blender rebuild.  Every dimension below is measured from the
#  MANUFACTURER STEP  (dg-switch.com/uploads/soft/230408/GT-USB-7005A-3D.zip,
#  sha256 bac2724e...c0c88fa) tessellated at 0.0035 mm and re-datumed.
#
#  DATUM:  Z = 0  is the PCB TOP SURFACE.
#          Y = 0 .. -5.00  is the mating direction (mouth faces -Y).
#          X = 0  is the connector centre line.
#  Units:  1 Blender unit = 1 mm.
#
#  run:  blender --background --python j1_build.py
# ---------------------------------------------------------------------------
import bpy, bmesh, math, os, json, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
OUT  = HERE

# --- datum conversion from the STEP frame -----------------------------------
PCB_TOP_IN_STEP_Y = 0.400          # measured: SMT tail solder faces
def Z(sy):  return sy - PCB_TOP_IN_STEP_Y     # STEP Y  -> Blender Z
def Y(sz):  return -sz                        # STEP Z  -> Blender Y

D = dict(
  # shell (stainless, Ni plated) -- rounded rectangle, wall 0.200
  shell_out_hw = 4.375, shell_out_hh = 1.480, shell_out_r = 1.150,
  shell_in_hw  = 4.175, shell_in_hh  = 1.280, shell_in_r  = 0.950,
  shell_y_front = Y(5.000), shell_y_back = Y(-1.700),
  # tongue
  tongue_hw_wide = 3.365, tongue_hw_narrow = 3.200,
  tongue_core_hh = 0.335, tongue_face_hh = 0.350,
  tongue_y_tip = Y(4.450), tongue_y_step = Y(2.100), tongue_y_root = Y(0.000),
  # contacts  (24 = 12 per row, 0.25 wide, 0.50 pitch, span 5.50)
  pitch = 0.500, c_w = 0.250, n_per_row = 12,
  c_y_front = Y(4.200), c_y_back = Y(1.200),
  c_band_front = Y(3.135), c_band_back = Y(2.204),
  c_proud = 0.0075,
  # mid plate
  mid_hh = 0.100,
  # rear housing (black LCP UL94 V-0) + ground plate
  rear_hw = 4.575, rear_y0 = Y(-1.650), rear_y1 = Y(-5.300),
  rear_z0 = Z(0.600), rear_z1 = Z(1.960),
  gp_hw = 3.980, gp_y0 = Y(-1.830), gp_y1 = Y(-4.920),
  gp_z0 = Z(1.960), gp_z1 = Z(2.160),
  skirt_x0 = 3.225, skirt_x1 = 4.575, skirt_z0 = Z(-0.700),
  # SMT tails  (12)
  tail_w = 0.200, tail_z0 = Z(0.400), tail_z1 = Z(0.500),
  tail_y0 = Y(-4.110), tail_y1 = Y(-4.810), tail_rise_z = Z(0.860),
  # through-hole pins (12)  measured X centres / Y bands
  th_rowA_x = (0.850, 1.700, 2.500), th_rowA_y = (Y(-2.300), Y(-2.700)),
  th_rowB_x = (0.400, 1.300, 2.875), th_rowB_y = (Y(-3.175), Y(-3.500)),
  th_w = 0.200, th_z_top = Z(1.260), th_z_bot = Z(-0.700),
  # mounting legs (4)
  leg_x_in = 3.050, leg_x_knee = 5.975, leg_x_out = 6.175,
  leg_tab_z0 = Z(0.500), leg_tab_z1 = Z(0.700), leg_drop_z = Z(-0.500),
  leg_front_y = (Y(1.700), Y(0.700)), leg_rear_y = (Y(-2.150), Y(-3.150)),
  # reference PCB
  pcb_t = 1.600, pcb_cut_hw = 4.700, pcb_cut_y1 = Y(-5.450),
)
CONTACT_X = [(-5.5/2) + i*D['pitch'] for i in range(D['n_per_row'])]   # -2.75 .. +2.75

# ---------------------------------------------------------------------------
#  bmesh helpers
# ---------------------------------------------------------------------------
def new_obj(name, bm, coll):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.validate(); ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def rrect(hw, hh, r, seg=20, step=None):
    """closed CCW rounded-rectangle profile in (x, z).
       step != None subdivides the straight runs to <= step mm (needed so the
       formed latch dimples can be displaced rather than booleaned)."""
    cx, cz = hw - r, hh - r
    arcs = []
    for ox, oz, a0 in ((cx, cz, 0.0), (-cx, cz, math.pi/2),
                       (-cx, -cz, math.pi), (cx, -cz, 3*math.pi/2)):
        arcs.append([(ox + r*math.cos(a0 + (math.pi/2)*i/seg),
                      oz + r*math.sin(a0 + (math.pi/2)*i/seg)) for i in range(seg+1)])
    pts = []
    for k, arc in enumerate(arcs):
        pts += arc
        a = arc[-1]; b = arcs[(k+1) % 4][0]
        if step:
            L = math.hypot(b[0]-a[0], b[1]-a[1]); n = max(1, int(math.ceil(L/step)))
            for i in range(1, n):
                pts.append((a[0] + (b[0]-a[0])*i/n, a[1] + (b[1]-a[1])*i/n))
    return pts

def bm_tube(outer, inner, ys, warp=None):
    """closed solid between two coaxial XZ profiles swept through the Y values
       in *ys*.  warp(x, y, z) -> dz is applied to every vertex."""
    bm = bmesh.new(); n = len(outer)
    def ring(prof, y):
        out = []
        for x, z in prof:
            dz = warp(x, y, z) if warp else 0.0
            out.append(bm.verts.new((x, y, z + dz)))
        return out
    O = [ring(outer, y) for y in ys]
    I = [ring(inner, y) for y in ys]
    for k in range(len(ys)-1):
        for i in range(n):
            j=(i+1)%n
            bm.faces.new((O[k][i],O[k][j],O[k+1][j],O[k+1][i]))
            bm.faces.new((I[k+1][i],I[k+1][j],I[k][j],I[k][i]))
    for i in range(n):                       # end caps
        j=(i+1)%n
        bm.faces.new((O[0][j],O[0][i],I[0][i],I[0][j]))
        bm.faces.new((O[-1][i],O[-1][j],I[-1][j],I[-1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm

def bm_prism(pts, y_is_axis, a0, a1):
    """extrude a closed 2-D profile.
       y_is_axis=True : pts are (x,z), extruded along Y from a0..a1
       y_is_axis=False: pts are (x,y), extruded along Z from a0..a1"""
    bm = bmesh.new(); n = len(pts)
    if y_is_axis:
        A=[bm.verts.new((p[0], a0, p[1])) for p in pts]
        B=[bm.verts.new((p[0], a1, p[1])) for p in pts]
    else:
        A=[bm.verts.new((p[0], p[1], a0)) for p in pts]
        B=[bm.verts.new((p[0], p[1], a1)) for p in pts]
    for i in range(n):
        j=(i+1)%n; bm.faces.new((A[i],A[j],B[j],B[i]))
    bm.faces.new(A); bm.faces.new(list(reversed(B)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm

def bm_box(x0,x1,y0,y1,z0,z1, bm=None):
    own = bm is None
    if own: bm = bmesh.new()
    v=[bm.verts.new(p) for p in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                                 (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        bm.faces.new([v[i] for i in f])
    if own:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); return bm
    return bm

def bevel(ob, width, segments=2, angle=35.0, only_verts=False):
    m = ob.modifiers.new("bev", 'BEVEL')
    m.width = width; m.segments = segments; m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle); m.harden_normals = False
    m.miter_outer = 'MITER_ARC'
    return m

def shade_smooth(ob, angle=32.0):
    for p in ob.data.polygons: p.use_smooth = True
    ob.data.use_auto_smooth = True if hasattr(ob.data,'use_auto_smooth') else None
    md = ob.modifiers.new("smooth_by_angle", 'SMOOTH_BY_ANGLE') if False else None

# ---------------------------------------------------------------------------
#  materials
# ---------------------------------------------------------------------------
def pbr(name, base, metallic, rough, ior=1.45, coat=0.0, emit=None, es=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    def s(k, v):
        if k in b.inputs: b.inputs[k].default_value = v
    s("Base Color", (*base, 1.0)); s("Metallic", metallic); s("Roughness", rough)
    s("IOR", ior); s("Coat Weight", coat)
    if emit is not None:
        s("Emission Color", (*emit, 1.0)); s("Emission Strength", es)
    return m

def mats():
    M = {}
    # 1  SHELL / 3 MID PLATE / 5 LATCH / 6 GROUND PLATE : stainless, Ni plated
    M['ni']    = pbr("MAT_stainless_Ni_plated", (0.804, 0.808, 0.812), 1.0, 0.185)
    M['ni2']   = pbr("MAT_stainless_midplate",  (0.740, 0.748, 0.756), 1.0, 0.300)
    # 2  HOUSING : high-temperature plastic, black, UL94 V-0  (LCP)
    M['lcp']   = pbr("MAT_LCP_black_UL94V0",    (0.0165,0.0165,0.0175), 0.0, 0.415, coat=0.12)
    # 4  TERMINALS : copper alloy, Au plating on contact area
    M['au']    = pbr("MAT_Au_plating",          (1.000, 0.772, 0.340), 1.0, 0.155)
    M['cu']    = pbr("MAT_copper_alloy",        (0.926, 0.610, 0.430), 1.0, 0.330)
    M['sn']    = pbr("MAT_tin_solder_plating",  (0.720, 0.716, 0.700), 1.0, 0.380)
    # reference PCB
    M['fr4']   = pbr("MAT_FR4_soldermask",      (0.030, 0.128, 0.070), 0.0, 0.480, coat=0.25)
    M['pad']   = pbr("MAT_pad_ENIG",            (0.930, 0.760, 0.430), 1.0, 0.290)
    # neutral CAD "clay" for the A/B reference - must NOT read as a real finish
    M['ref']   = pbr("MAT_vendor_reference",    (0.365, 0.425, 0.510), 0.0, 0.68)
    return M

def assign(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m)

# ---------------------------------------------------------------------------
#  build
# ---------------------------------------------------------------------------
def clean():
    for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials,
              bpy.data.lights, bpy.data.cameras, bpy.data.collections,
              bpy.data.worlds, bpy.data.node_groups):
        for x in list(c): c.remove(x, do_unlink=True)

def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c

def build():
    clean()
    M = mats()
    root  = coll("J1_GT-USB-7005A")
    c_met = coll("01_metal", root)
    c_pla = coll("02_plastic", root)
    c_ter = coll("03_terminals", root)
    c_ref = coll("09_reference", root)
    objs = {}

    # ---- 1. SHELL + stamped openings ----------------------------------------
    #  Measured from the vendor solid by extreme-surface scan of every face:
    #   * NO latch dimples exist on this part (an earlier assumption; deleted).
    #   * 2 x L-shaped CORNER WINDOWS where each front mounting leg is lanced
    #     out of the shell:  |X| 2.020 .. round the corner, Y -1.680..-0.700,
    #     everything above Z = -0.100 removed.
    #   * 2 x REAR TOP NOTCHES open to the shell's rear edge:
    #     |X| 2.838..3.213, Y +0.112 .. rear edge.
    outer = [(x, Z(z)) for x, z in
             rrect(D['shell_out_hw'], D['shell_out_hh'], D['shell_out_r'], 22, 0.16)]
    inner = [(x, Z(z)) for x, z in
             rrect(D['shell_in_hw'],  D['shell_in_hh'],  D['shell_in_r'],  22, 0.16)]
    y0, y1 = D['shell_y_front'], D['shell_y_back']
    ys = [y0]
    while ys[-1] < y1: ys.append(min(y1, ys[-1] + 0.45))
    for extra in (-1.680, -0.700, 0.112):
        if extra not in ys: ys.append(extra)
    ys = sorted(set(ys))
    bm = bm_tube(outer, inner, ys)
    shell = new_obj("J1_SHELL_stainless_Ni", bm, c_met)
    assign(shell, M['ni'])

    D['win_x0'], D['win_y'] = 2.020, (-1.680, -0.700)
    D['win_z0'] = -0.100
    D['notch_x'] = (2.838, 3.213); D['notch_y0'] = 0.112
    cutters = []
    for sx in (-1, 1):
        cx0, cx1 = sorted((sx*D['win_x0'], sx*9.0))
        cutters.append(bm_box(cx0, cx1, D['win_y'][0], D['win_y'][1],
                              D['win_z0'], 4.0))
        nx0, nx1 = sorted((sx*D['notch_x'][0], sx*D['notch_x'][1]))
        cutters.append(bm_box(nx0, nx1, D['notch_y0'], y1 + 0.5, Z(0.60), 4.0))
    for i, cb in enumerate(cutters):
        bmesh.ops.recalc_face_normals(cb, faces=cb.faces[:])
        o = new_obj(f"_shellcut_{i}", cb, c_met)
        o.hide_render = True; o.hide_viewport = True; o.parent = shell
        mo = shell.modifiers.new(f"cut{i}", 'BOOLEAN')
        mo.operation = 'DIFFERENCE'; mo.object = o; mo.solver = 'EXACT'
    bevel(shell, 0.035, 2, 40)          # bevel AFTER the cuts
    objs['shell'] = shell

    # ---- 2. TONGUE ----------------------------------------------------------
    hw, hn = D['tongue_hw_wide'], D['tongue_hw_narrow']
    yt, ys, yr = D['tongue_y_tip'], D['tongue_y_step'], D['tongue_y_root']
    rtip = 0.30
    plan = []
    seg = 10
    for i in range(seg+1):                       # front-left tip radius
        a = math.pi + (math.pi/2)*i/seg
        plan.append((-hw + rtip + rtip*math.cos(a), yt + rtip + rtip*math.sin(a)))
    for i in range(seg+1):                       # front-right tip radius
        a = 3*math.pi/2 + (math.pi/2)*i/seg
        plan.append((hw - rtip + rtip*math.cos(a), yt + rtip + rtip*math.sin(a)))
    plan += [(hw, ys), (hn, ys), (hn, yr), (-hn, yr), (-hn, ys), (-hw, ys)]
    tz = D['tongue_core_hh']
    bm = bm_prism(plan, False, Z(-tz), Z(tz))
    tongue = new_obj("J1_TONGUE_LCP", bm, c_pla)
    assign(tongue, M['lcp']); bevel(tongue, 0.030, 2, 30)
    objs['tongue'] = tongue

    # ---- 2b. MID PLATE (steel core, shows as the tongue edge band) ----------
    mp = [p for p in plan]
    bm = bm_prism(mp, False, Z(-D['mid_hh']), Z(D['mid_hh']))
    bmesh.ops.scale(bm, vec=Vector((1.0015, 1.0, 1.0)), verts=bm.verts[:])
    bm2 = bm_box(-hn, hn, yr, Y(-1.000), Z(-D['mid_hh']), Z(D['mid_hh']))
    me2 = bpy.data.meshes.new("_t"); bm2.to_mesh(me2); bm2.free()
    mid = new_obj("J1_MIDPLATE_stainless", bm, c_met)
    ob2 = bpy.data.objects.new("_mid_tail", me2); c_met.objects.link(ob2)
    ob2.hide_render = True; ob2.hide_viewport = True; ob2.parent = mid
    b = mid.modifiers.new("j", 'BOOLEAN'); b.operation='UNION'; b.object=ob2; b.solver='EXACT'
    assign(mid, M['ni2'])
    objs['mid'] = mid

    # ---- 3. CONTACTS  (24) --------------------------------------------------
    cw, cp = D['c_w'], D['c_proud']
    y0, y1 = D['c_y_front'], D['c_y_back']
    b0, b1 = D['c_band_front'], D['c_band_back']
    face, core = D['tongue_face_hh'], D['tongue_core_hh']
    for row, sgn in (("A", 1), ("B", -1)):
        bm = bmesh.new()
        for k, xc in enumerate(CONTACT_X):
            prof = [(y0, core), (y0, core+cp), (b0, core+cp), (b0, face),
                    (b1, face), (b1, core+cp), (y1, core+cp), (y1, core)]
            prof = [(p[0], sgn*p[1]) for p in prof]
            pts  = [(Z(p[1]), p[0]) for p in prof]     # temp (z,y)
            n = len(prof)
            A=[bm.verts.new((xc-cw/2, p[0], Z(p[1]))) for p in prof]
            B=[bm.verts.new((xc+cw/2, p[0], Z(p[1]))) for p in prof]
            for i in range(n):
                j=(i+1)%n; bm.faces.new((A[i],A[j],B[j],B[i]))
            bm.faces.new(A); bm.faces.new(list(reversed(B)))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        o = new_obj(f"J1_CONTACTS_row{row}_Au", bm, c_ter)
        assign(o, M['au']); bevel(o, 0.012, 2, 30)
        objs['contacts'+row] = o

    # ---- 3b. TERMINAL BLOCK (closes the cavity behind the tongue) ----------
    blk_o = [(x, Z(z)) for x, z in rrect(D['shell_in_hw']-0.035,
                                         D['shell_in_hh']-0.035,
                                         D['shell_in_r']-0.035, 20)]
    bm = bm_prism(blk_o, True, Y(0.000), Y(-1.700))
    blk = new_obj("J1_TERMINALBLOCK_LCP", bm, c_pla)
    assign(blk, M['lcp']); bevel(blk, 0.05, 2, 30)
    objs['block'] = blk

    # ---- 4. REAR HOUSING (black LCP) ---------------------------------------
    bm = bm_box(-D['rear_hw'], D['rear_hw'], D['rear_y0'], D['rear_y1'],
                D['rear_z0'], D['rear_z1'])
    for sx in (-1, 1):        # two ribs per side (measured at STEP Y = -0.45:
                              # material at |X| 3.225-3.675 and 4.375-4.575)
        for xa, xb in ((3.225, 3.675), (4.375, 4.575)):
            bm_box(*sorted((sx*xa, sx*xb)), Y(-4.375), D['rear_y1'],
                   D['skirt_z0'], D['rear_z0'], bm)
    # castellated comb that separates the 12 SMT tails at the rear edge
    #  (measured at STEP Y = 0.90, band Z -5.30..-4.45: 0.12 ribs on 0.50 pitch)
    for k in range(11):
        xc = -2.50 + k*0.50
        bm_box(xc-0.060, xc+0.060, Y(-4.450), D['rear_y1'],
               D['tail_z0'], D['th_z_top'], bm)
    for sx in (-1, 1):
        bm_box(*sorted((sx*2.850, sx*3.330)), Y(-4.450), D['rear_y1'],
               D['tail_z0'], D['th_z_top'], bm)
    bm_box(-D['rear_hw'], D['rear_hw'], Y(-1.650), Y(-2.100),
           Z(-0.500), D['rear_z0'], bm)                   # front web
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    hous = new_obj("J1_HOUSING_LCP_black", bm, c_pla)
    assign(hous, M['lcp']); bevel(hous, 0.075, 2, 30)
    objs['housing'] = hous

    # ---- 5. GROUND / SHIELD PLATE ------------------------------------------
    bm = bm_box(-D['gp_hw'], D['gp_hw'], D['gp_y0'], D['gp_y1'],
                D['gp_z0'], D['gp_z1'])
    gp = new_obj("J1_GROUNDPLATE_stainless_Ni", bm, c_met)
    assign(gp, M['ni']); bevel(gp, 0.06, 2, 30)
    objs['gp'] = gp

    # ---- 6. SMT TAILS (12) --------------------------------------------------
    tw = D['tail_w']
    bm = bmesh.new()
    for xc in CONTACT_X:
        bm_box(xc-tw/2, xc+tw/2, D['tail_y1'], D['tail_y0'],
               D['tail_z0'], D['tail_z1'], bm)                    # solder foot
        bm_box(xc-tw/2, xc+tw/2, D['tail_y0']-0.20, D['tail_y0'],
               D['tail_z0'], D['tail_rise_z'], bm)                # riser
        bm_box(xc-tw/2, xc+tw/2, Y(-2.400), D['tail_y0']-0.20,
               D['tail_rise_z']-0.10, D['tail_rise_z'], bm)       # run forward
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = new_obj("J1_TAILS_SMT_x12", bm, c_ter)
    assign(o, M['sn']); bevel(o, 0.020, 2, 32)
    objs['tails'] = o

    # ---- 7. THROUGH-HOLE PINS (12) -----------------------------------------
    bm = bmesh.new()
    for xs, (ya, yb) in ((D['th_rowA_x'], D['th_rowA_y']),
                         (D['th_rowB_x'], D['th_rowB_y'])):
        for ax in xs:
            for xc in (-ax, ax):
                y0, y1 = min(ya, yb), max(ya, yb)
                bm_box(xc-D['th_w']/2, xc+D['th_w']/2, y0, y1,
                       D['th_z_bot']+0.08, D['th_z_top'], bm)
                bm_box(xc-D['th_w']/2+0.03, xc+D['th_w']/2-0.03, y0+0.03, y1-0.03,
                       D['th_z_bot'], D['th_z_bot']+0.09, bm)      # lead-in tip
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = new_obj("J1_PINS_throughhole_x12", bm, c_ter)
    assign(o, M['sn']); bevel(o, 0.018, 2, 32)
    objs['pins'] = o

    # ---- 8. MOUNTING LEGS (4) ----------------------------------------------
    bm = bmesh.new()
    for (ya, yb) in (D['leg_front_y'], D['leg_rear_y']):
        y0, y1 = min(ya, yb), max(ya, yb)
        for s in (-1, 1):
            xi, xk, xo = D['leg_x_in'], D['leg_x_knee'], D['leg_x_out']
            bm_box(*sorted((s*xi, s*xk)), y0, y1, D['leg_tab_z0'], D['leg_tab_z1'], bm)
            bm_box(*sorted((s*(xi+0.15), s*xi)), y0, y1,
                   D['leg_tab_z1'], D['leg_tab_z1']+0.16, bm)
            bm_box(*sorted((s*xk, s*xo)), y0, y1, D['leg_drop_z'], D['leg_tab_z1'], bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    legs = new_obj("J1_LEGS_stainless_Ni_x4", bm, c_met)
    assign(legs, M['ni']); bevel(legs, 0.05, 2, 32)
    objs['legs'] = legs

    return root, c_ref, objs, M

# ---------------------------------------------------------------------------
#  reference PCB  (1.60 mm, D-012)  -- geometry study only, NOT a footprint
# ---------------------------------------------------------------------------
def build_pcb(root, M):
    c = coll("04_reference_PCB", root)
    t  = D['pcb_t']
    bm = bm_box(-13.0, 13.0, D['shell_y_front'], 12.0, -t, 0.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    pcb = new_obj("PCB_REF_1p60mm_D012", bm, c)
    assign(pcb, M['fr4'])

    cut = bmesh.new()
    bm_box(-D['pcb_cut_hw'], D['pcb_cut_hw'], D['shell_y_front']-1.0,
           D['pcb_cut_y1'], -t-1.0, 1.0, cut)                     # body cut-out
    for (ya, yb) in (D['leg_front_y'], D['leg_rear_y']):           # 4 leg slots
        y0, y1 = min(ya, yb), max(ya, yb); yc = (y0+y1)/2
        for s in (-1, 1):
            bm_box(s*6.075-0.20, s*6.075+0.20, yc-0.75, yc+0.75, -t-1.0, 1.0, cut)
    for xs, (ya, yb) in ((D['th_rowA_x'], D['th_rowA_y']),         # 12 pin holes
                         (D['th_rowB_x'], D['th_rowB_y'])):
        yc = (ya+yb)/2
        for ax in xs:
            for xc in (-ax, ax):
                cy = bmesh.new()
                bmesh.ops.create_cone(cy, cap_ends=True, cap_tris=False, segments=24,
                                      radius1=0.20, radius2=0.20, depth=t+2.0)
                bmesh.ops.translate(cy, vec=Vector((xc, yc, -t/2)), verts=cy.verts[:])
                me = bpy.data.meshes.new("_c"); cy.to_mesh(me); cy.free()
                for v in me.vertices: pass
                tmp = bpy.data.objects.new("_c", me); c.objects.link(tmp)
                tmp.hide_render = True; tmp.hide_viewport = True; tmp.parent = pcb
                b = pcb.modifiers.new("hole", 'BOOLEAN')
                b.operation='DIFFERENCE'; b.object=tmp; b.solver='EXACT'
    bmesh.ops.recalc_face_normals(cut, faces=cut.faces[:])
    cutter = new_obj("_pcb_cutter", cut, c)
    cutter.hide_render = True; cutter.hide_viewport = True; cutter.parent = pcb
    b = pcb.modifiers.new("cutout", 'BOOLEAN')
    b.operation='DIFFERENCE'; b.object=cutter; b.solver='EXACT'

    # derived land pattern (NOT the manufacturer's recommended footprint)
    bm = bmesh.new()
    for xc in CONTACT_X:
        bm_box(xc-0.15, xc+0.15, D['tail_y1']-0.30, D['tail_y0']+0.20, 0.0, 0.035, bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    pads = new_obj("PCB_REF_land_pattern_DERIVED_not_a_footprint", bm, c)
    assign(pads, M['pad'])
    return c, pcb, pads

# ---------------------------------------------------------------------------
#  studio
# ---------------------------------------------------------------------------
def area_light(name, loc, look_at, size, radiance, coll_):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape='RECTANGLE'
    ld.size = size; ld.size_y = size*0.65
    ld.energy = radiance * (size*size*0.65) * math.pi
    ob = bpy.data.objects.new(name, ld); coll_.objects.link(ob)
    ob.location = loc
    d = (Vector(look_at) - Vector(loc)).normalized()
    ob.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
    return ob

def world_gradient():
    w = bpy.data.worlds.new("STUDIO"); bpy.context.scene.world = w
    w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg  = nt.nodes.new("ShaderNodeBackground")
    ramp= nt.nodes.new("ShaderNodeValToRGB")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    tex = nt.nodes.new("ShaderNodeTexCoord")
    map_= nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(tex.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], map_.inputs['Value'])
    map_.inputs['From Min'].default_value = -1.0
    map_.inputs['From Max'].default_value =  1.0
    nt.links.new(map_.outputs['Result'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.020, 0.022, 0.026, 1)
    ramp.color_ramp.elements[1].position = 0.92
    ramp.color_ramp.elements[1].color = (0.400, 0.430, 0.480, 1)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 0.65
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def studio(root, M):
    c = coll("05_studio", root)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    # --factory-startup resets device prefs -> configure the GPU explicitly
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for t in ('METAL', 'OPTIX', 'CUDA', 'HIP', 'ONEAPI'):
            try:
                prefs.compute_device_type = t
                prefs.get_devices()
                if any(getattr(d, 'type', '') == t for d in prefs.devices):
                    break
            except Exception:
                continue
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = 'GPU'
        print("cycles device:", prefs.compute_device_type,
              [(d.name, d.type, d.use) for d in prefs.devices])
    except Exception as e:
        print("gpu setup failed, staying on CPU:", e)
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.012
    sc.cycles.adaptive_min_samples = 48
    sc.cycles.samples = 384
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 16
    sc.cycles.transmission_bounces = 8
    sc.cycles.glossy_bounces = 8
    sc.render.film_transparent = False
    sc.render.resolution_x = 2000; sc.render.resolution_y = 1400
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '16'
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = 'MILLIMETERS'
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        sc.view_settings.view_transform = 'Filmic'
    world_gradient()

    # sweep backdrop
    bm = bm_box(-160, 160, -160, 160, -1.9002, -1.9)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bd = new_obj("BACKDROP", bm, c)
    m = pbr("MAT_backdrop", (0.055, 0.058, 0.065), 0.0, 0.42); assign(bd, m)
    nt = m.node_tree; bs = nt.nodes["Principled BSDF"]
    grd = nt.nodes.new("ShaderNodeTexGradient"); grd.gradient_type = 'SPHERICAL'
    mp  = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord")
    ramp= nt.nodes.new("ShaderNodeValToRGB")
    mp.inputs['Scale'].default_value = (0.030, 0.030, 0.030)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], grd.inputs['Vector'])
    nt.links.new(grd.outputs['Color'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = 0.10
    ramp.color_ramp.elements[0].color = (0.020, 0.021, 0.024, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.150, 0.156, 0.170, 1)
    nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])

    area_light("KEY",  (-42,-46, 44), (0,-1,0), 55, 9.0,  c)
    area_light("FILL", ( 52,-30, 12), (0,-1,0), 70, 2.2,  c)
    area_light("RIM",  ( 10, 46, 34), (0,0,0),  50, 14.0, c)
    area_light("TOP",  (  0,-4, 70),  (0,-1,0), 90, 2.6,  c)
    for nm, loc, rad in (("STRIP_L", (-26,-14, 30), 26.0),
                         ("STRIP_R", ( 30,  2, 26), 18.0)):
        ld = bpy.data.lights.new(nm, 'AREA'); ld.shape='RECTANGLE'
        ld.size = 46.0; ld.size_y = 1.6
        ld.energy = rad * (46.0*1.6) * math.pi
        ob = bpy.data.objects.new(nm, ld); c.objects.link(ob); ob.location = loc
        d = (Vector((0,-1.0,-0.3)) - Vector(loc)).normalized()
        ob.rotation_euler = d.to_track_quat('-Z','Y').to_euler()

    area_light("CAVITY_FILL", (-5,-24, 3.2), (0,-2,-0.40), 22, 7.5, c)
    cam = bpy.data.cameras.new("CAM_hero"); cam.lens = 85
    cam.clip_start = 0.05; cam.clip_end = 2000
    co = bpy.data.objects.new("CAM_hero", cam); c.objects.link(co)
    co.location = (-19.5, -30.0, 16.5)
    co.rotation_euler = (Vector((0,-1.2,-0.3)) - Vector(co.location)
                         ).to_track_quat('-Z','Y').to_euler()
    sc.camera = co
    return c, co

# ---------------------------------------------------------------------------
#  vendor reference + verification
# ---------------------------------------------------------------------------
def load_reference(c_ref, M):
    ply = os.path.join(HERE, "GT-USB-7005A_vendor_ref.ply")
    if not os.path.exists(ply):
        print("!! reference ply missing:", ply); return None
    before = set(bpy.data.objects)
    bpy.ops.wm.ply_import(filepath=ply)
    new = [o for o in bpy.data.objects if o not in before]
    if not new: return None
    ref = new[0]; ref.name = "REF_vendor_STEP_GT-USB-7005A"
    for cc in list(ref.users_collection): cc.objects.unlink(ref)
    c_ref.objects.link(ref)
    assign(ref, M['ref'])
    ref.hide_render = True; ref.hide_viewport = False
    return ref

def verify(objs, ref):
    rep = {"datum": "Z=0 is PCB top surface; mouth at -Y; 1 BU = 1 mm",
           "source": "G-Switch manufacturer STEP, sha256 bac2724e...c0c88fa",
           "parts": {}, "checks": []}
    dg = bpy.context.evaluated_depsgraph_get()
    def bb(ob):
        o = ob.evaluated_get(dg)
        me = o.to_mesh()
        vs = [o.matrix_world @ v.co for v in me.vertices]
        nf = len(me.polygons)
        o.to_mesh_clear()
        return (min(v.x for v in vs), max(v.x for v in vs),
                min(v.y for v in vs), max(v.y for v in vs),
                min(v.z for v in vs), max(v.z for v in vs), nf)
    allv = []
    for k, ob in objs.items():
        x0,x1,y0,y1,z0,z1,nf = bb(ob)
        rep["parts"][ob.name] = dict(X=[round(x0,4),round(x1,4)],
                                     Y=[round(y0,4),round(y1,4)],
                                     Z=[round(z0,4),round(z1,4)])
        allv += [x0,x1]
    def chk(name, got, want, tol):
        ok = abs(got-want) <= tol
        rep["checks"].append(dict(check=name, got=round(got,4), want=want,
                                  tol=tol, pass_=bool(ok)))
        return ok
    s = rep["parts"][objs['shell'].name]
    chk("shell outer width",  s['X'][1]-s['X'][0], 8.750, 0.12)
    chk("shell outer height", s['Z'][1]-s['Z'][0], 2.960, 0.12)
    chk("board sink (PCB top to shell bottom)", -s['Z'][0], 1.880, 0.10)
    chk("shell top above PCB",  s['Z'][1], 1.080, 0.10)
    chk("connector length L",   s['Y'][1]-s['Y'][0], 6.700, 0.15)
    t = rep["parts"][objs['tongue'].name]
    chk("tongue width", t['X'][1]-t['X'][0], 6.730, 0.08)
    ca = rep["parts"][objs['contactsA'].name]
    chk("contact row span (outer edges)", ca['X'][1]-ca['X'][0], 5.750, 0.08)
    cb = rep["parts"][objs['contactsB'].name]
    chk("tongue + contact plating thickness", ca['Z'][1]-cb['Z'][0], 0.700, 0.03)
    chk("contact pitch x 11", (ca['X'][1]-ca['X'][0])-0.250, 5.500, 0.03)
    chk("connector axis below PCB top (CH)", -( (ca['Z'][1]+cb['Z'][0])/2 ), 0.400, 0.02)
    tl = rep["parts"][objs['tails'].name]
    chk("SMT tail solder plane at Z=0", tl['Z'][0], 0.000, 0.02)
    lg = rep["parts"][objs['legs'].name]
    chk("overall width across legs", lg['X'][1]-lg['X'][0], 12.350, 0.10)

    # stamped-opening probes: the shell must be ABSENT in both cut regions
    sh = objs['shell']
    pts = [sh.matrix_world @ v.co for v in sh.data.vertices]
    def none_in(xr, yr, zr):
        return not any(xr[0] < p.x < xr[1] and yr[0] < p.y < yr[1]
                       and zr[0] < p.z < zr[1] for p in pts)
    rep["checks"].append(dict(check="corner window open (leg lanced out of shell)",
        got=1.0 if none_in((2.30, 3.00), (-1.55,-0.85), (0.60, 1.20)) else 0.0,
        want=1.0, tol=0.0,
        pass_=none_in((2.30, 3.00), (-1.55,-0.85), (0.60, 1.20))))
    rep["checks"].append(dict(check="rear top notch open",
        got=1.0 if none_in((2.90, 3.15), (0.30, 1.60), (0.60, 1.20)) else 0.0,
        want=1.0, tol=0.0,
        pass_=none_in((2.90, 3.15), (0.30, 1.60), (0.60, 1.20))))
    rep["checks"].append(dict(check="shell top intact away from the openings",
        got=1.0 if not none_in((-1.0, 1.0), (-4.0,-2.5), (1.00, 1.10)) else 0.0,
        want=1.0, tol=0.0,
        pass_=not none_in((-1.0, 1.0), (-4.0,-2.5), (1.00, 1.10))))
    if ref is not None:
        import mathutils
        bm = bmesh.new(); bm.from_mesh(ref.data)
        bvh = mathutils.bvhtree.BVHTree.FromBMesh(bm)
        dev = {}
        for k, ob in objs.items():
            ds = []
            for v in ob.data.vertices:
                p = ob.matrix_world @ v.co
                hit = bvh.find_nearest(p)
                if hit and hit[0] is not None: ds.append((p-hit[0]).length)
            if ds:
                ds.sort()
                dev[ob.name] = dict(n=len(ds), median=round(ds[len(ds)//2],4),
                                    p95=round(ds[int(len(ds)*0.95)],4),
                                    max=round(ds[-1],4))
        bm.free(); rep["deviation_vs_vendor_mm"] = dev
    return rep

# ---------------------------------------------------------------------------
#  main
# ---------------------------------------------------------------------------
def apply_all(objs):
    """apply booleans / bevels so the saved mesh is real geometry"""
    for ob in list(objs.values()):
        bpy.context.view_layer.objects.active = ob
        for m in list(ob.modifiers):
            try: bpy.ops.object.modifier_apply(modifier=m.name)
            except Exception as e: print("  ! apply", ob.name, m.name, e)
    for ob in list(bpy.data.objects):
        if ob.name.startswith("_"):
            bpy.data.objects.remove(ob, do_unlink=True)

def smooth(objs):
    for ob in objs.values():
        for p in ob.data.polygons: p.use_smooth = True
        try:
            ob.data.set_sharp_from_angle(angle=math.radians(31))
        except Exception:
            try:
                ob.data.use_auto_smooth = True
                ob.data.auto_smooth_angle = math.radians(31)
            except Exception: pass

def render_to(cam, loc, aim, path, lens=85, res=(2000,1400), samples=None):
    sc = bpy.context.scene
    cam.location = loc
    d = (Vector(aim) - Vector(loc)).normalized()
    up = 'Y' if abs(d.z) < 0.999 else 'Z'
    cam.rotation_euler = d.to_track_quat('-Z', up).to_euler()
    cam.data.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    if samples: sc.cycles.samples = samples
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("  rendered ->", path)

def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    quick = "--quick" in argv
    root, c_ref, objs, M = build()
    c_pcb, pcb, pads = build_pcb(root, M)
    ref = load_reference(c_ref, M)
    c_st, cam = studio(root, M)
    apply_all(dict(objs, PCB=pcb))
    smooth(objs)
    rep = verify(objs, ref)
    with open(os.path.join(OUT, "VERIFICATION.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep["checks"], indent=1))
    print("DEV:", json.dumps(rep.get("deviation_vs_vendor_mm", {}), indent=1))

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "J1_GT-USB-7005A.blend"))
    print("saved blend")

    prev = "--preview" in argv
    def show_board(on):
        for o in (pcb, pads):
            o.hide_render = not on; o.hide_viewport = not on
    if not quick:
        sc = bpy.context.scene
        S  = 48 if prev else 384
        H  = (lambda a,b: (a//2,b//2)) if prev else (lambda a,b: (a,b))
        tag= "prev_" if prev else ""
        show_board(False)
        render_to(cam, (-17.0,-27.0,12.0), (0,-0.8,-0.25),
                  os.path.join(OUT,tag+"render_01_hero.png"), 70, H(2200,1500), S)
        render_to(cam, (0.0,-40.0,-0.40), (0,0,-0.40),
                  os.path.join(OUT,tag+"render_02_mating_face.png"), 100, H(1700,1700), S)
        if prev: return
        render_to(cam, (19.0,28.0,13.0), (0,1.6,-0.1),
                  os.path.join(OUT,"render_03_rear_three_quarter.png"), 70, (2200,1500), S)
        render_to(cam, (-15.0,20.0,16.0), (0,1.0,-0.2),
                  os.path.join(OUT,"render_04_terminals_underside.png"), 70, (2200,1500), S)
        show_board(True)
        render_to(cam, (-18.0,-24.0,13.0), (0,-0.5,-0.3),
                  os.path.join(OUT,"render_05_on_1p60mm_board.png"), 70, (2200,1500), S)
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = 17.0
        render_to(cam, (-40.0,0.15,-0.40), (0,0.15,-0.40),
                  os.path.join(OUT,"render_06_side_board_sink_ortho.png"), 70, (2000,900), S)
        cam.data.ortho_scale = 15.0
        render_to(cam, (0.0,-40.0,-0.40), (0,0,-0.40),
                  os.path.join(OUT,"render_07_front_elevation_ortho.png"), 70, (1700,1200), S)
        # --- A/B validation: identical top + side ortho of rebuild vs vendor solid
        show_board(False)
        mine = [o for o in bpy.data.objects if o.name.startswith("J1_")]
        refo = bpy.data.objects.get("REF_vendor_STEP_GT-USB-7005A")
        def only(which):
            for o in mine:
                o.hide_render = (which != "mine")
            if refo: refo.hide_render = (which != "ref")
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = 13.5
        for which in ("mine", "ref"):
            only(which)
            render_to(cam, (0.0, 0.15, 40.0), (0, 0.15, 0),
                      os.path.join(OUT, f"verify_top_{which}.png"), 70, (1500,1300), 96)
            render_to(cam, (0.0, -40.0, -0.40), (0, 0, -0.40),
                      os.path.join(OUT, f"verify_front_{which}.png"), 70, (1500,900), 96)
        only("mine")
        cam.data.type = 'PERSP'
        for ob in bpy.data.objects: ob.select_set(False)
        # exports
        for ob in bpy.data.objects: ob.select_set(False)
        for ob in bpy.data.objects:
            if ob.name.startswith("J1_"): ob.select_set(True)
        try:
            bpy.ops.wm.obj_export(filepath=os.path.join(OUT,"J1_GT-USB-7005A.obj"),
                                  export_selected_objects=True, global_scale=1.0,
                                  export_materials=True)
        except Exception as e: print("obj export:", e)
        try:
            bpy.ops.wm.stl_export(filepath=os.path.join(OUT,"J1_GT-USB-7005A.stl"),
                                  export_selected_objects=True, global_scale=1.0)
        except Exception as e: print("stl export:", e)
        try:
            bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,"J1_GT-USB-7005A.glb"),
                                      export_format='GLB', use_selection=True,
                                      export_yup=True, export_apply=True)
        except Exception as e: print("glb export:", e)
    print("DONE")

main()
