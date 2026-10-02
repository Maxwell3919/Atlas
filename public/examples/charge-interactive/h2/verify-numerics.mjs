// Run: node verify-numerics.mjs [directory of immutable source CSV/summary]
// Pure arithmetic and file checks; no browser, DOM, DFT or geometry generation.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {parseCSV,makeIntegrator,normalizeBoundary} from './numerics.mjs';
const base=fileURLToPath(new URL('.',import.meta.url));
const csv=fs.readFileSync(base+'planar.csv','utf8'), summary=JSON.parse(fs.readFileSync(base+'summary.json','utf8'));
const data=parseCSV(csv), {integrate,lambdaAt,positive1D,end,endpoint}=makeIntegrator(data);
// Independent reference accumulates every segment from 0, without using cumulative CSV values.
function reference(z){
 let total=0;
 for(let i=1;i<data.length;i++){
  const a=data[i-1],b=data[i];if(z<=a.z)break;
  const width=Math.min(z,b.z)-a.z, full=b.z-a.z;
  const v=a.lambda+(b.lambda-a.lambda)*width/full;
  total+=width*(a.lambda+v)/2;
 }
 return total;
}
let maxIntegralError=0,maxConservationError=0,maxCumulativeError=0,maxAreaRelationError=0;
const boundaries=Array.from({length:10001},(_,i)=>10*i/10000).concat([0,4.63,4.7,4.9,4.999999,5,5.000001,5.1,5.3,5.37,5.123456789,10,end]);
for(const b of boundaries){
 const left=integrate(b),right=endpoint-left;
 maxIntegralError=Math.max(maxIntegralError,Math.abs(left-reference(b)));
 maxConservationError=Math.max(maxConservationError,Math.abs(left+right-endpoint));
 assert(Number.isFinite(lambdaAt(b)));
}
for(const r of data){maxCumulativeError=Math.max(maxCumulativeError,Math.abs(r.T-reference(r.z)));maxAreaRelationError=Math.max(maxAreaRelationError,Math.abs(r.lambda-summary.area_A2*r.density));}
assert(maxIntegralError<1e-12);assert(maxConservationError<1e-14);assert(maxCumulativeError<1e-12);assert(maxAreaRelationError<1e-14);
assert(Math.abs(positive1D()-0.20193873954723515)<1e-12);
assert(positive1D()<summary.positive_3d_e);
assert(Math.abs(endpoint-summary.full_cell_residual_e)<1e-14);
assert.equal(normalizeBoundary('5.123456789'),5.123456789);assert.equal(normalizeBoundary(''),null);assert.equal(normalizeBoundary('no'),null);assert.equal(normalizeBoundary('Infinity'),null);assert.equal(normalizeBoundary(-1),0);assert.equal(normalizeBoundary(11),10);
const html=fs.readFileSync(base+'index.html','utf8');
const embedded=html.match(/<script id="csv-data"[^>]*>([\s\S]*?)<\/script>/)[1];
assert.deepEqual(parseCSV(embedded),data);
const embeddedSummary=JSON.parse(html.match(/<script id="summary-data"[^>]*>([\s\S]*?)<\/script>/)[1]);
assert.deepEqual(embeddedSummary,summary);
let sourceComparison='not requested';
if(process.argv[2]){
 const source=process.argv[2].replace(/\/$/,'')+'/';
 assert.deepEqual(fs.readFileSync(base+'planar.csv'),fs.readFileSync(source+'planar.csv'));
 assert.deepEqual(fs.readFileSync(base+'summary.json'),fs.readFileSync(source+'summary.json'));
 sourceComparison='CSV and summary byte-identical to immutable source';
}
console.log(JSON.stringify({status:'passed',boundaryCount:boundaries.length,rows:data.length,maxIntegralError_e:maxIntegralError,maxConservationError_e:maxConservationError,maxCumulativeError_e:maxCumulativeError,maxAreaRelationError_e_A:maxAreaRelationError,positive_1d_e:positive1D(),positive_3d_e:summary.positive_3d_e,endpoint_e:endpoint,sourceComparison,representative:boundaries.filter(b=>[0,4.9,5,5.1,5.123456789,10].includes(b)).filter((b,i,a)=>a.indexOf(b)===i).map(b=>({boundary_A:b,left_e:integrate(b),right_e:endpoint-integrate(b)})),limitations:['No DOM or browser interaction executed','Source JSON/CSV actual browser download awaits coordinator','3D summary consumed as source evidence; raw CHGCAR not recomputed']},null,2));
