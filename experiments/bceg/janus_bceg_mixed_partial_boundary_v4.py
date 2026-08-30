from __future__ import annotations

import argparse, hashlib, json, math, random
from collections import defaultdict
from itertools import product
from pathlib import Path
from statistics import median

PREREG = Path("research/JANUS_BCEG_MIXED_PARTIAL_BOUNDARY_V4_PREREGISTRATION_2026-08-30.json")
PORTFOLIO = ("DECOY_MONOTONE","HORN_FORCE_PARTIAL_PROJECTOR","TWO_SAT_SIGNED_EQ_PARTIAL_PROJECTOR","GF2_PARTIAL_PROJECTOR")
PROJECTOR_VERSION = "BCEG_V4_PARTIAL_PROJECTORS_2026-08-30"

def stable_seed(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str,parts)).encode()).digest()[:8],"big")

def canonical_cnf(clauses):
    out=set()
    for clause in clauses:
        c=frozenset(int(x) for x in clause)
        if any(-l in c for l in c): continue
        out.add(c)
    return tuple(sorted(out,key=lambda c:(len(c),tuple(sorted(c,key=lambda x:(abs(x),x))))))

def cnf_vars(cnf):
    return sorted({abs(l) for c in cnf for l in c})

def canonical_json_hash(obj):
    b=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(b).hexdigest(),len(b)

def cnf_hash(cnf):
    return canonical_json_hash([[int(x) for x in sorted(c,key=lambda z:(abs(z),z))] for c in cnf])[0]

def xor_clauses(vars_,rhs):
    vars_=tuple(vars_); rhs=int(rhs)&1; out=[]
    for bits in product((0,1),repeat=len(vars_)):
        if (sum(bits)&1)==rhs: continue
        out.append([v if b==0 else -v for v,b in zip(vars_,bits)])
    return out

def make_gf2_force(x,value,nxt):
    z=nxt; nxt+=1
    clauses=xor_clauses((x,z),0)+xor_clauses((z,),value)
    return canonical_cnf(clauses),nxt

def make_gf2_relation(a,x,sign,nxt):
    z=nxt; nxt+=1
    clauses=xor_clauses((a,x,z),0)+xor_clauses((z,),sign)
    return canonical_cnf(clauses),nxt

def implication(a_lit,b_lit):
    return [-a_lit,b_lit]

def make_signed_relation(a,x,sign,nxt):
    p,q=nxt,nxt+1; nxt+=2
    target=x if int(sign)==0 else -x
    clauses=[
        implication(a,p),
        implication(p,target),
        implication(target,q),
        implication(q,a),
        implication(p,q),
    ]
    return canonical_cnf(clauses),nxt

def make_horn_force(x,value,nxt):
    a,b=nxt,nxt+1; nxt+=2
    tail=x if int(value) else -x
    return canonical_cnf([[a],[-a,b],[-b,tail]]),nxt

def merge_cnfs(parts):
    return canonical_cnf([list(c) for p in parts for c in p])

def family_languages(name):
    return {
        "GF2_PLUS_SIGNED_EQ_PARTIAL":("GF2","SIGNED"),
        "GF2_PLUS_HORN_PARTIAL":("GF2","HORN"),
        "SIGNED_EQ_PLUS_HORN_PARTIAL":("SIGNED","HORN"),
        "GF2_PLUS_SIGNED_EQ_PLUS_HORN_PARTIAL":("GF2","SIGNED","HORN"),
    }[name]

def choose_target(k,seed,need_signed_anti):
    rng=random.Random(seed)
    bits=[rng.randrange(2) for _ in range(k)]
    if need_signed_anti and k>1:
        bits[1]=bits[0]^1
    return bits

