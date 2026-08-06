#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).with_name('.cn7u_repair1_producer')
source=b''.join(path.read_bytes() for path in sorted(root.iterdir()))
exec(compile(source,str(root),'exec'),globals())
