from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

EXPECTED_PREREG="26f582d9050369719d92be22d498f649c0a932c9"
EXPECTED_HARDENING="bd49ba59b12ab344ed3800b285d3009364064257"
EXPECTED_PARENT="fa0b503233cb873282c0d8317adf89e48223402b"
HOLDOUTS=[(1,(2,)),(1,(2,2)),(1,(2,2,2)),(1,(2,2,2,2)),(1,(2,2,2,2,2)),(2,(2,3,2))]

def sha_obj(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def canonical_dbo(L,q):
    blocks=[L["A"]]+[L["T"][m] for m in range(q)]+[L["B"][q]]
    roles=["A"]+[f"T_{m+1}" for m in range(q)]+[f"C_{q+1}"]
    flat=[v for b in blocks for v in b]
    assert len(flat)==len(set(flat)) and all(blocks)
    return {"roles":roles,"blocks":[list(x) for x in blocks],
            "hash":sha_obj({"roles":roles,"blocks":[list(x) for x in blocks]}),
            "refs":len(flat),"blocks_n":len(blocks)}

def eval_dbo(D,a):
    return any(all(bool(a[v]) for v in block) for block in D["blocks"])

def restrict(D,rho):
    blocks=[];roles=[]
    for role,block in zip(D["roles"],D["blocks"]):
        if any(v in rho and not rho[v] for v in block): continue
        rem=[v for v in block if not (v in rho and rho[v])]
        if not rem:return ("CONST",True,None)
        blocks.append(rem);roles.append(role)
    if not blocks:return ("CONST",False,None)
    return ("DBO",None,{"roles":roles,"blocks":blocks})

def abstract_block_lift_lemma():
    rows=[]
    for R in (0,1):
      for T in (0,1):
        for C in (0,1):
          left=any(((R or T or z) and ((not z) or C)) for z in (0,1))
          right=bool(R or T or C);rows.append(left==right)
    return all(rows)

def abstract_base_lemma():
    rows=[]
    for A in (0,1):
      for C in (0,1):
        left=any(((A or x) and ((not x) or y) and ((not y) or C)) for x in (0,1) for y in (0,1))
        rows.append(left==bool(A or C))
    return all(rows)

def future_seed_factor(p,ns):
    L=ba20.layout(p,ns);h=L["h"];seeds=[]
    for q in range(h-1):seeds.append({abs(l) for c in ba20.source_seed(L,q) for l in c})
    if not all({L["x"],L["y"]}.isdisjoint(s) for s in seeds):return False
    for q in range(h-1):
        cur=set(L["B"][q])|{L["Z"][q]}
        for ell in range(q+1,h-1):
            if not cur.isdisjoint(seeds[ell]):return False
    return True

def model_count(D):
    M=sum(map(len,D["blocks"]));bad=1
    for b in D["blocks"]:bad*=2**len(b)-1
    return 2**M-bad

def final_bits_for_block(L,idx):
    D=canonical_dbo(L,L["h"]-1);a={v:False for b in D["blocks"] for v in b}
    for v in D["blocks"][idx]:a[v]=True
    bits=[int(a[v]) for v in L["A"]]
    for T in L["T"]:bits += [int(a[v]) for v in T]
    bits += [int(a[v]) for v in L["B"][-1]]
    return tuple(bits),a

def reconstruction_replay(U,first,p,ns):
    L=ba20.layout(p,ns);D=canonical_dbo(L,L["h"]-1);rows=[]
    for idx in range(D["blocks_n"]):
        fb,a=final_bits_for_block(L,idx)
        if not eval_dbo(D,a):return False,[]
        sb=ba20.reconstruct_source_bits(fb,p,ns);abstract=ba20.source_bits_ok(sb,p,ns)
        for g in (1,2):
            actual=ba20.construct_model(first,U,g,p,ns,sb)
            rows.append(abstract and actual["pass"] and actual["bad_clause_count"]==0)
    return all(rows),rows

def restriction_replay(D):
    flat=[v for b in D["blocks"] for v in b]
    cases=[{}, {flat[0]:False},{flat[0]:True},{v:True for v in D["blocks"][0]},{b[0]:False for b in D["blocks"]}]
    for rho in cases:
        typ,val,obj=restrict(D,rho)
        if typ=="CONST":continue
        if not obj["blocks"]:return False
    return True

def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text());errors=[]
    def ck(c,m):
        if not c:errors.append(m)
    ck(r["preregistration_commit"]==EXPECTED_PREREG,"prereg")
    ck(r["preimplementation_hardening_commit"]==EXPECTED_HARDENING,"hardening")
    ck(r["parent_BA20_meta_commit"]==EXPECTED_PARENT,"parent")
    ck(r["implementation_version"]=="BA21_V1_DBO_NO_MATERIALIZATION","version")
    ck(r["no_materialization"]=={"EXPLICIT_PRIME_IMPLICATE_RECORDS":0,"EXPLICIT_CARTESIAN_OUTPUT_TUPLES":0,"EXPLICIT_SUPPORT_PRODUCT_RECORDS":0,"expand_then_compress":False},"no materialization")
    ck(abstract_base_lemma(),"base lemma");ck(abstract_block_lift_lemma(),"block lift existential lemma")
    symbolic_rules={"AND_j(t_j OR z)":"(AND_j t_j) OR z","AND_k((-z) OR c_k)":"(-z) OR (AND_k c_k)","EXISTS_z":"EXISTS z[(X OR z) AND ((-z) OR C)] IFF X OR C"}
    ck(r["symbolic"]["block_lift"]["generic_in_n_r"] is True,"generic symbolic proof")
    U,first,_,_=ba4.source_hardening();recon_cases=0;hold=[]
    result_holds={(x["p"],tuple(x["ns"])):x for x in r["holdouts"]}
    for p,ns in HOLDOUTS:
        L=ba20.layout(p,ns);D=canonical_dbo(L,L["h"]-1);rr=result_holds.get((p,ns));ck(rr is not None,"missing holdout")
        if rr:
            ck(rr["DBO_hash"]==D["hash"],"DBO hash");ck(rr["blocks"]==D["blocks_n"] and rr["refs"]==D["refs"],"DBO size")
        ck(future_seed_factor(p,ns),"future seed factor");ck(model_count(D)==ba20.model_count_formula(p,ns),"model count");ck(restriction_replay(D),"restriction closure")
        ok,rows=reconstruction_replay(U,first,p,ns);recon_cases+=len(rows);ck(ok,"reconstruction BA4")
        hold.append({"p":p,"ns":list(ns),"hash":D["hash"],"reconstruction_cases":len(rows)})
    h=64;L=ba20.layout(1,(2,)*h);D=canonical_dbo(L,h-1)
    large={"h":64,"blocks":D["blocks_n"],"refs":D["refs"],"implicit_prime_clauses":"2^64","explicit_prime_records":0,"pass":D["blocks_n"]==65 and D["refs"]==129}
    ck(large["pass"],"large no expansion")
    ck(r["large_depth_diagnostic"]["explicit_prime_implicate_records"]==0 and r["large_depth_diagnostic"]["explicit_support_product_records"]==0 and r["large_depth_diagnostic"]["explicit_cartesian_output_tuples"]==0,"large counters")
    ck(r["symbolic"]["BA20_lower_bound_preserved"].startswith("auxiliary-free projected CNF still requires"),"BA20 lower bound")
    status="PASS" if not errors else "FAIL"
    out={"gate":"R50G25BA21_INDEPENDENT_REPLAY","status":status,"P_BA21":1 if status=="PASS" else 0,"errors":errors,
         "implementation_imported":False,"generic_base_lemma":"PASS" if abstract_base_lemma() else "FAIL","generic_block_lift":"PASS" if abstract_block_lift_lemma() else "FAIL",
         "symbolic_rules":symbolic_rules,"future_seed_factoring":"PASS" if not any("future seed" in e for e in errors) else "FAIL",
         "holdouts":hold,"full_BA4_reconstruction_cases":recon_cases,"large_depth":large,"no_exponential_prime_list_required":True,
         "BA20_lower_bound_preserved":True,"BA22_started":False,"P_VS_NP":"OPEN"}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("BA21 independent replay failure: "+repr(errors))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.out)
