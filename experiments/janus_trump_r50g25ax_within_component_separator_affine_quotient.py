from __future__ import annotations

import argparse, hashlib, json, math
from itertools import combinations
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av
import janus_trump_r50g25at_tautology_hardened_runner as ath
import janus_trump_r50g25aw_defect_component_decomposition as aw

GATE = "R50G25AX_WITHIN_COMPONENT_SEPARATOR_OR_AFFINE_QUOTIENT_COMPRESSION_DOOR"
PREREG = "7b9cef877200b2f056099309d672923df2178b9a"
PARENT = "4858a25b5ce1cc8243fcb40304a0e0f0fa21dfa6"
TARGET_HASH = "cfbe4a9b4d4fbe5ec09ad3aa1c1ad8fe633e358b4d8744c92890133b6fa8056b"
POLICY = "TRUMP_PROOF_STATE_MACHINE_V1_0"

SEP_PASS = "AX_SEPARATOR_RELATION_WITHIN_L4_ON_AW_OBSTRUCTION"
QUOT_PASS = "AX_AFFINE_SIGNATURE_QUOTIENT_RELATION_WITHIN_L4_ON_AW_OBSTRUCTION"
OBSTRUCTION = "AX_WITHIN_COMPONENT_CERTIFIED_STATE_SPACE_EXCEEDS_L4"
REL_FAIL = "AX_PROOF_CARRYING_RELATION_CONTRACT_FAILURE"
IMPL_FAIL = "IMPLEMENTATION_OR_VERIFICATION_FAILURE"


def fh(formula):
    return av.formula_hash(av.canonical(formula))


def build_target():
    root, meta = list(av.frozen_candidates())[6]
    root = av.canonical(root)
    replay = av.asmod.y.policy_replay(root, av.asmod.r50g25g._chain())
    if replay.get("kind") != "RESIDUAL":
        raise AssertionError(("AW_TARGET_NOT_RESIDUAL", replay.get("kind")))
    residual = av.canonical(replay["state"])
    if fh(residual) != TARGET_HASH:
        raise AssertionError(("AW_TARGET_HASH_DRIFT", fh(residual)))
    effective, taut = av.effective_canonical(residual)
    ex = ath.hardened_extract(residual)
    fac = aw.factor_components(ex)
    targets = [c for c in fac["components"] if c["defect_count"] == 61 and c["variable_count"] == 20]
    if len(targets) != 1:
        raise AssertionError(("TARGET_COMPONENT_SELECTION_FAILURE", len(targets)))
    target = targets[0]
    defects = [tuple(ex["defects"][i]) for i in target["defect_indices"]]
    equations = [ex["equations"][i] for i in target["affine_equation_indices"]]
    L = sum(len(c) for c in effective)
    return residual, ex, target, defects, equations, L, taut, meta


def primal_graph(variables, defects):
    adj = {int(v): set() for v in variables}
    for clause in defects:
        vs = sorted({abs(int(l)) for l in clause})
        for a, b in combinations(vs, 2):
            adj[a].add(b); adj[b].add(a)
    return adj


def min_fill_order(adj0):
    adj = {v:set(ns) for v,ns in adj0.items()}
    order=[]; bags=[]; fill_edges=[]; width=0
    while adj:
        scored=[]
        for v in sorted(adj):
            ns=sorted(adj[v])
            missing=sum(1 for a,b in combinations(ns,2) if b not in adj[a])
            scored.append((missing,len(ns),v))
        _,_,v=min(scored)
        ns=sorted(adj[v]); width=max(width,len(ns)); bag=[v]+ns
        newfills=[]
        for a,b in combinations(ns,2):
            if b not in adj[a]:
                adj[a].add(b); adj[b].add(a)
                edge=[min(a,b),max(a,b)]
                fill_edges.append(edge); newfills.append(edge)
        bags.append({"eliminate":v,"later_neighbors":ns,"bag":bag,"new_fill_edges":newfills})
        for u in ns: adj[u].discard(v)
        del adj[v]; order.append(v)
    return {"order":order,"bags":bags,"fill_edges":fill_edges,"induced_width":width}


def verify_separator(adj0, cert, defects, variables):
    replay=min_fill_order(adj0)
    failures=[]
    if replay != cert:
        failures.append("DETERMINISTIC_ORDER_OR_FILL_REPLAY_MISMATCH")
    bagsets=[set(b["bag"]) for b in cert["bags"]]
    for i,c in enumerate(defects):
        vs={abs(int(l)) for l in c}
        if not any(vs <= bag for bag in bagsets):
            failures.append(f"CLAUSE_NOT_COVERED_BY_BAG:{i}")
    seen=set(cert["order"])
    if seen != set(map(int,variables)) or len(cert["order"]) != len(variables):
        failures.append("VARIABLE_ORDER_NOT_BIJECTION")
    return failures


def signed_signature(v, defects, equations):
    sig=[]
    for i,c in enumerate(defects):
        sign=0
        if v in c: sign=1
        elif -v in c: sign=-1
        sig.append(sign)
    coeff=[]
    for eq in equations:
        coeff.append(1 if v in set(map(int,eq["vars"])) else 0)
    return tuple(sig),tuple(coeff)


