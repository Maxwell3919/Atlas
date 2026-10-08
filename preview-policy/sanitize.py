"""Narrow postprocess of frozen public HTML; scientific source remains unchanged."""
import pathlib,re,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--preview',type=pathlib.Path,required=True);parser.add_argument('--receipt',type=pathlib.Path,required=True);args=parser.parse_args()
allow={
 'm/phonon-linewidth/qe/index.html':{'/Atlas/cases/epc-research-notes/#double-grid-research-record':1},
 'm/epc/qe/index.html':{'/Atlas/cases/epc-research-notes/#double-grid-research-record':1,'/Atlas/cases/epc-research-notes/#zrcl2-sc2c-k64-k96-record':1}}
pattern=re.compile(r'<a href="(?P<href>/Atlas/cases/epc-research-notes/#[^"]+)"\s*>(?P<label>.*?)</a>',re.S)
changes=[]
for rel,expected in allow.items():
 p=args.preview/rel;text=p.read_text();seen={};replacements=[]
 def replace(m):
  href=m['href'];assert href in expected,'Unapproved excluded target';seen[href]=seen.get(href,0)+1
  replacement='<span>'+m['label']+'</span><span>（未公开）</span>'
  replacements.append({'original':m.group(),'replacement':replacement,'href_removed':href});return replacement
 new=pattern.sub(replace,text);assert seen==expected,(rel,seen,expected)
 for change in replacements:assert change['href_removed'] not in new
 p.write_text(new);changes.append({'path':rel,'replacements':replacements})
args.receipt.write_text(json.dumps({'mode':'POSTPROCESS_NOT_NEW_BUILD','exact_hits':3,'changes':changes},ensure_ascii=False,indent=2)+'\n')
