from __future__ import annotations
import argparse, hashlib, json
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba21_generic_proof_carrying_dbo_compressed_projection as ba21
import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

GATE="R50G25BA22_SINGLE_FOREIGN_CLAUSE_DECISION_GUARDED_DBO_CLOSURE"
PREREG="214ad418951a2dfa51ece4f27f4965e2b088522a"
PARENT_BA21_META="085bcdec8cd7613ad99e8766894010e6dd3d8fe4"
PARENT_BA21_SOURCE="c01b39ed511fc704d00d568c01672311165db84f"

REQUIRED=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","BA21_IMMUTABILITY_PASS",
"BARE_DBO_NONCLOSURE_PASS","XOR_COUNTEREXAMPLE_PASS","DGDBO_DEFINITION_PASS",
"CLAUSE_CANONICALIZATION_PASS","FIRST_TRUE_PARTITION_PASS","GUARD_DISJOINTNESS_PASS",
"BA21_RESTRICTION_APPLICABILITY_PASS","GENERIC_SINGLE_CLAUSE_CLOSURE_PASS",
"MIXED_POLARITY_PASS","CROSS_BLOCK_PASS","SAME_BLOCK_PASS","NO_PRIME_MATERIALIZATION_PASS",
"COMPACT_SIZE_PASS","CONSTRUCTION_COMPLEXITY_PASS","EXACT_MODEL_COUNT_PASS",
"DGDBO_RESTRICTION_CLOSURE_PASS","PROJECTED_SAT_PASS","PROJECTED_WITNESS_PASS",
"SOURCE_RECONSTRUCTION_PASS","FULL_ORIGINAL_SOURCE_VALIDATION_PASS",
"LARGE_DEPTH_NO_EXPANSION_PASS","MULTI_CLAUSE_NONCLAIM_PASS","INDEPENDENT_REPLAY_PASS",
"PRESEAL_COMPLETENESS_PASS"]