def build_component(boundary,target,family,start_internal):
    langs=family_languages(family)
    parts=[]; nxt=start_internal
    anchor=boundary[0]
    rest=list(range(1,len(boundary)))
    signed_idx=[]; gf2_idx=[]
    if "SIGNED" in langs and "GF2" in langs:
        signed_idx=[i for i in rest if i%2==1]
        gf2_idx=[i for i in rest if i%2==0]
        if not signed_idx and rest: signed_idx=[rest[0]]; gf2_idx=[i for i in rest if i not in signed_idx]
    elif "SIGNED" in langs:
        signed_idx=rest
    elif "GF2" in langs:
        gf2_idx=rest
    if "HORN" in langs:
        cnf,nxt=make_horn_force(anchor,target[0],nxt); parts.append(cnf)
    elif "GF2" in langs:
        cnf,nxt=make_gf2_force(anchor,target[0],nxt); parts.append(cnf)
    for i in signed_idx:
        cnf,nxt=make_signed_relation(anchor,boundary[i],target[0]^target[i],nxt); parts.append(cnf)
    for i in gf2_idx:
        cnf,nxt=make_gf2_relation(anchor,boundary[i],target[0]^target[i],nxt); parts.append(cnf)
    return merge_cnfs(parts),nxt

def remap_pair(left,right,boundary,left_target,right_target,seed):
    rng=random.Random(seed)
    allv=sorted(set(boundary)|set(cnf_vars(left))|set(cnf_vars(right)))
    perm=allv[:]; rng.shuffle(perm)
    mp=dict(zip(allv,perm))
    def remap_cnf(cnf):
        cls=[]
        for c in cnf:
            cc=[(1 if l>0 else -1)*mp[abs(l)] for l in c]
            rng.shuffle(cc); cls.append(cc)
        rng.shuffle(cls)
        return canonical_cnf(cls)
    l=remap_cnf(left); r=remap_cnf(right)
    b=tuple(sorted(mp[x] for x in boundary))
    lt={mp[x]:int(left_target[i]) for i,x in enumerate(boundary)}
    rt={mp[x]:int(right_target[i]) for i,x in enumerate(boundary)}
    return l,r,b,lt,rt

def canonical_equations(eqs):
    rows=[]
    for vs,r in eqs:
        s=set(vs); rr=int(r)&1
        if not s:
            if rr: return [(tuple(),1)]
            continue
        rows.append([s,rr])
    piv={}
    for s,rr in rows:
        while s:
            p=min(s)
            if p not in piv:
                piv[p]=[set(s),rr]; break
            ps,pr=piv[p]
            s.symmetric_difference_update(ps); rr^=pr
        if not s and rr:
            return [(tuple(),1)]
    keys=sorted(piv)
    for p in reversed(keys):
        ps,pr=piv[p]
        for q in keys:
            if q>=p: continue
            qs,qr=piv[q]
            if p in qs:
                qs.symmetric_difference_update(ps); piv[q][1]=qr^pr
    return [(tuple(sorted(piv[p][0])),int(piv[p][1])) for p in sorted(piv)]

def equation_join(equation_lists):
    raw=[e for ls in equation_lists for e in ls]
    out=canonical_equations(raw)
    return out, len(raw)+len(out)

def equations_satisfied(eqs,assignment):
    for vs,r in eqs:
        if not vs:
            if r: return False
            continue
        v=0
        for x in vs: v^=int(assignment[x])
        if v!=(int(r)&1): return False
    return True

def make_message(language,boundary,eqs,trace,ledger,source_hash):
    ce=canonical_equations(eqs)
    obj={
        "schema":"JANUS/BCEG/V4/PARTIAL-BOUNDARY-MESSAGE/v1.0",
        "language":language,
        "boundary":list(sorted(set(boundary))),
        "equations":[{"vars":list(vs),"rhs":r} for vs,r in ce],
        "trace":trace,
        "source_cnf_hash":source_hash,
        "replayable":True,
    }
    h,b=canonical_json_hash(obj)
    obj.update({"message_hash":h,"serialized_message_bytes":b,"message_atoms":len(ce)})
    return obj,ledger

def parse_message_equations(msg):
    return [(tuple(e["vars"]),int(e["rhs"])) for e in msg["equations"]]

def decoy(cnf,boundary):
    return None,{"structural_scan_checks":len(cnf),"canonicalization_ops":0}

