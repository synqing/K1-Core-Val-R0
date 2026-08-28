import json, html, pathlib
D = "evidence/VAL-G2-2026-08-28/canonical-core-val-r0/repair-queue.json"
d = json.load(open(D))
e = lambda s: html.escape(str(s)) if s is not None else ""
def mono(items):
    if not items: return ""
    return " ".join(f'<code>{e(x)}</code>' for x in items)

SEV = {"P0":("critical","P0"),"P1":("high","P1"),"P2":("medium","P2"),"P3":("low","P3")}
EV  = {"NETLIST-CONFIRMED":"netlist","DATASHEET-DERIVED":"datasheet","BOM/CPL":"bom","DRAWING-ONLY":"drawing"}

c = d["counts"]; gb = d.get("global_blocker") or {}
txs = sorted(d["transactions"], key=lambda t: t.get("order") or 0)
decisions = d.get("decisions_for_captain") or []
withdrawn = d.get("withdrawn") or []
disagree  = d.get("disagreements") or []
precon    = d.get("preconditions") or []

def row(t, idx):
    sev = t.get("severity","P3"); scls, slab = SEV.get(sev,("low",sev))
    ev  = t.get("evidence_class",""); ecls = EV.get(ev,"drawing")
    blocked = t.get("blocked_on") or []
    dep = t.get("depends_on") or []
    hard = [b for b in blocked if b != "CAP-01"]
    flags = []
    if hard: flags.append(f'<span class="flag flag-block">blocked · {e(", ".join(hard))}</span>')
    if dep:  flags.append(f'<span class="flag flag-dep">after {e(", ".join(dep))}</span>')
    return f"""
<article class="fix sev-{scls}" data-sev="{e(sev)}" data-ev="{e(ev)}" data-block="{e(t.get('circuit_block',''))}">
  <div class="fix-rail"><span class="ord">{idx}</span></div>
  <div class="fix-body">
    <header class="fix-head">
      <code class="txid">{e(t.get('transaction_id'))}</code>
      <span class="chip chip-stage">{e(t.get('stage'))}</span>
      <span class="chip chip-ev ev-{ecls}">{e(ev)}</span>
      <span class="sev-tag sev-tag-{scls}">{slab}</span>
      <span class="blockname">{e(t.get('circuit_block'))}</span>
      {''.join(flags)}
    </header>
    <p class="what">{e(t.get('notes')) or e(t.get('expected_semantic_delta'))}</p>
    <dl class="detail">
      <dt>Objects</dt><dd>{mono(t.get('objects'))}</dd>
      <dt>Nets</dt><dd>{mono(t.get('nets'))}</dd>
      <dt>Expected result</dt><dd>{e(t.get('expected_semantic_delta'))}</dd>
      <dt>Visual delta</dt><dd>{e(t.get('expected_visual_delta'))}</dd>
      <dt>How to check</dt><dd>{e(t.get('inspection_criteria'))}</dd>
    </dl>
  </div>
</article>"""

blocks = sorted({t.get("circuit_block","") for t in txs if t.get("circuit_block")})
opts = "".join(f'<option value="{e(b)}">{e(b)}</option>' for b in blocks)

def pre_card(p):
    rows = ""
    for label, key in (("Inference","inference"),("Action","action")):
        v = p.get(key)
        if v: rows += f"<dt>{label}</dt><dd>{e(v)}</dd>"
    if p.get("settles"): rows += f"<dt>Settles</dt><dd>{mono(p.get('settles'))}</dd>"
    why = f'<p class="what">{e(p.get("why"))}</p>' if p.get("why") else ""
    dl  = f'<dl class="detail">{rows}</dl>' if rows else ""
    return f"""
<article class="pre">
  <header><code class="txid">{e(p.get('id'))}</code><span class="chip chip-stage">{e(p.get('kind'))}</span>
  <strong>{e(p.get('title'))}</strong></header>
  {why}{dl}
</article>"""
pre_html = "".join(pre_card(p) for p in precon)

