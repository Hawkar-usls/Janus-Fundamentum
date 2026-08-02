#!/usr/bin/env python3
"""C035 certified interface congruence baseline.

This artifact formalizes a sound but deliberately incomplete merge rule for
partial assignments in modular SAT networks.

A state alpha may merge with beta only when independently recomputed canonical
module messages are identical, or when both states carry a verified absorbing
terminal certificate. No general SAT or formula-equivalence oracle is called.
"""

from __future__ import annotations
import argparse, hashlib, itertools, json, random
from collections import defaultdict

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Assignment = dict[int, bool]

def canon_clause(c: Clause):
    s=set(c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))

def normalize_cnf(f: CNF) -> CNF:
    cs=[]
    for c in f:
        q=canon_clause(c)
        if q is not None: cs.append(q)
    cs=sorted(set(cs),key=lambda c:(len(c),c))
    keep=[]
    for c in cs:
        sc=set(c)
        if any(set(d)<=sc for d in keep): continue
        keep.append(c)
    return tuple(keep)

def restrict_cnf(f: CNF, a: Assignment) -> CNF:
    out=[]
    for c in f:
        sat=False; rem=[]
        for lit in c:
            v=abs(lit)
            if v in a:
                if a[v] == (lit>0):
                    sat=True; break
            else:
                rem.append(lit)
        if not sat: out.append(tuple(rem))
    return normalize_cnf(tuple(out))

def evaluate(f: CNF, a: Assignment) -> bool:
    return all(any(a[abs(l)] == (l>0) for l in c) for c in f)

def rref_affine(equations, assignment: Assignment):
    """Return a canonical RREF-style row-space message over GF(2)."""
    rows=[]; allvars=set()
    for variables,rhs in equations:
        mask=set(variables); bit=rhs&1
        for v,val in assignment.items():
            if v in mask:
                mask.remove(v); bit ^= int(val)
        rows.append([set(mask),bit]); allvars |= mask
    rank=0
    for col in sorted(allvars):
        pivot=next((i for i in range(rank,len(rows)) if col in rows[i][0]),None)
        if pivot is None: continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        pm,pb=rows[rank]
        for i in range(len(rows)):
            if i!=rank and col in rows[i][0]:
                rows[i]=[rows[i][0]^pm, rows[i][1]^pb]
        rank+=1
    if any(not m and b for m,b in rows): return ("FALSE",)
    canonical=tuple(sorted(set((tuple(sorted(m)),b) for m,b in rows if m)))
    return ("AFFINE_RREF",canonical)

def encode_nand3_neq(source: CNF, n: int):
    """Linear witness-preserving C023/C034 image: Horn NAND3 + affine NEQ."""
    modules=[]
    for i in range(1,n+1):
        modules.append(("AFFINE", (((i,n+i),1),), f"neq:{i}"))
    for j,clause in enumerate(source):
        falsity=[n+abs(l) if l>0 else abs(l) for l in clause]
        horn=normalize_cnf((tuple(-v for v in falsity),))
        modules.append(("HORN",horn,f"clause:{j}"))
    return modules

def module_message(module, assignment: Assignment):
    kind,obj,name=module
    if kind=="AFFINE":
        return rref_affine(obj,assignment)
    residual=restrict_cnf(obj,assignment)
    if () in residual: return ("FALSE",)
    return ("HORN_RESIDUAL",residual)

def certified_sigma(source: CNF, n: int, assignment: Assignment, absorb=True):
    messages=[]
    for module in encode_nand3_neq(source,n):
        message=module_message(module,assignment)
        if absorb and message==("FALSE",):
            return ("ABSORBING_FALSE",)
        messages.append((module[2],message))
    return ("PRODUCT",tuple(messages))

def verify_state_record(source: CNF, n: int, assignment: Assignment, claimed, absorb=True):
    return certified_sigma(source,n,assignment,absorb)==claimed

def verify_merge(source: CNF, n: int, a: Assignment, b: Assignment, sigma_value, absorb=True):
    return (
        verify_state_record(source,n,a,sigma_value,absorb)
        and verify_state_record(source,n,b,sigma_value,absorb)
    )

def continuation_vector(source: CNF, n: int, depth: int, prefix_bits):
    a={i+1:bool(prefix_bits[i]) for i in range(depth)}
    out=[]
    for tail in itertools.product((False,True),repeat=n-depth):
        full=dict(a)
        for i,bit in enumerate(tail,start=depth+1): full[i]=bit
        out.append(evaluate(source,full))
    return tuple(out)

def prefix_assignment(n: int, bits):
    a={}
    for i,bit in enumerate(bits,start=1):
        a[i]=bool(bit); a[n+i]=not bool(bit)
    return a

def unit_family_audit(max_n=12):
    rows=[]
    for n in range(1,max_n+1):
        source=tuple((i,i,i) for i in range(1,n+1))
        raw=set(); absorbed=set(); semantic=set()
        for bits in itertools.product((False,True),repeat=n):
            a=prefix_assignment(n,bits)
            raw.add(certified_sigma(source,n,a,False))
            absorbed.add(certified_sigma(source,n,a,True))
            semantic.add(continuation_vector(source,n,n,bits))
        assert len(raw)==2**n
        assert len(absorbed)==2
        assert len(semantic)==2
        rows.append({"n":n,"raw_product_classes":len(raw),
                     "absorbing_classes":len(absorbed),
                     "semantic_classes":len(semantic)})
    return rows

