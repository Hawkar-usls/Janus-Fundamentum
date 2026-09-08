from __future__ import annotations
import argparse, json
from pathlib import Path
import janus_trump_r50g25ba18_composite_pair_signature_derived_support_fanout as ba18

def main(out):
    r=ba18.run()
    Path(out).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    failed=[k for k,v in r['obligations'].items() if not v and k not in ('INDEPENDENT_REPLAY_PASS','PRESEAL_COMPLETENESS_PASS')]
    print('BA18_FALSIFIERS='+json.dumps(r['falsifiers'],sort_keys=True))
    print('BA18_FAILED_BUILDER_OBLIGATIONS='+json.dumps(failed,sort_keys=True))
    print('BA18_TERNARY_SUBPASSES='+json.dumps(r['ternary_subpasses'],sort_keys=True))
    print('BA18_TERNARY_KERNEL_N1='+json.dumps(r['ternary_carrier']['kernel_n1'],sort_keys=True))
    print('BA18_TERNARY_ADDITIVE_RECURRENCE='+json.dumps(r['ternary_carrier']['additive_recurrence'],sort_keys=True))
    if r['falsifiers'] or failed or not all(r['ternary_subpasses'].values()):
        raise SystemExit(1)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();main(a.out)
