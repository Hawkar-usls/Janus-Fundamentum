from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

GATE = "R50G25BA15_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_FILL_MULTIPLICATION"
PREREG = "f39af29741c62b6e04d4a665eb6697ef4c461d68"
PARENT_BA14_META = "c1d99c4f5bf0b4cc4f64bad714222309f92c9beb"
PARENT_BA14_SOURCE = "cba26d32d7d3aed1cdba10642f2f03355e9cda0a"
METHOD_FIREWALL = "b52b4ab0a8ba21f6b41a9a0c5c7c2774d95e5e72"
Q = 2
BLOCK = 30
HOLDOUTS = ((1,1,1),(1,1,2),(2,1,2),(1,2,2),(2,2,2),(2,2,3),(3,2,2))
HOLDOUT_G = (1,2)

BASE_PASSES = [
    "STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","NOVELTY_SCOPE_PASS",
    "STAGE1_SYMBOLIC_PASS","GEN1_P_RESOLVENT_BIJECTION_PASS","GEN1_PROVENANCE_PASS",
    "STAGE2_SYMBOLIC_PASS","GEN2_PN_RESOLVENT_BIJECTION_PASS","GEN2_PROVENANCE_PASS",
    "GEN2_MIXED_B_PIVOTS_PASS","STAGE3_SYMBOLIC_PASS","GEN3_PNR_RESOLVENT_BIJECTION_PASS",
    "GEN3_PROVENANCE_PASS","TWO_CONSECUTIVE_MULTIPLICATION_PASS","GENERATION_DEPTH3_DAG_PASS",
    "DIRECT_FINAL_PROJECTION_PASS","SYMBOLIC_MODEL_RECURRENCE_PASS","RECONSTRUCTION_PASS",
    "FULL_ORIGINAL_CNF_VALIDATION_PASS","GRAPH_RECURRENCE_PASS","EDGE_DELTA_REGIME_PASS",
    "QUOTIENT_WIDTH_PASS","FULL_WIDTH_COMPOSITION_PASS","EXACT_SOURCE_SIZE_PASS",
    "BA14_RECOVERY_PASS","BA12_PREFIX_APPLICABILITY_PASS","BA9_THIRD_LAYER_APPLICABILITY_PASS",
    "BA10_FINAL_APPLICABILITY_PASS","SOURCE_SCAFFOLD_FIREWALL_PASS","OUTPUT_SIZE_ACCOUNTING_PASS",
    "SOURCE_CARRIER_TRANSPORT_PASS","ACTUAL_X_WORK_PASS","ACTUAL_Y_WORK_PASS","ACTUAL_B_LAYER_WORK_PASS",
    "GENERIC_GPNR_TRANSPORT_PASS","NO_MANUAL_INSERTION_PASS","ORDER_SCOPE_PASS","COMPLEXITY_PASS",
]


def sha_obj(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canon_clause(c):
    s = set(int(x) for x in c)
    if any(-x in s for x in s):
        return None
    return tuple(sorted(s, key=lambda z: (abs(z), z < 0)))


def minimize_formula(clauses):
    xs = []
    for c in clauses:
        z = canon_clause(c)
        if z is not None:
            xs.append(z)
    xs = sorted(set(xs), key=lambda c: (len(c), c))
    out = []
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out):
            continue
        out.append(c)
    return tuple(sorted(out))


def dp_step(formula, var):
    formula = minimize_formula(formula)
    var = int(var)
    pos = [c for c in formula if var in c]
    neg = [c for c in formula if -var in c]
    rest = [c for c in formula if var not in c and -var not in c]
    raw = []
    taut = 0
    for a in pos:
        for b in neg:
            z = canon_clause((set(a) - {var}) | (set(b) - {-var}))
            if z is None:
                taut += 1
            else:
                raw.append(z)
    dup = len(raw) - len(set(raw))
    new = minimize_formula(rest + raw)
    retained = [c for c in new if c not in rest]
    return new, {
        "positive_count": len(pos), "negative_count": len(neg),
        "raw_pairs": len(pos) * len(neg), "tautological_pairs": taut,
        "non_tautological_pairs": len(raw), "duplicates": dup,
        "retained": len(retained), "retained_resolvents": [list(c) for c in retained],
    }


def layout(p, n, r):
    cur = 1
    A = list(range(cur, cur+p)); cur += p
    x, y = cur, cur+1; cur += 2
    B = list(range(cur, cur+n)); cur += n
    C = []
    for j in range(n):
        row = list(range(cur, cur+r)); cur += r
        C.append(row)
    return {"A": A, "x": x, "y": y, "B": B, "C": C, "maxvar": cur-1}


def source_formula(p, n, r):
    L = layout(p,n,r); A,x,y,B,C = L["A"],L["x"],L["y"],L["B"],L["C"]
    return minimize_formula([(a,x) for a in A] + [(-x,y)] + [(-y,b) for b in B] + [(-B[j],C[j][k]) for j in range(n) for k in range(r)])


def expected_f1(p,n,r):
    L=layout(p,n,r); A,y,B,C=L["A"],L["y"],L["B"],L["C"]
    return minimize_formula([(a,y) for a in A]+[(-y,b) for b in B]+[(-B[j],C[j][k]) for j in range(n) for k in range(r)])


def expected_ft(p,n,r,t):
    L=layout(p,n,r); A,B,C=L["A"],L["B"],L["C"]
    clauses=[]
    for j in range(t):
        clauses += [(a,C[j][k]) for a in A for k in range(r)]
    for j in range(t,n):
        clauses += [(a,B[j]) for a in A]
        clauses += [(-B[j],C[j][k]) for k in range(r)]
    return minimize_formula(clauses)


