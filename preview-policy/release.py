"""Release-only exclusion of one internal-locator JSON download; no scientific text edits."""
import argparse,pathlib,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--preview',type=pathlib.Path,required=True);p.add_argument('--expected',type=pathlib.Path);p.add_argument('--receipt',type=pathlib.Path,required=True);a=p.parse_args()
file='m/fermi-nesting/qe/index.html';target='/Atlas/examples/enrichment-20261003/strain/band-pair-check.json'
f=a.preview/file;t=f.read_text();old='<a href="'+target+'">检查记录</a>';new='<span>检查记录（本次未公开）</span>';assert t.count(old)==1
f.write_text(t.replace(old,new));assert target not in f.read_text()
assert not (a.preview/target.removeprefix('/Atlas/')).exists()
files={str(x.relative_to(a.preview)):hashlib.sha256(x.read_bytes()).hexdigest() for x in a.preview.rglob('*') if x.is_file()}
if a.expected:
 expected=json.loads(a.expected.read_text())['files'];assert files=={x['path']:x['sha256'] for x in expected},'Built output differs from reviewed exact release output'
a.receipt.write_text(json.dumps({'policy':'one internal-locator JSON excluded; one download anchor changed to nonclickable status','exact_hits':1,'page':file,'numerical_or_body_rewrite':False,'output_hash_check':bool(a.expected),'files':len(files)},ensure_ascii=False,indent=2)+'\n')
