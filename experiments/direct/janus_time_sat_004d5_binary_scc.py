#!/usr/bin/env python3
"""TIME-SAT-004D5 · Source-proven binary implication equivalences → parity.

Public research-only. Complete parity masks of clauses AFTER canonicalizing
literals via *two-way implications from ORIGINAL binary clauses* yield
ADDITIONAL source-entailed XOR equations. Keep every original clause.
Conservative skips: repeated-support variables / tautologies / malformed or
over-budget input / binary-only contradictory SCC. Never claim universal SAT.
"""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import json

from janus_time_sat_004d1_xor import MAX_N,MAX_ROWS,MAX_LITERALS,MAX_WIDTH
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor

def node(l):
    return 2*(abs(l)-1)+(0 if l>0 else 1)

def literal(i):
    v=i//2+1
    return v if i%2==0 else -v

def implication_graph(rows,n):
    if type(n) is not int or n<1 or n>MAX_N: return {"status":"ABSTAIN_INVALID_N"}
    if len(rows)>MAX_ROWS:return {"status":"ABSTAIN_ROW_BUDGET"}
    edges=[[] for _ in range(2*n)]
    rev=[[] for _ in range(2*n)]
    source_count=0
    lits=0
    for i,row in enumerate(rows):
        lits+=len(row)
        if lits>MAX_LITERALS:return {"status":"ABSTAIN_LITERAL_BUDGET"}
        if any(type(v) is not int or not 1<=abs(v)<=n for v in row):
            return {"status":"ABSTAIN_INVALID_LITERAL"}
        if len(row)!=2 or abs(row[0])==abs(row[1]):
            continue  # unit, tautology, repeated literal, wide: not binary SCC witnesses
        a,b=row
        for src,dst in ((-a,b),(-b,a)):
            u,v=node(src),node(dst)
            edges[u].append((v,i))
            rev[v].append(u)
        source_count+=1
    return {"status":"GRAPH_VALID","edges":edges,"reverse":rev,
            "source_binary_clause_count":source_count,
            "source_literal_occurrences":lits}

def components(edges,rev):
    n=len(edges);seen=bytearray(n);post=[]
    for start in range(n):
        if seen[start]:continue
        seen[start]=1;stack=[(start,0)]
        while stack:
            v,i=stack[-1]
            if i<len(edges[v]):
                dst,_=edges[v][i]
                stack[-1]=(v,i+1)
                if not seen[dst]:
                    seen[dst]=1;stack.append((dst,0))
            else:
                post.append(v);stack.pop()
    ids=[-1]*n;num=0
    for start in reversed(post):
        if ids[start]>=0:continue
        ids[start]=num;stack=[start]
        while stack:
            v=stack.pop()
            for u in rev[v]:
                if ids[u]<0:
                    ids[u]=num;stack.append(u)
        num+=1
    return ids,num

def equivalence_map(ids,n):
    if any(ids[node(v)]==ids[node(-v)] for v in range(1,n+1)):
        return None
    groups={}
    for k,c in enumerate(ids):groups.setdefault(c,[]).append(literal(k))
    representative={c:min(lits,key=lambda x:(abs(x),0 if x>0 else 1))
                    for c,lits in groups.items()}
    mapping={v:representative[ids[node(v)]] for v in range(1,n+1)}
    for v,l in mapping.items():
        if representative[ids[node(-v)]]!=-l:
            raise AssertionError("binary SCC complementation invariant failed")
    return mapping

def _path(edges,ids,src_lit,dst_lit,limit=10000):
    """Finite shortest original-clause-indexed implication path in the SAME SCC."""
    src,dst=node(src_lit),node(dst_lit)
    if ids[src]!=ids[dst]:raise AssertionError("witnessed alias not mutually reachable")
    if src==dst:return []
    q=deque([src]);prev={src:None}
    while q:
        u=q.popleft()
        for v,index in edges[u]:
            if ids[v]!=ids[src] or v in prev:continue
            prev[v]=(u,index)
            if v==dst:
                result=[]
                while v!=src:
                    old,edge_source=prev[v]
                    result.append([literal(old),literal(v),edge_source])
                    if len(result)>limit:raise OverflowError("witness path cap")
                    v=old
                return list(reversed(result))
            prev[v]=(u,index)
            q.append(v)
    raise AssertionError("SCC path unexpectedly missing")

def check_path_from_original(rows,path,start,stop):
    current=start
    for a,b,index in path:
        if a!=current or type(index) is not int or not 0<=index<len(rows):
            return False
        row=rows[index]
        if len(row)!=2 or abs(row[0])==abs(row[1]):
            return False
        x,y=row
        if not ((-x==a and y==b) or (-y==a and x==b)):
            return False
        current=b
    return current==stop

def _equation_key(variables,rhs,mapping=None):
    bits=set();parity=rhs
    for v in variables:
        l=mapping[v] if mapping is not None else v
        if l<0:parity^=1
        t=abs(l)
        if t in bits:bits.remove(t)
        else:bits.add(t)
    return (tuple(sorted(bits)),parity)

def _full_parities(rows,mapping):
    """Claim only complete source mask sets of width <=6 after SCC normalization."""
    groups={}
    mapped_change_rows=0
    for i,row in enumerate(rows):
        if not 1<=len(row)<=MAX_WIDTH:continue
        if len({abs(l) for l in row})!=len(row):continue
        transformed=[mapping[abs(l)]*(1 if l>0 else -1) for l in row]
        # Deliberately skip clauses that became tautologies or repeated variables.
        support=tuple(sorted(abs(l) for l in transformed))
        if len(set(support))!=len(support):continue
        signs=frozenset(v for v in transformed if v<0)
        mask=sum(1<<j for j,v in enumerate(support) if -v in signs)
        groups.setdefault(support,{}).setdefault(mask,[]).append(i)
        if tuple(transformed)!=tuple(row):mapped_change_rows+=1
    results={}
    for support,masks in sorted(groups.items()):
        k=len(support)
        for parity in (0,1):
            wanted=[m for m in range(1<<k) if m.bit_count()%2==parity]
            if not all(m in masks for m in wanted):continue
            key=(support,1^parity)
            indices=[masks[m][0] for m in wanted]
            results.setdefault(key,indices)
    return results, len(groups), mapped_change_rows

