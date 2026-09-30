from __future__ import print_function
import hashlib,os,re
raw=open('POTCAR.reference','rb').read()
blocks=re.findall(br'.*?End of Dataset[^\n]*(?:\n|$)',raw,re.S)
if len(blocks)!=4 or b''.join(blocks)!=raw:
 raise ValueError('Expected exactly four complete PAW datasets')
expected=[b'PAW_PBE Sn_d 06Sep2000',b'PAW_PBE Se 06Sep2000',b'PAW_PBE N 08Apr2002',b'PAW_PBE Sr_sv 07Sep2000']
for block,title in zip(blocks,expected):
 if title not in block: raise ValueError('Unexpected PAW dataset')
for name,parts in [('snse2',blocks[:2]),('sr2n',blocks[2:])]:
 data=b''.join(parts)
 if os.path.exists(name+'/POTCAR'): raise ValueError('POTCAR already exists')
 open(name+'/POTCAR','wb').write(data)
 out=['SHA256 '+hashlib.sha256(data).hexdigest()]
 for b in parts:
  out.extend(line.decode('ascii').strip() for line in b.splitlines() if b'TITEL' in line or b'ZVAL' in line)
 open(name+'/POTCAR.identity.txt','w').write('\n'.join(out)+'\n')
 print(name+' '+out[0])

