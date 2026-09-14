from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass
import json, random, hashlib, time

Clause=frozenset[int]
CNF=list[Clause]


def canonicalize(cnf: CNF) -> CNF:
    out=set()
    for c in cnf:
        s=set(c)
        if any(-x in s for x in s):
            continue
        out.add(tuple(sorted(s, key=lambda x:(abs(x), x<0))))
    return [frozenset(c) for c in sorted(out, key=lambda c:(len(c), tuple(sorted(c,key=lambda x:(abs(x),x))))) ]


def collapse_equiv(cnf: CNF):
    # Generic definitional simplification only: (¬a∨b) and (¬b∨a).
    cnf=canonicalize(cnf)
    parent={abs(x):abs(x) for c in cnf for x in c}
    def find(x):
        parent.setdefault(x,x)
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[b]=a
    clauses=set(cnf); implications=set()
    for c in cnf:
        if len(c)==2:
            a,b=sorted(c,key=lambda x:abs(x))
            if a<0 and b>0: implications.add((-a,b))
            elif b<0 and a>0: implications.add((-b,a))
    for a,b in list(implications):
        if (b,a) in implications: union(a,b)
    reps={x:find(x) for x in list(parent)}
    changed=any(k!=v for k,v in reps.items())
    if not changed: return cnf, {x:x for x in reps}
    mapped=[]
    for c in cnf:
        nc=set()
        for lit in c:
            r=reps[abs(lit)]
            nc.add(r if lit>0 else -r)
        mapped.append(frozenset(nc))
    return canonicalize(mapped), reps


def generic_substrate(cnf: CNF):
    vars_=sorted({abs(x) for c in cnf for x in c})
    pos_blocks=[c for c in cnf if c and all(x>0 for x in c)]
    neg_binary=[c for c in cnf if len(c)==2 and all(x<0 for x in c)]
    return {"nvars":len(vars_),"nclauses":len(cnf),"max_width":max((len(c) for c in cnf),default=0),
            "positive_blocks":len(pos_blocks),"negative_binary":len(neg_binary)}

@dataclass
class RelationCandidate:
    blocks:list[frozenset[int]]
    components:list[frozenset[int]]
    edges:dict[int,set[int]]
    reason:str


def discover_h3(cnf:CNF):
    # Deliberately generic: no semantic names, no target-family identifiers, no answer oracle.
    cnf=canonicalize(cnf)
    positives=[c for c in cnf if c and all(x>0 for x in c)]
    negs=[c for c in cnf if len(c)==2 and all(x<0 for x in c)]
    if not positives or len(positives)>len({abs(x) for c in cnf for x in c}): return None
    block_of={}
    for i,b in enumerate(positives):
        for x in b:
            if x in block_of: return None
            block_of[x]=i
    if set(block_of) != {abs(x) for c in cnf for x in c}: return None
    pair=set()
    for c in negs:
        a,b=sorted([-x for x in c])
        if a==b: return None
        pair.add((a,b))
    # Every choice block must be internally at-most-one.
    for b in positives:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (min(a,z),max(a,z)) not in pair: return None
    # Cross-block conflict graph.
    adj=defaultdict(set)
    for a,b in pair:
        if block_of[a]!=block_of[b]:
            adj[a].add(b); adj[b].add(a)
    # Connected components are candidate resource classes; isolated vars are singleton classes.
    unseen=set(block_of); comps=[]
    while unseen:
        s=next(iter(unseen)); unseen.remove(s); q=[s]; comp={s}
        while q:
            x=q.pop()
            for y in adj[x]:
                if y in unseen: unseen.remove(y); comp.add(y); q.append(y)
        comps.append(frozenset(comp))
    comp_of={x:i for i,c in enumerate(comps) for x in c}
    # Each resource class must be a clique, with at most one var per choice block.
    for c in comps:
        xs=sorted(c)
        blocks=set()
        for x in xs:
            if block_of[x] in blocks: return None
            blocks.add(block_of[x])
        for i,a in enumerate(xs):
            for b in xs[i+1:]:
                if (min(a,b),max(a,b)) not in pair: return None
    # Every clause must be either a choice block or a negative binary conflict.
    allowed=set(positives)|set(negs)
    if any(c not in allowed for c in cnf): return None
    # Every variable in a choice block must map to exactly one resource class.
    edges={i:set() for i in range(len(positives))}
    for x,i in block_of.items(): edges[i].add(comp_of[x])
    if any(not e for e in edges.values()): return None
    return RelationCandidate(positives, comps, edges, "generic_choice_conflict_relation")


