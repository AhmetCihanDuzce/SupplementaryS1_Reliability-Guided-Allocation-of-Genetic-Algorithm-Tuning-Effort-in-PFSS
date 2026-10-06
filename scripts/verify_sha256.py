#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path.cwd()
manifest=root/'SHA256_MANIFEST.txt'
failed=[]
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    sha, rel=line.split('  ',1)
    p=root/rel
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=sha: failed.append((rel,sha,got))
if failed:
    for rel,e,g in failed: print('FAIL',rel,e,g)
    raise SystemExit(1)
print(f'PASS: {sum(1 for x in manifest.read_text().splitlines() if x.strip())} files verified.')
