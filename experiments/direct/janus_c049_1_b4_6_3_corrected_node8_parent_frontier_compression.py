#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).with_name('.cn8f_candidate_producer')
source=b''.join(path.read_bytes() for path in sorted(root.iterdir()))
exec(compile(source,str(root),'exec'),globals())