dec_html = "".join(f"""
<article class="dec">
  <header><code class="txid">{e(x.get('id'))}</code><strong>{e(x.get('title'))}</strong></header>
  <p class="what"><span class="lbl">Recommendation</span> {e(x.get('recommendation'))}</p>
  <p class="ev-note"><span class="lbl">Evidence</span> {e(x.get('evidence'))}</p>
  <p class="blocks-note"><span class="lbl">Blocks</span> {mono(x.get('blocks'))}</p>
</article>""" for x in decisions)

wd_html = "".join(f"""
<article class="wd">
  <header><code class="txid">{e(x.get('id'))}</code><strong>{e(x.get('claim'))}</strong></header>
  <p><span class="lbl">Raised by</span> {e(x.get('raised_by'))}</p>
  <p><span class="lbl">Killed by</span> {e(x.get('killed_by'))}</p>
  <p><span class="lbl">What survives</span> {e(x.get('what_survives'))}</p>
</article>""" for x in withdrawn)

dis_html = "".join(f"""
<article class="dis">
  <header><code class="txid">{e(x.get('id'))}</code><strong>{e(x.get('question'))}</strong></header>
  <p><span class="lbl">Lane A</span> {e(x.get('lane_a'))}</p>
  <p><span class="lbl">Lane B</span> {e(x.get('lane_b'))}</p>
  <p><span class="lbl">Resolution</span> {e(x.get('resolution'))}</p>
</article>""" for x in disagree)

