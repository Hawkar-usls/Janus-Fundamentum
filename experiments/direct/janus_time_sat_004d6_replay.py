#!/usr/bin/env python3
"""Independent-code, same-administrator original-CNF resolution proof replay.

Does not call the 004D6 resolver; validates its exact steps and independently
recomputes all newly witnessed parity mask sets. NOT an external 004C witness.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import json


def _normal(row):
    if any(type(l) is not int or l==0 for l in row):
        return None
    s=set(row)
    if any(-v in s for v in s):
        return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))


def _replay_pair(pos,neg,pivot):
    if type(pivot) is not int or pivot<=0 or pivot not in pos or -pivot not in neg:
        return None
    merged=(set(pos)-{pivot}) | (set(neg)-{-pivot})
    if any(-v in merged for v in merged):
        return None
    if not 1<=len(merged)<=4:
        return None
    return tuple(sorted(merged,key=lambda x:(abs(x),x<0)))


def replay_all(rows,n,result):
    if result.get("status")!="SOURCE_RESOLUTION_BOUNDED_PASS":
        return False
    if result.get("source_n")!=n or result.get("source_clauses")!=len(rows):
        return False
    if result.get("original_clause_count_retained")!=len(rows):
        return False
    logical=json.dumps({"n":n,"rows":rows},separators=(",",":"))
    if sha256(logical.encode("ascii")).hexdigest()!=result.get("source_logical_sha256"):
        return False
    proof=result.get("resolution_proof_DAG")
    if type(proof) is not list or len(proof)>2000:
        return False
    table={}
    for i,clause in enumerate(rows):
        normalized=_normal(clause)
        if normalized is not None and len(normalized)<=4 and len(normalized)>=1:
            table[i]=normalized
    for j,step in enumerate(proof):
        if type(step) is not dict or type(step.get("id")) is not int:
            return False
        expected_id=len(rows)+j
        if step["id"]!=expected_id:
            return False
        parents=step.get("parents")
        if (type(parents) is not list or len(parents)!=2
            or any(type(p) is not int or p not in table or p>=expected_id for p in parents)):
            return False
        claim=step.get("clause")
        if type(claim) is not list or any(type(x) is not int for x in claim):
            return False
        computed=_replay_pair(table[parents[0]],table[parents[1]],step.get("pivot"))
        if computed is None or tuple(claim)!=computed:
            return False
        table[expected_id]=computed
    # Independently re-create complete sign masks from verified source+proof.
    groups=defaultdict(set)
    derived_groups=defaultdict(set)
    for i,clause in table.items():
        vars_=tuple(sorted(abs(x) for x in clause))
        if len(vars_)!=len(clause) or not 1<=len(vars_)<=4:
            return False
        mask=sum(1<<j for j,v in enumerate(vars_) if -v in clause)
        groups[vars_].add(mask)
        if i>=len(rows):
            derived_groups[vars_].add(mask)
    source_groups=defaultdict(set)
    for clause in rows:
        ncl=_normal(clause)
        if ncl is None or not 1<=len(ncl)<=4:continue
        support=tuple(sorted(abs(v) for v in ncl))
        mask=sum(1<<i for i,v in enumerate(support) if -v in ncl)
        source_groups[support].add(mask)

    discovered={}
    for support,masks in groups.items():
        for parity in (0,1):
            want={m for m in range(1<<len(support)) if m.bit_count()%2==parity}
            if not want.issubset(masks) or want.issubset(source_groups[support]):
                continue
            if not any(m in derived_groups[support] for m in want):
                return False
            discovered[(support,1^parity)]=want
    if result.get("new_complete_xor_sign_mask_equations")!=len(discovered):
        return False
    samples=result.get("new_witness_examples")
    if type(samples) is not list or len(samples)>8:
        return False
    for item in samples:
        if item.get("certificate")!="SOURCE_EXACT_RESOLUTION_DAG_AND_FULL_MASKS":
            return False
        vars_=item.get("variables");rhs=item.get("rhs")
        if type(vars_) is not list or vars_!=sorted(set(vars_)) or not 1<=len(vars_)<=4:
            return False
        if type(rhs) is not int or rhs not in (0,1):
            return False
        key=(tuple(vars_),rhs)
        if key not in discovered:
            return False
        ids=item.get("clause_ids")
        if type(ids) is not list or len(ids)!=(1<<(len(vars_)-1)):
            return False
        if len(set(ids))!=len(ids) or any(type(i) is not int or i not in table for i in ids):
            return False
        masks=set()
        for i in ids:
            clause=table[i]
            if tuple(sorted(abs(v) for v in clause))!=key[0]:
                return False
            mask=sum(1<<j for j,v in enumerate(key[0]) if -v in clause)
            masks.add(mask)
        if masks!=discovered[key] or not any(i>=len(rows) for i in ids):
            return False
    return True