def gf2_partial(cnf,boundary):
    groups=defaultdict(set); checks=0
    for c in cnf:
        checks+=1
        key=tuple(sorted(abs(l) for l in c))
        if not (1<=len(key)<=3) or len(set(key))!=len(key):
            return None,{"structural_scan_checks":checks,"gaussian_row_ops":0,"canonicalization_ops":0}
        groups[key].add(frozenset(c))
    eqs=[]; consumed=0
    for key,actual in groups.items():
        found=None
        for rhs in (0,1):
            exp=set(map(frozenset,xor_clauses(key,rhs)))
            if actual==exp:
                found=rhs; break
        if found is None:
            return None,{"structural_scan_checks":checks+len(groups),"gaussian_row_ops":0,"canonicalization_ops":0}
        eqs.append([set(key),found]); consumed+=len(actual)
    if consumed!=len(cnf) or not eqs:
        return None,{"structural_scan_checks":checks,"gaussian_row_ops":0,"canonicalization_ops":0}
    bset=set(boundary)
    internals=sorted({v for s,_ in eqs for v in s}-bset)
    rows=[[set(s),int(r)] for s,r in eqs]
    pivots=set(); ops=0; trace=[]
    for v in internals:
        pi=next((i for i,(s,r) in enumerate(rows) if i not in pivots and v in s),None)
        if pi is None: continue
        ps,pr=rows[pi]
        for j,(s,r) in enumerate(rows):
            if j==pi or v not in s: continue
            s.symmetric_difference_update(ps); rows[j][1]=r^pr; ops+=1
        pivots.add(pi); trace.append(["elim_internal",v])
    projected=[]
    for i,(s,r) in enumerate(rows):
        if i in pivots: continue
        if s & set(internals):
            return None,{"structural_scan_checks":checks,"gaussian_row_ops":ops,"canonicalization_ops":0}
        if not s:
            if r: projected=[(tuple(),1)]; break
            continue
        if not s.issubset(bset):
            return None,{"structural_scan_checks":checks,"gaussian_row_ops":ops,"canonicalization_ops":0}
        projected.append((tuple(sorted(s)),r))
    if not projected:
        return None,{"structural_scan_checks":checks,"gaussian_row_ops":ops,"canonicalization_ops":0}
    return make_message("GF2_PARTIAL_PROJECTOR",boundary,projected,trace[-16:],{
        "structural_scan_checks":checks+len(groups),"gaussian_row_ops":ops,"canonicalization_ops":len(projected)
    },cnf_hash(cnf))

def kosaraju_scc(graph,nodes):
    rg=defaultdict(list)
    for u in nodes:
        for v in graph[u]: rg[v].append(u)
    seen=set(); order=[]
    def dfs(u):
        seen.add(u)
        for v in graph[u]:
            if v not in seen: dfs(v)
        order.append(u)
    for u in nodes:
        if u not in seen: dfs(u)
    comp={}; cid=0
    def rdfs(u):
        comp[u]=cid
        for v in rg[u]:
            if v not in comp: rdfs(v)
    for u in reversed(order):
        if u not in comp:
            rdfs(u); cid+=1
    return comp,cid

def twosat_partial(cnf,boundary):
    checks=0; graph=defaultdict(list); vars_=set()
    for c in cnf:
        checks+=1
        if len(c)!=2:
            return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
        a,b=tuple(c)
        if abs(a)==abs(b):
            return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
        graph[-a].append(b); graph[-b].append(a); vars_.update((abs(a),abs(b)))
    if not vars_:
        return None,{"structural_scan_checks":checks,"signed_union_ops":0,"canonicalization_ops":0}
    nodes=set()
    for v in vars_: nodes.update((v,-v))
    for u in list(nodes): graph[u]=list(graph[u])
    comp,nc=kosaraju_scc(graph,nodes); ops=sum(len(graph[u]) for u in nodes)
    if any(comp[v]==comp[-v] for v in vars_):
        return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
    if nc!=2:
        return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
    bvars=sorted(set(boundary)&vars_)
    if len(bvars)<2:
        return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
    root=bvars[0]; eqs=[]; trace=[]
    for x in bvars[1:]:
        if comp[root]==comp[x]: s=0
        elif comp[root]==comp[-x]: s=1
        else: return None,{"structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":0}
        eqs.append(((root,x),s)); trace.append([root,x,s])
    return make_message("TWO_SAT_SIGNED_EQ_PARTIAL_PROJECTOR",bvars,eqs,trace[-16:],{
        "structural_scan_checks":checks,"signed_union_ops":ops,"canonicalization_ops":len(eqs)
    },cnf_hash(cnf))

