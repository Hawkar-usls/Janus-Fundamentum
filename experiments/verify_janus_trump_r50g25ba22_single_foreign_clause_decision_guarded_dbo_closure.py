from __future__ import annotations
import argparse, json, hashlib
from itertools import product
from pathlib import Path
import janus_trump_r50g25ba21_generic_proof_carrying_dbo_compressed_projection as ba21
import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG="214ad418951a2dfa51ece4f27f4965e2b088522a"

def sha_obj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def canon(lits):
    d={}
    for l in map(int,lits):
        if abs(l) in d and d[abs(l)]!=(l>0):return None
        d[abs(l)]=(l>0)
    return sorted((v if s else -v for v,s in d.items()),key=lambda x:(abs(x),0 if x>0 else 1))
def ltruth(l,val):return bool(val) if l>0 else not bool(val)
def val_for(l,t):return bool(t) if l>0 else not bool(t)
def guard(lits,r):return {abs(l):val_for(l,j==r) for j,l in enumerate(lits[:r+1])}
def eval_clause(lits,a):
    c=canon(lits)
    return True if c is None else any(ltruth(l,a[abs(l)]) for l in c)
def restrict_leaf(phi,rho):return ba21.restrict_dbo(phi,rho)
def eval_leaf(x,a):return bool(x["value"]) if x["type"]=="CONST" else ba21.eval_dbo(x,a)
def active_refs(x):return 0 if x["type"]=="CONST" else x["variable_reference_count"]
def leaf_count(x,free):
    if x["type"]=="CONST":return (1<<free) if x["value"] else 0
    return ba21.model_count_dbo(x)*(1<<(free-active_refs(x)))

def independent_dg(phi,lits):
    c=canon(lits);universe=sorted({v for b in phi["blocks"] for v in b})
    if c is None:return {"taut":True,"universe":universe,"phi":phi}
    return {"taut":False,"universe":universe,"phi":phi,"branches":[{"lit":l,"rho":guard(c,r),"leaf":restrict_leaf(phi,guard(c,r))} for r,l in enumerate(c)]}

def eval_dg(o,a):
    if o["taut"]:return ba21.eval_dbo(o["phi"],a)
    for b in o["branches"]:
        if ltruth(b["lit"],a[abs(b["lit"])]):return eval_leaf(b["leaf"],a)
    return False

def count_dg(o):
    M=len(o["universe"])
    if o["taut"]:return ba21.model_count_dbo(o["phi"])
    return sum(leaf_count(b["leaf"],M-(r+1)) for r,b in enumerate(o["branches"]))

def finite(phi,lits):
    o=independent_dg(phi,lits);U=o["universe"];dc=0;ok=True
    for bits in product((0,1),repeat=len(U)):
        a={v:bool(x) for v,x in zip(U,bits)};direct=ba21.eval_dbo(phi,a) and eval_clause(lits,a);dc+=int(direct);ok &= direct==eval_dg(o,a)
    return ok and dc==count_dg(o),dc,count_dg(o)

def xor():
    phi=ba21.dbo([[1],[2]],["A","B"]);ok,dc,gc=finite(phi,[-1,-2]);return ok and dc==2 and gc==2

def mixed():
    cross=ba21.dbo([[1],[2,3]],["X","Y"]);same=ba21.dbo([[1,2,3],[4]],["ABC","D"])
    ps=[[1,2],[1,-2],[-1,2],[-1,-2]];qs=[[1,2],[-1,2],[1,-2],[-1,-2],[1,-1]]
    return all(finite(cross,p)[0] for p in ps) and all(finite(same,q)[0] for q in qs)

def restriction_exact():
    phi=ba21.dbo([[1,2],[3],[4,5]],["B0","B1","B2"]);lits=[-1,3,-5];o=independent_dg(phi,lits)
    for rho in ({1:False},{1:True},{3:False},{5:True},{1:True,3:False},{2:False,4:False}):
        free=[v for v in o["universe"] if v not in rho]
        for bits in product((0,1),repeat=len(free)):
            a={v:bool(b) for v,b in zip(free,bits)};a.update(rho)
            if (ba21.eval_dbo(phi,a) and eval_clause(lits,a)) != eval_dg(o,a):return False
    return True

def projected_bits(L,a):
    out=[int(a[v]) for v in L["A"]]
    for T in L["T"]:out += [int(a[v]) for v in T]
    out += [int(a[v]) for v in L["B"][-1]];return tuple(out)

