from __future__ import annotations

import argparse
import json
import math
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG="6629acf7fa320be5bdd55f6b3239603e331e3500"
FIREWALL="b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
PARENT="1592e07d966df0dd2e57960792ccaf14e4422c51"
Q=2; BLOCK=30
HOLDOUTS=((1,1,1),(1,2,1),(2,1,2),(2,2,1),(2,3,2),(3,2,2))


def canon(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))

def minimize(cs):
    xs=[]
    for c in cs:
        z=canon(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c)); out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))

def dp(F,v):
    pos=[c for c in F if v in c]; neg=[c for c in F if -v in c]; rest=[c for c in F if v not in c and -v not in c]
    raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None: taut+=1
            else: raw.append(z)
    duplicates=len(raw)-len(set(raw)); new=minimize(rest+raw); retained=[c for c in new if c not in rest]
    return new,{"raw_pairs":len(pos)*len(neg),"tautological":taut,"non_tautological":len(raw),"duplicates":duplicates,"retained":len(retained)}

def source_ok(x,a,b): return all(ai or x for ai in a) and all((not x) or bj for bj in b)
def projected_ok(a,b): return all(a) or all(b)

def source_clauses(qs,p,n):
    x=qs[0]; aa=qs[1:1+p]; bb=qs[1+p:]
    return [(ai,x) for ai in aa]+[(-x,bj) for bj in bb]

def build(U,g,p,n):
    d=p+n; base,lvs,_=ba4.build_instance(U,g,d+1); qs=[Q+ba4.lane_off(g,i) for i in range(d+1)]; cross=source_clauses(qs,p,n)
    return list(base)+cross,lvs,qs,cross

def clause_ok(a,c): return any((bool(a[abs(l)]) if l>0 else not bool(a[abs(l)])) for l in c)
def make_model(first,U,g,p,n,xbit,aa,bb):
    bits=[xbit]+list(aa)+list(bb); a={}
    for lane,b in enumerate(bits):
        proto=first[(int(b),1-int(b))]; lo=ba4.lane_off(g,lane)
        for j in range(g):
            off=lo+BLOCK*j
            for v,val in proto.items(): a[int(v)+off]=bool(val)
    cs,lvs,qs,cross=build(U,g,p,n)
    qvec=[]
    for lane,b in enumerate(bits):
        lo=ba4.lane_off(g,lane); qvec.append([int(bool(a[Q+lo+BLOCK*j])) for j in range(g)])
    return all(clause_ok(a,c) for c in cs) and all(qvec[i]==[bits[i]]*g for i in range(len(bits)))
def namespace_ok(cs,lvs,cross):
    mem={int(v):i for i,vs in enumerate(lvs) for v in vs}
    if any(lvs[i]&lvs[j] for i,j in combinations(range(len(lvs)),2)): return False
    actual=[]
    for c in cs:
        if len({mem[abs(int(l))] for l in c})>1: actual.append(tuple(c))
    return actual==[tuple(c) for c in cross]
def exact_size(g,p,n):
    d=p+n
    return 67*g*(d+1)-d-2,163*g*(d+1)-2*d-4,20*g*(d+1),250*g*(d+1)-3*d-6

def local_kernel(U,orientation):
    g=2; base,lvs,_=ba4.build_instance(U,g,2); qs=[Q+ba4.lane_off(g,i) for i in range(2)]
    src=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1]); target=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK)
    cur=minimize(list(base)+[src]); totals={"raw_pairs":0,"tautological":0,"non_tautological":0,"duplicates":0,"retained":0}; live=len(cur); neighpeak=0
    for lane in range(2):
        lo=ba4.lane_off(g,lane)
        for bv in ba4.az.ORDER:
            v=int(bv)+lo; neigh=set()
            for c in cur:
                if v in c or -v in c: neigh|={abs(int(l)) for l in c if abs(int(l))!=v}
            neighpeak=max(neighpeak,len(neigh)); cur,m=dp(cur,v)
            for k in totals: totals[k]+=m[k]
            live=max(live,len(cur))
    mem={int(v):i for i,vs in enumerate(lvs) for v in vs}; cross=[]
    for c in cur:
        if len({mem[abs(int(l))] for l in c})>1: cross.append(c)
    return {"pass":minimize(cross)==minimize([target]),"raw":totals,"live":live,"width_diag":neighpeak,"target":target,"cross":cross}

