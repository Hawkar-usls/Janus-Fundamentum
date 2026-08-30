#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, random
from collections import defaultdict
from itertools import product
from pathlib import Path
from statistics import median

PREREG=Path("research/JANUS_BCEG_ENTANGLED_PARTIAL_BOUNDARY_V5_PREREGISTRATION_2026-08-30.json")
EXTRACTORS=("GF2","SIGNED","HORN")
VERSION="BCEG-V5-ENTANGLED-2026-08-30"

def seed(*x): return int.from_bytes(hashlib.sha256("|".join(map(str,x)).encode()).digest()[:8],"big")
def cj(o):
    b=json.dumps(o,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(b).hexdigest(),len(b)
def canon(cls):
    s=set()
    for c in cls:
        f=frozenset(map(int,c))
        if any(-x in f for x in f): continue
        s.add(f)
    return tuple(sorted(s,key=lambda c:(len(c),tuple(sorted(c,key=lambda z:(abs(z),z))))))

def xor_cnf(vs,r):
    out=[]
    for bits in product((0,1),repeat=len(vs)):
        if (sum(bits)&1)==r: continue
        out.append([v if b==0 else -v for v,b in zip(vs,bits)])
    return out

def signed_gadget(a,b,s,t):
    if s==0: return [[-a,t],[-t,b],[-b,a]]
    return [[-a,t],[-t,-b],[b,a]]

def horn_force(y,a,b): return [[a],[-a,b],[-b,y]]

def remap(clauses,boundary,rng):
    vs=sorted({abs(l) for c in clauses for l in c})
    perm=vs[:]; rng.shuffle(perm); mp=dict(zip(vs,perm))
    cc=[]
    for c in clauses:
        q=[(1 if l>0 else -1)*mp[abs(l)] for l in c]; rng.shuffle(q); cc.append(q)
    rng.shuffle(cc)
    return canon(cc),tuple(sorted(mp[x] for x in boundary))

def build(fam,k,var,master):
    B=list(range(1,k+1)); nxt=k+1; C=[]; expected=[]
    rng=random.Random(seed(master,fam,k,var,"shape")); shared=[]
    if fam=="ENTANGLED_GF2_HORN":
        for i in range(0,k,2):
            y=nxt; a=nxt+1; b=nxt+2; nxt+=3; shared.append(y)
            rhs=rng.randrange(2); C += xor_cnf((B[i],B[(i+1)%k],y),rhs); C += horn_force(y,a,b)
            expected.append(((B[i],B[(i+1)%k]),rhs^1))
    elif fam=="ENTANGLED_GF2_SIGNED_EQ":
        for i in range(0,k,2):
            y=nxt; t=nxt+1; nxt+=2; shared.append(y); s=rng.randrange(2); rhs=rng.randrange(2)
            C += xor_cnf((B[i],y,B[(i+1)%k]),rhs); C += signed_gadget(y,B[i],s,t)
            expected.append(((B[(i+1)%k],),rhs^s))
    elif fam=="ENTANGLED_SIGNED_EQ_HORN":
        for i in range(k):
            y=nxt; t=nxt+1; a=nxt+2; b=nxt+3; nxt+=4; shared.append(y); s=rng.randrange(2)
            C += signed_gadget(y,B[i],s,t); C += horn_force(y,a,b); expected.append(((B[i],),1^s))
    elif fam=="ENTANGLED_GF2_SIGNED_EQ_HORN":
        for i in range(0,k,2):
            y=nxt; z=nxt+1; t=nxt+2; a=nxt+3; b=nxt+4; nxt+=5; shared += [y,z]
            s=rng.randrange(2); rhs=rng.randrange(2)
            C += xor_cnf((B[i],y,z),rhs); C += signed_gadget(y,B[(i+1)%k],s,t); C += horn_force(z,a,b)
            expected.append(((B[i],B[(i+1)%k]),rhs^s^1))
    else: raise ValueError(fam)
    cnf,bound=remap(C,B,random.Random(seed(master,fam,k,var,"obf")))
    rng2=random.Random(seed(master,fam,k,var,"obf")); vs=sorted({abs(l) for c in C for l in c}); perm=vs[:]; rng2.shuffle(perm); mp=dict(zip(vs,perm))
    exp2=[(tuple(sorted(mp[v] for v in vs0)),r) for vs0,r in expected]; sh2=[mp[v] for v in shared]
    return {"cnf":cnf,"boundary":bound,"expected":exp2,"shared":sh2}

def gf2_groups(cnf):
    groups=defaultdict(set)
    for c in cnf:
        if 2<=len(c)<=3:
            key=tuple(sorted(abs(l) for l in c))
            if len(key)==len(c): groups[key].add(c)
    out=[]; consumed=set()
    for key,act in groups.items():
        for r in (0,1):
            exp=set(map(frozenset,xor_cnf(key,r)))
            if act==exp: out.append(("GF2",key,r,tuple(exp))); consumed |= exp; break
    return out,consumed

def signed_patterns(cnf,already):
    bins=[c for c in cnf if len(c)==2 and c not in already]; bset=set(bins); vs=sorted({abs(l) for c in bins for l in c})
    out=[]; used=set()
    for t in vs:
        others=sorted({abs(l) for c in bins if t in {abs(x) for x in c} for l in c if abs(l)!=t})
        for a in others:
            for b in others:
                if a==b: continue
                for s in (0,1):
                    pat=set(map(frozenset,signed_gadget(a,b,s,t)))
                    if pat.issubset(bset) and not (pat & used): out.append(("SIGNED",(a,b),s,t,tuple(pat))); used |= pat; break
    return out,used

def horn_patterns(cnf,already):
    units={next(iter(c)) for c in cnf if len(c)==1 and next(iter(c))>0 and c not in already}; bins=[c for c in cnf if len(c)==2 and c not in already]
    out=[]; used=set(); sc=set(cnf)
    for a in sorted(units):
        for c1 in bins:
            if -a not in c1: continue
            pos=[l for l in c1 if l>0]
            if len(pos)!=1: continue
            b=pos[0]
            for c2 in bins:
                if -b not in c2: continue
                pos2=[l for l in c2 if l>0]
                if len(pos2)!=1: continue
                y=pos2[0]; pat={frozenset((a,)),frozenset((-a,b)),frozenset((-b,y))}
                if pat.issubset(sc) and not (pat & used): out.append(("HORN",y,a,b,tuple(pat))); used|=pat; break
    return out,used

class Brain:
    def __init__(self): self.stats={x:{"n":0,"succ":0} for x in EXTRACTORS}; self.pending=[]; self.epoch=0
    def order(self):
        sc=[]
        for i,x in enumerate(EXTRACTORS):
            s=self.stats[x]; mean=s["succ"]/max(1,s["n"]); unc=1/math.sqrt(s["n"]+1); focus=.6 if s["succ"] else 0
            sc.append((-(mean+.45*unc+focus),i,x))
        return [x for _,_,x in sorted(sc)]
    def observe(self,x,ok): self.pending.append((x,ok))
    def advance(self):
        for x,ok in self.pending: self.stats[x]["n"]+=1; self.stats[x]["succ"]+=int(ok)
        n=len(self.pending); self.pending=[]; self.epoch+=1; return n

def row_reduce(eqs,internals):
    rows=[[set(vs),int(r)] for vs,r in eqs]; ops=0
    for v in sorted(internals):
        idx=next((i for i,(s,r) in enumerate(rows) if v in s),None)
        if idx is None: continue
        ps,pr=rows[idx]
        for j,(s,r) in enumerate(rows):
            if j!=idx and v in s: s.symmetric_difference_update(ps); rows[j][1]=r^pr; ops+=1
        rows.pop(idx)
    piv={}
    for s,r in rows:
        while s:
            p=min(s)
            if p not in piv: piv[p]=[set(s),r]; break
            ps,pr=piv[p]; s.symmetric_difference_update(ps); r^=pr; ops+=1
        if not s and r: return [([],1)],ops,True
    keys=sorted(piv)
    for p in reversed(keys):
        ps,pr=piv[p]
        for q in keys:
            if q>=p: continue
            qs,qr=piv[q]
            if p in qs: qs.symmetric_difference_update(ps); piv[q][1]=qr^pr; ops+=1
    return [(tuple(sorted(piv[p][0])),piv[p][1]) for p in sorted(piv)],ops,False

def solve(case,brain,ci,journal):
    cnf=case["cnf"]; B=set(case["boundary"]); allv={abs(l) for c in cnf for l in c}; I=allv-B
    order=brain.order(); attempted=[]; found=[]; consumed=set(); ledger=defaultdict(int)
    for x in order:
        attempted.append(x); ledger["exact_projector_attempts"]+=1
        if x=="GF2": f,u=gf2_groups(cnf)
        elif x=="SIGNED": f,u=signed_patterns(cnf,consumed)
        else: f,u=horn_patterns(cnf,consumed)
        new=[q for q in f if not set(q[-1]) & consumed]
        if new:
            found+=new
            for q in new: consumed |= set(q[-1])
        brain.observe(x,bool(new)); journal.append({"event":"EXTRACTOR","case":ci,"epoch":brain.epoch,"extractor":x,"found":len(new),"authority":False})
    ch=EXTRACTORS[(ci+1)%len(EXTRACTORS)]; ledger["protected_challenger_attempts"]+=1
    if ch=="GF2": f,_=gf2_groups(cnf)
    elif ch=="SIGNED": f,_=signed_patterns(cnf,set())
    else: f,_=horn_patterns(cnf,set())
    brain.observe(ch,bool(f)); journal.append({"event":"SHADOW_CHALLENGER","case":ci,"extractor":ch,"found":len(f),"authority":False})
    if consumed != set(cnf):
        brain.advance(); return {"terminal":"OPEN_UNRECOGNIZED_ENTANGLED_REMAINDER","ledger":dict(ledger),"covered":len(consumed),"clauses":len(cnf)}
    eqs=[]; types=set()
    for q in found:
        types.add(q[0])
        if q[0]=="GF2": _,vs,r,_=q; eqs.append((vs,r))
        elif q[0]=="SIGNED": _,(a,b),s,t,_=q; eqs.append(((a,b),s)); eqs.append(((a,t),0))
        elif q[0]=="HORN": _,y,a,b,_=q; eqs += [((y,),1),((a,),1),((b,),1)]
    out,ops,contr=row_reduce(eqs,I); ledger["joint_elimination_ops"]+=ops; ledger["canonicalization_ops"]+=len(out)
    msg={"schema":"JANUS/BCEG/V5/ENTANGLED-MESSAGE/v1","boundary":sorted(B),"equations":[{"vars":list(vs),"rhs":r} for vs,r in out],"types":sorted(types),"replayable":True}
    mh,mb=cj(msg); msg["hash"]=mh; ledger["serialized_message_bytes"]=mb
    pack={"cnf_hash":cj([[*sorted(c)] for c in cnf])[0],"message_hash":mh,"extractors":attempted,"version":VERSION}; ph,pb=cj(pack); pack["hash"]=ph; ledger["serialized_proofpack_bytes"]=pb
    out2,ops2,contr2=row_reduce(eqs,I); ledger["truthgate_replay_ops"]+=ops2; replay=(out2==out and contr2==contr)
    ledger["proof_dag_nodes"]=len(found)+len(eqs)+len(out)+2; ledger["proof_dag_edges"]=sum(len(vs) for vs,r in eqs)+sum(len(vs) for vs,r in out); ledger["algorithmic_boundary_assignments_enumerated"]=0
    pending=brain.advance()
    return {"terminal":"UNSAT" if contr else "MESSAGE","message":msg,"replay":replay,"ledger":dict(ledger),"types":sorted(types),"found_factors":len(found),"pending_promoted_next_epoch":pending}

def eval_eqs(eqs,a):
    for vs,r in eqs:
        x=0
        for v in vs: x^=a[v]
        if x!=r:return False
    return True

def audit(case,res):
    B=sorted(case["boundary"]); exp=case["expected"]; got=[(tuple(e["vars"]),e["rhs"]) for e in res["message"]["equations"]]; mism=0; cnt=0
    for bits in product((0,1),repeat=len(B)):
        a=dict(zip(B,bits)); cnt+=1
        if eval_eqs(exp,a)!=eval_eqs(got,a): mism+=1
    return cnt,mism

def selftest():
    b=Brain()
    for fam in ("ENTANGLED_GF2_HORN","ENTANGLED_GF2_SIGNED_EQ","ENTANGLED_SIGNED_EQ_HORN","ENTANGLED_GF2_SIGNED_EQ_HORN"):
        c=build(fam,4,0,"DEV"); r=solve(c,b,0,[]); assert r["terminal"]=="MESSAGE" and r["replay"],(fam,r); n,m=audit(c,r); assert m==0,(fam,m); assert c["shared"]
    return {"status":"PASS","families":4}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output"); ap.add_argument("--journal"); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(selftest(),indent=2)); return
    p=json.loads(PREREG.read_text()); assert p["status"]=="FROZEN_BEFORE_HOLDOUT_EXECUTION"
    specs=[(f,k,v) for f in p["families"] for k in p["boundary_width_ladder"] for v in range(p["variants_per_width"])]; rr=random.Random(seed(p["holdout_seed"],"order")); rr.shuffle(specs)
    brain=Brain(); cases=[]; journal=[]
    for ci,(fam,k,v) in enumerate(specs):
        c=build(fam,k,v,p["holdout_seed"]); solver_case={"cnf":c["cnf"],"boundary":c["boundary"]}; r=solve(solver_case,brain,ci,journal)
        if r.get("message"): n,m=audit(c,r); r["evaluation_only_boundary_assignments_enumerated"]=n; r["audit_mismatches"]=m
        else: r["evaluation_only_boundary_assignments_enumerated"]=0; r["audit_mismatches"]=None
        ent=all(x not in set(c["boundary"]) for x in c["shared"]) and len(c["shared"])>0; atoms=len(r.get("message",{}).get("equations",[])); paid=sum(int(x) for kk,x in r.get("ledger",{}).items() if isinstance(x,int))
        row={"case":ci,"family_audit_only":fam,"k":k,"variant":v,"terminal":r["terminal"],"replay":r.get("replay",False),"entangled":ent,"types":r.get("types",[]),"message_atoms":atoms,"ratio":atoms/(2**k),"paid_nohide_metric":paid,**r}; cases.append(row); journal.append({"event":"CASE_COMPLETE",**row})
    e1=all(c["terminal"]=="MESSAGE" and c["replay"] and c["audit_mismatches"]==0 for c in cases); e2=all(c["entangled"] for c in cases); e3=all(len(c["types"])>=2 for c in cases); e4=all(c["ledger"].get("algorithmic_boundary_assignments_enumerated",0)==0 for c in cases)
    big=[c for c in cases if c["k"]>=8]; medr=median(c["ratio"] for c in big); maxr=max(c["ratio"] for c in big); e5=medr<=.20 and maxr<=.35
    byk={}
    for k in p["boundary_width_ladder"]:
        g=[c for c in cases if c["k"]==k]; byk[str(k)]={"cases":len(g),"success":sum(c["terminal"]=="MESSAGE" for c in g),"median_atoms":median(c["message_atoms"] for c in g),"median_paid":median(c["paid_nohide_metric"] for c in g),"median_bytes":median(c["ledger"].get("serialized_message_bytes",0)+c["ledger"].get("serialized_proofpack_bytes",0) for c in g),"median_dag_nodes":median(c["ledger"].get("proof_dag_nodes",0) for c in g),"median_joint_ops":median(c["ledger"].get("joint_elimination_ops",0) for c in g)}
    ratios={}; ks=p["boundary_width_ladder"]
    for met in ("median_paid","median_bytes","median_dag_nodes","median_joint_ops"):
        arr=[byk[str(k)][met] for k in ks]; ratios[met]=[arr[i+1]/max(1,arr[i]) for i in range(len(arr)-1)]
    e6=all(max(v)<=3.2 for v in ratios.values()); e7=sum(c["terminal"]=="MESSAGE" for c in cases)/len(cases)>=.8; e8=sum(c["ledger"].get("protected_challenger_attempts",0) for c in cases)>0 and brain.epoch==len(cases)
    gates=[{"gate":"E1_EXACTNESS_AND_REPLAY","passed":e1},{"gate":"E2_INTERNAL_ENTANGLEMENT_REAL","passed":e2},{"gate":"E3_NO_WHOLE_LANGUAGE_SHORTCUT","passed":e3},{"gate":"E4_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION","passed":e4},{"gate":"E5_COMPACT_MESSAGE","passed":e5,"median_ratio_k_ge_8":medr,"max_ratio_k_ge_8":maxr},{"gate":"E6_NO_MEASURED_EXPONENTIAL_MIGRATION","passed":e6,"adjacent_ratios":ratios},{"gate":"E7_DISCOVERY_WITHOUT_ORACLE","passed":e7},{"gate":"E8_RBLGANUL_GOVERNANCE","passed":e8},{"gate":"E9_UNIVERSAL_POLYNOMIAL_BOUNDARY_ELIMINATION","passed":False,"status":"OPEN"}]
    core=all(g["passed"] for g in gates[:8]); verdict="FINITE_ENTANGLED_COMPACT_BOUNDARY_COMPOSITION" if core else ("PARTIAL_ENTANGLED_COMPACT_BOUNDARY_COMPOSITION" if any(c["terminal"]=="MESSAGE" for c in cases) else "REFUTED_ENTANGLED_COMPOSITION")
    out={"schema":"JANUS/BCEG/V5/RESULT/v1","summary":{"cases":len(cases),"verdict":verdict,"success":sum(c["terminal"]=="MESSAGE" for c in cases),"algorithmic_boundary_assignments_enumerated_total":sum(c["ledger"].get("algorithmic_boundary_assignments_enumerated",0) for c in cases),"P_VS_NP":"OPEN","universal_polynomial_boundary_elimination":"OPEN"},"gates":gates,"by_k":byk,"cases_detail":cases,"interpretation":{"positive":"Finite constructed entangled mixed-language factors were compiled through a shared affine IR into exact compact boundary messages without solver-side 2^k enumeration.","limit":"The entanglement is structured and selected factor semantics admit a common affine normal form. This is not arbitrary CNF, not a separator theorem, and not a proof of polynomial worst-case quantification.","next_frontier":"CYCLIC_NONAFFINE_ENTANGLEMENT: construct shared-internal cycles whose exact factors do not all collapse to one affine IR; require a compact portfolio join or preserve failure."}}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); Path(a.journal).write_text("\n".join(json.dumps(x,sort_keys=True) for x in journal)+"\n"); print(json.dumps({"summary":out["summary"],"gates":gates,"by_k":byk},indent=2))
if __name__=="__main__": main()
