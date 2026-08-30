#!/usr/bin/env python3
import argparse
from copy import deepcopy
import mk_bceg_r3c_w_choice_preserving_human_authority as base

GAMMA_TOP={"language","capabilities"}
W_TOP={"subject_token","G_declared","G_inferred","U","Consent","Constraints","Exit","Drift","Provenance"}
FORBIDDEN_GAMMA_SEMANTIC={"G_declared","G_inferred","U","Consent","Constraints","Exit","Drift","Provenance","subject_token"}
FORBIDDEN_W_AUTHORITY={"Gamma_L","capabilities"}

def recursive_keys(x):
    out=set()
    if isinstance(x,dict):
        for k,v in x.items():
            out.add(k); out.update(recursive_keys(v))
    elif isinstance(x,list):
        for v in x: out.update(recursive_keys(v))
    return out

def typed_namespace_ok(c):
    gamma=c["Gamma_L"]; w=c["W_t"]
    gamma_root=set(gamma.keys())
    w_root=set(w.keys())
    gamma_recursive=recursive_keys(gamma)
    w_recursive=recursive_keys(w)
    return (
        gamma_root == GAMMA_TOP
        and w_root == W_TOP
        and gamma_recursive.isdisjoint(FORBIDDEN_GAMMA_SEMANTIC)
        and w_recursive.isdisjoint(FORBIDDEN_W_AUTHORITY)
    )

def counterfactual_independence_ok(c):
    action=c["action"]
    # W-only mutation must not alter capability result.
    cap_before=base.gamma_admits(c["Gamma_L"],action)
    w_mut=deepcopy(c)
    w_mut["W_t"]["G_declared"]="COUNTERFACTUAL_OTHER_TARGET"
    w_mut["W_t"]["Consent"]["valid"]=not w_mut["W_t"]["Consent"]["valid"]
    cap_after=base.gamma_admits(w_mut["Gamma_L"],action)
    # Gamma-only mutation must not alter the W binding or make/erase W receipt validity.
    w_binding_before=base.w_binding(c["W_t"],action)
    receipt_before=base.verify_w_receipt(c["W_t"],action,c["W_receipt"])
    gamma_mut=deepcopy(c)
    gamma_mut["Gamma_L"]["capabilities"][action]["available"]=not gamma_mut["Gamma_L"]["capabilities"][action]["available"]
    w_binding_after=base.w_binding(gamma_mut["W_t"],action)
    receipt_after=base.verify_w_receipt(gamma_mut["W_t"],action,gamma_mut["W_receipt"])
    return cap_before==cap_after and w_binding_before==w_binding_after and receipt_before==receipt_after

def separation_ok(c):
    return typed_namespace_ok(c) and counterfactual_independence_ok(c)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--journal",required=True); a=ap.parse_args()
    base.separation_ok=separation_ok
    base.main(a.output,a.journal)

if __name__=="__main__": main()