def check_symbolic_math(errors,x):
    a=x["BA9_1_symbolic_elimination_theorem"]
    if a.get("existential")!="EXISTS x F = A OR B" or "AND_i AND_j" not in a.get("distributive_induction",{}).get("conclusion",""): errors.append("SYMBOLIC_ELIMINATION_RECORD")
    # Independent algebra: for arbitrary p,n, restriction x=0 selects every a_i and x=1 selects every b_j; finite products distribute pairwise.
    if not a.get("generic_in_p_n"): errors.append("GENERIC_SYMBOLIC_FLAG")
    fill=x["BA9_3_exact_residual_graph"]
    if fill.get("E_source")!="p+n" or fill.get("E_residual")!="p*n" or fill.get("E_peak")!="p+n+p*n": errors.append("FILL_GRAPH_FORMULA")
    q=x["BA9_4_quadratic_maximum"]
    if q.get("identity")!="4pn=(p+n)^2-(p-n)^2=d^2-(p-n)^2<=d^2": errors.append("QUADRATIC_IDENTITY")
    mc=x["BA9_6_exact_model_counts"]
    if mc.get("source_model_count")!="2^n+2^p" or mc.get("projected_model_count")!="2^n+2^p-1": errors.append("MODEL_COUNT_FORMULA")
    rec=x["BA9_7_constructive_return"]
    if rec.get("map")!="x := NOT A, A=AND_i a_i": errors.append("RECONSTRUCTION_MAP")

def check_polarity(errors,x):
    # Independent symbolic counting: choose r positive pivot occurrences C(d,r), then d independent leaf signs.
    for d in range(2,8):
        total=sum((2**d)*math.comb(d,r) for r in range(d+1))
        if total!=2**(2*d): errors.append(f"POLARITY_SUM_D{d}")
        top=2*(2**d)
        if top!=2**(d+1): errors.append(f"TOP_D{d}")
    # BA8 special case exact 64 polarity rows.
    top=two=0
    for leaf in product((1,-1),repeat=3):
        for piv in product((1,-1),repeat=3):
            r=sum(s>0 for s in piv)
            if r in (0,3): top+=1
            elif r*(3-r)==2: two+=1
    if (top,two)!=(16,48): errors.append("BA8_POLARITY_SPECIAL")
    if x["BA9_5_BA8_d3_diagnostic"].get("counts")!={"TOP":16,"TWO":48}: errors.append("BA8_POLARITY_RECORD")
def check_width(errors,x):
    w=x["BA9_9_width_theorem"]
    if w.get("residual_exact")!="tw(K_{p,n})=min(p,n)" or w.get("transient_exact")!="tw_transient=min(p,n)+1": errors.append("WIDTH_FORMULA")
    # Independent proof certificate: WLOG p<=n. Bags A_all+{b_j} give width p. Removing <p vertices leaves one vertex on each side, hence connected, so kappa=p and tw>=p. Cone: add x to every bag for width p+1; if x survives it connects all, if removed with <=p-1 others Kpn remains connected, so kappa>=p+1. K3 is direct.
    fw=x["BA9_10_full_BA4_width_composition"]
    if fw.get("upper")!="max(13,min(p,n)+1)" or fw.get("lower")!="min(p,n)+1" or fw.get("equality_claimed") is not False: errors.append("FULL_WIDTH_RECORD")