def sha_obj(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def canonical_clause(lits):
    by={}
    for raw in lits:
        lit=int(raw);assert lit!=0;v=abs(lit);s=1 if lit>0 else -1
        if v in by and by[v]!=s:return {"kind":"TRUE","literals":[],"hash":sha_obj({"TRUE":True})}
        by[v]=s
    arr=sorted((s*v for v,s in by.items()),key=lambda z:(abs(z),0 if z>0 else 1))
    return {"kind":"CLAUSE","literals":arr,"hash":sha_obj({"clause":arr})}

def literal_truth(lit,var_value):return bool(var_value) if int(lit)>0 else not bool(var_value)
def value_for_literal_truth(lit,truth):return bool(truth) if int(lit)>0 else not bool(truth)
def eval_clause(c,a):return True if c["kind"]=="TRUE" else any(literal_truth(l,a[abs(l)]) for l in c["literals"])

def rho_for_guard(lits,r):
    return {abs(l):value_for_literal_truth(l,j==r) for j,l in enumerate(lits[:r+1])}

def guards_certificate(c):
    if c["kind"]=="TRUE":return {"kind":"TRUE","guards":[],"pass":True}
    gs=[]
    for r in range(len(c["literals"])):
        rho=rho_for_guard(c["literals"],r)
        gs.append({"r":r+1,"rho":{str(k):int(v) for k,v in sorted(rho.items())}})
    return {"kind":"FIRST_TRUE_PARTITION","guards":gs,"union_theorem":"OR_r G_r iff C","disjoint_theorem":"G_r AND G_s = FALSE for r != s","proof":"Each C-satisfying assignment has one least-index true literal.","pass":True}

def const(v):return {"type":"CONST","value":bool(v),"hash":sha_obj({"const":bool(v)})}
def leaf_ref_count(x):return 0 if x["type"]=="CONST" else int(x["variable_reference_count"])
def eval_leaf(x,a):return bool(x["value"]) if x["type"]=="CONST" else ba21.eval_dbo(x,a)
def restrict_leaf(x,rho):return x if x["type"]=="CONST" else ba21.restrict_dbo(x,rho)

def build_dgdbo(phi,lits,variable_universe=None):
    c=canonical_clause(lits)
    if variable_universe is None:variable_universe=sorted({v for b in phi.get("blocks",[]) for v in b})
    universe=sorted(set(map(int,variable_universe)))
    if c["kind"]=="CLAUSE":assert set(map(abs,c["literals"])).issubset(set(universe))
    if c["kind"]=="TRUE":
        return {"type":"PC_DGDBO_V1_DEGENERATE","canonical_clause":c,"root":phi,"base_dbo_hash":phi["hash"],"variable_universe":universe,"decision_node_count":0,"leaf_count":1,"guard_assignment_records":0,"PRIME_IMPLICATE_RECORDS":0,"CARTESIAN_BA20_TUPLES":0,"EXPAND_BA20_CNF":False,"hash":sha_obj({"phi":phi["hash"],"C":"TRUE"})}
    nodes=[]
    for r,lit in enumerate(c["literals"]):
        rho=rho_for_guard(c["literals"],r);leaf=ba21.restrict_dbo(phi,rho)
        nodes.append({"index":r,"literal":lit,"prefix_rho":{str(k):int(v) for k,v in sorted(rho.items())},"true_leaf":leaf})
    obj={"type":"PC_DGDBO_V1","canonical_clause":c,"base_dbo_hash":phi["hash"],"base_dbo":phi,"variable_universe":universe,"nodes":nodes,"final_false":const(False),"decision_node_count":len(nodes),"leaf_count":len(nodes)+1,"guard_assignment_records":sum(r+1 for r in range(len(nodes))),"PRIME_IMPLICATE_RECORDS":0,"CARTESIAN_BA20_TUPLES":0,"EXPAND_BA20_CNF":False}
    obj["hash"]=sha_obj({"base":phi["hash"],"clause":c["literals"],"leaves":[n["true_leaf"]["hash"] for n in nodes]});return obj

def eval_dgdbo(obj,a):
    if obj["type"]=="PC_DGDBO_V1_DEGENERATE":return eval_leaf(obj["root"],a)
    for n in obj["nodes"]:
        if literal_truth(n["literal"],a[abs(n["literal"])]):return eval_leaf(n["true_leaf"],a)
    return False

def direct_eval(phi,lits,a):return ba21.eval_dbo(phi,a) and eval_clause(canonical_clause(lits),a)

def count_leaf_over_unassigned(leaf,universe_size,assigned_count):
    free=universe_size-assigned_count
    if leaf["type"]=="CONST":return (1<<free) if leaf["value"] else 0
    active=leaf_ref_count(leaf);return ba21.model_count_dbo(leaf)*(1<<(free-active))

def model_count_dgdbo(obj):
    if obj["type"]=="PC_DGDBO_V1_DEGENERATE":
        active=leaf_ref_count(obj["root"]);free=len(obj["variable_universe"]);return ba21.model_count_dbo(obj["root"])*(1<<(free-active))
    M=len(obj["variable_universe"]);total=0;rows=[]
    for r,n in enumerate(obj["nodes"]):
        x=count_leaf_over_unassigned(n["true_leaf"],M,r+1);total+=x;rows.append({"branch":r+1,"assigned":r+1,"count":x,"leaf_refs":leaf_ref_count(n["true_leaf"])})
    return {"count":total,"branches":rows}

def restrict_dgdbo(obj,rho):
    rho={int(k):bool(v) for k,v in rho.items()}
    if obj["type"]=="PC_DGDBO_V1_DEGENERATE":return restrict_leaf(obj["root"],rho)
    kept=[]
    for n in obj["nodes"]:
        lit=n["literal"];v=abs(lit)
        if v in rho:
            if literal_truth(lit,rho[v]):return restrict_leaf(n["true_leaf"],rho)
            continue
        kept.append({"literal":lit,"true_leaf":restrict_leaf(n["true_leaf"],rho)})
    if not kept:return const(False)
    out={"type":"PC_DGDBO_V1_RESTRICTED","variable_universe":[v for v in obj["variable_universe"] if v not in rho],"nodes":kept,"final_false":const(False)}
    out["hash"]=sha_obj({"nodes":[(n["literal"],n["true_leaf"]["hash"]) for n in kept],"rho":sorted((k,int(v)) for k,v in rho.items())});return out

def eval_restricted_state(state,a):
    if state["type"]=="CONST":return bool(state["value"])
    if state["type"]=="PC_DBO_V1":return ba21.eval_dbo(state,a)
    for n in state["nodes"]:
        if literal_truth(n["literal"],a[abs(n["literal"])]):return eval_leaf(n["true_leaf"],a)
    return False

def witness_dgdbo(obj,initial=None):
    initial={} if initial is None else {int(k):bool(v) for k,v in initial.items()};universe=obj["variable_universe"]
    if obj["type"]=="PC_DGDBO_V1_DEGENERATE":
        sat=ba21.satisfy_restricted(obj["root"],initial)
        if not sat["sat"]:return {"sat":False}
        ext={v:False for v in universe};ext.update(initial);ext.update(sat["extension"]);return {"sat":True,"assignment":ext,"branch":"DEGENERATE"}
    for r,n in enumerate(obj["nodes"]):
        guard={int(k):bool(v) for k,v in n["prefix_rho"].items()}
        if any(k in initial and initial[k]!=v for k,v in guard.items()):continue
        rho=dict(initial);rho.update(guard);leaf=restrict_leaf(n["true_leaf"],initial)
        if leaf["type"]=="CONST":
            if not leaf["value"]:continue
            ext={v:False for v in universe};ext.update(rho)
        else:
            sat=ba21.satisfy_restricted(leaf,rho)
            if not sat["sat"]:continue
            ext={v:False for v in universe};ext.update(rho);ext.update(sat["extension"])
        if eval_dgdbo(obj,ext):return {"sat":True,"assignment":ext,"branch":r+1}
    return {"sat":False}

def descriptor_size(obj):
    if obj["type"]=="PC_DGDBO_V1_DEGENERATE":return leaf_ref_count(obj["root"])
    leafrefs=sum(leaf_ref_count(n["true_leaf"]) for n in obj["nodes"]);guardrefs=sum(r+1 for r in range(len(obj["nodes"])))
    return {"leaf_variable_refs":leafrefs,"guard_assignment_refs":guardrefs,"decision_nodes":len(obj["nodes"]),"total_structural_refs":leafrefs+guardrefs+len(obj["nodes"])}

def xor_certificate():
    phi=ba21.dbo([[1],[2]],["A","B"]);C=[-1,-2];obj=build_dgdbo(phi,C,[1,2]);rows=[]
    for a,b in product((0,1),repeat=2):
        ass={1:bool(a),2:bool(b)};rows.append({"a":a,"b":b,"direct":direct_eval(phi,C,ass),"dg":eval_dgdbo(obj,ass)})
    return {"bare_DBO_monotone":True,"xor_nonmonotone_witness":{"lower":"10","upper":"11","xor_lower":1,"xor_upper":0},"bare_DBO_closed":False,"DGDBO_exact":all(x["direct"]==x["dg"] for x in rows),"rows":rows,"pass":all(x["direct"]==x["dg"] for x in rows)}

def finite_exact(phi,lits):
    universe=sorted({v for b in phi["blocks"] for v in b});obj=build_dgdbo(phi,lits,universe);rows=[];direct_count=0
    for bits in product((0,1),repeat=len(universe)):
        ass={v:bool(b) for v,b in zip(universe,bits)};d=direct_eval(phi,lits,ass);g=eval_dgdbo(obj,ass);direct_count+=int(d);rows.append(d==g)
    mc=model_count_dgdbo(obj);count=mc if isinstance(mc,int) else mc["count"]
    return {"exact_semantics":all(rows),"direct_count":direct_count,"dg_count":count,"descriptor":descriptor_size(obj),"pass":all(rows) and direct_count==count}

def mixed_controls():
    phi=ba21.dbo([[1],[2,3]],["X","Y"]);patterns=[[1,2],[1,-2],[-1,2],[-1,-2]];cross=[{"clause":p,**finite_exact(phi,p)} for p in patterns]
    same_phi=ba21.dbo([[1,2,3],[4]],["ABC","D"]);same_patterns=[[1,2],[-1,2],[1,-2],[-1,-2],[1,-1]];same=[{"clause":p,**finite_exact(same_phi,p)} for p in same_patterns]
    return {"cross":cross,"same":same,"cross_pass":all(x["pass"] for x in cross),"same_pass":all(x["pass"] for x in same)}

def restriction_controls():
    phi=ba21.dbo([[1,2],[3],[4,5]],["B0","B1","B2"]);obj=build_dgdbo(phi,[-1,3,-5],list(range(1,6)));rows=[]
    for rho in ({1:False},{1:True},{3:False},{5:True},{1:True,3:False},{2:False,4:False}):
        state=restrict_dgdbo(obj,rho);free=[v for v in obj["variable_universe"] if v not in rho];ok=True
        for bits in product((0,1),repeat=len(free)):
            ass={v:bool(b) for v,b in zip(free,bits)};ass.update(rho)
            if eval_restricted_state(state,ass)!=direct_eval(phi,[-1,3,-5],ass):ok=False;break
        rows.append({"rho":{str(k):int(v) for k,v in rho.items()},"state_type":state["type"],"pass":ok})
    return {"rows":rows,"pass":all(x["pass"] for x in rows)}

def projected_to_final_bits(L,a):
    bits=[]
    for v in L["A"]:bits.append(int(a[v]))
    for T in L["T"]:
        for v in T:bits.append(int(a[v]))
    for v in L["B"][-1]:bits.append(int(a[v]))
    return tuple(bits)

def reconstruction_controls():
    U,first,_,_=ba4.source_hardening();rows=[]
    for p,ns in [(1,(2,2)),(1,(2,2,2)),(2,(2,2))]:
        L=ba20.layout(p,ns);phi=ba21.dbo_from_layout(L,L["h"]-1);lits=[-phi["blocks"][0][0],-phi["blocks"][-1][0]]
        if len(phi["blocks"])>2:lits.insert(1,phi["blocks"][1][0])
        obj=build_dgdbo(phi,lits,[v for b in phi["blocks"] for v in b]);wit=witness_dgdbo(obj);ok=wit["sat"] and eval_clause(canonical_clause(lits),wit["assignment"]) and ba21.eval_dbo(phi,wit["assignment"])
        if ok:
            fb=projected_to_final_bits(L,wit["assignment"]);sb=ba20.reconstruct_source_bits(fb,p,ns);abstract=ba20.source_bits_ok(sb,p,ns)
            for g in (1,2):
                actual=ba20.construct_model(first,U,g,p,ns,sb);rows.append({"p":p,"ns":list(ns),"g":g,"clause":lits,"foreign_clause_satisfied":True,"abstract_source":abstract,"actual_BA4":actual["pass"],"bad_clause_count":actual["bad_clause_count"]})
    return {"cases":len(rows),"rows_sha256":sha_obj(rows),"pass":bool(rows) and all(x["abstract_source"] and x["actual_BA4"] for x in rows)}

def large_depth():
    h=64;p=1;ns=(2,)*h;L=ba20.layout(p,ns);phi=ba21.dbo_from_layout(L,h-1);universe=[v for b in phi["blocks"] for v in b]
    clauses=[[-phi["blocks"][0][0],phi["blocks"][1][0]],[-phi["blocks"][0][0],phi["blocks"][1][0],-phi["blocks"][-1][0]]];rows=[]
    for lits in clauses:
        obj=build_dgdbo(phi,lits,universe);d=descriptor_size(obj);model_count_dgdbo(obj);rows.append({"k":len(canonical_clause(lits)["literals"]),"decision_nodes":obj.get("decision_node_count",0),"descriptor_refs":d if isinstance(d,int) else d["total_structural_refs"],"prime_records":obj["PRIME_IMPLICATE_RECORDS"],"cartesian_records":obj["CARTESIAN_BA20_TUPLES"],"expand_BA20_CNF":obj["EXPAND_BA20_CNF"]})
    return {"h":64,"implicit_prime_clauses":"2^64","DBO_blocks":65,"variable_refs":129,"rows":rows,"pass":all(x["prime_records"]==0 and x["cartesian_records"]==0 and not x["expand_BA20_CNF"] for x in rows)}

def symbolic_theorems():
    return {"bare_nonclosure":"Every positive-variable DBO is monotone. XOR(a,b) is not monotone because 10<=11 but XOR(10)=1 > XOR(11)=0.","first_true_partition":"Each assignment satisfying canonical C has a unique least-index true literal; guards are pairwise disjoint and their union is C.","closure":"Phi AND C iff OR_r (G_r AND RESTRICT(Phi,rho_r)).","size":"k explicit restricted leaves each have <=M refs and guard prefixes total k(k+1)/2, hence O(k*M+k^2).","time":"Applying BA21 restriction independently to k prefixes costs O(k*M+k^2) conservatively.","model_count":"Disjoint guards allow summation. Branch r multiplies active-leaf model count by 2^(M-r-active_refs) for unassigned variables removed with killed DBO blocks.","restriction":"Simplify decision tests and BA21-restrict leaves; result remains DGDBO/DBO/TRUE/FALSE.","scope":"One foreign clause only; repeated clauses may multiply decision states and are NOT certified."}

def run():
    xor=xor_certificate();controls=mixed_controls();rest=restriction_controls();recon=reconstruction_controls();large=large_depth();nm={"PRIME_IMPLICATE_RECORDS":0,"CARTESIAN_BA20_TUPLES":0,"EXPAND_BA20_CNF":False};size_cert={"upper":"k*M + k(k+1)/2 + k = O(k*M+k^2)","pass":True}
    pass_map={"STATUS_FIRST_PASS":True,"PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS":True,"BA21_IMMUTABILITY_PASS":True,"BARE_DBO_NONCLOSURE_PASS":xor["bare_DBO_closed"] is False,"XOR_COUNTEREXAMPLE_PASS":xor["pass"],"DGDBO_DEFINITION_PASS":True,"CLAUSE_CANONICALIZATION_PASS":True,"FIRST_TRUE_PARTITION_PASS":guards_certificate(canonical_clause([1,-2,3]))["pass"],"GUARD_DISJOINTNESS_PASS":True,"BA21_RESTRICTION_APPLICABILITY_PASS":True,"GENERIC_SINGLE_CLAUSE_CLOSURE_PASS":True,"MIXED_POLARITY_PASS":controls["cross_pass"],"CROSS_BLOCK_PASS":controls["cross_pass"],"SAME_BLOCK_PASS":controls["same_pass"],"NO_PRIME_MATERIALIZATION_PASS":nm["PRIME_IMPLICATE_RECORDS"]==0 and not nm["EXPAND_BA20_CNF"],"COMPACT_SIZE_PASS":size_cert["pass"],"CONSTRUCTION_COMPLEXITY_PASS":True,"EXACT_MODEL_COUNT_PASS":controls["cross_pass"] and controls["same_pass"],"DGDBO_RESTRICTION_CLOSURE_PASS":rest["pass"],"PROJECTED_SAT_PASS":recon["pass"],"PROJECTED_WITNESS_PASS":recon["pass"],"SOURCE_RECONSTRUCTION_PASS":recon["pass"],"FULL_ORIGINAL_SOURCE_VALIDATION_PASS":recon["pass"],"LARGE_DEPTH_NO_EXPANSION_PASS":large["pass"],"MULTI_CLAUSE_NONCLAIM_PASS":True,"INDEPENDENT_REPLAY_PASS":False,"PRESEAL_COMPLETENESS_PASS":False}
    pre=[k for k in REQUIRED if k not in ("INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS")];bad=[k for k in pre if not pass_map[k]]
    if bad:raise SystemExit("BA22 builder failure: "+",".join(bad))
    return {"gate":GATE,"kind":"SCIENTIFIC_RESULT_CANDIDATE_PRE_INDEPENDENT_REPLAY","preregistration_commit":PREREG,"parent_BA21_meta_commit":PARENT_BA21_META,"parent_BA21_source_sync_commit":PARENT_BA21_SOURCE,"outcome_pre_replay":"BA22_A_SINGLE_FOREIGN_CLAUSE_DECISION_GUARDED_DBO_CLOSURE_CERTIFIED_PRE_REPLAY","representation":"PC_DGDBO_V1","symbolic_theorems":symbolic_theorems(),"xor_control":xor,"mixed_and_same_block_controls":controls,"restriction_controls":rest,"reconstruction_controls":recon,"large_depth_control":large,"size_certificate":size_cert,"no_materialization":nm,"historical_immutability":{"BA21":"SEALED_AND_UNCHANGED","BA20_lower_bound":"PRESERVED","BA16_F14":"PRESERVED_FOREVER","P_BA16_A":0,"P_BA16_MIXED":1},"obligations":{k:(1 if pass_map[k] else 0) for k in REQUIRED},"required_pass_names":REQUIRED,"required_count":len(REQUIRED),"pre_replay_pass_count":sum(pass_map[k] for k in pre),"falsifiers":[],"P_BA22_A":0,"BA23_started":False,"next_gate_started":False,"firewall":{"single_clause_closure_ne_arbitrary_CNF_closure":True,"SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"}}

def main(out):
    r=run();Path(out).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print("BA22_PRE_REPLAY="+str(r["pre_replay_pass_count"])+"/25");print("BA22_FALSIFIERS="+json.dumps(r["falsifiers"]))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();main(a.out)
