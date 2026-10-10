#!/usr/bin/env python3
"""Build graphify-out/vault-graph.html - a custom, self-contained D3 visualization of graph.json.
Run after any graph rebuild (/vault-sync and scripts/auto-vault-sync.sh call this)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphify-out"
g = json.loads((OUT / "graph.json").read_text())
d3 = (ROOT / "scripts/node_modules/d3.min.js").read_text()

nodes = [{
    "id": n["id"], "label": n.get("label", n["id"]), "c": n.get("community", 0),
    "cn": n.get("community_name", "") or f"Community {n.get('community', 0)}",
    "t": n.get("file_type", "concept"), "src": n.get("source_file", ""), "loc": n.get("source_location"),
    "r": n.get("rationale") or (n.get("metadata") or {}).get("rationale"),
} for n in g["nodes"]]
ids = {n["id"] for n in nodes}
links = [{
    "source": e["source"], "target": e["target"], "rel": e.get("relation", ""),
    "conf": e.get("confidence", "EXTRACTED"), "w": e.get("weight", 1),
} for e in g["links"] if e["source"] in ids and e["target"] in ids]
data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False).replace("</", "<\\/")

html = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Vault Graph</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#07080c;--panel:rgba(13,15,22,.88);--line:rgba(255,255,255,.08);--fg:#e8eaf0;--mute:#8b91a3;--acc:#7cf2c9}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:13px/1.45 -apple-system,Inter,Segoe UI,system-ui,sans-serif;overflow:hidden}
#bg{position:fixed;inset:0;background:radial-gradient(1200px 800px at 30% 20%,#12172a 0%,#07080c 55%),radial-gradient(900px 700px at 80% 90%,#101a1a 0%,transparent 60%)}
svg{position:fixed;inset:0;width:100%;height:100%;cursor:grab}svg:active{cursor:grabbing}
.link{stroke-opacity:.22;fill:none}.link.inf{stroke-dasharray:4 4}
.node circle.core{stroke:#000;stroke-width:.8}.hot circle.core{stroke:#fff;stroke-width:2}
.node text{pointer-events:none;fill:#dfe3ee;font-weight:600;text-shadow:0 0 4px #000,0 0 8px #000,0 1px 2px #000}
.dim{opacity:.06}
#top{position:fixed;top:14px;left:14px;right:14px;display:flex;gap:10px;align-items:center;pointer-events:none;z-index:5}
#top>*{pointer-events:auto}
h1{margin:0;font-size:15px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);font-weight:700;padding:9px 14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;backdrop-filter:blur(10px)}
h1 small{color:var(--mute);font-weight:500;letter-spacing:0;text-transform:none;margin-left:10px}
#q{flex:1;max-width:420px;padding:10px 14px;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--fg);font-size:14px;outline:none;backdrop-filter:blur(10px)}
#q:focus{border-color:var(--acc)}
.btn{padding:9px 13px;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--fg);cursor:pointer;backdrop-filter:blur(10px);font-size:12px}
.btn:hover{border-color:var(--acc)}.btn.on{color:var(--acc);border-color:var(--acc)}
#legend{position:fixed;left:14px;bottom:14px;max-height:55vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;backdrop-filter:blur(10px);width:290px;z-index:5}
#legend.min #lgs{display:none}#legend.min{width:auto}#legend h3{margin:2px 6px 8px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}
.lg{display:flex;align-items:center;gap:8px;padding:4px 6px;border-radius:6px;cursor:pointer;font-size:12px}
.lg:hover{background:rgba(255,255,255,.05)}.lg.off{opacity:.35}
.sw{width:10px;height:10px;border-radius:50%;flex:none;box-shadow:0 0 8px currentColor}
.lg span.n{color:var(--mute);margin-left:auto;font-variant-numeric:tabular-nums}
#side{position:fixed;top:64px;right:14px;bottom:14px;width:340px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;backdrop-filter:blur(12px);overflow:auto;transform:translateX(380px);transition:transform .25s;z-index:5}
#side.open{transform:none}
#side h2{margin:0 0 4px;font-size:17px;line-height:1.25}
#side .meta{color:var(--mute);font-size:12px;margin-bottom:10px}
#side .pill{display:inline-block;padding:2px 8px;border-radius:99px;font-size:11px;margin:0 6px 6px 0;border:1px solid var(--line)}
#side .src{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--acc);word-break:break-all;margin:8px 0}
#side h4{margin:14px 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}
.nb{display:flex;gap:8px;align-items:baseline;padding:5px 6px;border-radius:6px;cursor:pointer}
.nb:hover{background:rgba(255,255,255,.05)}.nb .rel{color:var(--mute);font-size:11px;flex:none;width:130px;font-family:ui-monospace,Menlo,monospace}
.rat{background:rgba(124,242,201,.06);border-left:2px solid var(--acc);padding:8px 10px;border-radius:4px;margin-top:8px;font-size:12px}
#x{position:absolute;top:10px;right:12px;background:none;border:0;color:var(--mute);font-size:18px;cursor:pointer}
#hint{position:fixed;bottom:14px;right:14px;color:var(--mute);font-size:11px;z-index:4}
#tip{position:fixed;pointer-events:none;background:#000d;border:1px solid var(--line);padding:6px 10px;border-radius:8px;font-size:12px;display:none;z-index:9;max-width:320px}
</style></head><body>
<div id="bg"></div><svg id="s"></svg>
<div id="top"><h1>Vault Graph<small id="stats"></small></h1><input id="q" placeholder="Search nodes…  (Enter = focus, Esc = clear)"><button class="btn" id="labels">labels: hubs</button><button class="btn" id="phys">physics: on</button><button class="btn" id="fit">fit</button></div>
<div id="legend"><h3 id="lgh">Communities · click to toggle <span style="float:right;cursor:pointer" id="lgm">-</span></h3><div id="lgs"></div></div>
<div id="side"><button id="x">×</button><div id="sc"></div></div>
<div id="tip"></div>
<div id="hint">scroll = zoom · drag = pan · click node = focus · dbl-click bg = reset</div>
<script>__D3__</script>
<script>
const DATA=__DATA__;
const svg=d3.select('#s'),W=()=>innerWidth,H=()=>innerHeight;
const deg=new Map();DATA.links.forEach(l=>{deg.set(l.source,(deg.get(l.source)||0)+1);deg.set(l.target,(deg.get(l.target)||0)+1)});
DATA.nodes.forEach(n=>n.d=deg.get(n.id)||0);
const comms=[...new Set(DATA.nodes.map(n=>n.c))];
const counts={};DATA.nodes.forEach(n=>counts[n.c]=(counts[n.c]||0)+1);
comms.sort((a,b)=>counts[b]-counts[a]);
const pal=["#7cf2c9","#ff7ab6","#8fb3ff","#ffd166","#c39bff","#ff9f6e","#6ee7f7","#b6f26e","#ff6b6b","#f7b2ff","#8ef0a7","#ffc978","#9ad0ff","#f2a0c9","#d6ff7c","#ff8fa3","#7ce0ff","#ffe07c","#b4a0ff","#a0ffdc","#ffb4a0","#c8ff9e","#9ec3ff","#ffa8e6","#bdf7ff","#ffd9a0","#d0a0ff"];
const color=c=>pal[comms.indexOf(c)%pal.length];
const cname={};DATA.nodes.forEach(n=>cname[n.c]=n.cn);
const rad=n=>3+Math.sqrt(n.d)*2.2;
const g=svg.append('g');
const defs=svg.append('defs');const f=defs.append('filter').attr('id','glow').attr('x','-50%').attr('y','-50%').attr('width','200%').attr('height','200%');
f.append('feGaussianBlur').attr('stdDeviation',3).attr('result','b');const m=f.append('feMerge');m.append('feMergeNode').attr('in','b');m.append('feMergeNode').attr('in','SourceGraphic');
const link=g.append('g').selectAll('line').data(DATA.links).join('line').attr('class',l=>'link'+(l.conf==='INFERRED'?' inf':'')).attr('stroke-width',l=>l.rel==='calls'?1.2:.8);
const node=g.append('g').selectAll('g').data(DATA.nodes).join('g').attr('class','node').call(d3.drag().on('start',(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y}).on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}));
node.filter(n=>n.d>8).append('circle').attr('class','halo').attr('r',n=>rad(n)*2.2).attr('fill',n=>color(n.c)).attr('opacity',.18).attr('stroke','none');
node.append('circle').attr('class','core').attr('r',rad).attr('fill',n=>color(n.c));
node.append('text').attr('dy',n=>rad(n)+11).attr('text-anchor','middle').attr('font-size',n=>n.d>20?13:n.d>8?11:9.5).text(n=>n.label.length>34?n.label.slice(0,32)+'…':n.label);
let labelMode=1;const applyLabels=()=>node.select('text').style('display',n=>labelMode===2||(labelMode===1&&n.d>=6)?null:'none');applyLabels();
const cx={};comms.forEach((c,i)=>{const a=i/comms.length*Math.PI*2,r=Math.min(W(),H())*.38*(1+counts[c]/120);cx[c]=[W()/2+Math.cos(a)*r,H()/2+Math.sin(a)*r]});
const sim=d3.forceSimulation(DATA.nodes).force('link',d3.forceLink(DATA.links).id(d=>d.id).distance(l=>l.source.c===l.target.c?30:120).strength(l=>l.source.c===l.target.c?.6:.05)).force('charge',d3.forceManyBody().strength(n=>-60-n.d*8).distanceMax(400)).force('collide',d3.forceCollide(n=>rad(n)+3)).force('x',d3.forceX(n=>cx[n.c][0]).strength(.22)).force('y',d3.forceY(n=>cx[n.c][1]).strength(.22)).force('center',d3.forceCenter(W()/2,H()/2).strength(.02)).alphaDecay(.035).velocityDecay(.45);
sim.on('tick.draw',()=>{link.attr('x1',l=>l.source.x).attr('y1',l=>l.source.y).attr('x2',l=>l.target.x).attr('y2',l=>l.target.y);node.attr('transform',n=>`translate(${n.x},${n.y})`)});
link.attr('stroke',l=>color(l.source.c??DATA.nodes.find(n=>n.id===l.source).c));
const zoom=d3.zoom().scaleExtent([.08,6]).on('zoom',e=>g.attr('transform',e.transform));svg.call(zoom);
svg.on('dblclick.zoom',null).on('dblclick',reset);
const adj=new Map();DATA.links.forEach(l=>{const s=l.source.id??l.source,t=l.target.id??l.target;(adj.get(s)||adj.set(s,new Set()).get(s)).add(t);(adj.get(t)||adj.set(t,new Set()).get(t)).add(s)});
const hidden=new Set();
function applyHidden(){node.style('display',n=>hidden.has(n.c)?'none':null);link.style('display',l=>hidden.has(l.source.c)||hidden.has(l.target.c)?'none':null)}
let focus=null;
function reset(){focus=null;node.classed('dim',false).classed('hot',false);link.classed('dim',false).attr('stroke-opacity',null);document.getElementById('side').classList.remove('open')}
function focusNode(n){focus=n;const nb=adj.get(n.id)||new Set();node.classed('dim',o=>o!==n&&!nb.has(o.id)).classed('hot',o=>o===n);link.classed('dim',l=>l.source!==n&&l.target!==n).attr('stroke-opacity',l=>l.source===n||l.target===n?.9:null);side(n);
 const t=d3.zoomTransform(svg.node());svg.transition().duration(500).call(zoom.transform,d3.zoomIdentity.translate(W()/2-n.x*t.k,H()/2-n.y*t.k).scale(t.k))}
function side(n){const s=document.getElementById('side');s.classList.add('open');const rels=DATA.links.filter(l=>l.source===n||l.target===n).map(l=>({o:l.source===n?l.target:l.source,rel:l.rel,conf:l.conf,dir:l.source===n?'→':'←'})).sort((a,b)=>b.o.d-a.o.d);
 document.getElementById('sc').innerHTML=`<h2>${esc(n.label)}</h2><div class="meta">${n.d} connections</div><span class="pill" style="border-color:${color(n.c)};color:${color(n.c)}">${esc(n.cn)}</span><span class="pill">${n.t}</span>${n.src?`<div class="src">${esc(n.src)}${n.loc?' · '+esc(String(n.loc)):''}</div>`:''}${n.r?`<div class="rat">${esc(n.r)}</div>`:''}<h4>Connections</h4>${rels.map((r,i)=>`<div class="nb" data-i="${i}"><span class="rel">${r.dir} ${esc(r.rel)}${r.conf==='INFERRED'?' ?':''}</span><span style="color:${color(r.o.c)}">${esc(r.o.label)}</span></div>`).join('')||'<div class="meta">none</div>'}`;
 s.querySelectorAll('.nb').forEach(el=>el.onclick=()=>focusNode(rels[+el.dataset.i].o))}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
node.on('click',(e,n)=>{e.stopPropagation();focusNode(n)});
const tip=document.getElementById('tip');
node.on('mouseenter',(e,n)=>{tip.style.display='block';tip.innerHTML=`<b>${esc(n.label)}</b><br><span style="color:${color(n.c)}">${esc(n.cn)}</span> · ${n.d} links`}).on('mousemove',e=>{tip.style.left=e.clientX+14+'px';tip.style.top=e.clientY+14+'px'}).on('mouseleave',()=>tip.style.display='none');
document.getElementById('x').onclick=reset;
document.getElementById('stats').textContent=`${DATA.nodes.length} nodes · ${DATA.links.length} edges · ${comms.length} communities`;
const lg=d3.select('#lgs').selectAll('div').data(comms).join('div').attr('class','lg').html(c=>`<span class="sw" style="background:${color(c)};color:${color(c)}"></span><span>${esc(cname[c])}</span><span class="n">${counts[c]}</span>`).on('click',(e,c)=>{hidden.has(c)?hidden.delete(c):hidden.add(c);lg.classed('off',d=>hidden.has(d));applyHidden()});
const q=document.getElementById('q');q.oninput=()=>{const v=q.value.trim().toLowerCase();if(!v){node.classed('dim',false);link.classed('dim',false);return}node.classed('dim',n=>!n.label.toLowerCase().includes(v));link.classed('dim',true)};
q.onkeydown=e=>{if(e.key==='Enter'){const v=q.value.trim().toLowerCase();const hit=DATA.nodes.filter(n=>n.label.toLowerCase().includes(v)).sort((a,b)=>b.d-a.d)[0];if(hit)focusNode(hit)}if(e.key==='Escape'){q.value='';reset()}};
document.getElementById('labels').onclick=e=>{labelMode=(labelMode+1)%3;e.target.textContent='labels: '+['off','hubs','all'][labelMode];applyLabels()};
let phys=true;document.getElementById('phys').onclick=e=>{phys=!phys;e.target.textContent='physics: '+(phys?'on':'off');e.target.classList.toggle('on',!phys);phys?sim.alpha(.3).restart():sim.stop()};
function fit(anim=true){const vis=DATA.nodes.filter(n=>!hidden.has(n.c));const xs=vis.map(n=>n.x),ys=vis.map(n=>n.y);const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);const L=document.getElementById('legend').classList.contains('min')?20:320,T=70,B=30,R=20;const k=Math.min((W()-L-R)/(x1-x0+40),(H()-T-B)/(y1-y0+40),2);const t=d3.zoomIdentity.translate(L+(W()-L-R)/2-(x0+x1)/2*k,T+(H()-T-B)/2-(y0+y1)/2*k).scale(k);(anim?svg.transition().duration(600):svg).call(zoom.transform,t)}
document.getElementById('fit').onclick=()=>fit();document.getElementById('lgm').onclick=e=>{const l=document.getElementById('legend');l.classList.toggle('min');e.target.textContent=l.classList.contains('min')?'+':'-';fit()};let tk=0;sim.on('tick.fit',()=>{if(++tk%40===0&&sim.alpha()>.05)fit()});sim.on('end',fit);
</script></body></html>"""
out = html.replace("__D3__", d3).replace("__DATA__", data)
(OUT / "vault-graph.html").write_text(out)
print(f"wrote {OUT/'vault-graph.html'} ({len(nodes)} nodes, {len(links)} edges, {len(out)//1024} KB)")
