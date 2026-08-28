#!/usr/bin/env python3
import json, zipfile, hashlib, re, math
from pathlib import Path
from collections import Counter, defaultdict

IN=Path('/mnt/data/ProPrj_K1-Core-Val-R0_2026-08-28(4).epro')
OUT=Path('/mnt/data/K1-Core-Val-R0-G2.1-BULK-CANDIDATE.epro')
REPORT=Path('/mnt/data/K1-Core-Val-R0-G2.1-independent-audit.json')

def h(b):return hashlib.sha256(b).hexdigest()
def load_nd(z,n):return [json.loads(x) for x in z.read(n).decode().splitlines() if x.strip()]
def trans(x,y,cx,cy,rot,mirror):
    if mirror:x=-x
    a=math.radians(rot%360);ca=round(math.cos(a),12);sa=round(math.sin(a),12)
    return round(cx+x*ca-y*sa,6),round(cy+x*sa+y*ca,6)

def build(z):
    names=z.namelist();esch=next(n for n in names if n.endswith('.esch'));recs=load_nd(z,esch);proj=json.loads(z.read('project.json'))
    comps={r[1]:{'record':r,'attrs':defaultdict(list)} for r in recs if r[0]=='COMPONENT'}
    wires={r[1]:r for r in recs if r[0]=='WIRE'}
    for r in recs:
        if r[0]=='ATTR' and r[2] in comps:comps[r[2]]['attrs'][r[3]].append(r)
    bydes=defaultdict(list)
    for cid,c in comps.items():
        for a in c['attrs'].get('Designator',[]):bydes[a[4]].append(cid)
    wattrs=defaultdict(list)
    for r in recs:
        if r[0]=='ATTR' and r[2] in wires and r[3]=='NET':wattrs[r[2]].append(r)
    seg=[]
    for wid,r in wires.items():
        for s in r[2]:
            if len(s)>=4:seg.append((wid,*map(float,s[:4])))
    symcache={}
    def syms(sid):
        if sid not in symcache:symcache[sid]=load_nd(z,f'SYMBOL/{sid}.esym')
        return symcache[sid]
    def partpins(sid,pname):
        part=None;pins={}
        for r in syms(sid):
            if r[0]=='PART':part=r[1]
            elif r[0]=='PIN' and part==pname:pins[r[1]]={'x':r[4],'y':r[5],'num':None,'name':None}
            elif r[0]=='ATTR' and r[2] in pins:
                if r[3]=='NUMBER':pins[r[2]]['num']=str(r[4])
                elif r[3]=='NAME':pins[r[2]]['name']=r[4]
        return pins
    pins=defaultdict(list)
    for des,cids in bydes.items():
        for cid in cids:
            c=comps[cid];did=(c['attrs'].get('Device') or [None])[0]
            if not did:continue
            sid=(c['attrs'].get('Symbol') or [[None,None,None,None,proj['devices'].get(did[4],{}).get('attributes',{}).get('Symbol')]])[0][4]
            if not sid:continue
            for lp,p in partpins(sid,c['record'][2]).items():
                if p['num'] is None:continue
                x,y=trans(p['x'],p['y'],c['record'][3],c['record'][4],c['record'][5],c['record'][6])
                pins[(des,p['num'])].append({'x':x,'y':y,'part':c['record'][2],'page':cid+lp,'name':p['name']})
    def onseg(px,py,x1,y1,x2,y2,tol=1e-6):
        return abs((px-x1)*(y2-y1)-(py-y1)*(x2-x1))<=tol and min(x1,x2)-tol<=px<=max(x1,x2)+tol and min(y1,y2)-tol<=py<=max(y1,y2)+tol
    def pn(des,num,part=None):
        vals=[]
        for p in pins.get((des,str(num)),[]):
            if part and p['part']!=part:continue
            ns=set()
            for wid,x1,y1,x2,y2 in seg:
                if onseg(p['x'],p['y'],x1,y1,x2,y2):ns.update(a[4] for a in wattrs.get(wid,[]))
            vals.append(sorted(ns))
        return vals
    return names,esch,recs,proj,comps,bydes,syms,partpins,pn

zi=zipfile.ZipFile(IN);zo=zipfile.ZipFile(OUT)
ni,ei,ri,pi,ci,bi,si,ppi,pni=build(zi)
no,eo,ro,po,co,bo,so,ppo,pno=build(zo)
errors=[];warnings=[]
# all archive JSON-ish core docs parse
for n in no:
    if n.endswith(('.esch','.esym','.efoo','.epcb')):
        try:load_nd(zo,n)
        except Exception as e:errors.append(f'parse:{n}:{e}')
    elif n=='project.json':
        try:json.loads(zo.read(n))
        except Exception as e:errors.append(f'parse project:{e}')
# primitive IDs unique
ids=[r[1] for r in ro if isinstance(r,list) and len(r)>1 and isinstance(r[1],str)]
dups=[x for x,c in Counter(ids).items() if c>1]
if dups:errors.append('duplicate primitive ids '+repr(dups[:20]))
# device / symbol / PART / footprint graph
missing_parts=[];missing_devs=[];missing_syms=[];missing_fps=[];symbol_mismatch=[]
for cid,c in co.items():
    dr=c['attrs'].get('Device',[])
    if not dr:missing_devs.append((cid,'none'));continue
    did=dr[0][4];dev=po.get('devices',{}).get(did)
    if not dev:missing_devs.append((cid,did));continue
    sid=dev.get('attributes',{}).get('Symbol')
    if not sid or f'SYMBOL/{sid}.esym' not in no:missing_syms.append((cid,sid));continue
    parts=[r[1] for r in so(sid) if r[0]=='PART']
    if c['record'][2] not in parts:missing_parts.append((cid,c['record'][2],sid,parts[:5]))
    sr=c['attrs'].get('Symbol',[])
    if sr and any(r[4]!=sid for r in sr):symbol_mismatch.append((cid,[r[4] for r in sr],sid))
    fp=dev.get('attributes',{}).get('Footprint','')
    if fp:
        if fp not in po.get('footprints',{}) or f'FOOTPRINT/{fp}.efoo' not in no:missing_fps.append((cid,fp))