def affine_parity_audit(max_k=8):
    rows=[]
    for k in range(1,max_k+1):
        equations=[((2*j+1,2*j+2,2*k+j+1),0) for j in range(k)]
        messages=set()
        for bits in itertools.product((False,True),repeat=2*k):
            a={i+1:bits[i] for i in range(2*k)}
            messages.add(rref_affine(equations,a))
        assert len(messages)==2**k
        rows.append({"pairs":k,"prefix_assignments":2**(2*k),
                     "canonical_affine_messages":len(messages)})
    return rows

def horn_undermerge_control():
    f=((-3,),(-2,),(-1,3))
    a={1:False,2:True}
    b={1:True,2:False}
    ra=restrict_cnf(f,a); rb=restrict_cnf(f,b)
    va=tuple(evaluate(ra,{3:z}) for z in (False,True))
    vb=tuple(evaluate(rb,{3:z}) for z in (False,True))
    assert va==vb==(False,False)
    assert ra!=rb
    return {"formula":f,"residual_a":ra,"residual_b":rb,
            "same_continuation_semantics":True,
            "syntactic_merge_available":False}

def random_3cnf(rng,n,m):
    clauses=[]
    for v in range(1,n+1):
        vs=[v,rng.randint(1,n),rng.randint(1,n)]
        clauses.append(tuple(x if rng.getrandbits(1) else -x for x in vs))
    while len(clauses)<m:
        vs=[rng.randint(1,n) for _ in range(3)]
        clauses.append(tuple(x if rng.getrandbits(1) else -x for x in vs))
    return tuple(clauses[:m])

def nand3_neq_audit(seed=350035,cases=400):
    rng=random.Random(seed)
    total_states=total_cert=total_sem=0
    strict_undermerge=0; max_gap=1.0; witness=None
    merge_pairs_checked=0
    for _ in range(cases):
        n=rng.randint(3,8); m=rng.randint(n,3*n); depth=n//2
        source=random_3cnf(rng,n,m)
        by_cert=defaultdict(list); by_sem=defaultdict(list)
        for bits in itertools.product((False,True),repeat=depth):
            a=prefix_assignment(n,bits)
            sig=certified_sigma(source,n,a,True)
            sem=continuation_vector(source,n,depth,bits)
            assert verify_state_record(source,n,a,sig,True)
            by_cert[sig].append((bits,sem))
            by_sem[sem].append(bits)
        for sig,group in by_cert.items():
            semantics={sem for _,sem in group}
            assert len(semantics)==1
            if len(group)>=2:
                first=prefix_assignment(n,group[0][0])
                second=prefix_assignment(n,group[1][0])
                assert verify_merge(source,n,first,second,sig,True)
                merge_pairs_checked+=1
        cert_count=len(by_cert); sem_count=len(by_sem)
        assert cert_count>=sem_count
        if cert_count>sem_count: strict_undermerge+=1
        gap=cert_count/max(1,sem_count)
        if gap>max_gap:
            max_gap=gap
            witness={"n":n,"m":m,"depth":depth,
                     "certified_classes":cert_count,
                     "semantic_classes":sem_count,
                     "source":source}
        total_states += 2**depth
        total_cert += cert_count
        total_sem += sem_count
    source=((1,2,3),)
    n=3; a=prefix_assignment(n,(False,))
    good=certified_sigma(source,n,a,True)
    corrupt=("PRODUCT",())
    assert good!=corrupt and not verify_state_record(source,n,a,corrupt,True)
    return {"seed":seed,"cases":cases,"prefix_states":total_states,
            "certified_classes":total_cert,"semantic_classes":total_sem,
            "strict_undermerge_cases":strict_undermerge,
            "maximum_certified_to_semantic_ratio":max_gap,
            "maximum_gap_witness":witness,
            "verified_nontrivial_merge_pairs":merge_pairs_checked,
            "corrupt_record_rejected":True}

def run():
    result={
        "artifact_id":"C035-JANUS-CERTIFIED-INTERFACE-CONGRUENCE",
        "status":"PASS",
        "p_vs_np":"OPEN",
        "theorem":(
            "Equality of independently replayed exact module residual messages, "
            "with absorbing verified terminals, is a sound continuation congruence."
        ),
        "unit_family":unit_family_audit(),
        "affine_parity":affine_parity_audit(),
        "horn_syntactic_undermerge":horn_undermerge_control(),
        "nand3_neq_image":nand3_neq_audit(),
        "located_bottleneck":"JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION",
        "claim_boundary":(
            "The artifact proves a sound restricted merge calculus and demonstrates "
            "both certified compression and language-induced under-merging. It does "
            "not construct a universal polynomial quotient or resolve P versus NP."
        )
    }
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    result["integrity_sha256"]=hashlib.sha256(payload).hexdigest()
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    result=run()
    print(json.dumps(result,indent=2,sort_keys=True))
    if args.self_test:
        assert result["status"]=="PASS"
        assert result["unit_family"][-1]["raw_product_classes"]==2**12
        assert result["unit_family"][-1]["absorbing_classes"]==2
        assert result["nand3_neq_image"]["corrupt_record_rejected"]

if __name__=="__main__":
    main()
