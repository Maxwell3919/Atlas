"""Copy only reviewed public input paths before Astro sees any content."""
import pathlib,json,hashlib,shutil,argparse
p=argparse.ArgumentParser();p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--destination',type=pathlib.Path,required=True);a=p.parse_args();root=a.manifest.resolve().parent.parent
assert not a.destination.exists(), 'Destination must be new'
rows=json.loads(a.manifest.read_text())['files'];assert len({x['path'] for x in rows})==len(rows)
for x in rows:
 rel=pathlib.PurePosixPath(x['path']);assert not rel.is_absolute() and '..' not in rel.parts
 src=root/str(rel);assert src.is_file() and not src.is_symlink();assert hashlib.sha256(src.read_bytes()).hexdigest()==x['sha256']
 dest=a.destination/str(rel);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
assert not (a.destination/'src/content/cases/epc-research-notes.md').exists()
(a.destination/'node_modules').symlink_to(root/'node_modules',target_is_directory=True)
print(json.dumps({'copied_public_inputs':len(rows),'private_source_present':False}))