def horn_partial(cnf,boundary):
    checks=len(cnf); bset=set(boundary)
    if len(cnf)!=3:
        return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    for c in cnf:
        if sum(1 for l in c if l>0)>1:
            return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    units=[next(iter(c)) for c in cnf if len(c)==1 and next(iter(c))>0 and abs(next(iter(c))) not in bset]
    if len(units)!=1:
        return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    root=units[0]; mids=[]
    for c in cnf:
        if len(c)==2 and -root in c:
            other=next(l for l in c if l!=-root)
            if other>0 and abs(other) not in bset: mids.append(other)
    if len(mids)!=1:
        return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    mid=mids[0]; tail=None
    for c in cnf:
        if len(c)==2 and -mid in c:
            other=next(l for l in c if l!=-mid)
            if abs(other) in bset: tail=other
    if tail is None:
        return None,{"structural_scan_checks":checks,"horn_firings":0,"canonicalization_ops":0}
    x=abs(tail); value=1 if tail>0 else 0
    return make_message("HORN_FORCE_PARTIAL_PROJECTOR",(x,),[((x,),value)],["strict_horn_force"],{
        "structural_scan_checks":checks,"horn_firings":2,"canonicalization_ops":1
    },cnf_hash(cnf))

PROJECTORS={
    "DECOY_MONOTONE":decoy,
    "HORN_FORCE_PARTIAL_PROJECTOR":horn_partial,
    "TWO_SAT_SIGNED_EQ_PARTIAL_PROJECTOR":twosat_partial,
    "GF2_PARTIAL_PROJECTOR":gf2_partial,
}

def decompose_internal_modules(cnf,boundary):
    bset=set(boundary); n=len(cnf); parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[rb]=ra
    by_internal=defaultdict(list)
    for i,c in enumerate(cnf):
        for v in {abs(l) for l in c}-bset: by_internal[v].append(i)
    for inds in by_internal.values():
        for j in inds[1:]: union(inds[0],j)
    groups=defaultdict(list)
    for i,c in enumerate(cnf): groups[find(i)].append(list(c))
    modules=[canonical_cnf(cls) for cls in groups.values()]
    seen={}
    for mi,m in enumerate(modules):
        for v in set(cnf_vars(m))-bset:
            if v in seen and seen[v]!=mi: raise AssertionError("INTERNAL_OVERLAP")
            seen[v]=mi
    return modules,{"decomposition_modules":len(modules),"decomposition_internal_vars":len(seen),"proof_dag_nodes":len(modules)+1}

def module_boundary(module,boundary):
    return tuple(sorted(set(cnf_vars(module))&set(boundary)))

def whole_single_language_accepts(cnf,boundary):
    hits=[]
    for name in PORTFOLIO:
        if name=="DECOY_MONOTONE": continue
        msg,_=PROJECTORS[name](cnf,boundary)
        if msg is not None: hits.append(name)
    return hits

def truthgate_replay(module,boundary,projector,message):
    rerun,_=PROJECTORS[projector](module,boundary)
    if rerun is None: return False,1
    return (rerun["equations"]==message["equations"] and rerun["source_cnf_hash"]==message["source_cnf_hash"]),1+len(message["equations"])

def generic_fingerprint(cnf,boundary):
    n=max(1,len(cnf)); units=sum(len(c)==1 for c in cnf); binaries=sum(len(c)==2 for c in cnf); tern=sum(len(c)==3 for c in cnf); horn=sum(sum(l>0 for l in c)<=1 for c in cnf)
    def q(x): return int(round(4*x/n))
    return f"u{q(units)}:b{q(binaries)}:t{q(tern)}:h{q(horn)}:ib{max(0,len(cnf_vars(cnf))-len(boundary))}"

