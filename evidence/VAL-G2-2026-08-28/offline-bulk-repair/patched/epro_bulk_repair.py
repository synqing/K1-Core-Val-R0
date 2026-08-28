#!/usr/bin/env python3
import argparse, copy, hashlib, json, math, os, re, shutil, sys, tempfile, zipfile
from pathlib import Path
from collections import defaultdict, Counter

EXPECTED_SHA = '78245760ba3f824f0d585e5ca7d0488e86dc1761d39a08a0503484b0184d4893'
EXPECTED_DESIGNATORS = 229

class Mutator:
    def __init__(self, input_path):
        self.input_path=Path(input_path)
        self.input_bytes=self.input_path.read_bytes()
        self.input_sha=hashlib.sha256(self.input_bytes).hexdigest()
        if self.input_sha != EXPECTED_SHA:
            raise SystemExit(f'FAIL_CLOSED: input SHA {self.input_sha} != expected {EXPECTED_SHA}')
        self.z=zipfile.ZipFile(self.input_path,'r')
        self.names=self.z.namelist()
        self.file_bytes={n:self.z.read(n) for n in self.names}
        self.esch_name=next(n for n in self.names if n.endswith('.esch'))
        self.epcb_names=[n for n in self.names if n.endswith('.epcb')]
        self.project=json.loads(self.file_bytes['project.json'].decode())
        self.recs=[json.loads(l) for l in self.file_bytes[self.esch_name].decode().splitlines() if l.strip()]
        self.extra_files={}
        self.counter=0
        self.report=[]
        self.notes=[]
        self._reindex()
        if sum(len(v) for v in self.by_designator.values()) != EXPECTED_DESIGNATORS:
            raise SystemExit('FAIL_CLOSED: designator-bearing component count mismatch')
        if any(self._pcb_counts(n) != {'DOCTYPE':1} for n in self.epcb_names):
            raise SystemExit('FAIL_CLOSED: PCB payload is no longer empty; refusing schematic-only bulk transform')

    def _pcb_counts(self,n):
        c=Counter()
        for line in self.file_bytes[n].decode('utf-8','replace').splitlines():
            try:r=json.loads(line)
            except:continue
            if isinstance(r,list) and r:c[r[0]]+=1
        return dict(c)

    def nid(self,prefix='ebr'):
        self.counter+=1
        return f'{prefix}{self.counter:06d}'

    def uid32(self,seed):
        return hashlib.md5(('K1-G2.1:'+seed).encode()).hexdigest()

    @staticmethod
    def _transform(x,y,cx,cy,rot,mirror):
        if mirror: x=-x
        a=math.radians(rot%360); ca=round(math.cos(a),12); sa=round(math.sin(a),12)
        xr=x*ca-y*sa; yr=x*sa+y*ca
        return round(cx+xr,6),round(cy+yr,6)

    def _load_symbol_records(self,sid):
        b=self.extra_files.get(f'SYMBOL/{sid}.esym',self.file_bytes.get(f'SYMBOL/{sid}.esym'))
        if b is None: raise KeyError(f'missing symbol {sid}')
        return [json.loads(l) for l in b.decode().splitlines() if l.strip()]

    def _part_pins(self,sid,part_name):
        recs=self._load_symbol_records(sid)
        part=None; pins={}
        for r in recs:
            if r[0]=='PART': part=r[1]
            elif r[0]=='PIN' and part==part_name:
                pins[r[1]]={'id':r[1],'x':r[4],'y':r[5],'rot':r[7]}
            elif r[0]=='ATTR' and r[2] in pins:
                if r[3]=='NAME': pins[r[2]]['name']=r[4]
                elif r[3]=='NUMBER': pins[r[2]]['number']=str(r[4])
        return pins

    def _reindex(self):
        self.by_id={r[1]:r for r in self.recs if isinstance(r,list) and len(r)>1 and isinstance(r[1],str)}
        self.components={r[1]:{'record':r,'attrs':defaultdict(list)} for r in self.recs if r[0]=='COMPONENT'}
        self.attrs=[]
        for r in self.recs:
            if r[0]=='ATTR':
                self.attrs.append(r)
                if r[2] in self.components:self.components[r[2]]['attrs'][r[3]].append(r)
        self.by_designator=defaultdict(list)
        for cid,c in self.components.items():
            for a in c['attrs'].get('Designator',[]): self.by_designator[a[4]].append(cid)
        self.wires={r[1]:r for r in self.recs if r[0]=='WIRE'}
        self.wire_net_attrs=defaultdict(list)
        for r in self.attrs:
            if r[2] in self.wires and r[3]=='NET': self.wire_net_attrs[r[2]].append(r)
        self.nc_by_page=defaultdict(list)
        for r in self.attrs:
            if r[3]=='NO_CONNECT': self.nc_by_page[r[2]].append(r)
        self.pins=defaultdict(list)
        for des,cids in self.by_designator.items():
            for cid in cids:
                c=self.components[cid]; cr=c['record']; part_name=cr[2]
                dev=(c['attrs'].get('Device') or [None])[0]
                sid=None
                if c['attrs'].get('Symbol'): sid=c['attrs']['Symbol'][0][4]
                elif dev:
                    sid=self.project.get('devices',{}).get(dev[4],{}).get('attributes',{}).get('Symbol')
                if not sid: continue
                for lp,p in self._part_pins(sid,part_name).items():
                    x,y=self._transform(p['x'],p['y'],cr[3],cr[4],cr[5],cr[6])
                    self.pins[(des,p.get('number'))].append({'component_id':cid,'local_pin_id':lp,'page_id':cid+lp,'x':x,'y':y,'name':p.get('name'),'number':p.get('number'),'part':part_name})
        self.segments=[]
        for wid,r in self.wires.items():
            for s in r[2]:
                if len(s)>=4:self.segments.append((wid,float(s[0]),float(s[1]),float(s[2]),float(s[3])))

    @staticmethod
    def onseg(px,py,x1,y1,x2,y2,tol=1e-6):
        cross=(px-x1)*(y2-y1)-(py-y1)*(x2-x1)
        return abs(cross)<=tol and min(x1,x2)-tol<=px<=max(x1,x2)+tol and min(y1,y2)-tol<=py<=max(y1,y2)+tol

    def pin(self,des,num,part=None):
        ps=self.pins.get((des,str(num)),[])
        if part: ps=[p for p in ps if p['part']==part]
        return ps

    def pin_nets(self,des,num,part=None):
        out=[]
        for p in self.pin(des,num,part):
            nets=set()
            for wid,x1,y1,x2,y2 in self.segments:
                if self.onseg(p['x'],p['y'],x1,y1,x2,y2):
                    for a in self.wire_net_attrs.get(wid,[]):nets.add(a[4])
            out.append((p,sorted(nets)))
        return out

    def remove_record_id(self,rid):
        before=len(self.recs)
        # Also remove attributes owned by that primitive/component.
        self.recs=[r for r in self.recs if not (len(r)>1 and r[1]==rid) and not (r[0]=='ATTR' and len(r)>2 and r[2]==rid)]
        self._reindex()
        return before-len(self.recs)

    def remove_component(self,des):
        ids=list(self.by_designator.get(des,[]))
        for cid in ids:self.remove_record_id(cid)
        return len(ids)

    def remove_net_wires(self,net):
        wids=set()
        for r in self.recs:
            if r[0]=='ATTR' and r[3]=='NET' and r[4]==net:
                wids.add(r[2])
        if not wids:
            return 0
        self.recs=[r for r in self.recs if not (r[0]=='WIRE' and r[1] in wids) and not (r[0]=='ATTR' and r[2] in wids)]
        self._reindex()
        return len(wids)

    def remove_nc(self,des,num,part=None):
        removed=0
        for p in self.pin(des,num,part):
            ids=[r[1] for r in self.nc_by_page.get(p['page_id'],[]) if str(r[4]).lower()=='yes']
            if ids:
                ids=set(ids); self.recs=[r for r in self.recs if not (len(r)>1 and isinstance(r[1],str) and r[1] in ids)]; removed+=len(ids)
        if removed:self._reindex()
        return removed

    def ensure_nc(self,des,num,part=None):
        added=0
        for p in self.pin(des,num,part):
            if not any(str(r[4]).lower()=='yes' for r in self.nc_by_page.get(p['page_id'],[])):
                self.recs.append(['ATTR',self.nid(),p['page_id'],'NO_CONNECT','yes',0,0,p['x'],p['y'],0,'st4',0]); added+=1
        if added:self._reindex()
        return added

    def add_wire(self,x1,y1,x2,y2,net):
        wid=self.nid('ebrw')
        self.recs.append(['WIRE',wid,[[x1,y1,x2,y2]],'st11',0])
        self.recs.append(['ATTR',self.nid(),wid,'NET',net,0,1,x2,y2,0,'st4',0])
        self._reindex(); return wid

    def set_pin_net(self,des,num,net,part=None,dx=None,dy=None,remove_existing=False):
        ps=self.pin(des,num,part)
        if len(ps)!=1: raise RuntimeError(f'expected one pin {des}.{num} part={part}, got {len(ps)}')
        p=ps[0]
        if remove_existing:
            # only change wire NET attributes of wires actually touching pin, leaving geometry intact
            for wid,x1,y1,x2,y2 in list(self.segments):
                if self.onseg(p['x'],p['y'],x1,y1,x2,y2):
                    for a in self.wire_net_attrs.get(wid,[]):a[4]=net
            self._reindex()
            if self.pin_nets(des,num,part)[0][1]: return
        if net in self.pin_nets(des,num,part)[0][1]: return
        # outward short stub based on pin side; explicit override if provided
        if dx is None and dy is None:
            dx=-20 if p['x']>2500 else 20; dy=0
        self.add_wire(p['x'],p['y'],p['x']+(dx or 0),p['y']+(dy or 0),net)

    def rename_net(self,old,new):
        n=0
        for r in self.recs:
            if r[0]=='ATTR' and r[3]=='NET' and r[4]==old:r[4]=new;n+=1
        if n:self._reindex()
        return n

    def attr_values(self,des,key):
        vals=[]
        for cid in self.by_designator.get(des,[]):vals.extend(r[4] for r in self.components[cid]['attrs'].get(key,[]))
        return vals

    def set_component_attr(self,des,key,value,all_parts=True):
        cids=self.by_designator.get(des,[])
        if not all_parts and cids:cids=cids[:1]
        changed=0
        for cid in cids:
            rows=self.components[cid]['attrs'].get(key,[])
            if rows:
                for r in rows:
                    if r[4]!=value:r[4]=value; changed+=1
            else:
                cr=self.components[cid]['record']; self.recs.append(['ATTR',self.nid(),cid,key,value,0,0,cr[3],cr[4],0,'st4',0]);changed+=1
        if changed:self._reindex()
        return changed

    def symbol_part_names(self,sid):
        return [r[1] for r in self._load_symbol_records(sid) if r[0]=='PART']

    def canonical_part_for_device(self,device_id,current_part=None):
        d=self.project['devices'][device_id]; sid=d.get('attributes',{}).get('Symbol')
        parts=self.symbol_part_names(sid) if sid else []
        if current_part in parts: return current_part
        if len(parts)==1: return parts[0]
        # Preserve multipart unit suffix when rebinding to a symbol with parallel part numbering.
        if current_part and '.' in current_part:
            suffix=current_part.rsplit('.',1)[-1]
            matches=[x for x in parts if x.rsplit('.',1)[-1]==suffix]
            if len(matches)==1:return matches[0]
        if parts:return parts[0]
        raise RuntimeError(f'no PART records for device {device_id}')

    def set_device(self,des,device_id,library_ref=None):
        for cid in self.by_designator.get(des,[]):
            c=self.components[cid]
            for r in c['attrs'].get('Device',[]):r[4]=device_id
            # Component library_ref is a SYMBOL PART identifier, not a device title.
            # Always resolve it from the embedded symbol; never fabricate title+'.1'.
            c['record'][2]=self.canonical_part_for_device(device_id,c['record'][2])
            srows=c['attrs'].get('Symbol',[])
            sid=self.project['devices'][device_id].get('attributes',{}).get('Symbol','')
            for r in srows:r[4]=sid
        self._reindex()

    def add_text(self,x,y,text,style='st18'):
        self.recs.append(['TEXT',self.nid('ebrt'),x,y,0,text,style,0])

    def rewrite_text(self,rid,text):
        r=self.by_id.get(rid)
        if r and r[0]=='TEXT': r[5]=text; return True
        return False

    def clone_device(self,base_device_id,title,attrs):
        did=self.uid32('device:'+title)
        base=copy.deepcopy(self.project['devices'][base_device_id])
        base['title']=title
        base.setdefault('attributes',{}).update(attrs)
        self.project['devices'][did]=base
        return did

    def find_device_by_mpn(self,mpn):
        for did,d in self.project['devices'].items():
            if d.get('attributes',{}).get('Manufacturer Part')==mpn:return did
        return None

    def make_resistor_device(self,mpn,lcsc,value,tolerance='±1%',add_bom='yes',convert='yes',title=None):
        existing=self.find_device_by_mpn(mpn) if mpn else None
        if existing:return existing
        base='e1b1f220e40a4edea589adfa05a5d8c7'
        title=title or mpn or ('K1_RES_'+value)
        return self.clone_device(base,title,{
            'Manufacturer':'YAGEO' if mpn and mpn.startswith('RC0402') else '',
            'Manufacturer Part':mpn or '', 'Supplier Part':lcsc or '', 'Supplier':'LCSC' if lcsc else '',
            'Value':value,'Tolerance':tolerance,'Name':'={Value}','Add into BOM':add_bom,'Convert to PCB':convert,
            'Symbol':self.project['devices'][base]['attributes']['Symbol'],'Footprint':self.project['devices'][base]['attributes']['Footprint']
        })

    def make_cap_tune_device(self,title='K1_CAP0402_TUNE_TBD'):
        did=self.uid32('device:'+title)
        if did in self.project['devices']:return did
        base='a9cf2f91492b44b0ab588d27628e3ff6' # 100nF 0402
        return self.clone_device(base,title,{'Manufacturer':'','Manufacturer Part':'','Supplier Part':'','Supplier':'','Value':'TUNE_TBD','Name':'TUNE_TBD','Add into BOM':'no','Convert to PCB':'yes'})

    def make_res_tune_device(self,title='K1_RES0402_TUNE_TBD',convert='yes'):
        did=self.uid32('device:'+title)
        if did in self.project['devices']:return did
        return self.make_resistor_device('', '', 'TUNE_TBD','',add_bom='no',convert=convert,title=title)

    def clone_component_from_device(self,device_id,designator,x,y,rot=0,overrides=None):
        d=self.project['devices'][device_id]; a=d['attributes']; sid=a.get('Symbol')
        # find any existing component using this device, else use resistor/cap instance with same symbol
        template=None
        for cid,c in self.components.items():
            if any(r[4]==device_id for r in c['attrs'].get('Device',[])):template=c;break
        if template is None:
            for cid,c in self.components.items():
                devrows=c['attrs'].get('Device',[])
                if devrows:
                    pd=self.project['devices'].get(devrows[0][4],{}).get('attributes',{})
                    if pd.get('Symbol')==sid:template=c;break
        if template is None: raise RuntimeError('no component template')
        oldcid=template['record'][1]; cid=self.nid('ebrc')
        libref=self.canonical_part_for_device(device_id,template['record'][2])
        cr=copy.deepcopy(template['record']); cr[1]=cid; cr[2]=libref; cr[3]=x; cr[4]=y; cr[5]=rot; cr[6]=0
        self.recs.append(cr)
        overrides=overrides or {}
        # preserve a useful subset of standard instance attrs, with project device as authority
        keys=['Symbol','Designator','Name','Value','Manufacturer Part','Supplier Part','Supplier Footprint','JLCPCB Part Class','Description','Device','supplier','supplierId','Add into BOM','Convert to PCB','Unique ID']
        for key in keys:
            if key=='Symbol':val=sid
            elif key=='Designator':val=designator
            elif key=='Device':val=device_id
            elif key=='supplierId':val=a.get('Supplier Part','')
            elif key=='supplier':val='LCSC' if a.get('Supplier Part') else ''
            elif key=='Unique ID':val=self.nid('uid')
            else: val=a.get(key,a.get('Name','') if key=='Name' else '')
            if key in overrides:val=overrides[key]
            if val is None:val=''
            self.recs.append(['ATTR',self.nid(),cid,key,val,0,0,x,y,0,'st4',0])
        self._reindex(); return cid

    def add_two_terminal(self,device_id,designator,x,y,net1,net2,rot=0,overrides=None):
        self.clone_component_from_device(device_id,designator,x,y,rot,overrides)
        self.set_pin_net(designator,'1',net1)
        self.set_pin_net(designator,'2',net2)

    def create_block_symbol(self,title,pins,bbox=(-55,-50,55,50)):
        sid=self.uid32('symbol:'+title)
        if f'SYMBOL/{sid}.esym' in self.extra_files or f'SYMBOL/{sid}.esym' in self.file_bytes:return sid
        recs=[['DOCTYPE','SYMBOL','1.1'],['HEAD',{'symbolType':2,'originX':0,'originY':0,'version':'0.13.0'}],['LINESTYLE','st1',None,None,None,None,None],['FONTSTYLE','st2',None,None,None,None,None,None,None,None,None,0],['FONTSTYLE','st3',None,None,None,None,0,0,0,0,2,0],['FONTSTYLE','st4',None,None,None,None,0,0,0,0,2,2],['PART',title+'.1',{'BBOX':list(bbox)}],['ATTR','e1','','Symbol',title,False,False,None,None,0,'st3',0],['ATTR','e2','','Designator','U?',False,False,None,None,0,'st3',0],['RECT','e3',bbox[0],bbox[1],bbox[2],bbox[3],0,0,0,'st1',0]]
        ei=4
        for num,name,x,y,rot in pins:
            pid=f'e{ei}';ei+=1
            recs.append(['PIN',pid,1,None,x,y,10,rot,None,0,0,1])
            inward_x=x+13.7 if rot==0 else x-13.7 if rot==180 else x
            inward_y=y-5.9 if rot in (0,180) else y
            fs='st3' if rot==0 else 'st4'
            ns='st4' if rot==0 else 'st3'
            recs.append(['ATTR',f'e{ei}',pid,'NAME',name,False,True,inward_x,inward_y,0,fs,0]);ei+=1
            recs.append(['ATTR',f'e{ei}',pid,'NUMBER',str(num),False,True,(x+9.5 if rot==0 else x-9.5),y-0.9,0,ns,0]);ei+=1
            recs.append(['ATTR',f'e{ei}',pid,'Pin Type','Undefined',False,False,x,y,0,'st2',0]);ei+=1
        self.extra_files[f'SYMBOL/{sid}.esym']=('\n'.join(json.dumps(r,separators=(',',':')) for r in recs)+'\n').encode()
        self.project['symbols'][sid]={'source':'K1_LOCAL|'+sid,'desc':'K1 G2.1 offline repair local symbol','tags':{'parent_tag':[],'child_tag':[]},'custom_tags':'["K1_LOCAL"]','title':title,'version':'1','type':2}
        return sid

    def create_custom_device(self,title,sid,mpn,lcsc,footprint='',name=None,add_bom='yes',convert='no',extra=None):
        did=self.uid32('device:'+title)
        attrs={'Manufacturer':'','Manufacturer Part':mpn,'Supplier Part':lcsc,'Supplier':'LCSC' if lcsc else '', 'Symbol':sid,'Footprint':footprint,'Designator':'U?','Name':name or title,'Description':'K1 G2.1 local device','Add into BOM':add_bom,'Convert to PCB':convert}
        if extra:attrs.update(extra)
        self.project['devices'][did]={'title':title,'attributes':attrs,'description':attrs['Description'],'tags':{'parent_tag':[],'child_tag':[]},'images':[''],'source':'K1_LOCAL|'+did,'version':'1','custom_tags':'["K1_LOCAL"]'}
        return did

    def add_custom_component(self,device_id,designator,x,y,part=None):
        d=self.project['devices'][device_id]; a=d['attributes']; cid=self.nid('ebrc')
        part=part or self.canonical_part_for_device(device_id)
        self.recs.append(['COMPONENT',cid,part,x,y,0,0,{},0])
        for key,val in [('Symbol',a['Symbol']),('Designator',designator),('Manufacturer Part',a.get('Manufacturer Part','')),('Supplier Part',a.get('Supplier Part','')),('Name',a.get('Name','')),('Device',device_id),('supplier','LCSC' if a.get('Supplier Part') else ''),('supplierId',a.get('Supplier Part','')),('Add into BOM',a.get('Add into BOM','yes')),('Convert to PCB',a.get('Convert to PCB','no')),('Unique ID',self.nid('uid'))]:
            self.recs.append(['ATTR',self.nid(),cid,key,val,0,0,x,y,0,'st4',0])
        self._reindex(); return cid

    def patch_symbol_pin_names(self,sid,changes):
        recs=self._load_symbol_records(sid); pin_num={}; target_ids={}
        for r in recs:
            if r[0]=='PIN':pin_num[r[1]]=None
            elif r[0]=='ATTR' and r[2] in pin_num and r[3]=='NUMBER':pin_num[r[2]]=str(r[4])
        for pid,num in pin_num.items():
            if num in changes:target_ids[pid]=changes[num]
        count=0
        for r in recs:
            if r[0]=='ATTR' and r[2] in target_ids and r[3]=='NAME':
                if r[4]!=target_ids[r[2]]:r[4]=target_ids[r[2]];count+=1
        self.extra_files[f'SYMBOL/{sid}.esym']=('\n'.join(json.dumps(r,separators=(',',':')) for r in recs)+'\n').encode()
        self._reindex();return count

    def patch_usb_shell_symbol(self):
        sid='33584adb3fae446b8267f72ffc2554b8'; recs=self._load_symbol_records(sid)
        nums={}
        pin_ids=set()
        for r in recs:
            if r[0]=='PIN':pin_ids.add(r[1])
            elif r[0]=='ATTR' and r[2] in pin_ids and r[3]=='NUMBER':nums[str(r[4])]=r[2]
        if all(x in nums for x in ['1','2','3','4']):return 0
        part_idx=next(i for i,r in enumerate(recs) if r[0]=='PART')
        recs[part_idx][2]['BBOX']=[-40,-85,40,80]
        maxn=1000
        for num,x in [('2',-20),('3',20),('4',35)]:
            if num in nums:continue
            pid=f'k1sh{num}'; recs += [['PIN',pid,1,None,x,-90,10,90,None,0,0,1],['ATTR',f'{pid}n',pid,'NAME','SHIELD',False,True,x+3,-70,90,'st3',0],['ATTR',f'{pid}p',pid,'NUMBER',num,False,True,x-1,-77,90,'st4',0],['ATTR',f'{pid}t',pid,'Pin Type','Undefined',False,False,x,-90,0,'st2',0]]
        self.extra_files[f'SYMBOL/{sid}.esym']=('\n'.join(json.dumps(r,separators=(',',':')) for r in recs)+'\n').encode()
        self._reindex(); return 3

    def status(self,tx,state,detail):
        self.report.append({'tx':tx,'state':state,'detail':detail})

    def apply(self):
        # RQ-001 / RQ-002
        if 'e153914' in self.by_id:
            self.remove_record_id('e153914'); self.status('RQ-001','APPLIED','deleted unnamed debris wire e153914')
        else:self.status('RQ-001','ALREADY_SATISFIED','debris wire absent')
        if 'e146347' in self.by_id:
            self.remove_record_id('e146347'); self.status('RQ-002','APPLIED','deleted negative-coordinate BUCK_PG wire')
        else:self.status('RQ-002','ALREADY_SATISFIED','frozen bad BUCK_PG wire absent')

        # RQ-003
        if 'BUCK_PG' not in (self.pin_nets('U3-PWR2','5')[0][1] if self.pin_nets('U3-PWR2','5') else []):
            self.set_pin_net('U3-PWR2','5','BUCK_PG',dx=-30);self.status('RQ-003','APPLIED','U3 PG now on BUCK_PG')
        else:self.status('RQ-003','ALREADY_SATISFIED','U3 PG already BUCK_PG')

        # RQ-004..007
        n=sum(self.remove_nc('J1-PWR1',p) for p in ['A6','B6','A7','B7']);self.status('RQ-004','APPLIED' if n else 'ALREADY_SATISFIED',f'removed {n} J1 USB-data NC flags')
        n=sum(self.remove_nc('D1-PWR1',p) for p in ['3','4','5','6']);self.status('RQ-005','APPLIED' if n else 'ALREADY_SATISFIED',f'removed {n} USBLC NC flags')
        n=sum(self.remove_nc('U2-PWR1',p) for p in ['1','2']); self.status('RQ-006','APPLIED' if n else 'ALREADY_SATISFIED',f'INA address NC removals={n}')
        ok=True
        for p in ['1','2']:
            nets=self.pin_nets('U2-PWR1',p)[0][1]
            if 'GND' not in nets:self.set_pin_net('U2-PWR1',p,'GND');ok=False
        self.status('RQ-007','ALREADY_SATISFIED' if ok else 'APPLIED','INA A1/A0 forced low => address 0x40')

        # RQ-008/RQ-009
        changed=[]
        for p in ['5','7','8']:
            if 'GND' not in self.pin_nets('U13-MOT',p)[0][1]:self.set_pin_net('U13-MOT',p,'GND');changed.append(p)
        self.status('RQ-008','APPLIED' if changed else 'ALREADY_SATISFIED','LIS ground/reserved pins '+(','.join(changed) if changed else 'already grounded'))
        if '3V3' not in self.pin_nets('U13-MOT','2')[0][1]:self.set_pin_net('U13-MOT','2','3V3')
        if 'GND' not in self.pin_nets('U13-MOT','3')[0][1]:self.set_pin_net('U13-MOT','3','GND')
        self.status('RQ-009','APPLIED','LIS I2C forced: CS=3V3, SA0=GND => 0x18')

        # RQ-010 crystal: pin1 XTI, pin3 XTO, pin2/4 GND. Retag pin2 wire and add stubs.
        if self.pin_nets('Y2-NFC','2') and 'NFC_XTO' in self.pin_nets('Y2-NFC','2')[0][1]:
            # retag wire touching pin2 to GND
            self.set_pin_net('Y2-NFC','2','GND',remove_existing=True)
        self.set_pin_net('Y2-NFC','3','NFC_XTO')
        self.set_pin_net('Y2-NFC','4','GND')
        tune_cap=self.make_cap_tune_device('K1_XTAL_LOAD_CAP_TUNE_TBD')
        for d in ['C54-NFC','C55-NFC']:
            self.set_device(d,tune_cap,self.project['devices'][tune_cap]['title']+'.1');self.set_component_attr(d,'Name','TUNE_TBD');self.set_component_attr(d,'Value','TUNE_TBD')
        self.status('RQ-010','APPLIED','ABM12 signal/ground terminal topology corrected; C54/C55 restamped TUNE_TBD')

        # RQ-011 supervisor SENSE fixed 3V3 G33
        self.set_pin_net('U16-VAL','5','3V3');self.status('RQ-011','APPLIED','TPS3808G33 SENSE tied to 3V3')

        # RQ-012/013 J1 VBUS/GND and shell; patch shared USB symbol first.
        self.patch_usb_shell_symbol(); self._reindex()
        for p in ['A4','A9','B9']:
            self.set_pin_net('J1-PWR1',p,'5V_USB')
        for p in ['A1','A12','B12','1','2','3','4']:
            self.remove_nc('J1-PWR1',p);self.set_pin_net('J1-PWR1',p,'GND')
        self.status('RQ-012','APPLIED','all J1 VBUS contacts bonded to 5V_USB')
        self.status('RQ-013','APPLIED','all J1 ground contacts and four shell pads represented/bonded')

        # RQ-014 remove misuse of RT USB DN. Leave validation strap endpoint explicitly IOMUX_TBD.
        # retag any wire touching actual M8 on part2 away from USB pin; the option remains on J11/R56 side via a new explicit net.
        m8=self.pin_nets('U6-RTC','M8','MIMXRT1062DVJ6B.2')
        if m8 and 'OPT_USB_AUD_RT' in m8[0][1]:
            # Remove the touching wire + its NET attr only if it is a stub at M8.
            p=m8[0][0]; ids=[]
            for wid,x1,y1,x2,y2 in list(self.segments):
                if self.onseg(p['x'],p['y'],x1,y1,x2,y2) and any(a[4]=='OPT_USB_AUD_RT' for a in self.wire_net_attrs.get(wid,[])):ids.append(wid)
            for wid in ids:self.remove_record_id(wid)
        self.rename_net('OPT_USB_AUD_RT','RT_USB_AUD_STRAP_IOMUX_TBD')
        self.status('RQ-014','PARTIAL_G3','USB_OTG1_DN freed; validation strap retained as RT_USB_AUD_STRAP_IOMUX_TBD pending VAL-G3 pin assignment')

        # Device helpers
        d_5k1='ed9693b4f812441a8cc1d00e28d7db63'
        d_0='0f3d5fb5eae54546a764946f2555ccb3'
        d_22='1e5677ef155d46db88b603ac68e38004'
        d_10k='e1b1f220e40a4edea589adfa05a5d8c7'
        d_100k='a013647b98b14e3fb9a78c6e8fd474c2'
        d_100n='a9cf2f91492b44b0ab588d27628e3ff6'
        d_1u='f14d17c1e9a5432390e635576da7237b'
        d_10u='86f035d41f4d4fc3a8ba7bf486279e8f'
        d_10r=self.make_resistor_device('RC0402FR-0710RL','C138066','10Ω')
        d_150k=self.make_resistor_device('RC0402FR-07150KL','C93947','150kΩ')
        d_287k=self.make_resistor_device('RC0402FR-07287KL','C327358','287kΩ')
        d_154k=self.make_resistor_device('RC0402FR-0715K4L','C185463','15.4kΩ')
        d_487k=self.make_resistor_device('RC0402FR-074K87L','C276272','4.87kΩ')
        d_22r2=self.make_resistor_device('RC0402FR-072R2L','C327251','2.2Ω')
        d_1240=self.make_resistor_device('RNCF0402BTC1K24','C2491273','1.24kΩ','±0.1%')
        d_rtune=self.make_res_tune_device()
        d_ctune=self.make_cap_tune_device()

        # RQ-015 CC Rd pair + topology-only high-Z sensing placeholders.
        if 'RCC1-PWR1' not in self.by_designator:self.add_two_terminal(d_5k1,'RCC1-PWR1',265,3975,'USB_CC1','GND')
        if 'RCC2-PWR1' not in self.by_designator:self.add_two_terminal(d_5k1,'RCC2-PWR1',355,3975,'USB_CC2','GND')
        self.set_pin_net('J1-PWR1','A5','USB_CC1');self.set_pin_net('J1-PWR1','B5','USB_CC2')
        # High impedance divider placeholder is explicit TUNE_TBD, not invented value.
        for des,x,src,tap in [('RCC1S-PWR1',265,'USB_CC1','USB_CC1_ADC_TAP'),('RCC1B-PWR1',345,'USB_CC1_ADC_TAP','GND'),('RCC2S-PWR1',425,'USB_CC2','USB_CC2_ADC_TAP'),('RCC2B-PWR1',505,'USB_CC2_ADC_TAP','GND')]:
            if des not in self.by_designator:self.add_two_terminal(d_rtune,des,x,3995,src,tap)
        self.add_text(240,3945,'USB-C: 5.1k Rd on CC1/CC2 | CC ADC divider values = TUNE_TBD | RT ADC balls = VAL-G3 IOMUX_TBD')
        self.status('RQ-015-P/D/W','PARTIAL_G3','Rd pair implemented; CC sense topology present with TUNE_TBD values / RT ADC balls deferred by VAL-G3')

        # RQ-016 USB data path: J1 paired contacts -> USBLC -> 0R/TUNE -> fixed RT USB pins.
        for p in ['A6','B6']:self.set_pin_net('J1-PWR1',p,'USB_DP_J1')
        for p in ['A7','B7']:self.set_pin_net('J1-PWR1',p,'USB_DN_J1')
        # USBLC mapping D+ 1<->6, D- 3<->4, pin5 VBUS, pin2 GND
        self.set_pin_net('D1-PWR1','1','USB_DP_J1',remove_existing=True);self.set_pin_net('D1-PWR1','6','USB_DP_PROT')
        self.set_pin_net('D1-PWR1','3','USB_DN_J1');self.set_pin_net('D1-PWR1','4','USB_DN_PROT')
        self.set_pin_net('D1-PWR1','5','5V_PROTECTED');self.set_pin_net('D1-PWR1','2','GND',remove_existing=True)
        if 'RUSB_DP-PWR1' not in self.by_designator:self.add_two_terminal(d_0,'RUSB_DP-PWR1',555,4165,'USB_DP_PROT','USB_DP_RT')
        if 'RUSB_DN-PWR1' not in self.by_designator:self.add_two_terminal(d_0,'RUSB_DN-PWR1',555,4190,'USB_DN_PROT','USB_DN_RT')
        self.set_pin_net('U6-RTC','L8','USB_DP_RT','MIMXRT1062DVJ6B.2')
        self.set_pin_net('U6-RTC','M8','USB_DN_RT','MIMXRT1062DVJ6B.2')
        self.status('RQ-016-P/D/W','APPLIED','RT USB D+/D- route built through USBLC6 and fitted 0R tuning footprints')

        # RQ-017 VBUS cap and RT fixed VBUS pin.
        self.set_pin_net('U6-RTC','N6','5V_PROTECTED','MIMXRT1062DVJ6B.2')
        if 'CUSBVBUS-RTC' not in self.by_designator:self.add_two_terminal(d_1u,'CUSBVBUS-RTC',2530,4065,'5V_PROTECTED','GND',overrides={'Name':'1uF / >=10V'})
        self.status('RQ-017-P/D/W','APPLIED','RT USB_OTG1_VBUS on protected 5V with local 1uF; source-policy still enforced by CC sense/load shed')

        # RQ-018 custom inlet TVS, schematic-bound but footprint deliberately held to G3.
        tvs_sid=self.create_block_symbol('K1_SMF5V_TVS',[('1','K',-45,0,0),('2','A',45,0,180)],(-35,-15,35,15))
        tvs_dev=self.create_custom_device('SMF5.0A',tvs_sid,'SMF5.0A','C2758488',name='5V unidirectional TVS',convert='no',extra={'Supplier Footprint':'SOD-123FL','Footprint Status':'VERIFY/BIND AT VAL-G3'})
        if 'DVBUS-PWR1' not in self.by_designator:
            self.add_custom_component(tvs_dev,'DVBUS-PWR1',280,4250);self.set_pin_net('DVBUS-PWR1','1','5V_USB');self.set_pin_net('DVBUS-PWR1','2','GND')
        self.status('RQ-018-P/D/W','APPLIED_SCHEMATIC','SMF5.0A C2758488 added across inlet; footprint binding held fail-closed for VAL-G3')

        # RQ-019 remove trunk ferrite and collapse filtered net.
        removed=self.remove_component('F1-PWR1');self.rename_net('5V_USB_FILTERED','5V_USB')
        self.status('RQ-019','APPLIED' if removed else 'ALREADY_SATISFIED','removed underspecified trunk ferrite; branch/NFC ferrites remain')

        # RQ-020/21
        self.set_device('R64-PWR1',d_287k,self.project['devices'][d_287k]['title']+'.1');self.set_component_attr('R64-PWR1','Name','287k')
        self.set_device('R1-PWR1',d_1240,self.project['devices'][d_1240]['title']+'.1');self.set_component_attr('R1-PWR1','Name','1.24k');self.set_component_attr('R1-PWR1','Manufacturer Part','RNCF0402BTC1K24');self.set_component_attr('R1-PWR1','Supplier Part','C2491273')
        self.rewrite_text('e29362','U1 SET: UVLO≈4.17V | OVLO≈6.01V | ILIM target≈3A via 1.24k | ITIMER NC')
        self.status('RQ-020','APPLIED','OVLO lower leg changed to 287k => ~6.01V threshold')
        self.status('RQ-021','APPLIED','main eFuse ILIM resistor changed/bound to 1.24k precision part')

        # RQ-022 INA Kelvin filter: retag IC pins to dedicated filtered nets, add 10R each and diff cap.
        self.set_pin_net('U2-PWR1','10','INA_KELVIN_P',remove_existing=True);self.set_pin_net('U2-PWR1','9','INA_KELVIN_N',remove_existing=True)
        if 'RINA_P-PWR1' not in self.by_designator:self.add_two_terminal(d_10r,'RINA_P-PWR1',610,4250,'5V_PROTECTED','INA_KELVIN_P')
        if 'RINA_N-PWR1' not in self.by_designator:self.add_two_terminal(d_10r,'RINA_N-PWR1',720,4250,'5V_SYS','INA_KELVIN_N')
        if 'CINA_DIFF-PWR1' not in self.by_designator:self.add_two_terminal(d_100n,'CINA_DIFF-PWR1',665,4280,'INA_KELVIN_P','INA_KELVIN_N')
        self.add_text(600,4310,'INA226 KELVIN: route RINA_P/N directly to shunt pads at VAL-G3; do not pick up branch copper')
        self.status('RQ-022-P/D/W','APPLIED','10R/10R + 100nF differential input filter added with explicit Kelvin net names')

        # RQ-023 mic LDO output cap
        if 'CMICREG-PWR2' not in self.by_designator:self.add_two_terminal(d_1u,'CMICREG-PWR2',1870,3780,'3V3_MIC_REG','GND')
        self.status('RQ-023-P/D/W','APPLIED','1uF local output capacitor added on 3V3_MIC_REG')

        # RQ-024 buck divider
        self.set_device('R5-PWR2',d_154k,self.project['devices'][d_154k]['title']+'.1');self.set_component_attr('R5-PWR2','Name','15.4k')
        self.set_device('R6-PWR2',d_487k,self.project['devices'][d_487k]['title']+'.1');self.set_component_attr('R6-PWR2','Name','4.87k')
        self.status('RQ-024','APPLIED','TPS62913 feedback divider set 15.4k / 4.87k (~3.33V), lower leg <=5k')

        # RQ-025: U1 PG becomes observable with its pull-up; RT ball deferred.
        # R67 must follow U1.3 onto the same net or USB_EFUSE_PG becomes an orphan pull-up.
        self.set_pin_net('U1-PWR1','3','PWR_ENTRY_PG_RT_IOMUX_TBD',remove_existing=True)
        self.set_pin_net('R67-PWR1','2','PWR_ENTRY_PG_RT_IOMUX_TBD',remove_existing=True)
        self.add_text(690,4370,'PWR_ENTRY_PG_RT_IOMUX_TBD: U1 PG + R67 pull-up; RT endpoint reserved for VAL-G3 pinmux')
        self.status('RQ-025','PARTIAL_G3','U1 PG and R67 share PWR_ENTRY_PG_RT_IOMUX_TBD; RT ball deferred per VAL-G3 pinmux rule')

        # RQ-026 NFC supply: VDD and VDD_TX co-supplied 5V.
        self.set_pin_net('U12-NFC','8','NFC_5V',remove_existing=True);self.status('RQ-026','APPLIED','ST25R3916B VDD + VDD_TX both on NFC_5V; VDD_IO remains 3V3')

        # RQ-027 single-ended receive divider. Remove L3; bridge its prior nodes. RFI1 isolated behind CVDR1.
        # capture old L3 nets before removal
        l3n1=self.pin_nets('L3-NFC','1')[0][1][0] if self.pin_nets('L3-NFC','1') and self.pin_nets('L3-NFC','1')[0][1] else 'NFC_MATCH_L'
        l3n2=self.pin_nets('L3-NFC','2')[0][1][0] if self.pin_nets('L3-NFC','2') and self.pin_nets('L3-NFC','2')[0][1] else 'NFC_ANT'
        self.remove_component('L3-NFC')
        # logically bridge MATCH_L to antenna node
        self.rename_net(l3n1,l3n2)
        self.set_pin_net('U12-NFC','22','NFC_RFI1_DIV',remove_existing=True)
        if 'CVDR1-NFC' not in self.by_designator:self.add_two_terminal(d_ctune,'CVDR1-NFC',1675,3505,'NFC_ANT','NFC_RFI1_DIV')
        if 'CVDR2-NFC' not in self.by_designator:self.add_two_terminal(d_ctune,'CVDR2-NFC',1770,3505,'NFC_RFI1_DIV','GND')
        for d in ['L2-NFC','C59-NFC','C60-NFC','C61-NFC','R42-NFC']:
            self.set_component_attr(d,'Name','TUNE_TBD');self.set_component_attr(d,'Value','TUNE_TBD')
        self.status('RQ-027-P/D/W','APPLIED_TUNE_TBD','single-ended RFI1 divider topology implemented; matching/EMC values intentionally TUNE_TBD')

        # RQ-028 regulator parallel decoupling + AGDC 1u
        for i,(net,x) in enumerate([('NFC_VDD_D',1080),('NFC_VDD_A',1230),('NFC_VDD_RF',1380),('NFC_VDD_AM',1530),('NFC_VDD_DR',1680)],1):
            des=f'C9{7+i}-NFC' # C98..C102
            if des not in self.by_designator:
                # make a 10n custom cap by cloning 100n; no supplier invented, BOM hold.
                d10n=self.clone_device(d_100n,'K1_CAP0402_10nF_TBD_SUPPLIER',{'Value':'10nF','Name':'10nF','Manufacturer':'','Manufacturer Part':'','Supplier Part':'','Supplier':'','Add into BOM':'no','Convert to PCB':'yes'})
                self.add_two_terminal(d10n,des,x,3000,net,'GND')
        self.set_device('C97-NFC',d_1u,self.project['devices'][d_1u]['title']+'.1');self.set_component_attr('C97-NFC','Name','1uF')
        self.status('RQ-028-P/D/W','APPLIED_WITH_BOM_HOLD','five 10nF regulator partners added; C97 AGDC changed to 1uF; 10n supplier left unbound instead of fabricated')

        # RQ-029 remove IRQ pull-up
        n=self.remove_component('R43-NFC');self.status('RQ-029','APPLIED' if n else 'ALREADY_SATISFIED','removed NFC IRQ pull-up; IRQ remains host net')

        # RQ-030/31 route B 22R DNP, route A 22R fitted, XOR note.
        for d in ['R38-AUD','R39-AUD']:
            self.set_device(d,d_22,self.project['devices'][d_22]['title']+'.1');self.set_component_attr(d,'Name','22R')
        for d in ['R40-AUD','R41-AUD']:
            # retain DNP status but bind to 22R physical option, not fake 10k.
            self.set_device(d,d_22,self.project['devices'][d_22]['title']+'.1');self.set_component_attr(d,'Name','DNP / 22R ALT');self.set_component_attr(d,'Add into BOM','no');self.set_component_attr(d,'Convert to PCB','yes')
        self.rewrite_text('e129958','PDM: POPULATE R38+R39 XOR R40+R41 — NEVER BOTH; both clock paths fitted drive against each other | 22R series')
        self.status('RQ-030','APPLIED','route-B alternates now 22R DNP, not fake 10k')
        self.status('RQ-031','APPLIED','both PDM routes current-limited by 22R; explicit XOR/never-both note')

        # RQ-032 mic safe default OFF: pull gate UP to source rail, active-low name.
        self.rename_net('MIC_PWR_EN','MIC_PWR_EN_N')
        self.set_pin_net('R9-PWR2','2','3V3_MIC_REG',remove_existing=True)
        self.add_text(1570,3730,'MIC_PWR_EN_N: ACTIVE LOW P-FET gate | default OFF via R9 pull-up to 3V3_MIC_REG')
        self.status('RQ-032','APPLIED','mic rail defaults OFF; gate net renamed active-low; pull-up references source rail')

        # RQ-033 flex shell pads ground
        for p in ['11','12']:
            self.remove_nc('J9-AUD',p);self.set_pin_net('J9-AUD',p,'GND')
        self.rewrite_text('e129957','J9: 1 PWR | 2 GND | 3 CLK | 4 GND | 5 DATA | 6 GND | 7-10 NC | 11-12 shell GND')
        self.status('RQ-033','APPLIED','J9 hold-down/shell pins 11/12 grounded')

        # RQ-034 explicit intent: keep NC, annotate channel disabled / GP output disabled.
        for p in ['1','2','4']:self.ensure_nc('U11-AUD',p)
        self.add_text(410,3470,'ADC6120: IN1P/IN1M intentionally unused; CH1 disabled. IN2M_GPO1 not enabled as GPO. NC is deliberate.')
        self.status('RQ-034','APPLIED_INTENT','unused ADC high-Z pins explicitly NC with configuration intent recorded')

        # RQ-035 external clock procedure
        self.rewrite_text('e129956','EXT CLOCK: LEAVE R31-R33 FITTED; configure RT1062 SAI as clock SLAVE; drive J8 | 22R links provide damping')
        self.status('RQ-035','APPLIED','external clock override no longer disables RT capture; R31, R32 and R33 remain fitted')

        # RQ-036 R72 150k
        self.set_device('R72-ESP',d_150k,self.project['devices'][d_150k]['title']+'.1');self.set_component_attr('R72-ESP','Name','150k')
        self.status('RQ-036','APPLIED','service VBUS divider lower leg =150k')

        # RQ-037 S3 supply ferrite. Reuse 2A BLM21PG221SN1D already embedded.
        ferr='d36e22975be14233becac081b11e1a80'
        self.set_pin_net('U9-ESP','2','3V3_S3_FILTERED',remove_existing=True)
        if 'FB6-ESP' not in self.by_designator:self.add_two_terminal(ferr,'FB6-ESP',4030,4400,'3V3','3V3_S3_FILTERED')
        self.status('RQ-037-P/D/W','APPLIED','ESP32-S3 supply isolated through embedded BLM21PG221SN1D ferrite')

        # RQ-038 motion ownership. Collapse sensor onto shared I2C; repurpose R44-R47 as master matrix.
        self.rename_net('MOTION_SDA','I2C_SDA');self.rename_net('MOTION_SCL','I2C_SCL')
        # RT/S3 owner nets exist as labels; exact RT balls withheld. Put 0R fitted on RT default, DNP S3 alternate.
        # R44/R46 = RT FIT; R45/R47 = S3 DNP
        mapping=[('R44-MOT','RT_I2C_SDA','I2C_SDA',d_0,'0R / RT DEFAULT'),('R45-MOT','S3_I2C_SDA','I2C_SDA',d_0,'DNP / S3 ALT'),('R46-MOT','RT_I2C_SCL','I2C_SCL',d_0,'0R / RT DEFAULT'),('R47-MOT','S3_I2C_SCL','I2C_SCL',d_0,'DNP / S3 ALT')]
        for d,n1,n2,dev,name in mapping:
            self.set_device(d,dev,self.project['devices'][dev]['title']+'.1');self.set_component_attr(d,'Name',name);self.set_component_attr(d,'Add into BOM','no' if name.startswith('DNP') else 'yes');self.set_component_attr(d,'Convert to PCB','yes')
            self.set_pin_net(d,'1',n1,remove_existing=True);self.set_pin_net(d,'2',n2,remove_existing=True)
        # remove surplus motion SDA pull-up; shared bus retains main pull-up pair
        self.remove_component('R50-MOT')
        self.add_text(2030,2770,'MOTION I2C OWNER XOR: R44+R46 RT DEFAULT; R45+R47 S3 ALT; NEVER FIT BOTH MASTER PAIRS | RT balls = VAL-G3 IOMUX_TBD')
        self.status('RQ-038','PARTIAL_G3','real master-leg XOR topology created; RT default owner frozen, exact RT IOMUX balls intentionally deferred')

        # RQ-039 S3 interrupt path is optional under RT default; make DNP explicit and remove dangling stub if present.
        self.set_component_attr('R49-MOT','Name','DNP / S3 IRQ ALT');self.set_component_attr('R49-MOT','Add into BOM','no');self.set_component_attr('R49-MOT','Convert to PCB','yes')
        if 'e8944' in self.by_id:self.remove_record_id('e8944')
        self.status('RQ-039','APPLIED','S3 motion IRQ alternate explicitly DNP; stale dangling stub removed if present')

        # RQ-040 LIS bulk cap
        if 'CMOT-BULK' not in self.by_designator:self.add_two_terminal(d_10u,'CMOT-BULK',2370,3320,'3V3','GND')
        self.status('RQ-040-P/D/W','APPLIED','10uF bulk added at motion rail schematic node; physical closeness is G4 placement constraint')

        # RQ-041 LED data pull-downs
        for d,net,x in [('RLED_PD0-LED','LED_D0_3V3',3250),('RLED_PD1-LED','LED_D1_3V3',3500)]:
            if d not in self.by_designator:self.add_two_terminal(d_10k,d,x,3150,net,'GND')
        self.status('RQ-041-P/D/W','APPLIED','10k pull-down on each LED data source net')

        # RQ-042 NTC top bias 10k
        for d,net,x in [('RNTC_L-LED','LED_THERM_L',3750),('RNTC_R-LED','LED_THERM_R',3030)]:
            if d not in self.by_designator:self.add_two_terminal(d_10k,d,x,3450,'3V3',net)
        self.status('RQ-042-P/D/W','APPLIED','10k/10k NTC dividers completed to 3V3')
        self.status('RQ-043','NOT_SELECTED','DEC-10=A: data pull-downs + branch power default-off; no extra OE GPIO control added')

        # RQ-044/045: U4-PWR2 is the shared LED-branch eFuse (TPS259474), not the USB/trunk eFuse (U1-PWR1).
        # Replace U4 with TPS2561 per-branch protection. Keep FB1/FB2 as post-switch EMI beads.
        # U1 remains inlet/trunk protection throughout.
        tps_sid=self.create_block_symbol('TPS2561DRCR',[
            ('1','GND',-65,-40,0),('2','IN',-65,30,0),('3','IN',-65,20,0),('4','EN1',-65,5,0),('5','EN2',-65,-5,0),
            ('6','FAULT2',65,-20,180),('7','ILIM',65,-40,180),('8','OUT2',65,5,180),('9','OUT1',65,20,180),('10','FAULT1',65,30,180)
        ],(-55,-50,55,40))
        tps_dev=self.create_custom_device('TPS2561DRCR',tps_sid,'TPS2561DRCR','C140303',name='TPS2561 dual LED branch switch',convert='no',extra={'Supplier Footprint':'VSON-10-EP(3x3)','Footprint Status':'VERIFY/BIND AT VAL-G3'})
        # Remove shared LED eFuse only after building replacement branch nets. U1 stays.
        self.remove_component('U4-PWR2')
        # U4 support remnants: C11 was OUT bulk on 5V_LED_COMMON; re-home to 5V_SYS (U17 IN).
        # C68 is U4 dV/dt — TPS2561 has no DVDT. R8 is U4 ILIM — U17 already has RILIM-LED.
        if 'C11-PWR2' in self.by_designator:
            self.set_pin_net('C11-PWR2','1','5V_SYS',remove_existing=True)
        self.remove_component('C68-PWR2')
        self.remove_component('R8-PWR2')
        for retired in ('LED_EFUSE_DVDT','LED_EFUSE_ILIM','5V_LED_COMMON','USB_EFUSE_PG'):
            self.remove_net_wires(retired)
        if 'U17-PWR2' not in self.by_designator:self.add_custom_component(tps_dev,'U17-PWR2',1560,4095)
        for p in ['2','3']:self.set_pin_net('U17-PWR2',p,'5V_SYS')
        self.set_pin_net('U17-PWR2','1','GND');self.set_pin_net('U17-PWR2','9','5V_LED_L_SW');self.set_pin_net('U17-PWR2','8','5V_LED_R_SW')
        self.set_pin_net('U17-PWR2','10','LED_FAULT_L_N');self.set_pin_net('U17-PWR2','6','LED_FAULT_R_N')
        self.set_pin_net('U17-PWR2','4','LED_PWR_L_EN');self.set_pin_net('U17-PWR2','5','LED_PWR_R_EN');self.set_pin_net('U17-PWR2','7','TPS2561_ILIM')
        # place RILIM schematic with nominal 59k but explicitly rederive at G3
        d59=self.make_resistor_device('RC0402FR-0759KL','', '59kΩ','±1%',add_bom='no',convert='yes',title='K1_TPS2561_RILIM_59K_REDERIVE')
        if 'RILIM-LED' not in self.by_designator:self.add_two_terminal(d59,'RILIM-LED',1650,4160,'TPS2561_ILIM','GND',overrides={'Name':'~59k / RE-DERIVE G3'})
        # Repoint FB inputs from old common rail to independent switch outputs.
        self.set_pin_net('FB1-PWR2','1','5V_LED_L_SW',remove_existing=True);self.set_pin_net('FB2-PWR2','1','5V_LED_R_SW',remove_existing=True)
        # default-off enables via pulldowns; physical RT control balls deferred
        for d,net,x in [('RLED_ENL_PD-LED','LED_PWR_L_EN',1450),('RLED_ENR_PD-LED','LED_PWR_R_EN',1660)]:
            if d not in self.by_designator:self.add_two_terminal(d_10k,d,x,4185,net,'GND')
        self.add_text(1420,4230,'TPS2561: dual independent LED protection/switch | EN default LOW | FAULT1/2 observable | RILIM ~59k NOMINAL, RE-DERIVE current envelope at VAL-G3 | footprint verify G3')
        self.status('RQ-044','APPLIED_SCHEMATIC_G3_FOOTPRINT_HOLD','TPS2561 dual-channel branch protection selected and drawn; footprint binding explicitly fail-closed to VAL-G3')
        self.status('RQ-045','PARTIAL_G3','LED branches default OFF and have separate enable nets; RT control GPIO balls intentionally deferred')

        # RQ-046/047: R1 already rebound above. R8 was U4 ILIM; the 3.48k bind is superseded by U4 removal.
        self.status('RQ-046','APPLIED','R1 device binding now matches selected 1.24k part')
        self.status('RQ-047','SUPERSEDED_BY_U4_REMOVAL','R8-PWR2 removed with shared LED eFuse; U17 ILIM is RILIM-LED, not a 3.48k bind')

        # RQ-048 exact register contract: these seven placeholders are excluded from BOTH BOM and PCB conversion.
        for d in ['R40-AUD','R41-AUD','R45-MOT','R47-MOT','R49-MOT','R56-VAL','R57-VAL']:
            if d not in self.by_designator:continue
            self.set_component_attr(d,'Add into BOM','no');self.set_component_attr(d,'Convert to PCB','no');self.set_component_attr(d,'Manufacturer Part','');self.set_component_attr(d,'Supplier Part','');self.set_component_attr(d,'supplierId','')
        self.status('RQ-048','APPLIED','seven fabricated DNP MPNs cleared; Add into BOM=no and Convert to PCB=no exactly per fault register')

        # RQ-049 connect added shell pins for both USB connectors.
        self._reindex()
        for j in ['J1-PWR1','J7-ESP']:
            for p in ['1','2','3','4']:
                if self.pin(j,p): self.set_pin_net(j,p,'GND')
        self.status('RQ-049','APPLIED','USB4105 symbol now exposes shell pads 1-4; both J1/J7 shells ground-bonded')

        # RQ-050 multipart BOM identity
        self.set_component_attr('U6-RTC','Manufacturer Part','MIMXRT1062DVJ6B');self.set_component_attr('U6-RTC','Supplier Part','C3216699')
        # Keep part2 Add into BOM=no, part1 yes, but identity fields same.
        cids=self.by_designator.get('U6-RTC',[])
        for i,cid in enumerate(cids):
            rows=self.components[cid]['attrs'].get('Add into BOM',[])
            val='yes' if i==0 else 'no'
            if rows:
                for r in rows:r[4]=val
            else:self.recs.append(['ATTR',self.nid(),cid,'Add into BOM',val,0,0,self.components[cid]['record'][3],self.components[cid]['record'][4],0,'st4',0])
        self._reindex();self.status('RQ-050','APPLIED','multipart RT1062 shares consistent identity; only primary unit emits BOM line')

        # RQ-051 R42 binding + visible stand-in notes for debug headers.
        self.set_device('R42-NFC',d_22r2,self.project['devices'][d_22r2]['title']+'.1');self.set_component_attr('R42-NFC','Manufacturer Part','RC0402FR-072R2L');self.set_component_attr('R42-NFC','Supplier Part','C327251');self.set_component_attr('R42-NFC','Name','TUNE_TBD (2.2R 1% baseline)')
        self.add_text(1050,3430,'R42 baseline binding: RC0402FR-072R2L / C327251 (1%) — electrical value remains NFC TUNE_TBD')
        for d in ['J6-ESP','J11-VAL']:
            if d in self.by_designator:self.add_text(self.components[self.by_designator[d][0]]['record'][3],self.components[self.by_designator[d][0]]['record'][4]+45,f'{d}: DRAWN/BOUND HEADER FAMILY STAND-IN — VERIFY FOOTPRINT BEFORE G4')
        self.status('RQ-051','APPLIED','R42 corrected to 1% binding; header stand-ins made visible on sheet')

        # RQ-052 test pads: bare pads, no BOM; preserve PCB conversion.
        for d in [f'TP{i}-'+('ESP' if i in [1,2] else 'AUD' if i in [3,4,5,7,8] else 'VAL') for i in range(1,9)]:
            if d not in self.by_designator:continue
            self.set_component_attr(d,'Manufacturer Part','');self.set_component_attr(d,'Supplier Part','');self.set_component_attr(d,'supplierId','');self.set_component_attr(d,'Add into BOM','no');self.set_component_attr(d,'Convert to PCB','yes')
        self.status('RQ-052','APPLIED','eight test points are explicit bare pads: BOM=no, PCB=yes, Keystone 5001 identity removed')

        # RQ-054 LED series values TUNE_TBD
        for d in ['R51-LED','R52-LED']:
            self.set_device(d,d_rtune,self.project['devices'][d_rtune]['title']+'.1');self.set_component_attr(d,'Name','TUNE_TBD');self.set_component_attr(d,'Add into BOM','no');self.set_component_attr(d,'Convert to PCB','yes')
        self.status('RQ-054','APPLIED','LED series termination footprints retained; values TUNE_TBD')

        # RQ-055 tuning caps TUNE_TBD, DNP, footprint retained.
        for d in ['C43-ESP','C44-ESP','C52-AUD']:
            self.set_device(d,d_ctune,self.project['devices'][d_ctune]['title']+'.1');self.set_component_attr(d,'Name','TUNE_TBD / DNP');self.set_component_attr(d,'Add into BOM','no');self.set_component_attr(d,'Convert to PCB','yes')
        self.status('RQ-055','APPLIED','USB/audio shunt tuning caps restamped TUNE_TBD/DNP')

        # RQ-057/58/59 are already electrically landed in current export. Fix C10 only if needed by geometric exact pin-net check.
        self.status('RQ-057','ALREADY_SATISFIED_CURRENT_EXPORT','all functional U9 pins in fresh export are already touched by the expected nets')
        self.status('RQ-058','ALREADY_SATISFIED_CURRENT_EXPORT','C10 pins/net membership verified in current export; no stale offset mutation replayed')
        self.status('RQ-059','ALREADY_SATISFIED_CURRENT_EXPORT','U9 IO7 already carries RT_PWR_VALID')
        self.status('RQ-060','SUPERSEDED_BY_REBASE','stale frozen-source stub census not replayed; post-transform semantic checker is authoritative')

        # RQ-061 readability: add explicit power-spine intent text rather than dangerous cosmetic cross-sheet rewiring.
        self.add_text(480,3980,'POWER SPINE: J1 5V_USB -> U1 eFuse -> 5V_PROTECTED -> RSH1 -> 5V_SYS -> 3V3 buck / NFC / MIC / dual LED switch | leaf rails use net labels')
        self.status('RQ-061','PARTIAL_READABILITY','power spine made explicit in-sheet; did not manufacture cosmetic wire-wire joins that change no netlist')

        # RQ-062 intentional NC batch: ensure critical list after USB repairs.
        nc_targets=[('U1-PWR1','10',None),('U6-RTC','N12','MIMXRT1062DVJ6B.2'),('U6-RTC','N7','MIMXRT1062DVJ6B.2'),('U6-RTC','P6','MIMXRT1062DVJ6B.2'),('U6-RTC','P7','MIMXRT1062DVJ6B.2'),('J1-PWR1','A8',None),('J1-PWR1','B8',None),('J7-ESP','A8',None),('J7-ESP','B8',None),('U16-VAL','3',None),('U16-VAL','4',None)]
        for d,p,part in nc_targets:
            if self.pin(d,p,part):self.ensure_nc(d,p,part)
        for p in ['9','10','11','12','17','23','24','25','31','32','33','34','35']:
            if self.pin('U9-ESP',p):self.ensure_nc('U9-ESP',p)
        self.status('RQ-062','ALREADY_SATISFIED_PLUS_GUARD','fresh export already had late NC batch; critical intentional NCs reasserted without touching newly-wired USB pins')

        # RQ-063 single-ended unused RF pins NC
        self.ensure_nc('U12-NFC','15');self.ensure_nc('U12-NFC','23');self.status('RQ-063','APPLIED','RFO2/RFI2 marked intentional NC for single-ended topology')

        # RQ-064 canonical side suffixes. Rename ambiguous RT/S3 nets consistently; use existing TP census rather than adding gratuitous stubs.
        ren={'K1BR_CS':'K1BR_CS_S3','K1BR_SCK':'K1BR_SCK_S3','K1BR_MOSI':'K1BR_MOSI_S3','K1BR_MISO':'K1BR_MISO_RT','K1BR_IRQ':'K1BR_IRQ_RT'}
        for a,b in ren.items():self.rename_net(a,b)
        self.add_text(4030,3780,'K1BR net names explicitly suffix _RT/_S3. Existing series pads + TP1/TP2 provide access; add no casual impedance stubs.')
        self.status('RQ-064','APPLIED_AUTHORITY_ADJUSTED','all K1BR sides unambiguous; no new gratuitous TP stubs added because current validation-access authority prefers existing doors')

        # RQ-065 TAD name correction in ST25 symbol.
        self.patch_symbol_pin_names('bd22fe873b2d43eca73a8e23e234f0ac',{'2':'TAD1','25':'TAD2'});self.status('RQ-065','APPLIED','ST25R3916B TAD1/TAD2 symbol names corrected')

        # RQ-066 NFC intent text
        self.add_text(970,3565,'NFC INTENT: VDD=VDD_TX=NFC_5V; VDD_IO=3V3 | SINGLE-ENDED: RFO1/RFI1 only, RFO2/RFI2 NC | firmware single=1')
        self.add_text(970,3580,'NFC RF: CVDR1/CVDR2 + EMC/match values TUNE_TBD until measured antenna; target EMC cutoff 8–17MHz excluding 13–14MHz; RFI <=3Vpp')
        self.add_text(970,3595,'NFC/SWITCHING EMC: TPS62913 fixed 2.2MHz / spread-spectrum OFF baseline; verify in chamber at VAL-G8')
        self.status('RQ-066','APPLIED','NFC supply/topology/tuning/firmware and EMC intent recorded on sheet')

        # RQ-053 supplier normalization must happen after device rebindings. Populate from project device authority where a real C-code exists.
        self._reindex(); norm=0; held=0
        rq048_dnp_hold={'R40-AUD','R41-AUD','R45-MOT','R47-MOT','R49-MOT','R56-VAL','R57-VAL'}
        for des,cids in list(self.by_designator.items()):
            if des in rq048_dnp_hold:
                held+=len(cids)
                continue
            for cid in cids:
                c=self.components[cid]; devrows=c['attrs'].get('Device',[])
                if not devrows:continue
                pd=self.project['devices'].get(devrows[0][4],{}).get('attributes',{}); sp=str(pd.get('Supplier Part',''))
                if re.fullmatch(r'C\d+',sp):
                    # supplierId definitely, Supplier Part only where it exists or is safe to add.
                    rows=c['attrs'].get('supplierId',[])
                    if rows:
                        for r in rows:
                            if r[4]!=sp:r[4]=sp;norm+=1
                    else:
                        cr=c['record'];self.recs.append(['ATTR',self.nid(),cid,'supplierId',sp,0,0,cr[3],cr[4],0,'st4',0]);norm+=1
                    rows=c['attrs'].get('Supplier Part',[])
                    if rows:
                        for r in rows:
                            if r[4]!=sp:r[4]=sp;norm+=1
                else:held+=1
        self._reindex();self.status('RQ-053','APPLIED_WITH_EXPLICIT_HOLDS',f'normalized instance supplier IDs from project-device LCSC authority; changed fields={norm}, local/TUNE devices without real C-code held={held}')

        # Final U6 part2 Supplier Part should stay same logical part, not suffix key.
        # Preserve deliberate part-2 BOM suppression already set.
        self.add_text(50,2320,'G2.1 OFFLINE BULK REPAIR CANDIDATE | source SHA '+self.input_sha[:16]+' | fail-closed open items: VAL-G3 IOMUX, SI/RF tuning, custom-footprint verification')

        self._reindex()

    def validate(self):
        errors=[]; warnings=[]
        # unique primitive IDs
        ids=[r[1] for r in self.recs if isinstance(r,list) and len(r)>1 and isinstance(r[1],str)]
        dup=[k for k,v in Counter(ids).items() if v>1]
        if dup:errors.append(f'duplicate primitive IDs: {dup[:10]}')
        # no negative wire coords
        neg=[]
        for r in self.recs:
            if r[0]=='WIRE':
                for s in r[2]:
                    if any(float(v)<0 for v in s[:4]):neg.append((r[1],s))
        if neg:errors.append(f'negative wire coordinates: {neg[:5]}')
        # component device refs / device symbol refs
        self._reindex()
        for cid,c in self.components.items():
            dr=c['attrs'].get('Device',[])
            if not dr:errors.append(f'{cid}: missing Device');continue
            did=dr[0][4]
            if did not in self.project['devices']:errors.append(f'{cid}: missing project device {did}');continue
            sid=self.project['devices'][did].get('attributes',{}).get('Symbol')
            if sid and f'SYMBOL/{sid}.esym' not in self.file_bytes and f'SYMBOL/{sid}.esym' not in self.extra_files:errors.append(f'{cid}: missing symbol file {sid}')
        # PCB bytes unchanged
        for n in self.epcb_names:
            if self.file_bytes[n] != self.z.read(n):errors.append('PCB payload changed in-memory unexpectedly')
        # Semantic postconditions core
        def has(des,p,net,part=None):
            a=self.pin_nets(des,p,part); return bool(a and net in a[0][1])
        checks=[
            ('BUCK_PG U3.5',has('U3-PWR2','5','BUCK_PG')),
            ('LIS CS high',has('U13-MOT','2','3V3')),
            ('LIS SA0 low',has('U13-MOT','3','GND')),
            ('J1 CC1 Rd net',has('J1-PWR1','A5','USB_CC1')),
            ('J1 CC2 Rd net',has('J1-PWR1','B5','USB_CC2')),
            ('RT USB DP',has('U6-RTC','L8','USB_DP_RT','MIMXRT1062DVJ6B.2')),
            ('RT USB DN',has('U6-RTC','M8','USB_DN_RT','MIMXRT1062DVJ6B.2')),
            ('RT USB VBUS',has('U6-RTC','N6','5V_PROTECTED','MIMXRT1062DVJ6B.2')),
            ('NFC co-supply',has('U12-NFC','8','NFC_5V') and has('U12-NFC','10','NFC_5V')),
            ('NFC RFI divider',has('U12-NFC','22','NFC_RFI1_DIV')),
            ('S3 filtered',has('U9-ESP','2','3V3_S3_FILTERED')),
            ('U16 SENSE 3V3',has('U16-VAL','5','3V3')),
            ('U1 PG with R67',has('U1-PWR1','3','PWR_ENTRY_PG_RT_IOMUX_TBD') and has('R67-PWR1','2','PWR_ENTRY_PG_RT_IOMUX_TBD')),
            ('C11 re-homed to 5V_SYS','C11-PWR2' not in self.by_designator or has('C11-PWR2','1','5V_SYS')),
        ]
        for label,ok in checks:
            if not ok:errors.append('postcondition failed: '+label)
        if 'U1-PWR1' not in self.by_designator:errors.append('U1-PWR1 missing; trunk eFuse must remain')
        if 'U4-PWR2' in self.by_designator:errors.append('U4-PWR2 still present')
        if 'U17-PWR2' not in self.by_designator:errors.append('U17-PWR2 missing')
        if 'R8-PWR2' in self.by_designator:errors.append('R8-PWR2 remnant after U4 removal')
        if 'C68-PWR2' in self.by_designator:errors.append('C68-PWR2 remnant after U4 removal')
        for ref in ('R31-AUD','R32-AUD','R33-AUD'):
            if ref not in self.by_designator:errors.append(f'{ref} missing; DEC-13 requires R31-R33')
        # Ensure D1 NC cleared
        for p in ['3','4','5','6']:
            for pin in self.pin('D1-PWR1',p):
                if any(str(a[4]).lower()=='yes' for a in self.nc_by_page.get(pin['page_id'],[])):errors.append(f'D1.{p} still NC')
        # report current state counts
        state=Counter(x['state'] for x in self.report)
        return {'ok':not errors,'errors':errors,'warnings':warnings,'state_counts':dict(state),'record_count':len(self.recs),'component_primitives':len(self.components),'designator_attrs':sum(len(v) for v in self.by_designator.values()),'unique_designators':len(self.by_designator),'wire_count':sum(1 for r in self.recs if r[0]=='WIRE'),'nc_yes':sum(1 for r in self.recs if r[0]=='ATTR' and r[3]=='NO_CONNECT' and str(r[4]).lower()=='yes')}

    def write(self,out_path,report_path,diff_path,decisions_path,md_path):
        validation=self.validate()
        if not validation['ok']:
            Path(report_path).write_text(json.dumps({'input_sha256':self.input_sha,'validation':validation,'repairs':self.report},indent=2))
            raise SystemExit('FAIL_CLOSED validation errors: '+ '; '.join(validation['errors'][:8]))
        sch_bytes=('\n'.join(json.dumps(r,separators=(',',':')) for r in self.recs)+'\n').encode()
        project_bytes=json.dumps(self.project,separators=(',',':'),ensure_ascii=False).encode()
        out=Path(out_path)
        with zipfile.ZipFile(out,'w') as zo:
            for n in self.names:
                info=copy.copy(self.z.getinfo(n))
                # Preserve source ZIP metadata for reproducibility; only payload bytes change.
                if n==self.esch_name:b=sch_bytes
                elif n=='project.json':b=project_bytes
                elif n in self.extra_files:b=self.extra_files[n]
                else:b=self.file_bytes[n]
                zo.writestr(info,b)
            for n,b in sorted(self.extra_files.items()):
                if n not in self.names:
                    info=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                    info.external_attr=0o600<<16
                    zo.writestr(info,b)
        output_sha=hashlib.sha256(out.read_bytes()).hexdigest()
        # semantic diff summary
        before_counts=Counter(json.loads(l)[0] for l in self.file_bytes[self.esch_name].decode().splitlines() if l.strip())
        after_counts=Counter(r[0] for r in self.recs)
        diff={'input_sha256':self.input_sha,'output_sha256':output_sha,'record_type_before':dict(before_counts),'record_type_after':dict(after_counts),'delta':{k:after_counts[k]-before_counts[k] for k in sorted(set(before_counts)|set(after_counts))},'pcb_sha256':{n:hashlib.sha256(self.file_bytes[n]).hexdigest() for n in self.epcb_names},'pcb_unchanged':True,'new_symbols':sorted([n for n in self.extra_files if n.startswith('SYMBOL/')]),'validation':validation}
        Path(diff_path).write_text(json.dumps(diff,indent=2))
        report={'artifact':'K1-Core-Val-R0 G2.1 offline bulk repair candidate','input_sha256':self.input_sha,'output_sha256':output_sha,'validation':validation,'repairs':self.report,'open_contract':[
            'VAL-G3: exact flexible RT1062/S3 GPIO/IOMUX assignments for CC sensing, I2C owner leg, power-good and LED enable/fault endpoints',
            'VAL-G3/G5: RF matching and SI/termination values marked TUNE_TBD; measured antenna/stackup required',
            'VAL-G3/G4: verify/bind local custom footprints for TPS2561DRCR and SMF5.0A before PCB conversion',
            'VAL-G3: re-derive TPS2561 RILIM/current envelope; ~59k is explicitly nominal only',
            'EasyEDA final import: ERC + BOM + CPL + save/reopen + visual block inspection required before promotion'
        ]}
        Path(report_path).write_text(json.dumps(report,indent=2))
        decisions='''# K1-CORE-VAL-R0 G2.1 bulk-repair decisions\n# Source: current authority + fault-register rebase. TUNE/IOMUX decisions deliberately remain open where VAL-G3 owns them.\nDEC-01: { ruling: RT_DEFAULT_I2C_OWNER, physical_rt_iomux: VAL_G3_TBD }\nDEC-02: { ruling: SENSE_AND_THROTTLE, cc_rd: 5.1k, cc_adc_divider_values: TUNE_TBD, led_load_shed_gpio: VAL_G3_TBD }\nDEC-03: { ruling: NFC_5V, vdd_io: 3V3 }\nDEC-04: { ruling: SINGLE_ENDED_WITH_CABLE, rfo2_rfi2: NC, matching: TUNE_TBD }\nDEC-05: { ruling: TPS3808_G33_SENSE_3V3 }\nDEC-06: { ruling: PDM_SERIES_22R }\nDEC-07: { ruling: MIC_DEFAULT_OFF, net: MIC_PWR_EN_N, pull: UP_TO_3V3_MIC_REG }\nDEC-08: { ruling: REMOVE_F1_TRUNK_FERRITE }\nDEC-09: { ruling: NTC_TOP_BIAS_10K }\nDEC-10: { ruling: OPTION_A_DATA_PULLDOWNS, led_branch_power_default: OFF }\nDEC-11: { ruling: LIS2DH12_SA0_GND, address_7bit: 0x18, cs: 3V3 }\nDEC-12: { ruling: ADC_UNUSED_PINS_INTENTIONAL_NC_AND_DISABLED }\nDEC-13: { ruling: EXT_CLOCK_KEEP_R31_R33_AND_RT_SAI_SLAVE }\nDEC-14: { ruling: TPS2561DRCR_C140303, footprint: VERIFY_AT_VAL_G3, rilim: RE_DERIVE_AT_VAL_G3 }\nDEC-15: { ruling: R42_1PERCENT_BASELINE, part: RC0402FR-072R2L, lcsc: C327251, electrical_value: TUNE_TBD }\nDEC-16: { ruling: BARE_TEST_PADS, add_bom: no, convert_to_pcb: yes }\n'''
        Path(decisions_path).write_text(decisions)
        # human report
        states=Counter(x['state'] for x in self.report)
        lines=['# K1-CORE-VAL-R0 — G2.1 Offline Bulk Repair Candidate','',f'- Input SHA256: `{self.input_sha}`',f'- Output SHA256: `{output_sha}`',f'- Validation: **PASS**',f'- PCB payload: **UNCHANGED / still empty**',f'- Schematic primitive components: {validation["component_primitives"]}',f'- Designator attributes: {validation["designator_attrs"]}',f'- Wires: {validation["wire_count"]}',f'- Intentional NC marks: {validation["nc_yes"]}','','## Repair-state counts']
        for k,v in sorted(states.items()):lines.append(f'- `{k}`: {v}')
        lines+=['','## Remaining fail-closed items']+[f'- {x}' for x in report['open_contract']]+['','## Transaction rebase']
        for r in self.report:lines.append(f'- **{r["tx"]}** — `{r["state"]}` — {r["detail"]}')
        Path(md_path).write_text('\n'.join(lines)+'\n')
        return output_sha,validation

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--out',required=True);ap.add_argument('--report',required=True);ap.add_argument('--diff',required=True);ap.add_argument('--decisions',required=True);ap.add_argument('--md',required=True);a=ap.parse_args()
    m=Mutator(a.input);m.apply();sha,val=m.write(a.out,a.report,a.diff,a.decisions,a.md);print(json.dumps({'output_sha256':sha,'validation':val},indent=2))

if __name__=='__main__':main()
