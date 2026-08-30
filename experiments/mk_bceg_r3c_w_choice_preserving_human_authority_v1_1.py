#!/usr/bin/env python3
import argparse
import mk_bceg_r3c_w_choice_preserving_human_authority as base

W_EXACT_KEYS={"G_declared","G_inferred","U","Consent","Constraints","Exit","Drift","Provenance","subject_token"}
CAPABILITY_EXACT_KEYS={"capabilities","available","semantic_status","cost_status","language"}

def recursive_keys(x):
    out=set()
    if isinstance(x,dict):
        for k,v in x.items():
            out.add(k)
            out.update(recursive_keys(v))
    elif isinstance(x,list):
        for v in x:
            out.update(recursive_keys(v))
    return out

def exact_separation_ok(c):
    gamma_keys=recursive_keys(c["Gamma_L"])
    w_keys=recursive_keys(c["W_t"])
    return gamma_keys.isdisjoint(W_EXACT_KEYS) and w_keys.isdisjoint(CAPABILITY_EXACT_KEYS)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--journal",required=True); a=ap.parse_args()
    base.separation_ok=exact_separation_ok
    base.main(a.output,a.journal)

if __name__=="__main__": main()