for arr,label in [(missing_devs,'missing devices'),(missing_syms,'missing symbols'),(missing_parts,'invalid component PART refs'),(symbol_mismatch,'symbol attrs mismatch'),(missing_fps,'missing footprints')]:
    if arr:errors.append(label+': '+repr(arr[:12]))
# designator uniqueness except multipart U6
dups_des={d:c for d,c in bo.items() if len(c)>1 and d!='U6-RTC'}
if dups_des:errors.append('duplicate designators '+repr({k:len(v) for k,v in dups_des.items()}))
if len(bo.get('U6-RTC',[]))!=2:errors.append('U6 multipart count !=2')
# PCB exact bytes
pcb=[n for n in no if n.endswith('.epcb')]
pcb_unchanged={n:(n in ni and zo.read(n)==zi.read(n)) for n in pcb}
if not all(pcb_unchanged.values()):errors.append('PCB bytes changed')
# changed archive members
common=set(ni)&set(no);changed=sorted(n for n in common if h(zi.read(n))!=h(zo.read(n)))
added=sorted(set(no)-set(ni));removed=sorted(set(ni)-set(no))
# exact DNP metadata RQ-048
def vals(des,k):
    out=[]
    for cid in bo.get(des,[]):out += [r[4] for r in co[cid]['attrs'].get(k,[])]
    return out
for des in ['R40-AUD','R41-AUD','R45-MOT','R47-MOT','R49-MOT','R56-VAL','R57-VAL']:
    for k,expected in [('Add into BOM','no'),('Convert to PCB','no'),('Manufacturer Part',''),('Supplier Part',''),('supplierId','')]:
        vv=vals(des,k)
        if not vv or any(v!=expected for v in vv):errors.append(f'RQ048 {des} {k}={vv!r}, expected {expected!r}')
# custom devices must not convert before footprint verification
for des in ['DVBUS-PWR1','U17-PWR2']:
    if vals(des,'Convert to PCB')!=['no']:errors.append(f'{des} custom footprint hold not fail-closed')
# key postconditions
checks={
'BUCK_PG':('U3-PWR2','5','BUCK_PG',None),
'LIS_CS':('U13-MOT','2','3V3',None),
'LIS_SA0':('U13-MOT','3','GND',None),
'RT_USB_DP':('U6-RTC','L8','USB_DP_RT','MIMXRT1062DVJ6B.2'),
'RT_USB_DN':('U6-RTC','M8','USB_DN_RT','MIMXRT1062DVJ6B.2'),
'RT_USB_VBUS':('U6-RTC','N6','5V_PROTECTED','MIMXRT1062DVJ6B.2'),
'NFC_VDD':('U12-NFC','8','NFC_5V',None),
'NFC_VDDTX':('U12-NFC','10','NFC_5V',None),
'NFC_RFI1':('U12-NFC','22','NFC_RFI1_DIV',None),
'S3_FILTERED':('U9-ESP','2','3V3_S3_FILTERED',None),
}
check_results={}
for name,(des,p,net,part) in checks.items():
    allnets=pno(des,p,part);ok=bool(allnets and any(net in x for x in allnets));check_results[name]={'ok':ok,'nets':allnets}
    if not ok:errors.append(f'postcondition {name} failed: {allnets}')
# no debris e153914, and e146347 still absent
out_ids=set(ids)
for rid in ['e153914','e146347']:
    if rid in out_ids:errors.append(f'stale primitive remains: {rid}')
# original 10n cloned supplier hold explicitly empty / BOM no where applicable
# reproducibility checked externally; record current hash only here
res={
 'audit':'independent structural/semantic audit; does not import into EasyEDA GUI',
 'input_sha256':h(IN.read_bytes()),'output_sha256':h(OUT.read_bytes()),
 'ok':not errors,'errors':errors,'warnings':warnings,
 'archive_entries_before':len(ni),'archive_entries_after':len(no),'changed_existing_members':changed,'added_members':added,'removed_members':removed,
 'pcb_unchanged':pcb_unchanged,
 'schematic_record_count':len(ro),'component_primitives':len(co),'designator_attributes':sum(len(v) for v in bo.values()),'unique_designators':len(bo),
 'device_count':len(po.get('devices',{})),'symbol_count':len(po.get('symbols',{})),'footprint_count':len(po.get('footprints',{})),
 'key_postconditions':check_results,
 'rq048_exact_metadata':{d:{k:vals(d,k) for k in ['Add into BOM','Convert to PCB','Manufacturer Part','Supplier Part','supplierId']} for d in ['R40-AUD','R41-AUD','R45-MOT','R47-MOT','R49-MOT','R56-VAL','R57-VAL']},
 'custom_footprint_holds':{d:vals(d,'Convert to PCB') for d in ['DVBUS-PWR1','U17-PWR2']}
}
REPORT.write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
raise SystemExit(0 if res['ok'] else 2)