bysev = c["by_severity"]; byev = c["by_evidence_class"]
HTML = f"""<title>K1 Core Val R0 Fault Register</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>
:root{{
  --ground:#F7F8FA; --surface:#FFFFFF; --surface-2:#EEF1F5;
  --ink:#0F1419; --ink-2:#3D4756; --muted:#69748A; --line:#D8DEE7;
  --copper:#B87333; --copper-dim:#8E5825;
  --critical:#B3261E; --high:#B45309; --medium:#1D4F91; --low:#6B7684;
  --netlist:#15803D; --datasheet:#7C3AED; --bom:#B45309; --drawing:#0E7490;
  --shadow:0 1px 2px rgba(15,20,25,.06),0 4px 14px rgba(15,20,25,.05);
}}
@media (prefers-color-scheme:dark){{
  :root:not([data-theme="light"]){{
    --ground:#12161C; --surface:#1A1F27; --surface-2:#222833;
    --ink:#E6EAF0; --ink-2:#B7C0CD; --muted:#8C97A6; --line:#2E3641;
    --copper:#D08B4C; --copper-dim:#B87333;
    --critical:#F0776B; --high:#E0A050; --medium:#7BA9E0; --low:#93A0B2;
    --netlist:#5FBF82; --datasheet:#B79BF0; --bom:#E0A050; --drawing:#5CB6C9;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 18px rgba(0,0,0,.3);
  }}
}}
:root[data-theme="dark"]{{
  --ground:#12161C; --surface:#1A1F27; --surface-2:#222833;
  --ink:#E6EAF0; --ink-2:#B7C0CD; --muted:#8C97A6; --line:#2E3641;
  --copper:#D08B4C; --copper-dim:#B87333;
  --critical:#F0776B; --high:#E0A050; --medium:#7BA9E0; --low:#93A0B2;
  --netlist:#5FBF82; --datasheet:#B79BF0; --bom:#E0A050; --drawing:#5CB6C9;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 6px 18px rgba(0,0,0,.3);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:"Source Sans 3",ui-sans-serif,system-ui,sans-serif;font-size:16px;line-height:1.6}}
.wrap{{max-width:1140px;margin:0 auto;padding:0 24px 96px}}
code{{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86em}}
h1,h2,h3{{font-family:Archivo,ui-sans-serif,system-ui,sans-serif;text-wrap:balance;margin:0}}
.eyebrow{{font-family:"JetBrains Mono",monospace;font-size:.72rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--copper);font-weight:500}}

header.masthead{{padding:56px 0 28px;border-bottom:2px solid var(--copper)}}
h1{{font-size:clamp(2rem,4.4vw,3rem);font-weight:700;letter-spacing:-.02em;margin:.35em 0 .3em}}
.sub{{color:var(--ink-2);max-width:62ch;font-size:1.05rem}}

.band{{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin:28px 0 0;border-radius:3px;overflow:hidden}}
.stat{{background:var(--surface);padding:14px 16px}}
.stat .n{{font-family:Archivo,sans-serif;font-size:1.9rem;font-weight:700;line-height:1;
  font-variant-numeric:tabular-nums;display:block}}
.stat .k{{font-family:"JetBrains Mono",monospace;font-size:.68rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);margin-top:6px;display:block}}
.n-critical{{color:var(--critical)}} .n-high{{color:var(--high)}}
.n-medium{{color:var(--medium)}} .n-low{{color:var(--low)}} .n-copper{{color:var(--copper)}}

.blocker{{margin:28px 0 0;border:1px solid var(--critical);border-left:4px solid var(--critical);
  background:var(--surface);border-radius:3px;padding:18px 20px;box-shadow:var(--shadow)}}
.blocker h3{{font-size:1rem;color:var(--critical);margin-bottom:6px}}
.blocker p{{margin:0;color:var(--ink-2);font-size:.95rem}}

h2.sec{{font-size:1.5rem;font-weight:600;margin:56px 0 6px;letter-spacing:-.01em}}
.sec-note{{color:var(--muted);font-size:.95rem;margin:0 0 20px;max-width:70ch}}

.controls{{position:sticky;top:0;z-index:5;background:var(--ground);
  padding:14px 0;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:10px;align-items:center}}
select,button.f{{font:inherit;font-size:.86rem;padding:6px 11px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);border-radius:3px;cursor:pointer}}
button.f[aria-pressed="true"]{{background:var(--copper);border-color:var(--copper);color:#fff}}
button.f:focus-visible,select:focus-visible{{outline:2px solid var(--copper);outline-offset:2px}}
.count-live{{margin-left:auto;font-family:"JetBrains Mono",monospace;font-size:.78rem;color:var(--muted)}}

.fix,.pre,.dec,.wd,.dis{{background:var(--surface);border:1px solid var(--line);border-radius:3px;
  margin-top:12px;box-shadow:var(--shadow)}}
.fix{{display:grid;grid-template-columns:52px 1fr}}
.fix-rail{{border-right:1px solid var(--line);display:flex;align-items:flex-start;
  justify-content:center;padding:16px 0;position:relative}}
.fix-rail::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px}}
.sev-critical .fix-rail::before{{background:var(--critical)}}
.sev-high .fix-rail::before{{background:var(--high)}}
.sev-medium .fix-rail::before{{background:var(--medium)}}
.sev-low .fix-rail::before{{background:var(--low)}}
.ord{{font-family:"JetBrains Mono",monospace;font-size:.8rem;color:var(--muted);
  font-variant-numeric:tabular-nums}}
.fix-body{{padding:14px 18px 16px;min-width:0}}
.fix-head{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}}
.txid{{font-weight:700;color:var(--ink);font-size:.82rem}}
.chip{{font-family:"JetBrains Mono",monospace;font-size:.66rem;letter-spacing:.06em;
  text-transform:uppercase;padding:2px 7px;border-radius:2px;border:1px solid var(--line);color:var(--muted)}}
.chip-stage{{background:var(--surface-2)}}
.chip-ev{{background:transparent;font-weight:500}}
.ev-netlist{{color:var(--netlist);border-color:var(--netlist)}}
.ev-datasheet{{color:var(--datasheet);border-color:var(--datasheet)}}
.ev-bom{{color:var(--bom);border-color:var(--bom)}}
.ev-drawing{{color:var(--drawing);border-color:var(--drawing)}}
.sev-tag{{font-family:"JetBrains Mono",monospace;font-size:.68rem;font-weight:700;padding:2px 6px;border-radius:2px;color:#fff}}
.sev-tag-critical{{background:var(--critical)}} .sev-tag-high{{background:var(--high)}}
.sev-tag-medium{{background:var(--medium)}} .sev-tag-low{{background:var(--low)}}
.blockname{{font-family:"JetBrains Mono",monospace;font-size:.74rem;color:var(--muted)}}
.flag{{font-size:.7rem;font-family:"JetBrains Mono",monospace;padding:2px 7px;border-radius:2px}}
.flag-block{{background:color-mix(in srgb,var(--critical) 14%,transparent);color:var(--critical)}}
.flag-dep{{background:var(--surface-2);color:var(--muted)}}
.what{{margin:0 0 10px;color:var(--ink);font-size:.97rem}}
dl.detail{{display:grid;grid-template-columns:auto 1fr;gap:3px 16px;margin:0;font-size:.88rem}}
dl.detail dt{{font-family:"JetBrains Mono",monospace;font-size:.66rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);padding-top:3px}}
dl.detail dd{{margin:0;color:var(--ink-2);min-width:0;overflow-wrap:anywhere}}
dl.detail dd code{{background:var(--surface-2);padding:1px 5px;border-radius:2px;color:var(--ink)}}
.lbl{{font-family:"JetBrains Mono",monospace;font-size:.64rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);margin-right:7px}}
.pre{{border-left:4px solid var(--copper)}}
.dec{{border-left:4px solid var(--medium)}}
.wd{{border-left:4px solid var(--low);opacity:.9}}
.dis{{border-left:4px solid var(--high)}}
.pre header,.dec header,.wd header,.dis header{{display:flex;flex-wrap:wrap;gap:9px;align-items:baseline;
  padding:14px 18px 0}}
.pre .what,.dec p,.wd p,.dis p{{padding:0 18px;margin:8px 0}}
.pre dl.detail{{padding:0 18px 16px}}
.dec p:last-child,.wd p:last-child,.dis p:last-child{{padding-bottom:16px}}
.dec header strong,.wd header strong,.dis header strong,.pre header strong{{font-family:Archivo,sans-serif;font-size:1rem}}
footer{{margin-top:64px;padding-top:20px;border-top:1px solid var(--line);
  color:var(--muted);font-size:.84rem}}
@media (max-width:640px){{ .fix{{grid-template-columns:36px 1fr}} dl.detail{{grid-template-columns:1fr}} }}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style>

<div class="wrap">
<header class="masthead">
  <span class="eyebrow">K1-CORE-VAL-R0 · VAL-G2.1 · frozen 489736:464c27d4</span>
  <h1>Fault register</h1>
  <p class="sub">Every fix the canonical single-sheet schematic needs before VAL-G2 can close.
  {c['repairs']} repairs, {c['declared_transactions']} declared transactions, ordered so that no
  transaction invalidates the evidence of one before it. Every entry is a proposal — the single
  writer reconfirms against live before acting.</p>

  <div class="band">
    <div class="stat"><span class="n n-copper">{c['repairs']}</span><span class="k">repairs</span></div>
    <div class="stat"><span class="n">{c['declared_transactions']}</span><span class="k">transactions</span></div>
    <div class="stat"><span class="n n-critical">{bysev['P0']}</span><span class="k">P0</span></div>
    <div class="stat"><span class="n n-high">{bysev['P1']}</span><span class="k">P1</span></div>
    <div class="stat"><span class="n n-medium">{bysev['P2']}</span><span class="k">P2</span></div>
    <div class="stat"><span class="n n-low">{bysev['P3']}</span><span class="k">P3</span></div>
    <div class="stat"><span class="n">{c['gated_on_a_captain_decision']}</span><span class="k">need a ruling</span></div>
    <div class="stat"><span class="n n-critical">{c['cannot_start_until_a_decision_is_made']}</span><span class="k">fully stalled</span></div>
  </div>

  <div class="blocker">
    <h3>{e(gb.get('id'))} — {e(gb.get('summary'))}</h3>
    <p>{e(gb.get('detail'))}</p>
  </div>
</header>

<h2 class="sec">Do these first</h2>
<p class="sec-note">Read-only. Neither is a canvas mutation, and both change what the repairs below are allowed to assume.</p>
{pre_html}

<h2 class="sec">The fixes</h2>
<p class="sec-note">In execution order. The stripe is severity; the outlined chip is how strong the
evidence is — <strong>netlist-confirmed</strong> means EasyEDA's own DRC names it,
<strong>datasheet-derived</strong> means a vendor document says the circuit is wrong and no
automated check on this host will ever see it.</p>

<div class="controls">
  <button class="f" data-sev="all" aria-pressed="true">All severities</button>
  <button class="f" data-sev="P0" aria-pressed="false">P0</button>
  <button class="f" data-sev="P1" aria-pressed="false">P1</button>
  <button class="f" data-sev="P2" aria-pressed="false">P2</button>
  <button class="f" data-sev="P3" aria-pressed="false">P3</button>
  <select id="ev"><option value="all">All evidence</option>
    <option value="NETLIST-CONFIRMED">Netlist-confirmed</option>
    <option value="DATASHEET-DERIVED">Datasheet-derived</option>
    <option value="BOM/CPL">BOM / CPL</option>
    <option value="DRAWING-ONLY">Drawing-only</option></select>
  <select id="blk"><option value="all">All blocks</option>{opts}</select>
  <span class="count-live" id="live"></span>
</div>

<div id="list">
{''.join(row(t,i+1) for i,t in enumerate(txs))}
</div>

<h2 class="sec">Rulings only you can make</h2>
<p class="sec-note">{len(decisions)} decisions that belong to Captain, not to a writer.
{c['cannot_start_until_a_decision_is_made']} repairs cannot start at all until these land.</p>
{dec_html}

<h2 class="sec">Where two lanes disagree</h2>
<p class="sec-note">Stated with both citations rather than silently resolved.</p>
{dis_html}

<h2 class="sec">Ruled out — do not re-raise</h2>
<p class="sec-note">{len(withdrawn)} findings were raised and then killed by evidence, including two
of the orchestrator's own. Recorded so they are not rediscovered and re-queued.</p>
{wd_html}

<footer>
  Generated from <code>repair-queue.json</code> · frozen denominator <code>489736:464c27d4</code> ·
  netlist evidence from the 14:58:52 GUI DRC · live has moved past the frozen hash, so every entry
  is a proposal for the single writer to reconfirm.
</footer>
</div>

<script>
(function(){{
  var sev="all", ev="all", blk="all";
  var items=[].slice.call(document.querySelectorAll(".fix"));
  var live=document.getElementById("live");
  function apply(){{
    var n=0;
    items.forEach(function(el){{
      var ok=(sev==="all"||el.dataset.sev===sev)&&(ev==="all"||el.dataset.ev===ev)&&(blk==="all"||el.dataset.block===blk);
      el.hidden=!ok; if(ok)n++;
    }});
    live.textContent=n+" of "+items.length+" shown";
  }}
  document.querySelectorAll("button.f").forEach(function(b){{
    b.addEventListener("click",function(){{
      document.querySelectorAll("button.f").forEach(function(o){{o.setAttribute("aria-pressed","false");}});
      b.setAttribute("aria-pressed","true"); sev=b.dataset.sev; apply();
    }});
  }});
  document.getElementById("ev").addEventListener("change",function(e){{ev=e.target.value;apply();}});
  document.getElementById("blk").addEventListener("change",function(e){{blk=e.target.value;apply();}});
  apply();
}})();
</script>
"""
out = pathlib.Path("/private/tmp/claude-501/-Users-spectrasynq-Workspace-Management-Software-K1-CORE-VAL-R0/b251c596-3b2a-4615-bea5-0fa176ec682a/scratchpad/fault-register.html")
out.write_text(HTML)
print("wrote", out, len(HTML), "bytes")
print("transactions rendered:", len(txs), "| decisions:", len(decisions), "| withdrawn:", len(withdrawn), "| disagreements:", len(disagree), "| preconditions:", len(precon))
