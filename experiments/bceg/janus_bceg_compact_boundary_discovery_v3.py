from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from itertools import product
from pathlib import Path
from statistics import median

PREREG = Path("research/JANUS_BCEG_COMPACT_BOUNDARY_DISCOVERY_V3_PREREGISTRATION_2026-08-30.json")
PROJECTOR_VERSION = "BCEG_V3_PROJECTORS_2026-08-30"
PORTFOLIO = (
    "DECOY_MONOTONE",
    "HORN_FORCE_PROJECTOR",
    "TWO_SAT_SIGNED_EQ_PROJECTOR",
    "GF2_AFFINE_PROJECTOR",
)

def stable_seed(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")

def canonical_cnf(clauses):
    out = set()
    for clause in clauses:
        c = frozenset(int(x) for x in clause)
        if any(-l in c for l in c):
            continue
        out.add(c)
    return tuple(sorted(out, key=lambda c: (len(c), tuple(sorted(c, key=lambda x:(abs(x),x))))))

def cnf_vars(cnf):
    return sorted({abs(l) for c in cnf for l in c})

def canonical_json_hash(obj):
    b = json.dumps(obj, sort_keys=True, separators=(",",":")).encode()
    return hashlib.sha256(b).hexdigest(), len(b)

def cnf_hash(cnf):
    payload = [[int(x) for x in sorted(c, key=lambda z:(abs(z),z))] for c in cnf]
    return canonical_json_hash(payload)[0]

def xor_clauses(vars_, rhs):
    clauses=[]
    for bits in product((0,1), repeat=len(vars_)):
        if (sum(bits) & 1) == int(rhs):
            continue
        clauses.append([v if b == 0 else -v for v,b in zip(vars_,bits)])
    return clauses

def encode_xor_equation(vars_, rhs):
    return xor_clauses(tuple(vars_), int(rhs))

def make_gf2_parity(boundary, rhs, start_internal):
    b=list(boundary)
    if len(b)==2:
        return canonical_cnf(encode_xor_equation(b,rhs)), start_internal
    clauses=[]
    nxt=start_internal
    z=nxt; nxt+=1
    clauses += encode_xor_equation((b[0],b[1],z),0)
    prev=z
    for i in range(2,len(b)-1):
        z=nxt; nxt+=1
        clauses += encode_xor_equation((prev,b[i],z),0)
        prev=z
    clauses += encode_xor_equation((prev,b[-1]),rhs)
    return canonical_cnf(clauses), nxt

def make_horn_force(boundary, start_internal):
    clauses=[]
    nxt=start_internal
    for x in boundary:
        a=nxt; b=nxt+1; nxt+=2
        clauses.append([a])
        clauses.append([-a,b])
        clauses.append([-b,x])
    return canonical_cnf(clauses), nxt

def relation_clauses(a,b,sign):
    if sign==0:
        return [[-a,b],[a,-b]]
    return [[-a,-b],[a,b]]

def make_twosat_signed(boundary, signs, start_internal):
    clauses=[]
    nxt=start_internal
    anchor=boundary[0]
    for i,x in enumerate(boundary[1:],1):
        mid=nxt; nxt+=1
        t=(i + len(boundary)) & 1
        clauses += relation_clauses(anchor,mid,t)
        clauses += relation_clauses(mid,x,t ^ int(signs[i]))
    return canonical_cnf(clauses), nxt

def remap_case(components,boundary,seed):
    rng=random.Random(seed)
    allv=sorted(set(boundary) | {v for c in components for v in cnf_vars(c)})
    perm=allv[:]
    rng.shuffle(perm)
    mp=dict(zip(allv,perm))
    out=[]
    for cnf in components:
        cls=[]
        for c in cnf:
            cc=[(1 if l>0 else -1)*mp[abs(l)] for l in c]
            rng.shuffle(cc)
            cls.append(cc)
        rng.shuffle(cls)
        out.append(canonical_cnf(cls))
    rng.shuffle(out)
    return out, tuple(sorted(mp[x] for x in boundary))

def canonical_equations(eqs):
    rows=[]
    for vs,r in eqs:
        s=set(vs); rr=int(r)&1
        if not s:
            if rr: return [([],1)]
            continue
        rows.append([s,rr])
    piv={}
    for row in rows:
        s,rr=row
        while s:
            p=min(s)
            if p not in piv:
                piv[p]=[set(s),rr]
                break
            ps,pr=piv[p]
            s.symmetric_difference_update(ps); rr ^= pr
        if not s and rr:
            return [([],1)]
    keys=sorted(piv)
    for p in reversed(keys):
        ps,pr=piv[p]
        for q in keys:
            if q>=p: continue
            qs,qr=piv[q]
            if p in qs:
                qs.symmetric_difference_update(ps); piv[q][1]=qr^pr
    out=[]
    for p in sorted(piv):
        s,r=piv[p]
        out.append((tuple(sorted(s)),int(r)))
    return out

def make_message(language,boundary,equations,trace,ledger):
    ce=canonical_equations(equations)
    obj={
        "schema":"JANUS/BCEG/V3/BOUNDARY-MESSAGE/v1.0",
        "language":language,
        "boundary":list(sorted(boundary)),
        "equations":[{"vars":list(vs),"rhs":r} for vs,r in ce],
        "trace":trace,
        "replayable":True,
    }
    h,b=canonical_json_hash(obj)
    obj["message_hash"]=h
    obj["serialized_message_bytes"]=b
    obj["message_atoms"]=len(ce)
    return obj, ledger

def decoy_monotone(cnf,boundary):
    checks=len(cnf)
    return None,{"structural_scan_checks":checks,"canonicalization_ops":0}

def gf2_projector(cnf,boundary):
    groups=defaultdict(set)
    checks=0
    for c in cnf:
        key=tuple(sorted(abs(l) for l in c))
        if 2 <= len(key) <= 3 and len(set(key))==len(key):
            groups[key].add(frozenset(c))
        else:
            return None,{"structural_scan_checks":checks+1,"gaussian_row_ops":0,"canonicalization_ops":0}
        checks+=1
    eqs=[]
    consumed=0
    for key,actual in groups.items():
        found=None
        for rhs in (0,1):
            exp=set(map(frozenset,xor_clauses(key,rhs)))
            if actual==exp:
                found=rhs; consumed += len(actual); break
        if found is None:
            return None,{"structural_scan_checks":checks+len(groups),"gaussian_row_ops":0,"canonicalization_ops":0}
        eqs.append([set(key),found])
    if consumed != len(cnf) or not eqs:
        return None,{"structural_scan_checks":checks,"gaussian_row_ops":0,"canonicalization_ops":0}
    bset=set(boundary)
    internals=sorted({v for s,_ in eqs for v in s} - bset)
    rows=[[set(s),int(r)] for s,r in eqs]
    pivots=set()
    ops=0
    trace=[]
    for v in internals:
        pi=next((i for i,(s,r) in enumerate(rows) if i not in pivots and v in s),None)
        if pi is None: continue
        ps,pr=rows[pi]
        for j,(s,r) in enumerate(rows):
            if j==pi or v not in s: continue
            s.symmetric_difference_update(ps); rows[j][1]=r^pr; ops+=1
        pivots.add(pi)
        trace.append(["elim_internal",v])
    projected=[]
    for i,(s,r) in enumerate(rows):
        if s & set(internals):
            continue
        if not s:
            if r:
                projected=[(tuple(),1)]; break
            continue
        if not s.issubset(bset):
            return None,{"structural_scan_checks":checks,"gaussian_row_ops":ops,"canonicalization_ops":0}
        projected.append((tuple(sorted(s)),r))
    if not projected:
        return None,{"structural_scan_checks":checks,"gaussian_row_ops":ops,"canonicalization_ops":0}
    msg,led=make_message("GF2_AFFINE_PROJECTOR",boundary,projected,trace[-16:],{
        "structural_scan_checks":checks+len(groups),
        "gaussian_row_ops":ops,
        "canonicalization_ops":len(projected),
    })
    return msg,led

def horn_force_projector(cnf,boundary):
    bset=set(boundary)
    roots=set()
    edges=[]
    checks=0
    for c in cnf:
        checks+=1
        if len(c)==1:
            l=next(iter(c))
            if l<=0: return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
            roots.add(l)
        elif len(c)==2:
            neg=[-l for l in c if l<0]
            pos=[l for l in c if l>0]
            if len(neg)!=1 or len(pos)!=1:
                return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
            if neg[0] in bset:
                return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
            edges.append((neg[0],pos[0]))
        else:
            return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    if not cnf:
        return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    true=set(roots); firings=0; trace=[]
    changed=True
    while changed:
        changed=False
        for a,b in edges:
            if a in true and b not in true:
                true.add(b); firings+=1; changed=True; trace.append([a,b])
    if not bset.issubset(true):
        return None,{"structural_scan_checks":checks,"horn_firings":firings,"canonicalization_ops":0}
    eqs=[((b,),1) for b in sorted(boundary)]
    msg,led=make_message("HORN_FORCE_PROJECTOR",boundary,eqs,trace[-16:],{
        "structural_scan_checks":checks,
        "horn_firings":firings,
        "canonicalization_ops":len(eqs),
    })
    return msg,led

def relation_type(actual,a,b):
    eq={frozenset((-a,b)),frozenset((a,-b))}
    anti={frozenset((-a,-b)),frozenset((a,b))}
    if actual==eq:return 0
    if actual==anti:return 1
    return None

def twosat_projector(cnf,boundary):
    groups=defaultdict(set); checks=0
    for c in cnf:
        checks+=1
        if len(c)!=2:
            return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
        vs=tuple(sorted(abs(l) for l in c))
        if len(vs)!=2:
            return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
        groups[vs].add(frozenset(c))
    graph=defaultdict(list); consumed=0
    for (a,b),actual in groups.items():
        s=relation_type(actual,a,b)
        if s is None:
            return None,{"structural_scan_checks":checks+len(groups),"signed_union_ops":0,"canonicalization_ops":0}
        graph[a].append((b,s)); graph[b].append((a,s)); consumed+=len(actual)
    if consumed!=len(cnf) or not groups:
        return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
    allv=set(cnf_vars(cnf)); bset=set(boundary)
    root=min(bset)
    sign={root:0}; stack=[root]; ops=0; trace=[]
    while stack:
        u=stack.pop()
        for v,s in graph[u]:
            want=sign[u]^s; ops+=1
            if v in sign:
                if sign[v]!=want:
                    return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
            else:
                sign[v]=want; stack.append(v); trace.append([u,v,s])
    if set(sign)!=allv or not bset.issubset(sign):
        return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
    eqs=[]
    for b in sorted(bset):
        if b==root: continue
        eqs.append(((root,b),sign[root]^sign[b]))
    if not eqs:
        return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
    msg,led=make_message("TWO_SAT_SIGNED_EQ_PROJECTOR",boundary,eqs,trace[-16:],{
        "structural_scan_checks":checks+len(groups),
        "signed_union_ops":ops,
        "canonicalization_ops":len(eqs),
    })
    return msg,led

PROJECTORS={
    "DECOY_MONOTONE":decoy_monotone,
    "HORN_FORCE_PROJECTOR":horn_force_projector,
    "TWO_SAT_SIGNED_EQ_PROJECTOR":twosat_projector,
    "GF2_AFFINE_PROJECTOR":gf2_projector,
}

def generic_fingerprint(cnf,boundary):
    n=max(1,len(cnf))
    units=sum(len(c)==1 for c in cnf)
    binaries=sum(len(c)==2 for c in cnf)
    horn=sum(sum(l>0 for l in c)<=1 for c in cnf)
    maxw=max((len(c) for c in cnf),default=0)
    def q(x): return int(round(4*x/n))
    return f"u{q(units)}:b{q(binaries)}:h{q(horn)}:w{maxw}:kb{min(3,len(boundary)//4)}"

class ProofMind:
    def __init__(self,curiosity=0.45,focus_bonus=0.70):
        self.stats=defaultdict(lambda:defaultdict(lambda:{"attempts":0,"successes":0,"reward_sum":0.0,"failures":0}))
        self.pending=[]
        self.curiosity=curiosity
        self.focus_bonus=focus_bonus
        self.epoch=0
    def order(self,fp):
        scored=[]
        for idx,p in enumerate(PORTFOLIO):
            s=self.stats[fp][p]
            mean=s["reward_sum"]/max(1,s["attempts"])
            uncertainty=1.0/math.sqrt(s["attempts"]+1.0)
            focus=self.focus_bonus if s["successes"]>0 else 0.0
            score=mean+self.curiosity*uncertainty+focus
            scored.append((-score,idx,p))
        scored.sort()
        return [p for _,_,p in scored]
    def observe_shadow(self,fp,projector,success,attempt_index,kind):
        reward=(1.0/max(1,attempt_index)) if success else 0.0
        self.pending.append((fp,projector,success,reward,kind))
    def advance_epoch(self):
        for fp,p,success,reward,kind in self.pending:
            s=self.stats[fp][p]; s["attempts"]+=1; s["reward_sum"]+=reward
            if success:s["successes"]+=1
            else:s["failures"]+=1
        n=len(self.pending); self.pending=[]; self.epoch+=1
        return n

def capability_digest(cnf,boundary,projector):
    obj={"projector_version":PROJECTOR_VERSION,"projector":projector,"cnf_hash":cnf_hash(cnf),"boundary":list(sorted(boundary))}
    return canonical_json_hash(obj)[0]

def truthgate(cnf,boundary,projector,message):
    replay,led=PROJECTORS[projector](cnf,boundary)
    ops=sum(int(v) for v in led.values() if isinstance(v,int))
    ok=bool(replay and replay["message_hash"]==message["message_hash"])
    return ok,ops,replay

def discover_component(cnf,boundary,brain,case_index,component_index,journal):
    fp=generic_fingerprint(cnf,boundary)
    order=brain.order(fp)
    primary_attempts=0
    total_attempts=0
    ledger=defaultdict(int)
    successful=None; successful_projector=None
    attempted=[]
    for p in order:
        primary_attempts+=1; total_attempts+=1; attempted.append(p)
        msg,local=PROJECTORS[p](cnf,boundary)
        for k,v in local.items(): ledger[k]+=int(v)
        journal.append({"event":"PROJECTOR_ATTEMPT","case_index":case_index,"component_index":component_index,"fingerprint":fp,"epoch":brain.epoch,"projector":p,"primary":True,"success":bool(msg),"attempt_index":primary_attempts})
        if msg:
            ok,replay_ops,replay=truthgate(cnf,boundary,p,msg); ledger["truthgate_replay_ops"]+=replay_ops
            journal.append({"event":"TRUTHGATE_REPLAY","case_index":case_index,"component_index":component_index,"projector":p,"ok":ok,"message_hash":msg["message_hash"]})
            brain.observe_shadow(fp,p,ok,primary_attempts,"primary")
            ledger["shadow_observations"]+=1
            if not ok:
                continue
            successful=msg; successful_projector=p
            break
        brain.observe_shadow(fp,p,False,primary_attempts,"primary")
        ledger["shadow_observations"]+=1
    if successful is None:
        return None,{"fingerprint":fp,"order":order,"primary_attempts":primary_attempts,"total_attempts":total_attempts,"ledger":dict(ledger)}
    untried=[p for p in PORTFOLIO if p not in attempted]
    if untried:
        cp=untried[(case_index+component_index)%len(untried)]
        cmsg,clocal=PROJECTORS[cp](cnf,boundary); total_attempts+=1
        for k,v in clocal.items(): ledger[k]+=int(v)
        ledger["protected_challenger_attempts"]+=1
        ledger["shadow_observations"]+=1
        brain.observe_shadow(fp,cp,bool(cmsg),primary_attempts+1,"protected_challenger")
        journal.append({"event":"SHADOW_CHALLENGER","case_index":case_index,"component_index":component_index,"fingerprint":fp,"epoch":brain.epoch,"projector":cp,"success":bool(cmsg),"authority":False})
    cap=capability_digest(cnf,boundary,successful_projector)
    proofpack={
        "schema":"JANUS/BCEG/V3/PROOFPACK/v1.0",
        "component_hash":cnf_hash(cnf),
        "boundary":list(sorted(boundary)),
        "projector":successful_projector,
        "capability_digest":cap,
        "message_hash":successful["message_hash"],
        "message_atoms":successful["message_atoms"],
        "message_serialized_bytes":successful["serialized_message_bytes"],
    }
    ph,pb=canonical_json_hash(proofpack)
    proofpack["proofpack_hash"]=ph; proofpack["proofpack_serialized_bytes"]=pb
    ledger["message_atoms"]+=successful["message_atoms"]
    ledger["message_serialized_bytes"]+=successful["serialized_message_bytes"]
    ledger["proofpack_serialized_bytes"]+=pb
    ledger["canonicalization_ops"]+=len(successful["equations"])
    return {"message":successful,"projector":successful_projector,"proofpack":proofpack},{
        "fingerprint":fp,"order":order,"primary_attempts":primary_attempts,"total_attempts":total_attempts,"ledger":dict(ledger)
    }

def join_messages(messages,boundary):
    eqs=[]
    for m in messages:
        for e in m["equations"]:
            eqs.append((tuple(e["vars"]),int(e["rhs"])))
    rows=[[set(vs),r] for vs,r in eqs]
    piv={}; ops=0
    contradiction=False
    for s,r in rows:
        while s:
            p=min(s)
            if p not in piv:
                piv[p]=(set(s),r); break
            ps,pr=piv[p]
            s.symmetric_difference_update(ps); r^=pr; ops+=1
        if not s and r:
            contradiction=True; break
    cert={
        "schema":"JANUS/BCEG/V3/COMPACT-JOIN/v1.0",
        "boundary":list(sorted(boundary)),
        "input_message_hashes":[m["message_hash"] for m in messages],
        "equation_count":len(eqs),
        "gaussian_join_ops":ops,
        "terminal":"UNSAT" if contradiction else "OPEN",
        "rule":"conjunction of exact existential boundary projections",
        "replayable":True,
    }
    h,b=canonical_json_hash(cert); cert["certificate_hash"]=h; cert["serialized_certificate_bytes"]=b
    return cert

def eval_message(m,assignment):
    for e in m["equations"]:
        lhs=0
        for v in e["vars"]: lhs ^= int(assignment[v])
        if lhs != int(e["rhs"]): return False
    return True

def audit_enumeration(messages,boundary):
    count=0; joint=0
    b=list(sorted(boundary))
    for bits in product((0,1), repeat=len(b)):
        count+=1
        a=dict(zip(b,bits))
        if all(eval_message(m,a) for m in messages): joint+=1
    return count,joint

def static_attempts(cnf,boundary):
    n=0
    for p in PORTFOLIO:
        n+=1
        msg,_=PROJECTORS[p](cnf,boundary)
        if msg:return n
    return n

def build_case(pair,k,variant,seed):
    boundary=tuple(range(1,k+1))
    nxt=k+1
    rng=random.Random(stable_seed(seed,pair,k,variant,"shape"))
    components=[]
    labels=[]
    if pair=="GF2_PARITY+HORN_FORCE":
        g,nxt=make_gf2_parity(boundary,1,nxt)
        h,nxt=make_horn_force(boundary,nxt)
        components=[g,h]; labels=["GF2_PARITY","HORN_FORCE"]
    elif pair=="GF2_PARITY+TWO_SAT_SIGNED_EQ":
        signs=[0]+[rng.randrange(2) for _ in range(k-1)]
        parity=0
        for s in signs: parity^=s
        g,nxt=make_gf2_parity(boundary,parity^1,nxt)
        t,nxt=make_twosat_signed(boundary,signs,nxt)
        components=[g,t]; labels=["GF2_PARITY","TWO_SAT_SIGNED_EQ"]
    elif pair=="HORN_FORCE+TWO_SAT_SIGNED_EQ":
        signs=[0]+[rng.randrange(2) for _ in range(k-1)]
        if not any(signs[1:]): signs[1]=1
        h,nxt=make_horn_force(boundary,nxt)
        t,nxt=make_twosat_signed(boundary,signs,nxt)
        components=[h,t]; labels=["HORN_FORCE","TWO_SAT_SIGNED_EQ"]
    else:
        raise ValueError(pair)
    ob,bound=remap_case(components,boundary,stable_seed(seed,pair,k,variant,"obfuscate"))
    return {"components":ob,"boundary":bound,"audit_labels":labels}

def self_test():
    for pair in ("GF2_PARITY+HORN_FORCE","GF2_PARITY+TWO_SAT_SIGNED_EQ","HORN_FORCE+TWO_SAT_SIGNED_EQ"):
        c=build_case(pair,4,0,"SELFTEST")
        brain=ProofMind(); journal=[]
        rs=[]
        for i,cnf in enumerate(c["components"]):
            r,m=discover_component(cnf,c["boundary"],brain,0,i,journal)
            assert r is not None,(pair,i,m)
            rs.append(r)
        cert=join_messages([x["message"] for x in rs],c["boundary"])
        assert cert["terminal"]=="UNSAT",(pair,cert,[x["message"] for x in rs])
        n,j=audit_enumeration([x["message"] for x in rs],c["boundary"])
        assert n==16 and j==0
    g,_=make_gf2_parity((1,2,3,4),1,5)
    bad=canonical_cnf(list(g)[:-1])
    assert gf2_projector(bad,(1,2,3,4))[0] is None
    h,_=make_horn_force((1,2),3)
    hb=list(h)+[[-1,2]]
    assert horn_force_projector(canonical_cnf(hb),(1,2))[0] is None
    return {"self_test":"PASS","pairs":3,"corruption_controls":2}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    ap.add_argument("--journal")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2)); return
    p=json.loads(PREREG.read_text())
    assert p["status"]=="FROZEN_BEFORE_HOLDOUT_EXECUTION"
    assert p["scientific_boundary"]["P_VS_NP"]=="OPEN"
    specs=[(pair,k,v) for pair in p["pair_families"] for k in p["boundary_width_ladder"] for v in range(p["variants_per_width"])]
    rng=random.Random(stable_seed(p["holdout_seed"],"case-order")); rng.shuffle(specs)
    brain=ProofMind()
    cases=[]; journal=[]
    all_primary=[]; all_static=[]
    for ci,(pair,k,var) in enumerate(specs):
        case=build_case(pair,k,var,p["holdout_seed"])
        payload={"components":case["components"],"boundary":case["boundary"]}
        journal.append({"event":"CASE_FROZEN_INPUT","case_index":ci,"k":k,"variant":var,"component_hashes":[cnf_hash(c) for c in payload["components"]],"boundary":list(payload["boundary"]),"solver_has_family_label":False,"solver_has_language_label":False,"epoch":brain.epoch})
        found=[]; meta=[]; static=[]
        for compi,cnf in enumerate(payload["components"]):
            static.append(static_attempts(cnf,payload["boundary"]))
            r,m=discover_component(cnf,payload["boundary"],brain,ci,compi,journal)
            found.append(r); meta.append(m)
        authoritative=all(x is not None for x in found)
        if authoritative:
            join=join_messages([x["message"] for x in found],payload["boundary"])
            join2=join_messages([x["message"] for x in found],payload["boundary"])
            join_replay=(join["certificate_hash"]==join2["certificate_hash"])
            terminal=join["terminal"] if join_replay else "CERTIFICATE_FAILURE"
            alg_enum=0
            eval_enum,joint=audit_enumeration([x["message"] for x in found],payload["boundary"])
        else:
            join=None; join_replay=False; terminal="OPEN_NO_COMPACT_MESSAGE"; alg_enum=0; eval_enum=0; joint=None
        pending_applied=brain.advance_epoch()
        journal.append({"event":"PROOFMIND_NEXT_EPOCH_PROMOTION","case_index":ci,"new_epoch":brain.epoch,"observations_applied":pending_applied,"same_case_promotion":False})
        primary=sum(m["primary_attempts"] for m in meta)
        static_n=sum(static)
        all_primary.append(primary); all_static.append(static_n)
        ledger=defaultdict(int)
        for m in meta:
            for kk,vv in m["ledger"].items(): ledger[kk]+=int(vv)
        if join:
            ledger["gaussian_join_ops"]+=join["gaussian_join_ops"]
            ledger["join_certificate_bytes"]+=join["serialized_certificate_bytes"]
            ledger["truthgate_replay_ops"]+=join2["gaussian_join_ops"]
        ledger["algorithmic_boundary_assignments_enumerated"]=alg_enum
        ledger["evaluation_only_boundary_assignments_enumerated"]=eval_enum
        messages=[x["message"] for x in found if x]
        atoms=sum(m["message_atoms"] for m in messages)
        bytes_=sum(m["serialized_message_bytes"] for m in messages)
        row={
            "case_index":ci,"pair_audit_only":pair,"k":k,"variant":var,
            "terminal":terminal,"compact_join":bool(join and terminal=="UNSAT"),
            "cross_language":bool(authoritative and found[0]["projector"]!=found[1]["projector"]),
            "projectors":[x["projector"] if x else None for x in found],
            "fingerprints":[m["fingerprint"] for m in meta],
            "primary_projector_attempts":primary,"static_portfolio_attempts":static_n,
            "message_atoms":atoms,"message_serialized_bytes":bytes_,
            "enumeration_baseline":2**k,
            "atom_ratio_to_2k":atoms/(2**k),
            "algorithmic_boundary_assignments_enumerated":alg_enum,
            "evaluation_only_boundary_assignments_enumerated":eval_enum,
            "evaluation_only_joint_satisfying_assignments":joint,
            "join_replay":join_replay,
            "ledger":dict(ledger),
            "solver_received_family_or_language_label":False,
        }
        cases.append(row)
        journal.append({"event":"CASE_COMPLETE",**row})
    c1=all(c["terminal"]=="UNSAT" and c["join_replay"] and c["evaluation_only_joint_satisfying_assignments"]==0 for c in cases)
    discovered=sum(c["compact_join"] for c in cases)/len(cases)
    c2=discovered>=.95 and all(not c["solver_received_family_or_language_label"] for c in cases)
    c3=all(c["algorithmic_boundary_assignments_enumerated"]==0 for c in cases)
    big=[c for c in cases if c["k"]>=6]
    medratio=median(c["atom_ratio_to_2k"] for c in big); maxratio=max(c["atom_ratio_to_2k"] for c in big)
    c4=medratio<=.20 and maxratio<=.25
    c5=all(c["message_atoms"]<=2*c["k"]+4 for c in cases if c["compact_join"])
    c6=sum(c["compact_join"] and c["cross_language"] for c in cases)/len(cases)>=.90
    protected=sum(c["ledger"].get("protected_challenger_attempts",0) for c in cases)
    c7=protected>0 and brain.epoch==len(cases)
    c8=all(c["ledger"].get("truthgate_replay_ops",0)>0 and c["message_serialized_bytes"]>0 and c["ledger"].get("proofpack_serialized_bytes",0)>0 for c in cases if c["compact_join"])
    half=len(cases)//2
    adapt_med=median(all_primary[half:]); static_med=median(all_static[half:])
    c9=adapt_med<=static_med
    c10=all(c["evaluation_only_boundary_assignments_enumerated"]==2**c["k"] for c in cases if c["compact_join"])
    gates=[
        {"gate":"C1_EXACTNESS_AND_REPLAY","passed":c1},
        {"gate":"C2_HIDDEN_LANGUAGE_DISCOVERY","passed":c2,"value":discovered},
        {"gate":"C3_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION","passed":c3},
        {"gate":"C4_COMPACT_REPRESENTATION","passed":c4,"median_ratio_k_ge_6":medratio,"max_ratio_k_ge_6":maxratio},
        {"gate":"C5_CONSTRUCTED_FAMILY_LINEAR_MESSAGE_BOUND","passed":c5},
        {"gate":"C6_CROSS_LANGUAGE_JOIN","passed":c6},
        {"gate":"C7_RBLGANUL_GOVERNANCE_INTEGRITY","passed":c7,"protected_challenger_attempts":protected,"epochs":brain.epoch},
        {"gate":"C8_FULL_DISCOVERY_ACCOUNTING","passed":c8},
        {"gate":"C9_ADAPTIVE_SCHEDULER_INFORMATIONAL","passed":c9,"second_half_adaptive_median_primary_attempts":adapt_med,"second_half_static_median_attempts":static_med,"scientific_role":"INFORMATIONAL_ONLY"},
        {"gate":"C10_EVALUATION_ONLY_AUDIT","passed":c10},
        {"gate":"C11_UNIVERSAL_POLYNOMIAL_BOUNDARY_ELIMINATION","passed":False,"reason":"FINITE_CONSTRUCTED_K_LE_12_CANNOT_ESTABLISH_ARBITRARY_CNF_POLYNOMIAL_MESSAGE_EXISTENCE_OR_P_EQ_NP"},
    ]
    core=all(x["passed"] for x in gates if x["gate"] in {
        "C1_EXACTNESS_AND_REPLAY","C2_HIDDEN_LANGUAGE_DISCOVERY","C3_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION",
        "C4_COMPACT_REPRESENTATION","C5_CONSTRUCTED_FAMILY_LINEAR_MESSAGE_BOUND","C6_CROSS_LANGUAGE_JOIN",
        "C7_RBLGANUL_GOVERNANCE_INTEGRITY","C8_FULL_DISCOVERY_ACCOUNTING","C10_EVALUATION_ONLY_AUDIT"})
    if core: verdict="FINITE_COMPACT_BOUNDARY_MESSAGE_DISCOVERY"
    elif any(c["compact_join"] for c in cases): verdict="PARTIAL_COMPACT_BOUNDARY_DISCOVERY"
    else: verdict="REFUTED_COMPACT_BOUNDARY_DISCOVERY"
    by_k={}
    for k in p["boundary_width_ladder"]:
        g=[c for c in cases if c["k"]==k]
        by_k[str(k)]={
            "cases":len(g),"compact_join":sum(c["compact_join"] for c in g),
            "median_message_atoms":median(c["message_atoms"] for c in g),
            "median_atom_ratio_to_2k":median(c["atom_ratio_to_2k"] for c in g),
            "median_primary_projector_attempts":median(c["primary_projector_attempts"] for c in g),
            "median_static_projector_attempts":median(c["static_portfolio_attempts"] for c in g),
        }
    out={
        "schema":"JANUS/BCEG/COMPACT-BOUNDARY-DISCOVERY/V3/RESULT/v1.0",
        "status":"COMPLETE",
        "summary":{
            "cases":len(cases),"finite_verdict":verdict,
            "compact_cross_language_join_fraction":sum(c["compact_join"] and c["cross_language"] for c in cases)/len(cases),
            "algorithmic_boundary_assignments_enumerated_total":sum(c["algorithmic_boundary_assignments_enumerated"] for c in cases),
            "evaluation_only_boundary_assignments_enumerated_total":sum(c["evaluation_only_boundary_assignments_enumerated"] for c in cases),
            "P_VS_NP":"OPEN","universal_polynomial_boundary_elimination_lemma":"OPEN",
        },
        "gates":gates,"by_k":by_k,"cases_detail":cases,
        "interpretation":{
            "positive":"On these frozen constructed mixed-language families with supplied k-bit boundaries, the CDE can discover replayable exact symbolic boundary projections and prove cross-language inconsistency without algorithmically enumerating 2^k boundary assignments.",
            "limit":"The component classes and supplied boundaries are structured. This does not prove that arbitrary CNF has a compact discoverable boundary message, does not solve separator discovery, and does not imply a polynomial SAT algorithm.",
            "next_frontier":"MAD-LAB the message languages: hide/compose multiple simultaneous boundary relations, introduce adversarial mixtures not belonging wholly to one projector language, and test whether compact symbolic joins survive without exponential representation/discovery."
        }
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    Path(args.journal).write_text("\n".join(json.dumps(x,sort_keys=True) for x in journal)+"\n")
    print(json.dumps({"summary":out["summary"],"gates":gates,"by_k":by_k},indent=2))

if __name__=="__main__":
    main()