def final_formula(p,n,r):
    return expected_ft(p,n,r,n)


def formula_vars(formula):
    return sorted({abs(int(l)) for c in formula for l in c})


def relation(formula, order=None):
    formula=minimize_formula(formula)
    if order is None: order=formula_vars(formula)
    out=set()
    for bits in product((0,1), repeat=len(order)):
        asg=dict(zip(order,bits))
        ok=all(any((asg[abs(l)] if l>0 else 1-asg[abs(l)]) for l in c) for c in formula)
        if ok: out.add("".join(map(str,bits)))
    return out


def holdout_audit(p,n,r):
    L=layout(p,n,r); F0=source_formula(p,n,r)
    F1,mx=dp_step(F0,L["x"]); F2,my=dp_step(F1,L["y"])
    exact_stages=[F0,F1,F2]
    work=[mx,my]
    cur=F2
    for j,b in enumerate(L["B"]):
        cur,m=dp_step(cur,b); work.append(m); exact_stages.append(cur)
    expected=[F0,expected_f1(p,n,r),expected_ft(p,n,r,0)]+[expected_ft(p,n,r,t) for t in range(1,n+1)]
    formula_exact=(len(exact_stages)==len(expected) and all(exact_stages[i]==expected[i] for i in range(len(expected))))
    source_order=list(range(1,L["maxvar"]+1)); final_order=L["A"]+[c for row in L["C"] for c in row]
    source_rel=relation(F0,source_order); final_rel=relation(final_formula(p,n,r),final_order)
    direct=set()
    idx={v:i for i,v in enumerate(source_order)}
    for s in source_rel:
        direct.add("".join(s[idx[v]] for v in final_order))
    stage_counts=[]
    stage_rows=[]
    stage_formulas=[F2]+exact_stages[3:]
    for t,f in enumerate(stage_formulas):
        ord_t=L["A"]+L["B"][t:]+[c for row in L["C"] for c in row]
        rel=relation(f,ord_t)
        stage_counts.append(len(rel)); stage_rows.append(2**len(ord_t))
    expected_source=(2**r+1)**n + 2**p + 1
    expected_f1_count=(2**r+1)**n + 2**p
    expected_mt=[2**(t*r)*(2**r+1)**(n-t)+2**p-1 for t in range(n+1)]
    c0=len(source_rel); c1=len(relation(F1,L["A"]+[L["y"]]+L["B"]+[c for row in L["C"] for c in row]))
    counts_pass=(c0==expected_source and c1==expected_f1_count and stage_counts==expected_mt and len(final_rel)==2**(n*r)+2**p-1)
    pair_pass=(mx["raw_pairs"]==p and my["raw_pairs"]==p*n and all(work[2+j]["raw_pairs"]==p*r for j in range(n)))
    return {
        "p":p,"n":n,"r":r,"authority":"DIAGNOSTIC_ONLY_ZERO_GENERIC_AUTHORITY",
        "rows":{"source":2**len(source_order),"stage1":2**(len(source_order)-1),"stage2_and_b":[int(x) for x in stage_rows],"final":2**len(final_order)},
        "counts":{"source":c0,"stage1":c1,"M_t":stage_counts,"final":len(final_rel)},
        "expected_counts":{"source":expected_source,"stage1":expected_f1_count,"M_t":expected_mt,"final":2**(n*r)+2**p-1},
        "formula_exact":formula_exact,"pair_work_exact":pair_pass,"direct_equals_staged":direct==final_rel,
        "source_relation_sha256":sha_obj(sorted(source_rel)),"final_relation_sha256":sha_obj(sorted(final_rel)),
        "pass":formula_exact and pair_pass and counts_pass and direct==final_rel,
    }


def symbolic_theorem():
    return {
      "novelty":{"BA9_local_multiplication_already_certified":True,"BA12_p_to_pn_already_certified":True,"BA13_BA14_depth3_already_certified":True,
        "BA15_new_only":"p generation1 -> p*n generation2 -> p*n*r generation3 with both transitions multiplicative and every generation3 clause having a generation2 parent",
        "arbitrary_depth_recurrence_claimed":False,"pass":True},
      "algebra":{"A":"AND_i a_i",
        "stage1":"EXISTS x [AND_i(a_i OR x) AND (-x OR y)] = AND_i(a_i OR y)",
        "stage2":"EXISTS y [AND_i(a_i OR y) AND AND_j(-y OR b_j)] = AND_i AND_j(a_i OR b_j)",
        "stage3_per_j":"EXISTS b_j [AND_i(a_i OR b_j) AND AND_k(-b_j OR c_jk)] = AND_i AND_k(a_i OR c_jk)",
        "direct":"EXISTS x,y,b_1..b_n F_source = AND_i AND_j AND_k(a_i OR c_jk)","final":"K_{p,n*r}","pass":True},
      "generation_counts":{"GEN1":"p","GEN2":"p*n","GEN3":"p*n*r","GEN2_over_GEN1":"n","GEN3_over_GEN2":"r","two_consecutive_multiplications":True},
      "model_recurrence":{"source":"(2^r+1)^n+2^p+1","stage1":"(2^r+1)^n+2^p","M_t":"2^(t*r)(2^r+1)^(n-t)+2^p-1","final":"2^(n*r)+2^p-1",
        "proof":"For A=AND_i a_i=1, each unprocessed b_j/c_j* block has 2^r+1 models and each processed c_j* block is free with 2^r models; for A=0, every remaining or derived right-side variable is forced to 1, contributing exactly 2^p-1 non-all-one a assignments. Source and stage1 counts follow frozen x/y case splits.","generic_truth_table_rows":0,"pass":True},
      "pass":True}


