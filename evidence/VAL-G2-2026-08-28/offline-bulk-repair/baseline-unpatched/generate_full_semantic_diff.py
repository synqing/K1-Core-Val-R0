#!/usr/bin/env python3
import json, zipfile, math, hashlib
from pathlib import Path
from collections import defaultdict
IN=Path('/mnt/data/ProPrj_K1-Core-Val-R0_2026-08-28(4).epro')
OUT=Path('/mnt/data/K1-Core-Val-R0-G2.1-BULK-CANDIDATE.epro')
PREFIX=Path('/mnt/data/K1-Core-Val-R0-G2.1')

def load_nd(z,n):return [json.loads(x) for x in z.read(n).decode().splitlines() if x.strip()]
def tf(x,y,cx,cy,rot,mir):
    if mir:x=-x
    a=math.radians(rot%360);ca=round(math.cos(a),12);sa=round(math.sin(a),12)
    return round(cx+x*ca-y*sa,6),round(cy+x*sa+y*ca,6)
def onseg(px,py,x1,y1,x2,y2,tol=1e-6):
    return abs((px-x1)*(y2-y1)-(py-y1)*(x2-x1))<=tol and min(x1,x2)-tol<=px<=max(x1,x2)+tol and min(y1,y2)-tol<=py<=max(y1,y2)+tol

def extract(path):
    z=zipfile.ZipFile(path); names=z.namelist(); esch=next(n for n in names if n.endswith('.esch')); recs=load_nd(z,esch); proj=json.loads(z.read('project.json'))
    comps={r[1]:{'r':r,'attrs':defaultdict(list)} for r in recs if r[0]=='COMPONENT'}; wires={r[1]:r for r in recs if r[0]=='WIRE'}
    for r in recs:
        if r[0]=='ATTR' and r[2] in comps: comps[r[2]]['attrs'][r[3]].append(r[4])
    bydes=defaultdict(list)
    for cid,c in comps.items():
        for d in c['attrs'].get('Designator',[]):bydes[d].append(cid)
    wattrs=defaultdict(list)
    for r in recs:
        if r[0]=='ATTR' and r[2] in wires and r[3]=='NET':wattrs[r[2]].append(r[4])
    seg=[]
    for wid,r in wires.items():
        for s in r[2]:
            if len(s)>=4:seg.append((wid,*map(float,s[:4])))
    symcache={}
    def syms(sid):
        if sid not in symcache:symcache[sid]=load_nd(z,f'SYMBOL/{sid}.esym')
        return symcache[sid]
    # designator snapshots
    ds={}
    for des,cids in sorted(bydes.items()):
        units=[]
        for cid in cids:
            c=comps[cid]; did=(c['attrs'].get('Device') or [''])[0]; pd=proj.get('devices',{}).get(did,{}).get('attributes',{})
            def one(k):return c['attrs'].get(k,[''])[0] if c['attrs'].get(k) else ''
            units.append({'component_id':cid,'part':c['r'][2],'device_id':did,'symbol':one('Symbol') or pd.get('Symbol',''),'manufacturer_part':one('Manufacturer Part'),'supplier_part':one('Supplier Part'),'supplier_id':one('supplierId'),'add_into_bom':one('Add into BOM'),'convert_to_pcb':one('Convert to PCB'),'name':one('Name'),'value':one('Value'),'project_device_title':proj.get('devices',{}).get(did,{}).get('title',''),'project_footprint':pd.get('Footprint','')})
        ds[des]=units
    # pin->nets snapshots
    pinmap={}
    net_members=defaultdict(list)
    for des,cids in bydes.items():
        for cid in cids:
            c=comps[cid]; did=(c['attrs'].get('Device') or [''])[0]; pd=proj.get('devices',{}).get(did,{}).get('attributes',{});sid=(c['attrs'].get('Symbol') or [pd.get('Symbol','')])[0]
            if not sid:continue
            part=None;pins={}
            for r in syms(sid):
                if r[0]=='PART':part=r[1]
                elif r[0]=='PIN' and part==c['r'][2]:pins[r[1]]={'x':r[4],'y':r[5],'number':'','name':''}
                elif r[0]=='ATTR' and r[2] in pins:
                    if r[3]=='NUMBER':pins[r[2]]['number']=str(r[4])
                    elif r[3]=='NAME':pins[r[2]]['name']=str(r[4])
            for lp,p in pins.items():
                x,y=tf(p['x'],p['y'],c['r'][3],c['r'][4],c['r'][5],c['r'][6]);ns=set()
                for wid,x1,y1,x2,y2 in seg:
                    if onseg(x,y,x1,y1,x2,y2):ns.update(wattrs.get(wid,[]))
                key=f'{des}|{c["r"][2]}|{p["number"]}|{p["name"]}'
                pinmap[key]=sorted(ns)
                for net in ns:net_members[net].append(key)
    net_members={k:sorted(v) for k,v in sorted(net_members.items())}
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'designators':ds,'pins':pinmap,'net_members':net_members}