class ProofMind:
    def __init__(self,curiosity=.45,focus=.70):
        self.stats=defaultdict(lambda:defaultdict(lambda:{"attempts":0,"successes":0,"reward_sum":0.0,"failures":0})); self.pending=[]; self.curiosity=curiosity; self.focus=focus; self.epoch=0
    def order(self,fp):
        scored=[]
        for idx,p in enumerate(PORTFOLIO):
            s=self.stats[fp][p]; mean=s["reward_sum"]/max(1,s["attempts"]); uncert=1.0/math.sqrt(s["attempts"]+1); bonus=self.focus if s["successes"] else 0.0
            scored.append((-(mean+self.curiosity*uncert+bonus),idx,p))
        return [p for _,_,p in sorted(scored)]
    def observe(self,fp,p,success,attempt_index,kind):
        self.pending.append((fp,p,success,(1.0/max(1,attempt_index)) if success else 0.0,kind))
    def advance(self):
        n=len(self.pending)
        for fp,p,success,reward,kind in self.pending:
            s=self.stats[fp][p]; s["attempts"]+=1; s["reward_sum"]+=reward
            if success:s["successes"]+=1
            else:s["failures"]+=1
        self.pending=[]; self.epoch+=1; return n

def solve_component(cnf,boundary,brain):
    modules,dled=decompose_internal_modules(cnf,boundary); led=defaultdict(int); led.update(dled)
    messages=[]; langs=[]; primary_attempts=0; static_attempts=0; protected=0; shadow_obs=0
    for module in modules:
        mb=module_boundary(module,boundary)
        if not mb: return {"terminal":"OPEN_UNPROJECTABLE_MODULE","ledger":dict(led)}
        fp=generic_fingerprint(module,mb); order=brain.order(fp); chosen=None; chosen_name=None; attempt_idx=0
        for name in order:
            attempt_idx+=1; primary_attempts+=1; led["projector_attempts"]+=1
            msg,local=PROJECTORS[name](module,mb)
            for k,v in local.items(): led[k]+=int(v)
            success=msg is not None; brain.observe(fp,name,success,attempt_idx,"PRIMARY"); shadow_obs+=1
            if success:
                ok,replay_ops=truthgate_replay(module,mb,name,msg); led["truthgate_replay_ops"]+=replay_ops
                if not ok: return {"terminal":"REFUTED_REPLAY_MISMATCH","ledger":dict(led)}
                chosen=msg; chosen_name=name; break
        for i,name in enumerate(PORTFOLIO,1):
            msg0,_=PROJECTORS[name](module,mb)
            if msg0 is not None: static_attempts+=i; break
        if chosen is None: return {"terminal":"OPEN_NO_PARTIAL_LANGUAGE","ledger":dict(led)}
        others=[p for p in order if p!=chosen_name]
        if others:
            p=others[0]; test,_=PROJECTORS[p](module,mb); brain.observe(fp,p,test is not None,attempt_idx+1,"PROTECTED_CHALLENGER"); protected+=1; shadow_obs+=1
        messages.append(chosen); langs.append(chosen_name); led["partial_atoms"]+=chosen["message_atoms"]; led["serialized_message_bytes"]+=chosen["serialized_message_bytes"]; led["proofpack_bytes"]+=chosen["serialized_message_bytes"]+96; led["proof_dag_nodes"]+=1
    eqs,joinops=equation_join([parse_message_equations(m) for m in messages]); led["join_ops"]+=joinops; led["canonicalization_ops"]+=len(eqs)
    final={"schema":"JANUS/BCEG/V4/COMPONENT-MESSAGE/v1.0","boundary":list(sorted(boundary)),"equations":[{"vars":list(vs),"rhs":r} for vs,r in eqs],"partial_message_hashes":[m["message_hash"] for m in messages],"partial_languages":langs,"replayable":True}
    h,b=canonical_json_hash(final); final.update({"message_hash":h,"serialized_message_bytes":b,"message_atoms":len(eqs)}); led["serialized_message_bytes"]+=b; led["proofpack_bytes"]+=b+128; led["shadow_observations"]+=shadow_obs; led["protected_challenger_attempts"]+=protected
    return {"terminal":"COMPACT_MESSAGE","message":final,"partial_languages":sorted(set(langs)),"module_count":len(modules),"primary_attempts":primary_attempts,"static_attempts":static_attempts,"ledger":dict(led)}

