import {parseCSV,makeIntegrator,normalizeBoundary} from './numerics.mjs';
'use strict';
const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
const csv=$('csv-data').textContent;
const data=parseCSV(csv),summary=JSON.parse($('summary-data').textContent);
const {integrate,lambdaAt,positive1D,end,endpoint}=makeIntegrator(data);
let boundary=5,announceTimer,lastHeight=0,stateURL;
function scientific(n){return (n>=0?'+':'−')+Math.abs(n).toExponential(3).replace('e-',' × 10⁻').replace('e+',' × 10⁺').replace(/([⁻⁺])(\d+)/,(_,s,d)=>s+d.replace(/\d/g,c=>'⁰¹²³⁴⁵⁶⁷⁸⁹'[c]));}
function format(n){return Math.abs(n)<1e-6?'≈ 0':(n>0?'+':'−')+Math.abs(n).toFixed(4);}
function boundaryText(){return boundary.toString();}
function node(tag,attrs={},text){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function el(svg,tag,attrs,text){const n=node(tag,attrs,text);svg.append(n);return n;}
function path(pts,x,y,key){return pts.map((p,i)=>(i?'L':'M')+x(p.z).toFixed(3)+','+y(p[key]).toFixed(3)).join(' ');}
function draw(svg,isDensity){
 const w=Math.max(240,svg.getBoundingClientRect().width),h=isDensity?205:178;
 svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('height',h);svg.replaceChildren();
 const margin={l:47,r:12,t:27,b:32},pw=w-margin.l-margin.r,ph=h-margin.t-margin.b;
 const ymin=isDensity?-.15:-.12,ymax=isDensity?.36:.12;
 const x=z=>margin.l+z/10*pw,y=v=>margin.t+(ymax-v)/(ymax-ymin)*ph;
 const ticks=isDensity?[-.1,0,.1,.2,.3]:[-.1,0,.1];
 const defs=el(svg,'defs');const clip=node('clipPath',{id:svg.id+'-clip'});clip.append(node('rect',{x:margin.l,y:margin.t,width:pw,height:ph}));defs.append(clip);
 el(svg,'rect',{x:margin.l,y:margin.t,width:pw,height:ph,fill:'none',stroke:'#d8dedb','stroke-width':1});
 for(const t of ticks){el(svg,'line',{x1:margin.l,x2:w-margin.r,y1:y(t),y2:y(t),stroke:t===0?'#9badaf':'#e7ebe7','stroke-width':1});el(svg,'text',{x:margin.l-8,y:y(t)+4,'text-anchor':'end'},t===0?'0':t.toFixed(1));}
 const xticks=w<460?[0,5,10]:[0,2,4,6,8,10];for(const t of xticks){el(svg,'text',{x:x(t),y:h-15,'text-anchor':'middle'},String(t));}
 el(svg,'text',{x:w-margin.r,y:h-1,'text-anchor':'end'},'z / Å');
 const g=el(svg,'g',{'clip-path':`url(#${svg.id}-clip)`});
 el(g,'rect',{x:x(0),y:margin.t,width:Math.max(0,x(boundary)-x(0)),height:ph,fill:'#28614e','fill-opacity':'.035'});
 if(isDensity){
  for(let i=0;i<data.length-1;i++){const a=data[i],b=data[i+1];let pieces=[[a,b]];if(a.lambda*b.lambda<0){const c={z:a.z-a.lambda*(b.z-a.z)/(b.lambda-a.lambda),lambda:0};pieces=[[a,c],[c,b]];}for(const [p,q] of pieces){const positive=p.lambda+q.lambda>=0;el(g,'path',{d:`M${x(p.z)},${y(0)}L${x(p.z)},${y(p.lambda)}L${x(q.z)},${y(q.lambda)}L${x(q.z)},${y(0)}Z`,fill:positive?'#f5d596':'#b0dfe7'});}}
  el(g,'path',{d:path(data,x,y,'lambda'),fill:'none',stroke:'#526971','stroke-width':1.5});
 }else{const dense=[];for(let i=0;i<data.length-1;i++){for(let j=0;j<5;j++){const z=data[i].z+(data[i+1].z-data[i].z)*j/5;dense.push({z,T:integrate(z)});}}dense.push(data.at(-1));el(g,'path',{d:path(dense,x,y,'T'),fill:'none',stroke:'#28614e','stroke-width':2.1});}
 for(const a of [4.63,5.37])el(g,'line',{x1:x(a),x2:x(a),y1:margin.t,y2:margin.t+ph,stroke:'#9badaf','stroke-dasharray':'2 4','stroke-width':1});
 if(isDensity){el(svg,'text',{x:x(4.63)-5,y:14,'text-anchor':'end',class:'atom-label'},'H · 4.63');el(svg,'text',{x:x(5.37)+5,y:14,'text-anchor':'start',class:'atom-label'},'5.37 · H');}
 el(g,'line',{x1:x(boundary),x2:x(boundary),y1:margin.t,y2:margin.t+ph,stroke:'#28614e','stroke-width':2,'stroke-dasharray':'5 4'});
 el(g,'circle',{cx:x(boundary),cy:y(isDensity?lambdaAt(boundary):integrate(boundary)),r:4.4,fill:'#28614e',stroke:'#fffefa','stroke-width':1.5});
 const bx=Math.max(margin.l+4,Math.min(w-margin.r-4,x(boundary)));const anchor=boundary<.7?'start':boundary>9.3?'end':'middle';
 el(svg,'text',{x:bx,y:margin.t+13,'text-anchor':anchor,class:'boundary-label'},'b');
 const hit=el(svg,'rect',{x:margin.l,y:margin.t,width:pw,height:ph,fill:'transparent',style:'cursor:ew-resize;touch-action:none','data-drag-area':'true'});
 const pointer=e=>{const r=svg.getBoundingClientRect();setBoundary(((e.clientX-r.left)*w/r.width-margin.l)/pw*10);};
 svg.onpointerdown=e=>{if(e.target.hasAttribute('data-drag-area')){if(e.pointerType==='mouse'&&e.button!==0)return;e.preventDefault();svg.setPointerCapture(e.pointerId);svg.dataset.dragging='1';pointer(e);}};
 svg.onpointermove=e=>{if(svg.dataset.dragging==='1')pointer(e);};
 svg.onpointerup=e=>{delete svg.dataset.dragging;if(svg.hasPointerCapture(e.pointerId))svg.releasePointerCapture(e.pointerId);};
 svg.onpointercancel=()=>{delete svg.dataset.dragging;};
}

function reportHeight(){
 const height=Math.ceil($('widget').getBoundingClientRect().height)+24;
 if(height!==lastHeight){lastHeight=height;if(window.parent!==window)window.parent.postMessage({type:'atlas-charge-height',height},window.location.origin);}
}
function update(inputEditing=false){
 const left=integrate(boundary),right=endpoint-left,b=boundaryText();
 $('boundary').value=boundary;$('boundary-value').textContent=b+' Å';
 if(!inputEditing)$('boundary-number').value=boundary;
 for(const side of ['left','right']){
  const value=side==='left'?left:right;
  $(side+'-value').innerHTML=format(value)+' <small>e</small>';
  $(side+'-precise').textContent=scientific(value)+' e';
  $('compact-'+side).textContent=format(value)+' e';
 }
 $('compact-boundary').textContent='b = '+b+' Å';
 $('residual').textContent=scientific(endpoint)+' e';
 $('boundary-commentary').textContent=boundary===5?'在 5 Å 对称面，两侧净数都约为零；键区积累与两端耗尽在各半胞内抵消。':boundary===0||boundary===10?'一个区间为空，另一个覆盖全胞，读数保留存档中的微小残差。':`左区间净${left>0?'增':'少'} ${Math.abs(left).toFixed(4)} 个电子。边界偏移圈入了不同空间；密度和 H 的位置保持固定。`;
 document.querySelectorAll('[data-boundary]').forEach(e=>e.setAttribute('aria-pressed',Math.abs(Number(e.dataset.boundary)-boundary)<1e-12));
 $('boundary').setAttribute('aria-valuetext',`边界 ${b} 埃，左侧 ${left.toExponential(4)} 个电子，右侧 ${right.toExponential(4)} 个电子`);
 draw($('density-plot'),true);draw($('cumulative-plot'),false);
 const state={definition:summary.definition,boundary_A:boundary,regions:[{lo_A:0,hi_A:boundary,delta_e:left},{lo_A:boundary,hi_A:end,delta_e:right}],endpoint_e:endpoint,positive_1d_e:positive1D(),positive_3d_e:summary.positive_3d_e,quadrature:summary.quadrature,source_summary:'summary.json',source_csv:'planar.csv',source_sha256_uncompressed:summary.source_sha256_uncompressed};
 const previous=stateURL;stateURL=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)+'\n'],{type:'application/json'}));
 $('download-state').href=stateURL;if(previous)setTimeout(()=>URL.revokeObjectURL(previous),60000);
 clearTimeout(announceTimer);announceTimer=setTimeout(()=>{$('live-value').textContent=`边界 ${b} 埃，左侧 ${format(left)} 个电子，右侧 ${format(right)} 个电子。`;},250);
 reportHeight();
}
function setBoundary(value,inputEditing=false){const next=normalizeBoundary(value);if(next===null)return;boundary=next;update(inputEditing);}
// The range accepts exact typed state; only pointer movement on the slider snaps to 0.01 Å.
$('boundary').addEventListener('input',e=>setBoundary(Math.round(Number(e.target.value)*100)/100));
$('boundary-number').addEventListener('input',e=>{const next=normalizeBoundary(e.target.value);if(next!==null)setBoundary(next,true);});
$('boundary-number').addEventListener('change',e=>{setBoundary(e.target.value);e.target.value=boundary;});
for(const id of ['boundary','boundary-number'])$(id).addEventListener('keydown',e=>{
 if(['Home','End','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
  e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?10:boundary+(['ArrowRight','ArrowUp'].includes(e.key)?0.01:-0.01);setBoundary(Number(n.toPrecision(14)));$('boundary-number').value=boundary;
 }
});
document.querySelectorAll('[data-boundary]').forEach(b=>b.addEventListener('click',()=>setBoundary(b.dataset.boundary)));
$('reset').addEventListener('click',()=>setBoundary(5));
$('positive-1d').textContent=positive1D().toFixed(10)+' e';
$('positive-3d').textContent=summary.positive_3d_e.toFixed(10)+' e';
new ResizeObserver(()=>update()).observe($('density-plot').parentElement);
new ResizeObserver(reportHeight).observe($('widget'));
window.addEventListener('message',e=>{if(e.source===window.parent && e.origin===window.location.origin && e.data?.type==='atlas-charge-size-request'){lastHeight=0;reportHeight();}});
window.addEventListener('pagehide',()=>{if(stateURL)URL.revokeObjectURL(stateURL);});
window.atlasCharge={integrate,lambdaAt,setBoundary,getState:()=>({boundary,left:integrate(boundary),right:endpoint-integrate(boundary),endpoint,rows:data.length}),data,summary};
// Preserve the original inspection hook for the coordinator's regression checks.
window.atlasPrototype=window.atlasCharge;
update();