b=extract(IN);a=extract(OUT)
# designator diff
added=sorted(set(a['designators'])-set(b['designators']));removed=sorted(set(b['designators'])-set(a['designators']));changed={}
for d in sorted(set(a['designators'])&set(b['designators'])):
    if a['designators'][d]!=b['designators'][d]:changed[d]={'before':b['designators'][d],'after':a['designators'][d]}
designator={'input_sha256':b['sha256'],'output_sha256':a['sha256'],'added':{d:a['designators'][d] for d in added},'removed':{d:b['designators'][d] for d in removed},'changed':changed,'unchanged_count':len(set(a['designators'])&set(b['designators']))-len(changed)}
# pin/net diff
padd=sorted(set(a['pins'])-set(b['pins']));prem=sorted(set(b['pins'])-set(a['pins']));pch={}
for k in sorted(set(a['pins'])&set(b['pins'])):
    if a['pins'][k]!=b['pins'][k]:pch[k]={'before':b['pins'][k],'after':a['pins'][k]}
netadd=sorted(set(a['net_members'])-set(b['net_members']));netrem=sorted(set(b['net_members'])-set(a['net_members']));netch={}
for n in sorted(set(a['net_members'])&set(b['net_members'])):
    if a['net_members'][n]!=b['net_members'][n]:netch[n]={'before':b['net_members'][n],'after':a['net_members'][n]}
netdiff={'input_sha256':b['sha256'],'output_sha256':a['sha256'],'pin_membership':{'added_pins':{k:a['pins'][k] for k in padd},'removed_pins':{k:b['pins'][k] for k in prem},'changed_pins':pch},'nets':{'added':{n:a['net_members'][n] for n in netadd},'removed':{n:b['net_members'][n] for n in netrem},'changed':netch}}
# BOM diff unit snapshots focusing identity/state fields already present in designator snapshot
bomfields=['manufacturer_part','supplier_part','supplier_id','add_into_bom','convert_to_pcb','device_id','project_footprint']
def slim(units):return [{k:u.get(k,'') for k in ['part']+bomfields} for u in units]
bomchg={}
for d in sorted(set(a['designators'])|set(b['designators'])):
    bb=slim(b['designators'].get(d,[]));aa=slim(a['designators'].get(d,[]))
    if aa!=bb:bomchg[d]={'before':bb,'after':aa}
bom={'input_sha256':b['sha256'],'output_sha256':a['sha256'],'changed_designators':bomchg,'changed_count':len(bomchg)}
Path(str(PREFIX)+'-designator-diff.json').write_text(json.dumps(designator,indent=2))
Path(str(PREFIX)+'-net-membership-diff.json').write_text(json.dumps(netdiff,indent=2))
Path(str(PREFIX)+'-bom-state-diff.json').write_text(json.dumps(bom,indent=2))
summary={'input_sha256':b['sha256'],'output_sha256':a['sha256'],'designators_added':len(added),'designators_removed':len(removed),'designators_changed':len(changed),'pin_entries_added':len(padd),'pin_entries_removed':len(prem),'pin_entries_changed':len(pch),'nets_added':len(netadd),'nets_removed':len(netrem),'nets_changed':len(netch),'bom_state_designators_changed':len(bomchg)}
Path(str(PREFIX)+'-full-diff-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