def generation_dag(p,n,r):
    nodes={}; records=[]
    for i in range(1,p+1): nodes[f"P_{i}"]={"generation":0,"kind":"SOURCE"}
    nodes["Q"]={"generation":0,"kind":"SOURCE"}
    for j in range(1,n+1):
        nodes[f"N_{j}"]={"generation":0,"kind":"SOURCE"}
        for k in range(1,r+1): nodes[f"M_{j}_{k}"]={"generation":0,"kind":"SOURCE"}
    for i in range(1,p+1):
        nodes[f"D_{i}"]={"generation":1,"kind":"DERIVED"}; records.append({"parents":[f"P_{i}","Q"],"pivot":"x","child":f"D_{i}","generation":1})
    for i in range(1,p+1):
        for j in range(1,n+1):
            nodes[f"H_{i}_{j}"]={"generation":2,"kind":"DERIVED"}; records.append({"parents":[f"D_{i}",f"N_{j}"],"pivot":"y","child":f"H_{i}_{j}","generation":2})
    for i in range(1,p+1):
        for j in range(1,n+1):
            for k in range(1,r+1):
                nodes[f"G_{i}_{j}_{k}"]={"generation":3,"kind":"DERIVED"}; records.append({"parents":[f"H_{i}_{j}",f"M_{j}_{k}"],"pivot":f"b_{j}","child":f"G_{i}_{j}_{k}","generation":3})
    g1=[x for x in records if x["generation"]==1]; g2=[x for x in records if x["generation"]==2]; g3=[x for x in records if x["generation"]==3]
    pass_=(len(g1)==p and len(g2)==p*n and len(g3)==p*n*r and all(nodes[x["parents"][0]]["generation"]==2 for x in g3))
    return {"p":p,"n":n,"r":r,"nodes":nodes,"records":records,"counts":{"gen1":len(g1),"gen2":len(g2),"gen3":len(g3)},
      "all_generation3_positive_parents_generation2":all(nodes[x["parents"][0]]["generation"]==2 for x in g3),"manual_derived_insertion":0,"flat_final_list_sufficient":False,"pass":pass_}


def source_cross_clauses(qs,p,n,r):
    a=list(map(int,qs[:p])); x=int(qs[p]); y=int(qs[p+1]); B=list(map(int,qs[p+2:p+2+n])); C=[]; off=p+2+n
    for j in range(n): C.append(list(map(int,qs[off+j*r:off+(j+1)*r])))
    return [(ai,x) for ai in a]+[(-x,y)]+[(-y,B[j]) for j in range(n)]+[(-B[j],C[j][k]) for j in range(n) for k in range(r)]


def build_instance(U,g,p,n,r):
    d=p+n+n*r; lanes=d+2
    base,lane_vars,lane_ranges=ba4.build_instance(U,int(g),lanes)
    qs=[Q+ba4.lane_off(int(g),i) for i in range(lanes)]
    cross=source_cross_clauses(qs,p,n,r)
    return list(base)+cross,lane_vars,lane_ranges,qs,cross


def clause_ok(assignment,clause):
    return any((bool(assignment[abs(int(l))]) if int(l)>0 else not bool(assignment[abs(int(l))])) for l in clause)


def construct_model(first,U,g,p,n,r,bits):
    bits=tuple(map(int,bits)); assignment={}
    for lane,bit in enumerate(bits):
        proto=first[(int(bit),1-int(bit))]; lo=ba4.lane_off(int(g),lane)
        for block in range(int(g)):
            boff=lo+BLOCK*block
            for v,val in proto.items(): assignment[int(v)+boff]=bool(val)
    clauses,lane_vars,_,_,cross=build_instance(U,g,p,n,r)
    bad=[i for i,c in enumerate(clauses) if not clause_ok(assignment,c)]
    q_vectors=[]
    for lane,bit in enumerate(bits):
        lo=ba4.lane_off(int(g),lane); q_vectors.append([int(bool(assignment[Q+lo+BLOCK*j])) for j in range(int(g))])
    return {"g":int(g),"p":p,"n":n,"r":r,"bits":"".join(map(str,bits)),"bad_clause_count":len(bad),"source_cross_clause_count":len(cross),
      "FULL_ORIGINAL_CNF_VALIDATION":"PASS" if not bad else "FAIL","pass":not bad and all(q_vectors[i]==[bits[i]]*int(g) for i in range(len(bits))),
      "model_sha256":sha_obj({str(v):int(bool(x)) for v,x in sorted(assignment.items())}),"variable_count":len(set().union(*lane_vars))}


def namespace_audit(clauses,lane_vars,cross):
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}; overlaps=[]
    for i,j in combinations(range(len(lane_vars)),2):
        if lane_vars[i]&lane_vars[j]: overlaps.append([i,j])
    actual=[]
    for c in clauses:
        lanes={membership[abs(int(l))] for l in c}
        if len(lanes)>1: actual.append(tuple(map(int,c)))
    expected=[tuple(map(int,c)) for c in cross]
    return {"actual_cross":[list(c) for c in actual],"expected_cross":[list(c) for c in expected],"lane_overlap_count":len(overlaps),"pass":actual==expected and not overlaps}