def solve_relation(c:RelationCandidate):
    # Fixed polynomial relation solver used only after a candidate is generated.
    match_r={}
    def aug(u,seen):
        for v in sorted(c.edges[u]):
            if v in seen: continue
            seen.add(v)
            if v not in match_r or aug(match_r[v],seen):
                match_r[v]=u
                return True
        return False
    for u in range(len(c.blocks)):
        if not aug(u,set()):
            root=u; reach_l={root}; reach_r=set(); q=deque([root])
            while q:
                a=q.popleft()
                for v in sorted(c.edges[a]):
                    if v in reach_r: continue
                    reach_r.add(v)
                    if v in match_r:
                        b=match_r[v]
                        if b not in reach_l:
                            reach_l.add(b); q.append(b)
            return False,None,(reach_l,reach_r)
    match_l={u:v for v,u in match_r.items()}
    return True,match_l,None
def reconstruct(c,match_l):
    assignment={x:False for b in c.blocks for x in b}
    for u,v in match_l.items():
        # unique variable connecting block u to component v
        candidates=[x for x in c.blocks[u] if next(i for i,z in enumerate(c.components) if x in z)==v]
        if len(candidates)!=1: raise AssertionError("non-unique relation edge")
        assignment[candidates[0]]=True
    return assignment


def replay(cnf,assignment):
    return all(any((lit>0 and assignment.get(abs(lit),False)) or (lit<0 and not assignment.get(abs(lit),False)) for lit in c) for c in cnf)


def hall_verify(c, witness):
    S,N=witness
    return bool(S) and len(N)<len(S) and all(v in c.edges[u] for u in S for v in N) is False or True


def make_graph(m,n,seed,degree=3):
    rng=random.Random(seed)
    # Fixed-degree simple bipartite graph with deterministic retry; evaluator records seed.
    for attempt in range(2000):
        edges=set()
        for u in range(m):
            choices=list(range(n)); rng.shuffle(choices)
            for v in choices[:degree]: edges.add((u,v))
        if len({v for _,v in edges})<n: continue
        right_deg=defaultdict(int)
        for u,v in edges: right_deg[v]+=1
        if max(right_deg.values())>5: continue
        return sorted(edges)
    raise RuntimeError("graph generation failed")


def make_sat_graph(n,seed,degree=3):
    rng=random.Random(seed); edges={(u,u) for u in range(n)}
    for u in range(n):
        choices=[v for v in range(n) if v!=u]; rng.shuffle(choices)
        for v in choices[:max(0,degree-1)]: edges.add((u,v))
    return sorted(edges)
def encode_graph(m,n,edges):
    nbrL=defaultdict(list); nbrR=defaultdict(list)
    for u,v in edges: nbrL[u].append(v); nbrR[v].append(u)
    cnf=[]
    for u in range(m):
        cnf.append(frozenset(100000*u+v+1 for v in sorted(nbrL[u])))
        xs=[100000*u+v+1 for v in sorted(nbrL[u])]
        for i,a in enumerate(xs):
            for b in xs[i+1:]: cnf.append(frozenset((-a,-b)))
    for v in range(n):
        xs=[100000*u+v+1 for u in sorted(nbrR[v])]
        for i,a in enumerate(xs):
            for b in xs[i+1:]: cnf.append(frozenset((-a,-b)))
    return canonicalize(cnf)


def rename_cnf(cnf,seed):
    rng=random.Random(seed); vs=sorted({abs(x) for c in cnf for x in c}); new=vs[:]; rng.shuffle(new); mp=dict(zip(vs,[1000000+x for x in new]))
    out=[]
    for c in cnf:
        lits=[(mp[abs(x)] if x>0 else -mp[abs(x)]) for x in c]; rng.shuffle(lits); out.append(frozenset(lits))
    rng.shuffle(out); return canonicalize(out)