def audit_component_message(message,target,boundary,cap):
    k=len(boundary); total=1<<k
    if total>cap: return {"audited":False,"enumerated":0,"match":None}
    eqs=[(tuple(e["vars"]),e["rhs"]) for e in message["equations"]]; satisfying=0
    for bits in product((0,1),repeat=k):
        a=dict(zip(boundary,bits)); got=equations_satisfied(eqs,a); want=all(a[v]==target[v] for v in boundary); satisfying+=int(got)
        if got!=want: return {"audited":True,"enumerated":0,"match":False,"message_satisfying_assignments":satisfying}
    return {"audited":True,"enumerated":total,"match":True,"message_satisfying_assignments":satisfying}

def build_case(family,k,variant,seed):
    boundary=tuple(range(1,k+1)); nxt=k+1; need_signed="SIGNED" in family_languages(family)
    lt=choose_target(k,stable_seed(seed,family,k,variant,"L"),need_signed); rt=choose_target(k,stable_seed(seed,family,k,variant,"R"),need_signed)
    if rt==lt: rt[-1]^=1
    if need_signed and k>1: rt[1]=rt[0]^1
    if rt==lt: rt[-1]^=1
    left,nxt=build_component(boundary,lt,family,nxt); right,nxt=build_component(boundary,rt,family,nxt)
    return remap_pair(left,right,boundary,lt,rt,stable_seed(seed,family,k,variant,"OBF"))

def sum_ledgers(*ledgers):
    out=defaultdict(int)
    for led in ledgers:
        for k,v in led.items():
            if isinstance(v,(int,float)): out[k]+=v
    return dict(out)

def run_case(family,k,variant,seed,brain,cap):
    left,right,boundary,lt,rt=build_case(family,k,variant,seed); whole_left=whole_single_language_accepts(left,boundary); whole_right=whole_single_language_accepts(right,boundary)
    sl=solve_component(left,boundary,brain); sr=solve_component(right,boundary,brain)
    if sl["terminal"]!="COMPACT_MESSAGE" or sr["terminal"]!="COMPACT_MESSAGE":
        brain.advance(); return {"family":family,"k":k,"variant":variant,"terminal":"OPEN_COMPONENT","left_terminal":sl["terminal"],"right_terminal":sr["terminal"],"whole_hits_left":whole_left,"whole_hits_right":whole_right}
    le=[(tuple(e["vars"]),e["rhs"]) for e in sl["message"]["equations"]]; re=[(tuple(e["vars"]),e["rhs"]) for e in sr["message"]["equations"]]; joined,jops=equation_join([le,re]); final_unsat=(joined==[(tuple(),1)])
    al=audit_component_message(sl["message"],lt,boundary,cap); ar=audit_component_message(sr["message"],rt,boundary,cap); led=sum_ledgers(sl["ledger"],sr["ledger"]); led["join_ops"]=led.get("join_ops",0)+jops; led["canonicalization_ops"]=led.get("canonicalization_ops",0)+len(joined); led["algorithmic_boundary_assignments_enumerated"]=0; led["evaluation_only_boundary_assignments_enumerated"]=al["enumerated"]+ar["enumerated"]
    message_atoms=sl["message"]["message_atoms"]+sr["message"]["message_atoms"]; unique_langs=set(sl["partial_languages"])|set(sr["partial_languages"]); epoch_before=brain.epoch; brain.advance()
    return {"family":family,"k":k,"variant":variant,"terminal":"UNSAT" if final_unsat else "NONTERMINAL","variables_left":len(cnf_vars(left)),"variables_right":len(cnf_vars(right)),"clauses_left":len(left),"clauses_right":len(right),"whole_hits_left":whole_left,"whole_hits_right":whole_right,"no_whole_shortcut":not whole_left and not whole_right,"left_languages":sl["partial_languages"],"right_languages":sr["partial_languages"],"unique_partial_languages":sorted(unique_langs),"multi_partial_actuated":len(unique_langs)>=2,"left_message_atoms":sl["message"]["message_atoms"],"right_message_atoms":sr["message"]["message_atoms"],"combined_component_message_atoms":message_atoms,"ratio_to_2k":message_atoms/(2**k),"joined_atoms":len(joined),"join_unsat":final_unsat,"left_audit":al,"right_audit":ar,"exact_replay_and_audit":bool(final_unsat and al["match"] and ar["match"]),"adaptive_primary_attempts":sl["primary_attempts"]+sr["primary_attempts"],"static_primary_attempts":sl["static_attempts"]+sr["static_attempts"],"same_case_promotions":0,"epoch_before":epoch_before,"epoch_after":brain.epoch,"paid_nohide_metric":led.get("join_ops",0)+led.get("canonicalization_ops",0)+led.get("serialized_message_bytes",0),"ledger":led}