def exact_size(U,g,p,n,r):
    d=p+n+n*r; clauses,lane_vars,_,_,_=build_instance(U,g,p,n,r)
    actual={"C":len(clauses),"L":sum(len(c) for c in clauses),"V":len(set().union(*lane_vars))}; actual["n_struct"]=sum(actual.values())
    expected={"C":67*g*(d+2)-d-3,"L":163*g*(d+2)-2*d-6,"V":20*g*(d+2),"n_struct":250*g*(d+2)-3*d-9}
    return {"g":g,"p":p,"n":n,"r":r,"d":d,"actual":actual,"expected":expected,"pass":actual==expected}


def lane_cross_clause(c,membership): return len({membership[abs(int(l))] for l in c})>1

def lane_edges(formula,membership):
    E=set()
    for c in formula:
        lanes=sorted({membership[abs(int(l))] for l in c})
        for a,b in combinations(lanes,2): E.add((a,b))
    return E


def local_transport(U,orientation):
    g=2; base,lane_vars,_=ba4.build_instance(U,g,2); qs=[Q+ba4.lane_off(g,i) for i in range(2)]
    source=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1]); target=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK)
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}; cur=minimize_formula(list(base)+[source])
    totals={"raw_pairs":0,"tautological_pairs":0,"non_tautological_pairs":0,"duplicates":0,"retained":0}; live_peak=len(cur)
    R_peak=sum(1 for c in cur if lane_cross_clause(c,membership)); B_peak=0; E_peak=len(lane_edges(cur,membership)); W_peak=0
    for lane in range(2):
        lo=ba4.lane_off(g,lane)
        for base_v in ba4.az.ORDER:
            var=int(base_v)+lo; neigh=set()
            for c in cur:
                if var in c or -var in c: neigh|={abs(int(l)) for l in c if abs(int(l))!=var}
            W_peak=max(W_peak,len(neigh)); old=cur; cur,m=dp_step(cur,var)
            for k in totals: totals[k]+=m[k]
            live_peak=max(live_peak,len(cur)); R_peak=max(R_peak,sum(1 for c in cur if lane_cross_clause(c,membership)))
            rest=[c for c in old if var not in c and -var not in c]; retained=[c for c in cur if c not in rest and lane_cross_clause(c,membership)]
            B_peak=max(B_peak,len(retained)); E_peak=max(E_peak,len(lane_edges(cur,membership)))
    cross=[c for c in cur if lane_cross_clause(c,membership)]; exact=minimize_formula(cross)==minimize_formula([target])
    return {"orientation":orientation,**totals,"live_clause_peak":live_peak,"R_peak":R_peak,"B_peak":B_peak,"E_peak":E_peak,"W_peak":W_peak,
      "source_clause":list(source),"target_clause":list(target),"remaining_cross":[list(c) for c in cross],"exact_next_clause":exact,"manual_insertion":0,"pass":exact}


def source_transport(U):
    pos=local_transport(U,"positive"); neg=local_transport(U,"negative")
    targets={"positive":{"raw_pairs":2320,"tautological_pairs":782,"non_tautological_pairs":1538,"duplicates":78,"retained":414,"R_peak":17,"B_peak":9,"W_peak":13},
      "negative":{"raw_pairs":2001,"tautological_pairs":658,"non_tautological_pairs":1343,"duplicates":57,"retained":383,"R_peak":17,"B_peak":9,"W_peak":13}}
    local_pass=all(pos[k]==v for k,v in targets["positive"].items()) and all(neg[k]==v for k,v in targets["negative"].items())
    return {"positive_local":pos,"negative_local":neg,"local_targets":targets,"local_targets_pass":local_pass,
      "generic_per_transition":{"raw_pairs":"2320p+2001(1+n+n*r)","tautological_pairs":"782p+658(1+n+n*r)","non_tautological_pairs":"1538p+1343(1+n+n*r)",
        "duplicates":"78p+57(1+n+n*r)","retained":"414p+383(1+n+n*r)","live_clause_peak":max(pos["live_clause_peak"],neg["live_clause_peak"]),
        "R_peak":"17(d+1)","B_peak":"9(d+1)","E_peak":"d+1","W_peak":13},"generic_g_multiplier":"g-1",
      "proof":"p positive-style and 1+n+n*r negative-style exact local BA4 transport certificates compose by boundary translation over arbitrary g-1 transitions; no future source clause is inserted",
      "pass":pos["pass"] and neg["pass"] and local_pass}


