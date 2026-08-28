#!/usr/bin/env python3
"""Map the Option-C fixture into Captain's ten fixed domain boxes."""
from __future__ import annotations
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE, OUTPUT = HERE / "FIXTURE-PLAN.json", HERE / "LAYOUT-PLAN.json"

# Exact source-space corners of Captain's persisted 5 x 2 box grid.
CONTAINERS = {
  1: (-90,165,845,1280,"1. POWER ENTRY + CURRENT SENSE"),
  2: (890,165,1850,1285,"2. POWER CONVERSION + DISTRIBUTION"),
  3: (1900,165,2860,1285,"3. RT1062 COMPUTE + CORE POWER"),
  4: (2910,165,3870,1285,"4. RT1062 BOOT + CLOCK + DEBUG"),
  5: (3925,165,4885,1285,"5. ESP32-S3 RADIO + SERVICE + K1BR"),
  6: (-115,-1020,845,100,"6. AUDIO CAPTURE + CLOCK + MIC FLEX"),
  7: (885,-1020,1845,100,"7. NFC FRONT END + ANTENNA"),
  8: (1895,-1030,2855,90,"8. MOTION / ACCELEROMETER"),
  9: (2910,-1030,3870,90,"9. LED DATA + TEMPERATURE"),
 10: (3925,-1035,4885,85,"10. DEBUG / RECOVERY + VALIDATION OPTIONS"),
}
SUFFIX_BY_CONTAINER = {
  1: "PWR",
  2: "PWR",
  3: "RTC",
  4: "RTDBG",
  5: "ESP",
  6: "AUD",
  7: "NFC",
  8: "MOT",
  9: "LED",
 10: "VAL",
}
GROUP = {
 "POWER_ENTRY":1,"POWER_SENSE":1,"POWER_BUCK":2,"POWER_LED":2,"POWER_BRANCH":2,
 "RT_CORE":3,"RT_DECOUPLE":3,"RT_CLOCK_MEM":4,"RT_DEBUG":4,
 "ESP_CORE":5,"ESP_USB":5,"K1BR":5,"AUDIO_ADC":6,"AUDIO_CLOCK":6,"AUDIO_MIC":6,
 "NFC":7,"MOTION":8,"LED_DATA":9,"OPTIONS":10,"DEBUG_FABRIC":10,
}
TITLE_OWNER = {1:"POWER_ENTRY",2:"POWER_BUCK",3:"RT_CORE",4:"RT_CLOCK_MEM",5:"ESP_CORE",6:"AUDIO_ADC",7:"NFC",8:"MOTION",9:"LED_DATA",10:"OPTIONS"}
REGION = {
 "POWER_ENTRY":(80,250,760,650),"POWER_SENSE":(-20,720,780,1135),
 "POWER_BUCK":(940,800,1800,1140),"POWER_LED":(940,500,1800,760),"POWER_BRANCH":(940,220,1800,460),
 "RT_CORE":(1950,560,2810,1135),"RT_DECOUPLE":(1950,220,2810,505),
 "RT_CLOCK_MEM":(2960,700,3820,1135),"RT_DEBUG":(2960,220,3820,650),
 "ESP_CORE":(3975,760,4835,1135),"ESP_USB":(3975,480,4835,715),"K1BR":(3975,220,4835,440),
 "AUDIO_ADC":(-65,-300,795,20),"AUDIO_CLOCK":(-65,-625,795,-340),"AUDIO_MIC":(-65,-965,795,-665),
 "NFC":(935,-965,1795,15),"MOTION":(1945,-975,2805,5),"LED_DATA":(2960,-975,3820,5),
 "OPTIONS":(3975,-400,4835,10),"DEBUG_FABRIC":(3975,-975,4835,-450),
}
POWER_ENTRY = {"J1":[190,310],"F1":[350,310],"D1":[500,310],"U1":[690,310],"C1":[210,465],"C2":[350,465],"R1":[490,465],"R2":[630,465],"CS11":[250,590],"CS22":[430,590],"CS33":[610,590]}
RT_CORE = {"U6":[2040,830],"U7":[2680,1030],"R10":[2600,850],"R11":[2760,850],"C18":[2600,690],"R12":[2760,690],"SW1":[2600,535],"C19":[2760,535]}

def grid(refs, region, columns=None):
  x1,y1,x2,y2=region; n=len(refs)
  columns=columns or min(5,max(2,math.ceil(math.sqrt(n*(x2-x1)/max(1,y2-y1)))))
  rows=math.ceil(n/columns)
  xs=[round(x1+70+i*(x2-x1-140)/max(1,columns-1)) for i in range(columns)]
  ys=[round(y1+60+i*(y2-y1-120)/max(1,rows-1)) for i in range(rows)]
  return {r:[xs[i%columns],ys[i//columns]] for i,r in enumerate(refs)}

def place(block, refs):
  if block=="POWER_ENTRY": return POWER_ENTRY
  if block=="RT_CORE": return RT_CORE
  if block=="ESP_CORE":
    fixed={"U9":[4060,905],"J6":[4760,905]}; rest=[r for r in refs if r not in fixed]
    return fixed | grid(rest,(4230,790,4650,1125),3)
  return grid(refs,REGION[block],6 if block=="RT_DECOUPLE" else None)

def main():
  fixture=json.loads(FIXTURE.read_text()); ids={b["id"] for b in fixture["blocks"]}
  if ids != set(GROUP) or ids != set(REGION): raise SystemExit("fixture/layout block mismatch")
  domains={}; origins=[]
  for seq,b in enumerate(fixture["blocks"],1):
    bid=b["id"]; refs=list(b["component_refs"]); parts=place(bid,refs)
    if set(parts)!=set(refs): raise SystemExit(f"{bid} ref mismatch")
    cid=GROUP[bid]; left,bottom,right,top,title=CONTAINERS[cid]
    for ref,(x,y) in parts.items():
      if not(left+20<=x<=right-20 and bottom+20<=y<=top-20): raise SystemExit(f"{bid}.{ref} outside box {cid}")
      origins.append((x,y))
    domains[bid]={"sequence":seq,"container":cid,"suffix":SUFFIX_BY_CONTAINER[cid],"title":[left+30,top-40,title] if TITLE_OWNER[cid]==bid else None,"box":{"x1":left,"y1":bottom,"x2":right,"y2":top},"parts":parts,"additional_units":([{"ref":"U6","tag":"U6u2","sub_part_name":"MIMXRT1062DVJ6B.2","x":2330,"y":830}] if bid=="RT_CORE" else [])}
  if len(origins)!=len(set(origins)): raise SystemExit("component origins collide")
  out={"schema_version":2,"coordinate_unit":"0.01_inch","page_bounds":{"left":-115,"bottom":-1035,"right":4885,"top":1285},"layout_rule":"Captain's ten fixed boxes are immutable; automatic rectangle creation is forbidden.","designator_rule":"Every live schematic reference ends in - plus its 3-5 character domain suffix.","containers":{str(k):{"x1":v[0],"y1":v[1],"x2":v[2],"y2":v[3],"title":v[4],"suffix":SUFFIX_BY_CONTAINER[k]} for k,v in CONTAINERS.items()},"domains":domains}
  OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(f"WROTE {OUTPUT}\nBOXES=10 BLOCKS={len(domains)} COMPONENT_ORIGINS={len(origins)+1}")
  return 0

if __name__=="__main__": raise SystemExit(main())
