// Restricted to the public two-atom, real Gamma Si example. Reject other mappings.
export function parseSiModes(csv, diagnostics, axsf, modesText) {
  const table = (text) => { const [header, ...lines] = text.trim().split(/\r?\n/); const keys=header.split(','); return lines.map(line=>Object.fromEntries(line.split(',').map((v,i)=>[keys[i],v]))); };
  if (!/q\s*=\s*0\.0+\s+0\.0+\s+0\.0+/.test(modesText)) throw Error('Expected Gamma mode file');
  const rows=table(csv).filter(r=>r.asr==='crystal');
  const freq=table(diagnostics).filter(r=>r.asr==='crystal');
  if(rows.length!==12 || freq.length!==6) throw Error('Expected six modes and two atoms');
  const lattice = axsf.match(/PRIMVEC\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)/)?.slice(1).map(r=>r.trim().split(/\s+/).map(Number));
  if (!lattice?.flat().every(Number.isFinite)) throw Error('Invalid lattice');
  const frames=[...axsf.matchAll(/PRIMCOORD\s+(\d+)\s*\n\s*2\s+1\s*\n([^\n]+)\n([^\n]+)/g)];
  if(frames.length!==6) throw Error('Expected six AXSF mode blocks');
  const modeHits=[...modesText.matchAll(/freq\s*\(\s*(\d+)\)\s*=.*?=\s*([-+\d.]+)\s*\[cm-1\]([\s\S]*?)(?=freq|\*{4}|$)/g)];
  if(modeHits.length!==6) throw Error('Expected six native frequencies');
  const modes=Array.from({length:6},(_,i)=>{
    const r=rows.filter(r=>Number(r.mode)===i+1).sort((a,b)=>Number(a.atom)-Number(b.atom));
    if(r.length!==2 || r.some((r,j)=>Number(r.atom)!==j+1))throw Error('Atom order mismatch');
    const atoms=r.map(r=>({position:['x_angstrom','y_angstrom','z_angstrom'].map(k=>Number(r[k])),vector:['ux_real','uy_real','uz_real'].map(k=>Number(r[k]))}));
    if(!atoms.flatMap(a=>[...a.position,...a.vector]).every(Number.isFinite) || r.some(r=>['ux_imag','uy_imag','uz_imag'].some(k=>Number(r[k])!==0)))throw Error('Requires finite real Gamma displacements');
    const norm=Math.hypot(...atoms.flatMap(a=>a.vector));if(Math.abs(norm-1)>2e-6)throw Error('Unexpected whole-mode norm');
    const f=freq.find(r=>Number(r.mode)===i+1);const frequency=Number(f?.['frequency_cm-1']);
    const hit=modeHits[i];if(Number(hit[1])!==i+1 || Math.abs(Number(hit[2])-frequency)>1e-8)throw Error('Frequency mapping mismatch');
    const native=[...hit[3].matchAll(/\(\s*([^\n]+)\)/g)].map(x=>x[1].trim().split(/\s+/).map(Number));
    const frame=frames[i];if(Number(frame[1])!==i+1)throw Error('AXSF mode order');
    [frame[2],frame[3]].forEach((line,j)=>{
      const [symbol,...v]=line.trim().split(/\s+/);if(symbol!=='Si' || v.length!==6)throw Error('AXSF species');
      const n=v.map(Number);
      atoms[j].position.forEach((x,k)=>{if(Math.abs(x-n[k])>5.1e-6)throw Error('Position mapping');});
      atoms[j].vector.forEach((x,k)=>{
        if(Math.abs(x-native[j]?.[2*k])>1e-8 || native[j]?.[2*k+1]!==0)throw Error('Native displacement mapping');
        if(Math.abs(.1*x/norm-n[k+3])>5.1e-6)throw Error('AXSF whole-mode scaling mismatch');
      });
    });
    return {number:i+1,frequency,atoms,norm};
  });
  return {lattice,modes,asr:'crystal',q:[0,0,0],positionUnit:'Å',displayAmplitudeUnit:'Å',axsfWholeModeScale:0.1};
}
export function displacement(mode, phaseDegrees, amplitude) {
  if(!Number.isFinite(phaseDegrees) || !Number.isFinite(amplitude) || amplitude<0 || amplitude>1)throw Error('Invalid display parameters');
  const factor=amplitude*Math.cos(phaseDegrees*Math.PI/180)/mode.norm;
  return mode.atoms.map(a=>a.position.map((p,k)=>p+factor*a.vector[k]));
}