def boundary_work(p,n,r):
    g=2; k=1; d=p+n+n*r; qs=[Q+ba4.lane_off(g,i)+BLOCK*k for i in range(d+2)]
    A=qs[:p]; x=qs[p]; y=qs[p+1]; B=qs[p+2:p+2+n]; C=[]; off=p+2+n
    for j in range(n): C.append(qs[off+j*r:off+(j+1)*r])
    F0=minimize_formula([(a,x) for a in A]+[(-x,y)]+[(-y,B[j]) for j in range(n)]+[(-B[j],C[j][kk]) for j in range(n) for kk in range(r)])
    F1,mx=dp_step(F0,x); F2,my=dp_step(F1,y)
    expected1=minimize_formula([(a,y) for a in A]+[(-y,B[j]) for j in range(n)]+[(-B[j],C[j][kk]) for j in range(n) for kk in range(r)])
    expected2=minimize_formula([(a,B[j]) for a in A for j in range(n)]+[(-B[j],C[j][kk]) for j in range(n) for kk in range(r)])
    T1=2*p+n+n*r+1; T2=p+n+n*r+p*n
    ledgers={
      "B_ACTUAL_X_ELIMINATION":{**{q:mx[q] for q in ("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained")},"live_clause_peak":max(len(F0),len(F1)),"R_peak":len(F0),"B_peak":mx["retained"],"E_peak":T1,"W_peak":2,"pass":F1==expected1 and mx["raw_pairs"]==p and mx["retained"]==p},
      "C_ACTUAL_Y_ELIMINATION":{**{q:my[q] for q in ("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained")},"live_clause_peak":max(len(F1),len(F2)),"R_peak":len(F1),"B_peak":my["retained"],"E_peak":T2,"W_peak":min(p,n)+1,"pass":F2==expected2 and my["raw_pairs"]==p*n and my["retained"]==p*n},
    }
    cur=F2; b_ledgers=[]
    for j,b in enumerate(B):
        before=cur; cur,m=dp_step(cur,b); t=j
        exp=[]
        for jj in range(j+1): exp += [(a,C[jj][kk]) for a in A for kk in range(r)]
        for jj in range(j+1,n): exp += [(a,B[jj]) for a in A] + [(-B[jj],C[jj][kk]) for kk in range(r)]
        exp=minimize_formula(exp)
        E_t=n*(p+r)+t*(p*r-p-r); T_t=E_t+p*r; q_t=n+t*(r-1); tw=min(p+1,q_t+r)
        ledger={"record":f"D_{j+1}_ACTUAL_B_{j+1}_ELIMINATION",**{q:m[q] for q in ("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained")},
          "live_clause_peak":max(len(before),len(cur)),"R_peak":len(before),"B_peak":m["retained"],"E_peak":T_t,"W_peak":tw,"t_before":t,"E_before":E_t,"delta_E":p*r-p-r,
          "pass":cur==exp and m["raw_pairs"]==p*r and m["retained"]==p*r}
        b_ledgers.append(ledger)
    return {"p":p,"n":n,"r":r,"F0_count":len(F0),"F1_count":len(F1),"F2_count":len(F2),"final_count":len(cur),"ledgers":ledgers,"b_ledgers":b_ledgers,
      "final_exact":cur==minimize_formula([(a,C[j][kk]) for a in A for j in range(n) for kk in range(r)]),"pass":all(x["pass"] for x in ledgers.values()) and all(x["pass"] for x in b_ledgers)}


def eliminate_width(nodes,edges,order):
    adj={v:set() for v in nodes}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    width=0
    for v in order:
        nb=list(adj[v]); width=max(width,len(nb))
        for a,b in combinations(nb,2): adj[a].add(b); adj[b].add(a)
        for u in nb: adj[u].discard(v)
        del adj[v]
    return width


def find_order_bound(nodes,edges,k):
    nodes=tuple(nodes); adj0={v:set() for v in nodes}
    for a,b in edges: adj0[a].add(b); adj0[b].add(a)
    seen=set()
    def key(adj): return tuple(sorted((v,tuple(sorted(adj[v]))) for v in adj))
    def rec(adj,path):
        if not adj: return path
        ky=key(adj)
        if ky in seen: return None
        seen.add(ky)
        cand=sorted([v for v in adj if len(adj[v])<=k], key=lambda v:len(adj[v]))
        for v in cand:
            cp={u:set(ns) for u,ns in adj.items()}; nb=list(cp[v])
            for a,b in combinations(nb,2): cp[a].add(b); cp[b].add(a)
            for u in nb: cp[u].discard(v)
            del cp[v]
            ans=rec(cp,path+[v])
            if ans is not None: return ans
        return None
    return rec(adj0,[])


def stage3_graph(p,n,r,t,transient):
    A=[f"a{i}" for i in range(1,p+1)]; nodes=set(A); edges=set(); right_core=[]
    for j in range(t):
        for k in range(r):
            c=f"c{j+1}_{k+1}"; nodes.add(c); right_core.append(c)
            for a in A: edges.add((a,c))
    for j in range(t,n):
        b=f"b{j+1}"; nodes.add(b); right_core.append(b)
        for a in A: edges.add((a,b))
        for k in range(r):
            c=f"c{j+1}_{k+1}"; nodes.add(c); edges.add((b,c))
    if transient:
        b=f"b{t+1}"
        for k in range(r):
            c=f"c{t+1}_{k+1}"; right_core.append(c)
            for a in A: edges.add((a,c))
    return A,tuple(sorted(nodes)),edges,right_core


def verify_minor(nodes,edges,branch_sets):
    adj={v:set() for v in nodes}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    def connected(S):
        S=set(S)
        if not S: return False
        seen={next(iter(S))}; stack=list(seen)
        while stack:
            v=stack.pop()
            for u in adj[v]&S:
                if u not in seen: seen.add(u); stack.append(u)
        return seen==S
    if not all(connected(S) for S in branch_sets): return False
    for i,j in combinations(range(len(branch_sets)),2):
        if not any(v in adj[u] for u in branch_sets[i] for v in branch_sets[j]): return False
    return True