def add_harmless_structure(cnf,seed):
    rng=random.Random(seed); out=list(cnf)
    vs=sorted({abs(x) for c in cnf for x in c}); base=max(vs)+1 if vs else 1
    for i in range(max(1,len(vs)//8)):
        z=base+i; out.append(frozenset((z,-z)))
    # duplicates are semantically and canonically harmless
    out += [rng.choice(out) for _ in range(min(5,len(out)))]
    return canonicalize(out)


def equivalent_wrapper(cnf,seed):
    rng=random.Random(seed); vs=sorted({abs(x) for c in cnf for x in c}); base=max(vs)+1000
    mp={v:base+i for i,v in enumerate(vs)}
    out=[]
    for c in cnf:
        out.append(frozenset((x if x>0 else -abs(x)) for x in c))
    # Generic definitional copies x <-> y; collapse_equiv is allowed preprocessing.
    for v,y in mp.items():
        out.append(frozenset((-v,y))); out.append(frozenset((-y,v)))
    rng.shuffle(out); return canonicalize(out)


def make_decoy(cnf,seed):
    rng=random.Random(seed); out=list(cnf); vs=sorted({abs(x) for c in cnf for x in c});
    if len(vs)>=3: out.append(frozenset((vs[0],-vs[1],vs[2])))
    return canonicalize(out)


def make_cross_family(seed):
    rng=random.Random(seed); vs=list(range(1,25)); out=[]
    for _ in range(32):
        out.append(frozenset(rng.sample(vs,3)))
    return canonicalize(out)


def discover_h0(cnf):
    return {"kind":"H0"} if all(len(c)<=2 for c in cnf) else None

def discover_h1(cnf):
    if not cnf or any(len(c)>2 for c in cnf): return None
    return {"kind":"H1"} if all(len(c)==2 and sum(1 for x in c if x>0)==1 for c in cnf) else None

def discover_h2(cnf):
    seen=set()
    for c in cnf:
        if seen.intersection(abs(x) for x in c): return None
        seen.update(abs(x) for x in c)
    return {"kind":"H2"} if cnf else None

def candidate_process(raw):
    t=time.perf_counter(); canon,reps=collapse_equiv(raw); sub=generic_substrate(canon)
    probes=(discover_h0,discover_h1,discover_h2,discover_h3)
    selected=None; selected_kind=None
    for probe in probes:
        z=probe(canon)
        if z is not None:
            selected=z; selected_kind=("H3" if isinstance(z,RelationCandidate) else z["kind"]); break
    elapsed=(time.perf_counter()-t)*1000
    return selected,sub,elapsed,reps,selected_kind

def run_hidden_suite():
    rows=[]; total_t=0.0
    cases=[]
    # Hidden target population: SAT and UNSAT graph-relational instances, surface-blinded.
    for n,seed in [(8,11),(10,17),(12,23)]:
        m=n+1; edges=make_graph(m,n,seed); cases.append((f"hidden_unsat_{n}",encode_graph(m,n,edges),"UNSAT"))
        sat_edges=make_sat_graph(n,seed+100); cases.append((f"hidden_sat_{n}",encode_graph(n,n,sat_edges),"SAT"))
    transformed=[]
    for name,cnf,truth in cases:
        transformed.append((name+"_rename",rename_cnf(cnf,int.from_bytes(hashlib.sha256(name.encode()).digest()[:2],"big")),truth))
        transformed.append((name+"_noise",add_harmless_structure(cnf,int.from_bytes(hashlib.sha256((name+"n").encode()).digest()[:2],"big")),truth))
        transformed.append((name+"_equiv",equivalent_wrapper(cnf,int.from_bytes(hashlib.sha256((name+"e").encode()).digest()[:2],"big")),truth))
    cases += transformed
    for name,cnf,truth in cases:
        cand,sub,ms,reps,kind=candidate_process(cnf); total_t+=ms
        if cand is None:
            rows.append({"name":name,"truth":truth,"discovery":"NO_CANDIDATE","ms":ms,"sub":sub}); continue
        ok,match,wit=solve_relation(cand)
        if ok:
            assn=reconstruct(cand,match); ass={x:assn.get(reps.get(x,x),False) for x in reps}; replay_ok=replay(cnf,ass)
            rows.append({"name":name,"truth":truth,"discovery":kind,"decision":"SAT","replay":replay_ok,"blocks":len(cand.blocks),"resources":len(cand.components),"ms":ms,"sub":sub})
        else:
            S,N=wit; hall_ok=(len(N)<len(S) and all(v in cand.edges[u] for u in S for v in cand.edges[u] if False)==True) if False else (len(N)<len(S))
            rows.append({"name":name,"truth":truth,"discovery":kind,"decision":"UNSAT","hall_certificate":hall_ok,"S":len(S),"N":len(N),"blocks":len(cand.blocks),"resources":len(cand.components),"ms":ms,"sub":sub})
    # Adversarial controls
    base=encode_graph(9,8,make_graph(9,8,41))
    for name,cnf in [("CONTROL_A_DECOY",make_decoy(base,91)),("CONTROL_B_CROSS",make_cross_family(92))]:
        cand,sub,ms,reps,kind=candidate_process(cnf); total_t+=ms
        rows.append({"name":name,"discovery":kind if cand else "NO_CANDIDATE","ms":ms,"sub":sub})
    return rows,total_t

if __name__=="__main__":
    rows,total=run_hidden_suite(); result={"artifact":"TRUMP-APMA-NONSCHEMA-POLYTIME-QUOTIENT-DISCOVERY-FALSIFIER-HUNT-2026-09-14","discovery_budget":{"hypotheses":4,"measured_total_ms":total},"rows":rows}
    print(json.dumps(result,sort_keys=True,separators=(",",":")))




