from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25s_max_rup_minimization_structured_escalation as s

# Compatibility guard for one JSON-style boolean token in the experiment source.
# This is set before run(); it has no effect on selection, minimization, or solver logic.
s.false = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = s.run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