def replay_equation_certificate(rows,example):
    """Source-only independent checker from original binary clauses + sign masks."""
    if example.get("certificate_status")!="SOURCE_BINARY_PATHS_AND_FULL_MASKS":
        return False
    support=example["variables"]
    if not support or support!=sorted(set(support)):return False
    width=len(support);rhs=example["rhs"]
    masks=[m for m in range(1<<width) if m.bit_count()%2!=(rhs&1)]
    source_indices=example["original_clause_indices"]
    if len(source_indices)!=len(masks) or len(set(source_indices))!=len(masks):
        return False
    substitutions=example["substitutions"]
    proven={}
    for sub in substitutions:
        src=int(sub["positive_original_variable"])
        mapped=int(sub["canonical_signed_literal"])
        if src in proven or src<=0 or abs(mapped)<=0:return False
        if not (check_path_from_original(rows,sub["forward"],src,mapped)
                and check_path_from_original(rows,sub["reverse"],mapped,src)):
            return False
        proven[src]=mapped
    actual_mask_set=set()
    for index in source_indices:
        if type(index) is not int or index<0 or index>=len(rows):
            return False
        original=rows[index]
        if len(original)!=width or len({abs(l) for l in original})!=width:
            return False
        canonical=[]
        for lit in original:
            src=abs(lit)
            if src not in proven:
                return False
            signed=proven[src]*(1 if lit>0 else -1)
            canonical.append(signed)
        if sorted(abs(x) for x in canonical)!=support:return False
        mask=sum(1<<j for j,v in enumerate(support) if -v in canonical)
        if mask in actual_mask_set:return False
        actual_mask_set.add(mask)
    return sorted(actual_mask_set)==masks

def source_proven_implied_xor(rows,n,*,max_examples=8):
    g=implication_graph(rows,n)
    if g["status"]!="GRAPH_VALID":
        return {"status":g["status"],"new_implied_equations":None}
    ids,count=components(g["edges"],g["reverse"])
    mapping=equivalence_map(ids,n)
    base={
        "schema":"JANUS-TIME-SAT-004D5-IMPLIED-XOR-FROM-BINARY-SCC-V1",
        "source_original_clauses_unmodified":True,
        "source_n":n,"source_clauses":len(rows),
        "binary_original_clause_count":g["source_binary_clause_count"],
        "SCC_component_count":count,
        "SAT_UNSAT":"NOT_ATTEMPTED",
        "outside_admin_witness":"NOT_DONE",
        "production_C023":"UNCHANGED"
    }
    if mapping is None:
        return {**base,"status":"ABSTAIN_BINARY_ONLY_SCC_CONTRADICTION_UNCERTIFIED",
                "new_implied_equations":None}
    aliases={v:l for v,l in mapping.items() if v!=l}
    base["nontrivial_source_proven_signed_variable_aliases"]=len(aliases)
    normalized,supports,mapped_rows=_full_parities(rows,mapping)
    base["normalized_supported_groups_scanned"]=supports
    base["rows_with_modified_sign_or_variable"]=mapped_rows
    prior=extract_paged_mixed_xor(rows,n)
    if prior["status"]!="SOURCE_PARTITION_VERIFIED":
        return {**base,"status":"ABSTAIN_BASELINE_NOT_VERIFIED","new_implied_equations":None}
    baseline={_equation_key(eq["variables"],eq["rhs"],mapping)
              for eq in prior["equations"]}
    baseline={x for x in baseline if x[0]}  # do not turn contradictions into units
    newly=[(key,indices) for key,indices in normalized.items() if key not in baseline]
    base.update({
        "status":"WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS",
        "original_explicit_XOR_equation_count":len(prior["equations"]),
        "canonicalized_full_XOR_equations":len(normalized),
        "new_implied_XOR_equations_beyond_prior_canonical_baseline":len(newly),
        "new_implied_source_clause_index_hash":sha256(json.dumps(
            [[list(k[0]),k[1],indices] for k,indices in newly],
            separators=(",",":")).encode()).hexdigest(),
        "complete_original_CNF_retained_for_all_future_solver_use":True,
    })
    examples=[];skipped_proof_budget=0
    for (support,rhs),indices in newly[:max_examples]:
        used=sorted({abs(l) for i in indices for l in rows[i]})
        substitutions=[]
        try:
            for v in used:
                mapped=mapping[v]
                substitutions.append({
                    "positive_original_variable":v,
                    "canonical_signed_literal":mapped,
                    "forward":_path(g["edges"],ids,v,mapped),
                    "reverse":_path(g["edges"],ids,mapped,v)})
        except OverflowError:
            skipped_proof_budget+=1;continue
        example={"variables":list(support),"rhs":rhs,
                 "original_clause_indices":indices,
                 "substitutions":substitutions,
                 "certificate_status":"SOURCE_BINARY_PATHS_AND_FULL_MASKS"}
        if not replay_equation_certificate(rows,example):
            raise AssertionError("new GF2 parity source implication certificate invalid")
        examples.append(example)
    base["sample_witnesses_original_source_replayed"]=examples
    base["sample_certificate_budget_exhausted"]=skipped_proof_budget
    base["sample_count"]=len(examples)
    return base