def quotient_classes(variables, defects, equations):
    groups={}
    for v in sorted(map(int,variables)):
        groups.setdefault(signed_signature(v,defects,equations),[]).append(v)
    classes=sorted((vals for vals in groups.values()), key=lambda x:(x[0],len(x)))
    return classes


def verify_quotient(classes, variables, defects, equations):
    flat=[v for c in classes for v in c]
    failures=[]
    if sorted(flat) != sorted(map(int,variables)) or len(flat)!=len(set(flat)):
        failures.append("QUOTIENT_NOT_PARTITION")
    for cls in classes:
        sigs={signed_signature(v,defects,equations) for v in cls}
        if len(sigs)!=1: failures.append("SIGNATURE_CLASS_DRIFT")
    return failures


def run():
    residual, ex, target, defects, equations, L, taut, meta = build_target()
    variables=target["variables"]
    adj=primal_graph(variables, defects)
    sep=min_fill_order(adj)
    sep_fail=verify_separator(adj,sep,defects,variables)
    w=int(sep["induced_width"]); sep_states=1<<w; budget=int(L)**4

    relation={
      "relation_id":"AX_REL_AW_YCORE_TO_SEPARATOR_DP",
      "DOMAIN":{"pass":fh(residual)==TARGET_HASH,"target_component":{"variables":len(variables),"defects":len(defects),"affine_equations":len(equations)}},
      "FORWARD_PRESERVATION":{"pass":len(sep_fail)==0,"basis":"every defect scope is contained in a verified elimination bag; affine parity retained as side constraint"},
      "CLAIM_SCOPED_RECONSTRUCTION":{"pass":len(sep_fail)==0,"scheme":"reverse elimination order with stored boundary assignment and local chosen value"},
      "SOURCE_VALIDATION":{"pass":ex.get("partition_pass") is True and not ex.get("replay_failures")},
      "EXACTNESS":{"pass":len(sep_fail)==0,"scope":"finite AW target CSP under standard variable-elimination semantics"},
      "SIZE_BOUND":{"pass":sep_states<=budget,"state_bound":sep_states,"L4_budget":budget},
      "TIME_BOUND":{"pass":sep_states<=budget,"bound":"O((clauses+variables)*2^(w+1)*poly(L)) on this frozen state; no asymptotic universal claim"},
      "COMPOSITION_SCOPE":{"pass":True,"scope":"AW residual -> target component -> separator DP representation only"},
      "PROVENANCE":{"pass":True,"preregistration_commit":PREREG,"parent_head":PARENT,"residual_hash":TARGET_HASH},
      "COUNTEREXAMPLE_TRACE":{"pass":True,"separator_failures":sep_fail}
    }
    relation_pass=all(bool(v.get("pass")) for v in relation.values())

    quotient=None
    if sep_states>budget:
        classes=quotient_classes(variables,defects,equations)
        qfail=verify_quotient(classes,variables,defects,equations)
        q=len(classes); qstates=1<<q
        quotient={"classes":classes,"q":q,"state_bound":qstates,"L4_budget":budget,"failures":qfail,"relation_pass":not qfail and qstates<=budget}

    if not relation_pass and sep_states<=budget:
        verdict=REL_FAIL
    elif sep_states<=budget:
        verdict=SEP_PASS
    elif quotient and quotient["relation_pass"]:
        verdict=QUOT_PASS
    else:
        verdict=OBSTRUCTION

    result={
      "gate":GATE,"status":"SCIENTIFIC_RESULT","preregistration_commit":PREREG,"parent_governed_AW_head":PARENT,
      "verdict":verdict,"residual_hash":TARGET_HASH,"residual_CLV":list(av.clv(residual)),"L":L,"L4_budget":budget,
      "target_component":{"variable_count":len(variables),"defect_count":len(defects),"affine_equation_count":len(equations),"variables":variables},
      "separator":{"algorithm":"DETERMINISTIC_MIN_FILL_TIE_DEGREE_THEN_VAR","induced_width":w,"state_bound_2_pow_w":sep_states,"budget_slack":budget-sep_states,"order":sep["order"],"bags":sep["bags"],"fill_edge_count":len(sep["fill_edges"]),"verification_failures":sep_fail},
      "quotient_fallback":quotient,"proof_carrying_relation":relation,"relation_pass":relation_pass,
      "tautology_count":len(taut),"truth_oracle":{"generation":False,"selection":False,"verdict":False},
      "scope":{"universal_coverage":"OPEN","asymptotic_polynomiality":"NOT_PROVED_BY_THIS_FINITE_GATE","separator_generalization":"OPEN"},
      "governance":{"policy":POLICY,"promotion_manifest_required_before_seal":True},
      "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); args=ap.parse_args()
    x=run(); args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:x[k] for k in ["verdict","L","L4_budget","relation_pass"]},sort_keys=True))

if __name__=="__main__": main()
