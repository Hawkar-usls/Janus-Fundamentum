#!/usr/bin/env python3
"""
JANUS C021 Cognitive Portfolio Search
Software-only search cycle using ideas extracted from:
- Hawkar-usls/iNaiHR: four candidate expansions
- Hawkar-usls/aura-oracle-tg: typed PAST/OBSTACLE/GUIDE/OUTCOME framing
- Hawkar-usls/Hrain: persistent proof-DAG / provenance memory
- JANUS Gate: independent witness/proof verification

The experiment constructs a sound heterogeneous SAT portfolio for four
polynomially tractable languages:
  1. 2-SAT
  2. Horn
  3. dual-Horn
  4. canonical bounded-arity affine/XOR blocks

It then tests:
- exact agreement with brute force on restricted families;
- heterogeneous component composition;
- definitional-extension masking and certified unmasking;
- coverage failure on generic 3-CNF;
- proof-DAG deduplication versus semantic state explosion.

This does NOT prove P=NP.
No swarm, device, NAS, model API, Telegram backend, or physical system is used.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]

SOURCE_PINS = {
    "iNaiHR": "e9be39c7f36c92e3f31d4f1c60251bbf41e04c63",
    "AURA": "b5360f08ea6b5369fbd7f56d09d7be93438628a6",
    "HRain": "8699617c3c5eb8ecd83732ba46e5bdfb2d0f6399",
}


def canonical_clause(c: Iterable[int]) -> Clause:
    vals = set(int(x) for x in c)
    return tuple(sorted(vals, key=lambda x: (abs(x), x < 0)))


def canonical_formula(f: Iterable[Iterable[int]]) -> CNF:
    clauses = [canonical_clause(c) for c in f]
    return tuple(sorted(clauses))


def vars_of(f: CNF) -> list[int]:
    return sorted({abs(l) for c in f for l in c})


def satisfies(f: CNF, a: dict[int, bool]) -> bool:
    return all(any(a.get(abs(l), False) == (l > 0) for l in c) for c in f)


def brute_force(f: CNF) -> tuple[bool, dict[int, bool] | None, int]:
    vs = vars_of(f)
    checks = 0
    for bits in itertools.product([False, True], repeat=len(vs)):
        checks += 1
        a = dict(zip(vs, bits))
        if satisfies(f, a):
            return True, a, checks
    return False, None, checks


def simplify_with_assignment(f: CNF, a: dict[int, bool]) -> CNF | None:
    out: list[Clause] = []
    for c in f:
        sat = False
        rem = []
        for l in c:
            v = abs(l)
            if v in a:
                if a[v] == (l > 0):
                    sat = True
                    break
            else:
                rem.append(l)
        if sat:
            continue
        if not rem:
            return None
        out.append(canonical_clause(rem))
    return canonical_formula(out)


def verify_sat(f: CNF, witness: Any) -> bool:
    if not isinstance(witness, dict):
        return False
    try:
        a = {int(k): bool(v) for k, v in witness.items()}
    except (TypeError, ValueError):
        return False
    return satisfies(f, a)


def formula_hash(f: CNF) -> str:
    payload = json.dumps(f, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


class ProofDAG:
    def __init__(self) -> None:
        self.nodes: list[dict[str, Any]] = []
        self._index: dict[str, int] = {}

    def add(self, node_type: str, payload: dict[str, Any], parents: Iterable[int] = ()) -> int:
        normalized = {
            "node_type": node_type,
            "payload": payload,
            "parents": sorted(set(int(x) for x in parents)),
        }
        key = hashlib.sha256(
            json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if key in self._index:
            return self._index[key]
        idx = len(self.nodes)
        node = {"id": idx, "hash": key, **normalized}
        self.nodes.append(node)
        self._index[key] = idx
        return idx


@dataclass
class SolverResult:
    status: str
    language: str
    witness: dict[int, bool] | None = None
    certificate: dict[str, Any] | None = None
    reason: str = ""
    dag_root: int | None = None


def is_2sat(f: CNF) -> bool:
    return all(len(c) <= 2 for c in f)


def lit_index(l: int, n: int) -> int:
    v = abs(l) - 1
    return 2 * v + (0 if l > 0 else 1)


def index_lit(i: int) -> int:
    v = i // 2 + 1
    return v if i % 2 == 0 else -v


def solve_2sat(f: CNF, dag: ProofDAG) -> SolverResult:
    if not is_2sat(f):
        return SolverResult("OPEN", "2SAT", reason="recognizer_rejected")
    actual_vars = vars_of(f)
    n = max(actual_vars, default=0)
    g = [[] for _ in range(2*n)]
    rg = [[] for _ in range(2*n)]
    edge_clause: dict[tuple[int, int], int] = {}
    for ci, c in enumerate(f):
        if len(c) == 1:
            a = c[0]
            edges = [(-a, a)]
        elif len(c) == 2:
            a, b = c
            edges = [(-a, b), (-b, a)]
        else:
            return SolverResult("UNSAT", "2SAT", certificate={"empty_clause": ci})
        for x, y in edges:
            u, v = lit_index(x, n), lit_index(y, n)
            g[u].append(v); rg[v].append(u); edge_clause[(u,v)] = ci

    seen = [False]*(2*n)
    order: list[int] = []
    def dfs(u: int) -> None:
        seen[u] = True
        for v in g[u]:
            if not seen[v]:
                dfs(v)
        order.append(u)
    for u in range(2*n):
        if not seen[u]:
            dfs(u)
    comp = [-1]*(2*n)
    def rdfs(u: int, cid: int) -> None:
        comp[u] = cid
        for v in rg[u]:
            if comp[v] < 0:
                rdfs(v, cid)
    cid = 0
    for u in reversed(order):
        if comp[u] < 0:
            rdfs(u, cid); cid += 1

    def path_within(src: int, dst: int, c_id: int) -> list[tuple[int,int,int]] | None:
        q=[src]; prev={src:None}
        for u in q:
            if u == dst:
                break
            for v in g[u]:
                if comp[v] == c_id and v not in prev:
                    prev[v] = u; q.append(v)
        if dst not in prev:
            return None
        rev=[]; cur=dst
        while prev[cur] is not None:
            p=prev[cur]
            rev.append((p,cur,edge_clause[(p,cur)]))
            cur=p
        return list(reversed(rev))

    for v in actual_vars:
        p, q = lit_index(v,n), lit_index(-v,n)
        if comp[p] == comp[q]:
            p1 = path_within(p,q,comp[p]) or []
            p2 = path_within(q,p,comp[p]) or []
            cert = {
                "variable": v,
                "path_pos_to_neg": [[index_lit(a), index_lit(b), ci] for a,b,ci in p1],
                "path_neg_to_pos": [[index_lit(a), index_lit(b), ci] for a,b,ci in p2],
            }
            root = dag.add("TEAR_2SAT_SCC", cert)
            return SolverResult("UNSAT","2SAT",certificate=cert,dag_root=root)
    a = {v: comp[lit_index(v,n)] > comp[lit_index(-v,n)] for v in actual_vars}
    if not satisfies(f,a):
        a = {v: not val for v,val in a.items()}
    root = dag.add("LAUGHTER_SAT_WITNESS", {"language":"2SAT","witness":a})
    return SolverResult("SAT","2SAT",witness=a,dag_root=root)


def verify_2sat_cert(f: CNF, cert: Any) -> bool:
    if not isinstance(cert, dict):
        return False
    try:
        v = int(cert["variable"])
        paths = [cert["path_pos_to_neg"], cert["path_neg_to_pos"]]
    except Exception:
        return False
    for path, start, end in zip(paths, [v,-v], [-v,v]):
        cur = start
        for step in path:
            if not isinstance(step, list) or len(step) != 3:
                return False
            x,y,ci = step
            if x != cur or not (0 <= ci < len(f)):
                return False
            c=f[ci]
            valid = (len(c)==1 and c[0]==y and x==-y) or (
                len(c)==2 and ((-x in c) and (y in c))
            )
            if not valid:
                return False
            cur=y
        if cur != end:
            return False
    return True


def is_horn(f: CNF) -> bool:
    return all(sum(1 for l in c if l > 0) <= 1 for c in f)


def horn_solve(f: CNF, dag: ProofDAG, language: str = "HORN") -> SolverResult:
    if not is_horn(f):
        return SolverResult("OPEN", language, reason="recognizer_rejected")
    rules: list[tuple[set[int], int | None, int]] = []
    for ci,c in enumerate(f):
        body={abs(l) for l in c if l < 0}
        heads=[l for l in c if l > 0]
        rules.append((body,heads[0] if heads else None,ci))
    true_vars:set[int]=set()
    derivation:dict[int,dict[str,Any]]={}
    changed=True
    while changed:
        changed=False
        for body,head,ci in rules:
            if head is not None and head not in true_vars and body <= true_vars:
                true_vars.add(head)
                derivation[head]={"clause":ci,"premises":sorted(body)}
                changed=True
    for body,head,ci in rules:
        if head is None and body <= true_vars:
            cert={"goal_clause":ci,"required_true":sorted(body),"derivations":{str(k):v for k,v in derivation.items()}}
            root=dag.add("TEAR_HORN_FORWARD",cert)
            return SolverResult("UNSAT",language,certificate=cert,dag_root=root)
    a={v:(v in true_vars) for v in vars_of(f)}
    root=dag.add("LAUGHTER_SAT_WITNESS",{"language":language,"witness":a})
    return SolverResult("SAT",language,witness=a,dag_root=root)


def verify_horn_cert(f: CNF, cert: Any) -> bool:
    if not isinstance(cert,dict) or not is_horn(f):
        return False
    try:
        goal=int(cert["goal_clause"])
        derivs={int(k):v for k,v in cert["derivations"].items()}
    except Exception:
        return False
    if not (0 <= goal < len(f)):
        return False
    true:set[int]=set(); pending=dict(derivs); progress=True
    while pending and progress:
        progress=False
        for v,d in list(pending.items()):
            ci=d.get("clause"); prem=set(d.get("premises",[]))
            if not isinstance(ci,int) or not (0<=ci<len(f)) or not prem <= true:
                continue
            c=f[ci]
            if v not in c or any(l>0 and l!=v for l in c):
                return False
            if {abs(l) for l in c if l<0} != prem:
                return False
            true.add(v); del pending[v]; progress=True
    if pending:
        return False
    goal_clause=f[goal]
    return not any(l>0 for l in goal_clause) and {abs(l) for l in goal_clause} <= true


def flip_formula(f: CNF) -> CNF:
    return canonical_formula([[-l for l in c] for c in f])


def solve_dual_horn(f: CNF, dag: ProofDAG) -> SolverResult:
    if not all(sum(1 for l in c if l < 0) <= 1 for c in f):
        return SolverResult("OPEN","DUAL_HORN",reason="recognizer_rejected")
    inner=horn_solve(flip_formula(f),dag,language="DUAL_HORN_INTERNAL")
    if inner.status=="SAT":
        a={v:not val for v,val in (inner.witness or {}).items()}
        root=dag.add("LAUGHTER_SAT_WITNESS",{"language":"DUAL_HORN","witness":a}, [inner.dag_root] if inner.dag_root is not None else [])
        return SolverResult("SAT","DUAL_HORN",witness=a,dag_root=root)
    if inner.status=="UNSAT":
        cert={"flipped_horn_certificate":inner.certificate}
        root=dag.add("TEAR_DUAL_HORN",cert,[inner.dag_root] if inner.dag_root is not None else [])
        return SolverResult("UNSAT","DUAL_HORN",certificate=cert,dag_root=root)
    return SolverResult("OPEN","DUAL_HORN")


def verify_dual_horn_cert(f: CNF, cert: Any) -> bool:
    return isinstance(cert,dict) and verify_horn_cert(flip_formula(f),cert.get("flipped_horn_certificate"))


def falsifying_assignment(c: Clause) -> tuple[tuple[int,...], tuple[int,...]]:
    vs=tuple(sorted(abs(l) for l in c))
    bits=tuple(1 if next(l for l in c if abs(l)==v)<0 else 0 for v in vs)
    return vs,bits


def detect_xor_system(f: CNF, max_arity: int = 5) -> tuple[list[tuple[list[int],int]], dict[str,Any]] | None:
    groups:dict[tuple[int,...],list[Clause]]={}
    for c in f:
        if len(c)<1 or len(c)>max_arity or len({abs(l) for l in c})!=len(c):
            return None
        key=tuple(sorted(abs(l) for l in c))
        groups.setdefault(key,[]).append(c)
    eqs=[]; details=[]
    for vs,clauses in groups.items():
        expected=1 << (len(vs)-1)
        unique={canonical_clause(c) for c in clauses}
        if len(unique)!=expected:
            return None
        parities=set(); falsified=set()
        for c in unique:
            _,bits=falsifying_assignment(c)
            falsified.add(bits); parities.add(sum(bits)&1)
        if len(falsified)!=expected or len(parities)!=1:
            return None
        rhs=1-next(iter(parities))
        eqs.append((list(vs),rhs))
        details.append({"vars":list(vs),"rhs":rhs,"clauses":[list(c) for c in sorted(unique)]})
    return eqs,{"blocks":details}


def gf2_solve(eqs: list[tuple[list[int],int]]) -> tuple[str,dict[int,bool]|None,dict[str,Any]]:
    allv=sorted({v for vs,_ in eqs for v in vs}); pos={v:i for i,v in enumerate(allv)}
    rows=[]; combos=[]
    for ri,(vs,b) in enumerate(eqs):
        mask=0
        for v in vs: mask ^= 1<<pos[v]
        rows.append([mask,b]); combos.append(1<<ri)
    pivot_row=0; pivots={}
    for col in range(len(allv)):
        sel=next((r for r in range(pivot_row,len(rows)) if (rows[r][0]>>col)&1),None)
        if sel is None: continue
        rows[pivot_row],rows[sel]=rows[sel],rows[pivot_row]
        combos[pivot_row],combos[sel]=combos[sel],combos[pivot_row]
        for r in range(len(rows)):
            if r!=pivot_row and ((rows[r][0]>>col)&1):
                rows[r][0]^=rows[pivot_row][0]; rows[r][1]^=rows[pivot_row][1]; combos[r]^=combos[pivot_row]
        pivots[col]=pivot_row; pivot_row+=1
    for r,(mask,b) in enumerate(rows):
        if mask==0 and b==1:
            return "UNSAT",None,{"xor_row_combination":[i for i in range(len(eqs)) if (combos[r]>>i)&1]}
    x=[0]*len(allv)
    for col,r in sorted(pivots.items(),reverse=True):
        rhs=rows[r][1]; s=0
        for j in range(col+1,len(allv)):
            if (rows[r][0]>>j)&1: s^=x[j]
        x[col]=rhs^s
    return "SAT",{v:bool(x[pos[v]]) for v in allv},{"rank":len(pivots)}


def solve_xor(f: CNF, dag: ProofDAG) -> SolverResult:
    detected=detect_xor_system(f)
    if detected is None:
        return SolverResult("OPEN","XOR",reason="recognizer_rejected")
    eqs,meta=detected; status,a,cert=gf2_solve(eqs)
    if status=="SAT":
        if not satisfies(f,a or {}): return SolverResult("OPEN","XOR",reason="internal_witness_failure")
        root=dag.add("LAUGHTER_SAT_WITNESS",{"language":"XOR","witness":a,"meta":meta})
        return SolverResult("SAT","XOR",witness=a,certificate=meta,dag_root=root)
    full={"equations":eqs,"combination":cert["xor_row_combination"],"meta":meta}
    root=dag.add("TEAR_XOR_PARITY",full)
    return SolverResult("UNSAT","XOR",certificate=full,dag_root=root)


def verify_xor_cert(f: CNF, cert: Any) -> bool:
    detected=detect_xor_system(f)
    if detected is None or not isinstance(cert,dict): return False
    eqs,_=detected; idx=cert.get("combination")
    if not isinstance(idx,list) or not idx: return False
    parity={}; rhs=0
    for i in idx:
        if not isinstance(i,int) or not (0<=i<len(eqs)): return False
        vs,b=eqs[i]; rhs^=b
        for v in vs: parity[v]=parity.get(v,0)^1
    return rhs==1 and all(x==0 for x in parity.values())


LANGS=("2SAT","HORN","DUAL_HORN","XOR")

def solve_portfolio(f: CNF, dag: ProofDAG) -> tuple[SolverResult,list[dict[str,Any]]]:
    formula_node=dag.add("ROOT_FORMULA",{"sha256":formula_hash(f),"clauses":[list(c) for c in f]})
    attempts=[]
    solvers=[solve_2sat,horn_solve,solve_dual_horn,solve_xor]
    for name,solver in zip(LANGS,solvers):
        r=solver(f,dag,language="HORN") if name=="HORN" else solver(f,dag)
        attempt=dag.add("GUIDE_LANGUAGE_ATTEMPT",{"language":name,"status":r.status,"reason":r.reason},[formula_node])
        attempts.append({"language":name,"status":r.status,"reason":r.reason,"dag_node":attempt})
        if r.status in ("SAT","UNSAT"):
            out=dag.add("OUTCOME",{"language":name,"status":r.status},[attempt]+([r.dag_root] if r.dag_root is not None else []))
            r.dag_root=out; return r,attempts
    obs=dag.add("OBSTACLE_NO_RECOGNIZED_LANGUAGE",{"languages":list(LANGS)},[formula_node])
    return SolverResult("OPEN","NONE",reason="portfolio_exhausted",dag_root=obs),attempts


def verify_result(f: CNF, r: SolverResult) -> bool:
    if r.status=="SAT": return verify_sat(f,{str(k):v for k,v in (r.witness or {}).items()})
    if r.status=="UNSAT":
        if r.language=="2SAT": return verify_2sat_cert(f,r.certificate)
        if r.language=="HORN": return verify_horn_cert(f,r.certificate)
        if r.language=="DUAL_HORN": return verify_dual_horn_cert(f,r.certificate)
        if r.language=="XOR": return verify_xor_cert(f,r.certificate)
    return r.status=="OPEN"


def primal_components(f: CNF) -> list[set[int]]:
    vs=set(vars_of(f)); adj={v:set() for v in vs}
    for c in f:
        cv={abs(l) for l in c}
        for a in cv: adj[a] |= cv-{a}
    comps=[]
    while vs:
        start=next(iter(vs)); stack=[start]; comp={start}; vs.remove(start)
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v in vs: vs.remove(v); comp.add(v); stack.append(v)
        comps.append(comp)
    return comps


def split_by_components(f: CNF) -> list[CNF]:
    return [canonical_formula([c for c in f if {abs(l) for l in c} <= comp]) for comp in primal_components(f)]


def solve_componentwise(f: CNF, dag: ProofDAG) -> SolverResult:
    comps=split_by_components(f)
    if len(comps)<=1: return solve_portfolio(f,dag)[0]
    witnesses={}; roots=[]
    for comp in comps:
        r,_=solve_portfolio(comp,dag)
        if r.status=="OPEN": return SolverResult("OPEN","HETEROGENEOUS_COMPONENTS",reason="component_open")
        roots.append(r.dag_root)
        if r.status=="UNSAT":
            cert={"component":[list(c) for c in comp],"inner_language":r.language,"inner_certificate":r.certificate}
            root=dag.add("TEAR_COMPONENT_UNSAT",cert,[x for x in roots if x is not None])
            return SolverResult("UNSAT","HETEROGENEOUS_COMPONENTS",certificate=cert,dag_root=root)
        witnesses.update(r.witness or {})
    root=dag.add("LAUGHTER_COMBINED_WITNESS",{"witness":witnesses},[x for x in roots if x is not None])
    return SolverResult("SAT","HETEROGENEOUS_COMPONENTS",witness=witnesses,dag_root=root)


def or_definition_clauses(a:int,b:int,z:int) -> list[Clause]:
    return [canonical_clause((-a,z)),canonical_clause((-b,z)),canonical_clause((a,b,-z))]


def strip_or_definitions(f: CNF) -> tuple[CNF,list[dict[str,int]]]:
    remaining=list(f); defs=[]; changed=True
    while changed:
        changed=False; vars_now=vars_of(canonical_formula(remaining)); occ={v:[] for v in vars_now}
        for i,c in enumerate(remaining):
            for l in c: occ[abs(l)].append(i)
        for z,idxs in sorted(occ.items()):
            if len(idxs)!=3: continue
            clauses=[remaining[i] for i in idxs]
            others=sorted({abs(l) for c in clauses for l in c if abs(l)!=z})
            if len(others)!=2: continue
            a,b=others; expected={canonical_clause(c) for c in or_definition_clauses(a,b,z)}
            if set(clauses)==expected:
                remaining=[c for i,c in enumerate(remaining) if i not in set(idxs)]
                defs.append({"z":z,"a":a,"b":b}); changed=True; break
    return canonical_formula(remaining),defs


def extend_or_definitions(a: dict[int,bool], defs:list[dict[str,int]]) -> dict[int,bool]:
    out=dict(a)
    for d in reversed(defs): out[d["z"]]=out.get(d["a"],False) or out.get(d["b"],False)
    return out


def solve_with_definition_unmasking(f: CNF, dag: ProofDAG) -> SolverResult:
    core,defs=strip_or_definitions(f)
    if not defs: return solve_componentwise(f,dag)
    trans=dag.add("TRANSFORM_STRIP_OR_DEFINITIONS",{"definitions":defs,"core_sha256":formula_hash(core)})
    r=solve_componentwise(core,dag)
    if r.status=="SAT":
        w=extend_or_definitions(r.witness or {},defs)
        if not satisfies(f,w): return SolverResult("OPEN","DEF_UNMASK",reason="recovery_failed")
        root=dag.add("LAUGHTER_RECOVERED_WITNESS",{"witness":w},[trans]+([r.dag_root] if r.dag_root is not None else []))
        return SolverResult("SAT","DEF_UNMASK",witness=w,dag_root=root)
    if r.status=="UNSAT":
        cert={"definitions":defs,"core":[list(c) for c in core],"inner_language":r.language,"inner_certificate":r.certificate}
        root=dag.add("TEAR_EQSAT_REDUCTION",cert,[trans]+([r.dag_root] if r.dag_root is not None else []))
        return SolverResult("UNSAT","DEF_UNMASK",certificate=cert,dag_root=root)
    return SolverResult("OPEN","DEF_UNMASK",reason="unmasked_core_open")


def shift_formula(f: CNF, offset:int) -> CNF:
    return canonical_formula([[(1 if l>0 else -1)*(abs(l)+offset) for l in c] for c in f])


def random_2sat(rng:random.Random,n:int,m:int)->CNF:
    return canonical_formula([[v if rng.random()<.5 else -v for v in rng.sample(range(1,n+1),rng.choice((1,2)))] for _ in range(m)])


def random_horn(rng:random.Random,n:int,m:int)->CNF:
    cs=[]
    for _ in range(m):
        width=rng.randint(1,min(4,n)); vs=rng.sample(range(1,n+1),width); head=rng.choice(vs+[None])
        cs.append([v if v==head else -v for v in vs])
    return canonical_formula(cs)


def random_dual_horn(rng:random.Random,n:int,m:int)->CNF:
    return flip_formula(random_horn(rng,n,m))


def encode_xor_eq(vs:list[int],rhs:int)->list[Clause]:
    return [canonical_clause([(-v if bit else v) for v,bit in zip(vs,bits)]) for bits in itertools.product([0,1],repeat=len(vs)) if (sum(bits)&1)!=rhs]


def random_xor(rng:random.Random,n:int,m:int)->CNF:
    cs=[]; seen=set(); attempts=0
    while len(seen)<m and attempts<1000:
        attempts+=1; k=rng.choice((2,3,4)); vs=tuple(sorted(rng.sample(range(1,n+1),min(k,n))))
        if vs in seen: continue
        seen.add(vs); cs.extend(encode_xor_eq(list(vs),rng.randint(0,1)))
    return canonical_formula(cs)


def random_generic_3cnf(rng:random.Random,n:int,m:int)->CNF:
    return canonical_formula([[v if rng.random()<.5 else -v for v in rng.sample(range(1,n+1),3)] for _ in range(m)])


def mixed_formula(rng:random.Random)->CNF:
    parts=[]; off=0
    for gen in [random_2sat,random_horn,random_dual_horn,random_xor]:
        part=shift_formula(gen(rng,4,5),off); parts.extend(part); off+=4
    return canonical_formula(parts)


def mask_components_with_or_chain(f:CNF)->CNF:
    comps=primal_components(f)
    if len(comps)<2: return f
    cs=list(f); nextv=max(vars_of(f),default=0)+1; reps=[min(c) for c in comps]
    for a,b in zip(reps,reps[1:]): cs.extend(or_definition_clauses(a,b,nextv)); nextv+=1
    return canonical_formula(cs)


def run(seed:int=9379992,per_family:int=120,mixed_cases:int=160,generic_cases:int=240)->dict[str,Any]:
    rng=random.Random(seed); family_stats={}; total_mismatches=0
    for name,gen in [("2SAT",random_2sat),("HORN",random_horn),("DUAL_HORN",random_dual_horn),("XOR",random_xor)]:
        solved=verified=mismatch=sat_n=unsat_n=0
        for _ in range(per_family):
            f=gen(rng,6,8); truth,_,_=brute_force(f); sat_n+=truth; unsat_n+=not truth
            dag=ProofDAG(); r,_=solve_portfolio(f,dag)
            if r.status!="OPEN": solved+=1
            ok=verify_result(f,r); verified+=ok
            if r.status=="OPEN" or (r.status=="SAT")!=truth or not ok: mismatch+=1
        family_stats[name]={"cases":per_family,"solved":solved,"verified":verified,"mismatches_or_open":mismatch,"sat":sat_n,"unsat":unsat_n}
        total_mismatches+=mismatch

    mixed={"cases":mixed_cases,"direct_open":0,"component_solved":0,"component_mismatch":0,"masked_component_open":0,"unmasked_solved":0,"unmasked_mismatch":0,"detected_definitions":0}
    for _ in range(mixed_cases):
        f=mixed_formula(rng); truth=all(brute_force(comp)[0] for comp in split_by_components(f))
        direct,_=solve_portfolio(f,ProofDAG())
        if direct.status=="OPEN": mixed["direct_open"]+=1
        comp=solve_componentwise(f,ProofDAG())
        if comp.status!="OPEN": mixed["component_solved"]+=1
        if comp.status=="OPEN" or (comp.status=="SAT")!=truth or (comp.status=="SAT" and not satisfies(f,comp.witness or {})): mixed["component_mismatch"]+=1
        masked=mask_components_with_or_chain(f); truth2=truth
        naive=solve_componentwise(masked,ProofDAG())
        if naive.status=="OPEN": mixed["masked_component_open"]+=1
        _,defs=strip_or_definitions(masked); mixed["detected_definitions"]+=len(defs)
        unmasked=solve_with_definition_unmasking(masked,ProofDAG())
        if unmasked.status!="OPEN": mixed["unmasked_solved"]+=1
        if unmasked.status=="OPEN" or (unmasked.status=="SAT")!=truth2 or (unmasked.status=="SAT" and not satisfies(masked,unmasked.witness or {})): mixed["unmasked_mismatch"]+=1

    generic={"cases":generic_cases,"portfolio_solved":0,"open":0,"false_accepts":0}
    for _ in range(generic_cases):
        f=random_generic_3cnf(rng,7,18); truth,_,_=brute_force(f); r,_=solve_portfolio(f,ProofDAG())
        if r.status=="OPEN": generic["open"]+=1
        else:
            generic["portfolio_solved"]+=1
            if (r.status=="SAT")!=truth or not verify_result(f,r): generic["false_accepts"]+=1

    hard=random_generic_3cnf(rng,11,34); backdoor_checks=0; found=None; vs=vars_of(hard)
    for k in range(0,4):
        for subset in itertools.combinations(vs,k):
            backdoor_checks+=1; good=True
            for bits in itertools.product([False,True],repeat=k):
                simp=simplify_with_assignment(hard,dict(zip(subset,bits)))
                if simp is None: continue
                r,_=solve_portfolio(simp,ProofDAG())
                if r.status=="OPEN": good=False; break
            if good: found=list(subset); break
        if found is not None: break

    dag=ProofDAG(); f=random_horn(rng,8,12)
    for _ in range(100): solve_portfolio(f,dag)
    repeated_nodes=len(dag.nodes)
    assertions={
        "restricted_families_exact":total_mismatches==0,
        "mixed_components_exact":mixed["component_mismatch"]==0 and mixed["component_solved"]==mixed_cases,
        "masked_unmasking_exact":mixed["unmasked_mismatch"]==0 and mixed["unmasked_solved"]==mixed_cases,
        "masked_breaks_naive_components":mixed["masked_component_open"]>0,
        "generic_sound":generic["false_accepts"]==0,
        "generic_incomplete":generic["open"]>0,
        "proof_dag_deduplicates_repetition":repeated_nodes<20,
    }
    return {
        "audit":"JANUS_C021_COGNITIVE_PORTFOLIO_SEARCH",
        "status":"PASS" if all(assertions.values()) else "FAIL",
        "software_only":True,"swarm_touched":False,"devices_touched":False,"model_apis_called":False,
        "source_pins":SOURCE_PINS,"seed":seed,"languages":list(LANGS),"family_stats":family_stats,
        "mixed_heterogeneous":mixed,"generic_3cnf":generic,
        "bounded_backdoor_search":{"n_vars":len(vs),"tested_subsets":backdoor_checks,"max_size_tested":3,"found_backdoor":found,"verdict":"FOUND_WITHIN_BOUND" if found is not None else "NOT_FOUND_WITHIN_BOUND","warning":"Exhaustive subset and assignment search is not a polynomial selector."},
        "proof_dag_repetition":{"identical_portfolio_runs":100,"unique_nodes":repeated_nodes},
        "assertions":assertions,
        "p_equals_np_progress":"NEW_SOUND_RESTRICTED_META_OBSERVER_NOT_GENERAL_SAT",
        "positive_result":"A four-candidate typed Observer can soundly solve and compose recognized 2-SAT, Horn, dual-Horn and canonical affine/XOR modules, preserve proof provenance in a deduplicated HRain-style DAG, and recover witnesses through certified definitional unmasking.",
        "obstruction":"Generic 3-CNF remains OPEN. Exact search for a useful backdoor/decomposition requires combinatorial subset and assignment exploration. Therefore the fusion improves a polynomial portfolio on a strict structural envelope, but does not supply the missing universal polynomial language/decomposition selector.",
        "next_search_target":"Learn or derive a representation-robust, certificate-producing selector whose total candidate-generation, decomposition, proof and recovery cost is bounded polynomially on every CNF; attack it with extension-variable obfuscation and planted cross-language modules."
    }


def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=9379992); ap.add_argument("--per-family",type=int,default=120); ap.add_argument("--mixed-cases",type=int,default=160); ap.add_argument("--generic-cases",type=int,default=240); ap.add_argument("--output",type=Path); ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args(); res=run(args.seed,args.per_family,args.mixed_cases,args.generic_cases)
    if args.output: args.output.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(res,ensure_ascii=False,indent=2))
    if args.self_test and res["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