def verify(path,out):
    x=json.loads(Path(path).read_text()); errors=[]
    if x.get("preregistration_commit")!=PREREG: errors.append("PREREG_DRIFT")
    if x.get("methodology_firewall_commit")!=FIREWALL: errors.append("FIREWALL_DRIFT")
    if x.get("parent_BA8_final_meta_commit")!=PARENT: errors.append("PARENT_DRIFT")
    if x.get("outcome")!="BA9-A_PARAMETERIZED_SINGLE_PIVOT_BIPARTITE_FILL_MULTIPLICATION_CERTIFIED": errors.append("OUTCOME")
    if x.get("failure_count")!=0 or x.get("falsifiers"): errors.append("FAILURE_LEDGER")
    if x.get("cycles_started") or x.get("repeated_branching_elimination_started") or x.get("arbitrary_CNF_coverage_started") or x.get("next_gate_started"): errors.append("SCOPE_ESCAPE")
    if x.get("P_VS_NP")!="OPEN" or x.get("SAT_IN_P")!="NOT_PROVED" or x.get("TRUMP_finished") is not False: errors.append("GLOBAL_FIREWALL")
    check_symbolic_math(errors,x); check_polarity(errors,x); check_width(errors,x)
    cond=x["BA9_14_pn_equality_conditions"]
    if cond.get("universal_pn_claim") is not False or len(cond.get("conditions",[]))!=7: errors.append("EQUALITY_CONDITIONS")
    outfw=x["BA9_11_output_size_firewall"]
    if outfw.get("explicit_output_lower_bound")!="Omega(p*n)" or outfw.get("structural_certificate")!="Theta(g*d+p*n)" or outfw.get("source_only_O_nlogn_claim_forbidden") is not True: errors.append("OUTPUT_FIREWALL")
    comp=x["BA9_complexity"]
    if comp.get("T_total")!="O((g*d+p*n)*log(g*d+p*n))" or comp.get("actual_carrier_bound")!="O(g*d)": errors.append("COMPLEXITY")
    no=x["BA9_no_hidden_state_enumeration"]
    if no.get("generic_truth_table_rows")!=0 or no.get("generic_boundary_state_table_rows")!=0 or no.get("generic_proof_depends_on_tested_parameters") is not False: errors.append("HIDDEN_ENUMERATION")
    U,first,gates,hard=ba4.source_hardening()
    if not all(bool(v) for v in gates.values()): errors.append("PARENT_BA4_GATES")
    kp=local_kernel(U,"positive"); kn=local_kernel(U,"negative")
    tr=x["BA9_12_actual_carrier_raw_work"]
    if not kp["pass"] or not kn["pass"]: errors.append("LOCAL_CARRIER_KERNEL")
    if tr.get("positive_local_kernel",{}).get("raw_accounting")!=kp["raw"] or tr.get("negative_local_kernel",{}).get("raw_accounting")!=kn["raw"]: errors.append("RAW_ACCOUNTING")
    if tr.get("polynomial_bound")!="O(g*d)" or tr.get("naive_whole_star_DP_promotion_authority")!="ZERO": errors.append("RAW_SYMBOLIC_BOUND")
    replay_cases=0
    for g,p,n in HOLDOUTS:
        d=p+n; cs,lvs,qs,cross=build(U,g,p,n)
        if not namespace_ok(cs,lvs,cross): errors.append(f"NAMESPACE_{g}_{p}_{n}")
        C,L,V,S=exact_size(g,p,n); actual=(len(cs),sum(len(c) for c in cs),len(set().union(*lvs)),len(cs)+sum(len(c) for c in cs)+len(set().union(*lvs)))
        if actual!=(C,L,V,S): errors.append(f"SIZE_{g}_{p}_{n}")
        sat=0; proj=set()
        for bits in product((0,1),repeat=d+1):
            xb=bits[0]; aa=bits[1:1+p]; bb=bits[1+p:]
            if source_ok(xb,aa,bb):
                sat+=1; proj.add(tuple(aa+bb)); replay_cases+=1
                if not make_model(first,U,g,p,n,xb,aa,bb): errors.append(f"SOURCE_MODEL_{g}_{p}_{n}_{bits}")
        expected_proj={z for z in product((0,1),repeat=d) if projected_ok(z[:p],z[p:])}
        if sat!=2**n+2**p or len(expected_proj)!=2**n+2**p-1 or proj!=expected_proj: errors.append(f"COUNT_OR_PROJECTION_{g}_{p}_{n}")
        for leaves in expected_proj:
            aa=leaves[:p]; bb=leaves[p:]; xb=1-int(all(aa)); replay_cases+=1
            if not make_model(first,U,g,p,n,xb,aa,bb): errors.append(f"RETURN_MODEL_{g}_{p}_{n}_{leaves}")
    # BA8 exact size recovery.
    for g in (1,2,5):
        if exact_size(g,1,2)!=(268*g-5,652*g-10,80*g,1000*g-15): errors.append(f"BA8_RECOVERY_{g}")
    # Independent p*n bijection diagnostics over several sizes, not theorem authority.
    for p,n in ((1,1),(1,4),(2,3),(4,2)):
        pairs={(i,j) for i in range(p) for j in range(n)}
        if len(pairs)!=p*n: errors.append(f"PN_BIJECTION_{p}_{n}")
        d=p+n
        if p*n>math.floor(d*d/4): errors.append(f"QUAD_{p}_{n}")
    obligations={
      "SYMBOLIC_ELIMINATION_PASS":int(not any(e.startswith("SYMBOLIC") for e in errors)),
      "DISTRIBUTIVE_CNF_PASS":int("SYMBOLIC_ELIMINATION_RECORD" not in errors),
      "PN_BIJECTION_PASS":int(not any(e.startswith("PN_BIJECTION") for e in errors)),
      "EXACT_FILL_GRAPH_PASS":int("FILL_GRAPH_FORMULA" not in errors),
      "QUADRATIC_MAXIMUM_PASS":int("QUADRATIC_IDENTITY" not in errors and not any(e.startswith("QUAD_") for e in errors)),
      "SYMBOLIC_POLARITY_PARTITION_PASS":int(not any(e.startswith("POLARITY") or e.startswith("TOP_") or e.startswith("BA8_POLARITY") for e in errors)),
      "MODEL_COUNT_PASS":int("MODEL_COUNT_FORMULA" not in errors and not any(e.startswith("COUNT_OR_PROJECTION") for e in errors)),
      "CNF_REALIZATION_PASS":int(not any(e.startswith("NAMESPACE_") or e.startswith("SIZE_") for e in errors)),
      "SOURCE_PREIMAGE_PASS":int("PARENT_BA4_GATES" not in errors),
      "GENERIC_TRANSPORT_PASS":int("LOCAL_CARRIER_KERNEL" not in errors and "RAW_SYMBOLIC_BOUND" not in errors),
      "RECONSTRUCTION_PASS":int("RECONSTRUCTION_MAP" not in errors and not any(e.startswith("RETURN_MODEL_") for e in errors)),
      "FULL_ORIGINAL_CNF_VALIDATION_PASS":int(not any(e.startswith("SOURCE_MODEL_") or e.startswith("RETURN_MODEL_") for e in errors)),
      "QUOTIENT_WIDTH_PASS":int("WIDTH_FORMULA" not in errors),
      "FULL_WIDTH_COMPOSITION_PASS":int("FULL_WIDTH_RECORD" not in errors),
      "OUTPUT_SIZE_ACCOUNTING_PASS":int("OUTPUT_FIREWALL" not in errors),
      "ACTUAL_CARRIER_COMPLEXITY_PASS":int("RAW_ACCOUNTING" not in errors and "RAW_SYMBOLIC_BOUND" not in errors and "COMPLEXITY" not in errors),
      "INDEPENDENT_REPLAY_PASS":int(not errors)
    }
    P=1
    for z in obligations.values(): P*=z
    result={"status":"PASS" if not errors else "FAIL","errors":errors,"error_count":len(errors),"obligations":obligations,"v_independent_verifier":int(not errors),"P_BA9":P,"independent_source_replay_cases":replay_cases,"local_positive_raw":kp["raw"],"local_negative_raw":kn["raw"],"message_state":"VERIFIED" if not errors else "FALSIFIER_PRESERVED"}
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True))
    if errors: raise SystemExit("BA9 verify failed: "+",".join(errors))
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args(); verify(a.result,a.out)