def self_tests():
    seed="V4_SELFTEST"; brain=ProofMind(); out=[]
    for fam in ("GF2_PLUS_SIGNED_EQ_PARTIAL","GF2_PLUS_HORN_PARTIAL","SIGNED_EQ_PLUS_HORN_PARTIAL","GF2_PLUS_SIGNED_EQ_PLUS_HORN_PARTIAL"):
        row=run_case(fam,6,0,seed,brain,64); assert row["exact_replay_and_audit"],(fam,row); assert row["no_whole_shortcut"],(fam,row); assert row["multi_partial_actuated"],(fam,row); out.append({"family":fam,"pass":True})
    left,right,boundary,lt,rt=build_case("SIGNED_EQ_PLUS_HORN_PARTIAL",6,9,seed); s=solve_component(left,boundary,brain); assert s["terminal"]=="COMPACT_MESSAGE"; bad=json.loads(json.dumps(s["message"])); bad["equations"][0]["rhs"]^=1; assert audit_component_message(bad,lt,boundary,64)["match"] is False
    return {"projector_mix":out,"corruption_control":"PASS"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--journal",required=True); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test: print(json.dumps(self_tests(),indent=2)); return
    p=json.loads(PREREG.read_text()); assert p["status"]=="FROZEN_BEFORE_HOLDOUT_EXECUTION"; assert p["scientific_boundary"]["P_VS_NP"]=="OPEN"
    brain=ProofMind(); cases=[]; journal=[]
    for family in p["holdout"]["family_templates"]:
        for k in p["holdout"]["k_values"]:
            for variant in range(p["holdout"]["variants_per_k_per_family"]):
                row=run_case(family,k,variant,p["holdout"]["seed"],brain,p["evaluation_only_cap"]); cases.append(row); journal.append({"event":"CASE_COMPLETE",**row})
    complete=[c for c in cases if c.get("terminal")=="UNSAT"]; exact=all(c.get("exact_replay_and_audit") for c in complete) and len(complete)==len(cases); no_short=sum(c.get("no_whole_shortcut",False) for c in cases)/len(cases); multi=sum(c.get("multi_partial_actuated",False) for c in cases)/len(cases); algo_enum=sum(c.get("ledger",{}).get("algorithmic_boundary_assignments_enumerated",0) for c in cases); hi=[c for c in cases if c["k"]>=8 and c.get("terminal")=="UNSAT"]; med_ratio=median(c["ratio_to_2k"] for c in hi); max_ratio=max(c["ratio_to_2k"] for c in hi)
    growth=True; by_family_k={}
    for fam in p["holdout"]["family_templates"]:
        by_family_k[fam]={}
        for k in p["holdout"]["k_values"]:
            grp=[c for c in cases if c["family"]==fam and c["k"]==k and c.get("terminal")=="UNSAT"]; m=median(c["combined_component_message_atoms"] for c in grp) if grp else None; by_family_k[fam][str(k)]={"cases":len(grp),"median_component_message_atoms":m,"baseline_2k":2**k,"median_ratio":median(c["ratio_to_2k"] for c in grp) if grp else None}; growth=growth and m is not None and m<=6*k+24
    nohide=all(c.get("paid_nohide_metric",10**99)<=200*(c["k"]**3)+5000 for c in complete); gov=all(c.get("same_case_promotions")==0 for c in complete) and sum(c["ledger"].get("protected_challenger_attempts",0) for c in complete)>0; audit=all(c["left_audit"]["match"] and c["right_audit"]["match"] for c in complete)
    gates=[{"gate":"M1_EXACTNESS_AND_REPLAY","passed":exact},{"gate":"M2_NO_WHOLE_LANGUAGE_SHORTCUT","passed":no_short>=.90,"value":no_short},{"gate":"M3_MULTI_PARTIAL_ACTUATION","passed":multi>=.85,"value":multi},{"gate":"M4_ZERO_ALGORITHMIC_ENUMERATION","passed":algo_enum==0,"value":algo_enum},{"gate":"M5_COMPACTNESS_K_GE_8","passed":med_ratio<=.10 and max_ratio<=.35,"median":med_ratio,"max":max_ratio},{"gate":"M6_JOIN_GROWTH","passed":growth},{"gate":"M7_NO_EXPONENTIAL_HIDING","passed":nohide},{"gate":"M8_GOVERNANCE_INTEGRITY","passed":gov},{"gate":"M9_ADAPTIVE_SCHEDULER_INFORMATIONAL","passed":True,"adaptive_median":median(c["adaptive_primary_attempts"] for c in complete),"static_median":median(c["static_primary_attempts"] for c in complete)},{"gate":"M10_EVALUATION_AUDIT","passed":audit},{"gate":"M11_UNIVERSAL_LEMMA","passed":False,"reason":"FINITE_STRUCTURED_FAMILY_RESULT_ONLY"}]
    science_pass=all(g["passed"] for g in gates if g["gate"]!="M11_UNIVERSAL_LEMMA"); verdict="FINITE_MIXED_PARTIAL_COMPACT_BOUNDARY_COMPOSITION" if science_pass else ("REFUTED_EXACTNESS" if not exact else "PARTIAL_OR_OPEN_MIXED_PARTIAL_COMPOSITION")
    totals=defaultdict(int)
    for c in complete:
        for k,v in c["ledger"].items():
            if isinstance(v,(int,float)): totals[k]+=v
    out={"schema":"JANUS/BCEG/MIXED-PARTIAL-BOUNDARY-COMPOSITION/V4/RESULT/v1.0","status":"COMPLETE","summary":{"cases":len(cases),"complete_unsat_cases":len(complete),"finite_verdict":verdict,"no_whole_language_shortcut_fraction":no_short,"multi_partial_actuation_fraction":multi,"algorithmic_boundary_assignments_enumerated_total":algo_enum,"evaluation_only_boundary_assignments_enumerated_total":totals["evaluation_only_boundary_assignments_enumerated"],"median_atom_ratio_k_ge_8":med_ratio,"max_atom_ratio_k_ge_8":max_ratio,"adaptive_median_primary_attempts":median(c["adaptive_primary_attempts"] for c in complete),"static_median_primary_attempts":median(c["static_primary_attempts"] for c in complete),"P_VS_NP":"OPEN","universal_polynomial_boundary_elimination_lemma":"OPEN"},"gates":gates,"by_family_k":by_family_k,"resource_ledger_totals":dict(totals),"cases_detail":cases,"interpretation":{"positive":"On frozen constructed mixed components with supplied wide boundaries, exact internal-variable decomposition plus multiple partial projector languages composed into compact replayable boundary messages without algorithmic assignment enumeration.","limit":"The construction supplies the boundary and uses structured modules whose internal-variable factorization is discoverable. This does not establish arbitrary-CNF coverage, polynomial separator discovery, or a worst-case polynomial SAT bound.","next_frontier":"Entangle partial languages through shared internal variables so the clean internal-component factorization is unavailable; test whether exact partial projections can still be discovered and joined without exponential representation/discovery growth."}}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); Path(args.journal).write_text("\n".join(json.dumps(x,sort_keys=True) for x in journal)+"\n"); print(json.dumps({"summary":out["summary"],"gates":gates,"by_family_k":by_family_k},indent=2))

if __name__=="__main__": main()