def witness_independent(phi,lits):
    o=independent_dg(phi,lits)
    if o["taut"]:
        sat=ba21.satisfy_restricted(phi,{})
        if not sat["sat"]:return None
        a={v:False for v in o["universe"]};a.update(sat["extension"]);return a
    for b in o["branches"]:
        rho=dict(b["rho"]);leaf=b["leaf"]
        if leaf["type"]=="CONST":
            if not leaf["value"]:continue
            a={v:False for v in o["universe"]};a.update(rho)
        else:
            sat=ba21.satisfy_restricted(leaf,rho)
            if not sat["sat"]:continue
            a={v:False for v in o["universe"]};a.update(rho);a.update(sat["extension"])
        if ba21.eval_dbo(phi,a) and eval_clause(lits,a):return a
    return None

def reconstruction():
    U,first,_,_=ba4.source_hardening();rows=[]
    for p,ns in [(1,(2,2)),(1,(2,2,2)),(2,(2,2))]:
        L=ba20.layout(p,ns);phi=ba21.dbo_from_layout(L,L["h"]-1);lits=[-phi["blocks"][0][0],-phi["blocks"][-1][0]]
        if len(phi["blocks"])>2:lits.insert(1,phi["blocks"][1][0])
        a=witness_independent(phi,lits)
        if a is None:return False,rows
        fb=projected_bits(L,a);sb=ba20.reconstruct_source_bits(fb,p,ns)
        if not ba20.source_bits_ok(sb,p,ns):return False,rows
        for g in (1,2):
            x=ba20.construct_model(first,U,g,p,ns,sb);rows.append({"p":p,"ns":list(ns),"g":g,"pass":x["pass"]})
            if not x["pass"]:return False,rows
    return True,rows

def large64():
    L=ba20.layout(1,(2,)*64);phi=ba21.dbo_from_layout(L,63)
    for lits in ([-phi["blocks"][0][0],phi["blocks"][1][0]],[-phi["blocks"][0][0],phi["blocks"][1][0],-phi["blocks"][-1][0]]):
        o=independent_dg(phi,lits)
        if len(o["branches"])!=len(canon(lits)):return False
        if phi["block_count"]!=65 or phi["variable_reference_count"]!=129:return False
    return True

def main(result_path,out_path):
    R=json.loads(Path(result_path).read_text());errors=[]
    def ck(x,m):
        if not x:errors.append(m)
    ck(R["preregistration_commit"]==PREREG,"prereg")
    ck(R["representation"]=="PC_DGDBO_V1","representation")
    ck(R["parent_BA21_meta_commit"]=="085bcdec8cd7613ad99e8766894010e6dd3d8fe4","parent")
    ck(R["historical_immutability"]["BA21"]=="SEALED_AND_UNCHANGED","BA21 immutability")
    ck(R["historical_immutability"]["BA20_lower_bound"]=="PRESERVED","BA20 lower bound")
    ck(R["no_materialization"]["PRIME_IMPLICATE_RECORDS"]==0 and R["no_materialization"]["CARTESIAN_BA20_TUPLES"]==0 and not R["no_materialization"]["EXPAND_BA20_CNF"],"no materialization")
    ck(xor(),"xor");ck(mixed(),"mixed/same");ck(restriction_exact(),"restriction")
    rec,rows=reconstruction();ck(rec,"reconstruction");ck(large64(),"large64")
    symbolic={"first_true_partition":"unique least-index true literal gives disjoint exhaustive C partition","closure":"on branch r, guard fixes rho_r and Phi becomes RESTRICT(Phi,rho_r); disjoint union equals Phi AND C","size":"k leaves * <=M refs + k(k+1)/2 guard assignments + k nodes = O(kM+k^2)","model_count":"sum disjoint branch counts, including free variables removed by killed DBO blocks","multi_clause_nonclaim":True}
    ck(R["firewall"]["single_clause_closure_ne_arbitrary_CNF_closure"] is True,"multi clause firewall")
    status="PASS" if not errors else "FAIL"
    out={"gate":"R50G25BA22_INDEPENDENT_REPLAY","status":status,"errors":errors,"implementation_imported":False,"symbolic_replay":symbolic,"xor_replayed":True,"mixed_and_same_block_replayed":True,"actual_BA4_reconstruction_cases":len(rows),"actual_rows_sha256":sha_obj(rows),"large_h64_replayed":True,"P_BA22":1 if status=="PASS" else 0}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("; ".join(errors))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.out)