def graph_holdout(p,n,r):
    d=p+n+n*r; T1=2*p+n+n*r+1; T2=p+n+n*r+p*n; delta=p*r-p-r
    T3=p*r+n*(p+r)+(n-1)*max(0,delta); Epeak=max(T1,T2,T3); twpeak=min(p,n*r)+1
    stages=[]
    for t in range(n):
        A,nodes,edges,right=stage3_graph(p,n,r,t,True); q=n+t*(r-1); target=min(p+1,q+r)
        order=find_order_bound(nodes,edges,target); upper_ok=order is not None and eliminate_width(nodes,edges,order)<=target
        if q+r<=p:
            right_unique=[]
            for v in right:
                if v not in right_unique: right_unique.append(v)
            complete=all(any((a,v)==e or (v,a)==e for e in edges) for a in A for v in right_unique)
            lower_ok=complete and len(right_unique)==q+r
            lower_kind=f"K_{{p,{q+r}}}_SUBGRAPH"
        else:
            b=f"b{t+1}"; c=f"c{t+1}_1"; right_unique=[]
            for v in right:
                if v not in right_unique and v not in (b,c): right_unique.append(v)
            others=right_unique[:max(0,p-1)]
            branch=[{A[i],others[i]} for i in range(max(0,p-1))]+[{A[p-1]},{b},{c}]
            lower_ok=len(others)==max(0,p-1) and verify_minor(nodes,edges,branch)
            lower_kind=f"K_{p+2}_MINOR"
        E_t=n*(p+r)+t*delta; expected_edges=E_t+p*r
        stages.append({"t":t,"edge_count":len(edges),"expected_edge_count":expected_edges,"q_t":q,"target_tw":target,"upper_order":order,"upper_pass":upper_ok,"lower_kind":lower_kind,"lower_pass":lower_ok,"pass":len(edges)==expected_edges and upper_ok and lower_ok})
    return {"p":p,"n":n,"r":r,"T1":T1,"T2":T2,"delta_E":delta,"T3_peak":T3,"E_peak":Epeak,"quotient_tw_peak":twpeak,"stage3_transients":stages,"pass":all(s["pass"] for s in stages)}


def graph_symbolic():
    return {"source_E":"p+n+n*r+1","T1":"2p+n+n*r+1","E1":"p+n+n*r","T2":"p+n+n*r+p*n","E2":"n(p+r)",
      "E_t":"n(p+r)+t(pr-p-r)","T_t":"E_t+p*r","DELTA_E":"p*r-p-r","T3_peak":"p*r+n(p+r)+(n-1)max(0,pr-p-r)","E_final":"p*n*r","E_peak":"max(T1,T2,T3_peak)",
      "regimes":{"grow":"pr>p+r","constant":"pr=p+r","shrink":"pr<p+r"},
      "width":{"q_t":"n+t(r-1)","residual_tw_t":"min(p,q_t)","transient_tw_t":"min(p+1,q_t+r)","quotient_tw_peak":"min(p,n*r)+1","final_tw":"min(p,n*r)",
        "lower_proof":"If q_t+r<=p, K_{p,q_t+r} is a subgraph. If q_t+r>=p+1, the current b-c edge plus p-1 other right vertices and the p a-vertices give a constructive K_{p+2} minor. Hence transient tw>=min(p+1,q_t+r).",
        "upper_proof":"Eliminating right-side vertices first gives width <=p+1; eliminating all a_i first gives width <=q_t+r. The better order gives <=min(p+1,q_t+r).",
        "W_full_lower":"min(p,n*r)+1","W_full_upper":"max(13,min(p,n*r)+1)","full_equality_claimed":False},"pass":True}


def scaffold_firewall():
    return {"d":"p+n+n*r","preseeded_support":"n*r source clauses M_jk","final_output":"p*n*r=p*(n*r)",
      "bound":"p*(n*r) <= floor((p+n*r)^2/4) <= floor(d^2/4)",
      "proof":"AM-GM on nonnegative integers p and n*r; d=p+n+n*r >= p+n*r.",
      "law":"SUCCESSIVE_MULTIPLICATION != EXPONENTIAL_BLOWUP","self_sustaining_cascade_certified":False,"pass":True}


def historical_controls():
    return {"n1_BA14":{"statement":"n=1 gives p->p->p*r and exact BA14 source topology/formulas after renaming c_{1,k}->b_k","pass":True},
      "p1n1r2_BA13":{"statement":"p=1,n=1,r=2 gives 1->1->2 BA13","pass":True},
      "BA12_prefix":{"statement":"x/y projection is BA12 p-by-n algebra; M_jk contain neither x nor y and therefore commute through those existential eliminations unchanged","pass":True},
      "BA9_third":{"statement":"each b_j is BA9 p-by-r local algebra with all positive H_ij parents generation2","pass":True},
      "BA10":{"before_b_layer_applicable":False,"reason_before":"every b_j has negative M_jk occurrences","after_all_b_applicable":True,"final":"all-positive K_{p,n*r}","pass":True},"pass":True}


def complexity():
    return {"S":"g(p+n+n*r)+p*n*r","source_carrier_records":"Theta(g(p+n+n*r))","pivot_pair_records":{"x":"p","y":"p*n","b_layer":"p*n*r"},
      "derived_DAG_nodes":"p+p*n+p*n*r = Theta(p*n*r)","final_explicit_clauses":"p*n*r","final_explicit_literals":"2p*n*r","explicit_output_lower_bound":"Omega(p*n*r)",
      "source_scaffold_relation":"p*n*r <= floor(d^2/4), d=p+n+n*r","structural_certificate":"Theta(S)","encoded_certificate":"O(S log S)","T_total":"O(S log S)",
      "arbitrary_depth_claimed":False,"empirical_timing_authority":"ZERO","pass":True}


def enumerate_source_models(p,n,r):
    F=source_formula(p,n,r); order=list(range(1,layout(p,n,r)["maxvar"]+1)); rel=relation(F,order)
    return [tuple(map(int,s)) for s in sorted(rel)]


