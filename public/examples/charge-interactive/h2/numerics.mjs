// Frozen-density quadrature; no geometry or density modification.
export function parseCSV(csv) {
 const rows=csv.trim().split(/\r?\n/).slice(1).map(l=>l.split(',').map(Number));
 if(rows.length!==145 || rows.some(r=>r.length!==4 || r.some(v=>!Number.isFinite(v)))) throw new Error('Expected 145 finite four-column samples');
 if(rows.some((r,i)=>i && r[0]<=rows[i-1][0])) throw new Error('z must increase');
 return rows.map(r=>({z:r[0],density:r[1],lambda:r[2],T:r[3]}));
}
export function makeIntegrator(data) {
 const end=data.at(-1).z, endpoint=data.at(-1).T;
 function integrate(z) {
  if(!Number.isFinite(z)) throw new Error('Boundary must be finite');
  if(z<=0)return 0;if(z>=end)return endpoint;
  let lo=0,hi=data.length-1;
  while(hi-lo>1){const mid=(lo+hi)>>1;if(data[mid].z<=z)lo=mid;else hi=mid;}
  const a=data[lo],b=data[hi],dx=z-a.z;
  return a.T+a.lambda*dx+(b.lambda-a.lambda)/(b.z-a.z)*dx*dx/2;
 }
 function lambdaAt(z) {
  if(z<=0)return data[0].lambda;if(z>=end)return data.at(-1).lambda;
  let i=0;while(data[i+1].z<z)i++;
  const a=data[i],b=data[i+1];return a.lambda+(b.lambda-a.lambda)*(z-a.z)/(b.z-a.z);
 }
 function positive1D() {
  let total=0;
  for(let i=1;i<data.length;i++){
   const a=data[i-1],b=data[i],width=b.z-a.z;
   if(a.lambda>=0 && b.lambda>=0)total+=(a.lambda+b.lambda)*width/2;
   else if(a.lambda*b.lambda<0){const positive=Math.max(a.lambda,b.lambda);total+=width*positive*positive/(2*Math.abs(b.lambda-a.lambda));}
  }
  return total;
 }
 return {integrate,lambdaAt,positive1D,end,endpoint};
}
export function normalizeBoundary(value) {
 if(String(value).trim()==='')return null;
 const n=Number(value);return Number.isFinite(n)?Math.max(0,Math.min(10,n)):null;
}
