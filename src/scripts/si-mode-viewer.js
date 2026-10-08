import { displacement } from '../lib/si-mode-data.js';
for(const root of document.querySelectorAll('[data-si-mode-viewer]')){
 const data=JSON.parse(root.querySelector('[data-mode-data]').textContent);
 const get=name=>root.querySelector(`[data-${name}]`);
 const canvas=root.querySelector('canvas'),ctx=canvas.getContext('2d');
 if(!ctx){get('status').textContent='浏览器不支持画布，请下载原数据。';continue;}
 let phase=0,amplitude=.1,number=4,view='xz',playing=false,frame=0,last=0;
 function render(target,width,height){
  const mode=data.modes[number-1],positions=displacement(mode,phase,amplitude);
  const axes=view==='xy'?[0,1]:view==='yz'?[1,2]:[0,2];
  const corners=Array.from({length:8},(_,i)=>[0,1,2].map(k=>data.lattice.reduce((sum,v,j)=>sum+((i>>j)&1)*v[k],0)));
  const limits=axes.map(k=>[Math.min(...corners.map(p=>p[k]))-1.4,Math.max(...corners.map(p=>p[k]))+1.4]);
  const chartTop=105,chartBottom=height-70;
  const scale=Math.min((width-64)/(limits[0][1]-limits[0][0]),(chartBottom-chartTop)/(limits[1][1]-limits[1][0]));
  const center=limits.map(([lo,hi])=>(lo+hi)/2);
  const project=p=>[width/2+scale*(p[axes[0]]-center[0]),(chartTop+chartBottom)/2-scale*(p[axes[1]]-center[1])];
  target.clearRect(0,0,width,height);target.fillStyle='#ffffff';target.fillRect(0,0,width,height);
  target.font='15px system-ui';target.lineWidth=1.5;target.fillStyle='#20354b';
  // CSS-sized labels are never reduced with the original 720-pixel bitmap.
  const labels=[`Mode ${number} · ${mode.frequency.toFixed(6)} cm⁻¹`,
   `Projection ${view} · phase ${phase.toFixed(1)}°`,
   `Whole-mode A = ${amplitude.toFixed(2)} Å`];
  labels.forEach((text,i)=>target.fillText(text,14,25+i*25));
  target.strokeStyle='#b7c5ce';for(let i=0;i<8;i++)for(let j=0;j<3;j++){const z=i^(1<<j);if(z>i){const a=project(corners[i]),b=project(corners[z]);target.beginPath();target.moveTo(...a);target.lineTo(...b);target.stroke();}}
  mode.atoms.forEach((a,i)=>{const p=project(a.position),q=project(positions[i]);target.strokeStyle='#8796a4';target.beginPath();target.arc(...p,9,0,2*Math.PI);target.stroke();target.strokeStyle='#284f91';target.beginPath();target.moveTo(...p);target.lineTo(...q);target.stroke();target.fillStyle=i?'#b86126':'#275593';target.beginPath();target.arc(...q,7,0,2*Math.PI);target.fill();const label='Si '+(i+1),metrics=target.measureText(label),padding=12;
    const labelWidth=Math.max(metrics.width,metrics.actualBoundingBoxRight||0);
    const leftInk=Math.max(0,metrics.actualBoundingBoxLeft||0);
    let labelX=q[0]+12;
    if(labelX+labelWidth>width-padding)labelX=q[0]-12-labelWidth;
    labelX=Math.max(padding+leftInk,Math.min(labelX,width-padding-labelWidth));
    const ascent=metrics.actualBoundingBoxAscent||15,descent=metrics.actualBoundingBoxDescent||0;
    const labelY=Math.max(padding+ascent,Math.min(q[1]-12,height-padding-descent));
    target.fillText(label,labelX,labelY);});
  target.fillStyle='#20354b';target.strokeStyle='#20354b';target.beginPath();target.moveTo(16,height-49);target.lineTo(16+scale,height-49);target.stroke();target.fillText('1 Å',24+scale,height-44);
  target.fillText(`Axes ${view[0]} / ${view[1]} · coordinates Å`,14,height-24);
  target.font='14px system-ui';target.fillText('Display scale, not thermal amplitude',14,height-5);
 }
 function draw(){
  const width=canvas.getBoundingClientRect().width,height=canvas.getBoundingClientRect().height;
  const dpr=window.devicePixelRatio||1;
  const pixelWidth=Math.round(width*dpr),pixelHeight=Math.round(height*dpr);
  if(canvas.width!==pixelWidth||canvas.height!==pixelHeight){canvas.width=pixelWidth;canvas.height=pixelHeight;}
  ctx.setTransform(pixelWidth/width,0,0,pixelHeight/height,0,0);
  render(ctx,width,height);
  get('phase').value=String(Math.round(phase));get('phase-label').textContent=phase.toFixed(0)+'°';get('amplitude-label').textContent=amplitude.toFixed(2)+' Å';
 }
 function status(){get('status').textContent=`模式 ${number}，${data.modes[number-1].frequency.toFixed(6)} cm⁻¹；${playing?'演示播放':'已暂停'}。`;get('play').textContent=playing?'暂停':'播放';get('play').setAttribute('aria-pressed',String(playing));}
 function tick(time){if(!playing)return;if(last)phase=(phase+Math.min(time-last,100)*.06)%360;last=time;draw();frame=requestAnimationFrame(tick);}
 function pause(){playing=false;cancelAnimationFrame(frame);last=0;status();}
 function toggle(){if(playing)pause();else{playing=true;last=0;status();frame=requestAnimationFrame(tick);}}
 get('play').addEventListener('click',toggle);
 get('export').addEventListener('click',()=>{
  pause();draw();
  const snapshot=document.createElement('canvas');snapshot.width=1200;snapshot.height=800;
  const exportContext=snapshot.getContext('2d');
  if(!exportContext){get('export-status').textContent='PNG 导出不可用。';return;}
  exportContext.setTransform(2,0,0,2,0,0);render(exportContext,600,400);
  const filename=`si-gamma-mode${number}-${view}-phase${phase.toFixed(1)}-A${amplitude.toFixed(2)}A.png`;
  snapshot.toBlob(blob=>{
   if(!blob){get('export-status').textContent='PNG 导出失败，请重试。';return;}
   const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=filename;link.click();
   setTimeout(()=>URL.revokeObjectURL(url),1000);
   get('export-status').textContent='已导出当前视图：'+filename;
  },'image/png');
 });
 get('phase').addEventListener('input',e=>{pause();phase=Number(e.target.value);draw();});
 get('amplitude').addEventListener('input',e=>{amplitude=Number(e.target.value);draw();});
 get('mode').addEventListener('change',e=>{pause();number=Number(e.target.value);draw();status();});
 get('view').addEventListener('change',e=>{view=e.target.value;draw();});
 get('reset').addEventListener('click',()=>{pause();phase=0;amplitude=.1;number=4;view='xz';get('mode').value='4';get('view').value='xz';get('amplitude').value='.1';draw();status();});
 canvas.addEventListener('keydown',e=>{if(e.key===' '){e.preventDefault();toggle();}else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(e.key)){e.preventDefault();pause();phase=e.key==='Home'?0:(phase+(['ArrowLeft','ArrowDown'].includes(e.key)?-5:5)+360)%360;draw();}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
 new ResizeObserver(()=>draw()).observe(canvas);
 draw();status();
}