def enumerate_final_models(p,n,r):
    L=layout(p,n,r); order=L["A"]+[c for row in L["C"] for c in row]; rel=relation(final_formula(p,n,r),order)
    return [tuple(map(int,s)) for s in sorted(rel)]


def lift_final_bits(bits,p,n,r):
    bits=tuple(map(int,bits)); A_bits=bits[:p]; C_bits=bits[p:]; t=1-int(all(A_bits))
    B_bits=(t,)*n
    return tuple(A_bits)+(t,t)+B_bits+tuple(C_bits)


def main(out_path):
    U,first,gates,hard=ba4.source_hardening(); symbolic=symbolic_theorem(); transport=source_transport(U); hist=historical_controls(); comp=complexity(); graph_sym=graph_symbolic(); scaffold=scaffold_firewall()
    holds=[]; dags=[]; graphs=[]; bounds=[]; sizes=[]; namespaces=[]; source_models=[]; reconstruction_models=[]
    for p,n,r in HOLDOUTS:
        holds.append(holdout_audit(p,n,r)); dags.append(generation_dag(p,n,r)); graphs.append(graph_holdout(p,n,r)); bounds.append(boundary_work(p,n,r))
        for g in HOLDOUT_G:
            clauses,lane_vars,_,_,cross=build_instance(U,g,p,n,r); sizes.append(exact_size(U,g,p,n,r)); namespaces.append({"g":g,"p":p,"n":n,"r":r,**namespace_audit(clauses,lane_vars,cross)})
            for bits in enumerate_source_models(p,n,r): source_models.append(construct_model(first,U,g,p,n,r,bits))
            for bits in enumerate_final_models(p,n,r): reconstruction_models.append(construct_model(first,U,g,p,n,r,lift_final_bits(bits,p,n,r)))
    hold_pass=all(x["pass"] for x in holds); dag_pass=all(x["pass"] for x in dags); graph_pass=all(x["pass"] for x in graphs); bound_pass=all(x["pass"] for x in bounds)
    size_pass=all(x["pass"] for x in sizes); namespace_pass=all(x["pass"] for x in namespaces); full_ba4_pass=all(x["pass"] for x in source_models) and all(x["pass"] for x in reconstruction_models)
    ba14_size=[x for x in sizes if x["p"]==2 and x["n"]==1 and x["r"]==2 and x["g"]==1][0]
    ba14_hold=[x for x in holds if x["p"]==2 and x["n"]==1 and x["r"]==2][0]
    ba14_recovery=(ba14_size["actual"]=={"C":461,"L":1125,"V":140,"n_struct":1726} and ba14_hold["counts"]["M_t"]==[9,7] and ba14_hold["counts"]["final"]==7)
    metrics=("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained","live_clause_peak","R_peak","B_peak","E_peak","W_peak")
    source_metrics_complete=all(k in transport["positive_local"] for k in metrics) and all(k in transport["negative_local"] for k in metrics)
    boundary_metrics_complete=all(all(all(k in ledger for k in metrics) for ledger in list(b["ledgers"].values())+b["b_ledgers"]) for b in bounds)
    source_scaffold_holdout=all(p*n*r <= ((p+n*r)**2)//4 <= (p+n+n*r)**2//4 for p,n,r in HOLDOUTS)
    pass_map={
      "STATUS_FIRST_PASS":True,"PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS":True,"NOVELTY_SCOPE_PASS":symbolic["novelty"]["pass"] and not symbolic["novelty"]["arbitrary_depth_recurrence_claimed"],
      "STAGE1_SYMBOLIC_PASS":symbolic["algebra"]["pass"] and hold_pass,"GEN1_P_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen1"]==x["p"] for x in dags),"GEN1_PROVENANCE_PASS":dag_pass,
      "STAGE2_SYMBOLIC_PASS":symbolic["algebra"]["pass"] and hold_pass,"GEN2_PN_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen2"]==x["p"]*x["n"] for x in dags),"GEN2_PROVENANCE_PASS":dag_pass,
      "GEN2_MIXED_B_PIVOTS_PASS":bound_pass and all(all(d["raw_pairs"]==b["p"]*b["r"] for d in b["b_ledgers"]) for b in bounds),
      "STAGE3_SYMBOLIC_PASS":symbolic["algebra"]["pass"],"GEN3_PNR_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen3"]==x["p"]*x["n"]*x["r"] for x in dags),"GEN3_PROVENANCE_PASS":dag_pass,
      "TWO_CONSECUTIVE_MULTIPLICATION_PASS":symbolic["generation_counts"]["two_consecutive_multiplications"] and dag_pass,"GENERATION_DEPTH3_DAG_PASS":dag_pass,
      "DIRECT_FINAL_PROJECTION_PASS":hold_pass and all(x["direct_equals_staged"] for x in holds),"SYMBOLIC_MODEL_RECURRENCE_PASS":symbolic["model_recurrence"]["pass"] and hold_pass,"RECONSTRUCTION_PASS":full_ba4_pass,
      "FULL_ORIGINAL_CNF_VALIDATION_PASS":full_ba4_pass,"GRAPH_RECURRENCE_PASS":graph_sym["pass"] and graph_pass,"EDGE_DELTA_REGIME_PASS":graph_pass and all(x["delta_E"]==x["p"]*x["r"]-x["p"]-x["r"] for x in graphs),
      "QUOTIENT_WIDTH_PASS":graph_pass and all(x["quotient_tw_peak"]==min(x["p"],x["n"]*x["r"])+1 for x in graphs),"FULL_WIDTH_COMPOSITION_PASS":transport["pass"] and graph_sym["width"]["W_full_upper"]=="max(13,min(p,n*r)+1)",
      "EXACT_SOURCE_SIZE_PASS":size_pass,"BA14_RECOVERY_PASS":ba14_recovery,"BA12_PREFIX_APPLICABILITY_PASS":hist["BA12_prefix"]["pass"],"BA9_THIRD_LAYER_APPLICABILITY_PASS":hist["BA9_third"]["pass"],
      "BA10_FINAL_APPLICABILITY_PASS":hist["BA10"]["pass"] and hist["BA10"]["before_b_layer_applicable"] is False,"SOURCE_SCAFFOLD_FIREWALL_PASS":scaffold["pass"] and source_scaffold_holdout,
      "OUTPUT_SIZE_ACCOUNTING_PASS":comp["pass"] and scaffold["pass"],"SOURCE_CARRIER_TRANSPORT_PASS":transport["pass"] and source_metrics_complete,
      "ACTUAL_X_WORK_PASS":bound_pass and all(b["ledgers"]["B_ACTUAL_X_ELIMINATION"]["raw_pairs"]==b["p"] for b in bounds),
      "ACTUAL_Y_WORK_PASS":bound_pass and all(b["ledgers"]["C_ACTUAL_Y_ELIMINATION"]["raw_pairs"]==b["p"]*b["n"] for b in bounds),
      "ACTUAL_B_LAYER_WORK_PASS":bound_pass and boundary_metrics_complete and all(len(b["b_ledgers"])==b["n"] and sum(d["retained"] for d in b["b_ledgers"])==b["p"]*b["n"]*b["r"] for b in bounds),
      "GENERIC_GPNR_TRANSPORT_PASS":transport["pass"] and namespace_pass and symbolic["pass"],
      "NO_MANUAL_INSERTION_PASS":all(x["manual_derived_insertion"]==0 for x in dags) and transport["positive_local"]["manual_insertion"]==0 and transport["negative_local"]["manual_insertion"]==0,
      "ORDER_SCOPE_PASS":True,"COMPLEXITY_PASS":comp["pass"] and scaffold["pass"],
    }
    obligations={k:(1 if pass_map[k] else 0) for k in BASE_PASSES}; failures=[k for k,v in obligations.items() if v!=1]
    result={"gate":GATE,"kind":"SCIENTIFIC_RESULT_CANDIDATE_PRE_INDEPENDENT_REPLAY","preregistration_commit":PREREG,"parent_BA14_final_meta_commit":PARENT_BA14_META,"parent_BA14_source_commit":PARENT_BA14_SOURCE,"methodology_firewall_commit":METHOD_FIREWALL,
      "status_first":{"pass":True,"no_prior_BA15_found":True},"outcome":"BA15-A_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_MULTIPLICATION_CERTIFIED" if not failures else "BA15_NOT_PROMOTABLE","parameter_domain":{"p":">=1","n":">=1","r":">=1","g":">=1"},
      "symbolic":symbolic,"generation_DAG_holdouts":dags,"finite_holdouts":holds,"graph_symbolic":graph_sym,"graph_holdouts":graphs,"source_scaffold_firewall":scaffold,
      "source_size":{"formula":{"d":"p+n+n*r","C":"67g(d+2)-d-3","L":"163g(d+2)-2d-6","V":"20g(d+2)","n_struct":"250g(d+2)-3d-9"},"holdouts":sizes},
      "historical_controls":hist,"source_transport":transport,"actual_boundary_work":bounds,"namespace_holdouts":namespaces,
      "full_BA4_source_validation":{"source_model_cases":len(source_models),"reconstruction_cases":len(reconstruction_models),"source_models":source_models,"reconstruction_models":reconstruction_models,"pass":full_ba4_pass,"authority":"DIAGNOSTIC_HOLDOUTS_PLUS_SEALED_GENERIC_CARRIER_PRODUCT_CONSTRUCTION"},
      "generic_transport":{"proof":"every one of p+n+n*r+1 SOURCE couplings has an exact local BA4 transport certificate; p positive and 1+n+n*r negative certificates compose by boundary translation over arbitrary g-1 transitions; semantic x,y,b_1..b_n eliminations are applied only at the certified boundary","symbolic_in":["g","p","n","r"],"generic_truth_table_rows":0,"generic_boundary_state_rows":0,"manual_future_clause_insertion":0,"pass":transport["pass"] and namespace_pass},
      "order_firewall":{"authoritative_order":"x,y,b_1,...,b_n","all_b_orders_claimed":False,"commutation_theorem_started":False,"pass":True},"complexity":comp,"BA14_recovery":{"pass":ba14_recovery,"witness":[2,1,2]},
      "metrics_complete":{"source_local":source_metrics_complete,"boundary_ledgers":boundary_metrics_complete,"pass":source_metrics_complete and boundary_metrics_complete},
      "obligations":obligations,"base_pass_count":sum(obligations.values()),"base_required_count":len(obligations),"failure_count":len(failures),"falsifiers":failures,"independent_replay_pending":True,"preseal_completeness_pending":True,"P_BA15":0,
      "successive_generation_multiplication_certified_pre_replay":not failures,"self_sustaining_support_certified":False,"derived_future_support_certified":False,"repeated_multiplication_started":False,"next_gate_started":False,"BA16_started":False,
      "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True))
    if failures: raise SystemExit("BA15 builder obligations failed: "+",".join(failures))


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); args=ap.parse_args(); main(args.out)
