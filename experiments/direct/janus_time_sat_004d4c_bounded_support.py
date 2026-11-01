#!/usr/bin/env python3
"""JANUS TIME-SAT-004D4C: bounded-support complete-XOR partial source partition.

A strict, conservative alternative to 004D4's ALL-OR-NOTHING group-budget
abstention. Keep at most max_groups distinct source supports in the index,
continue validating ALL original clauses, and retain any unindexed clauses
unchanged as ordinary CNF. Every extracted parity equation is witnessed
by a COMPLETE original-source sign-mask group. Exhaustive truth equivalence
on tiny controls; original-source SAT model verification still mandatory.

Never claim no XOR exists when index budget is reached. Never claim SAT/UNSAT.
Not a universal SAT solver, a performance win, or a production component.
"""
from __future__ import annotations
from janus_time_sat_004d1_xor import (
    MAX_N, MAX_ROWS, MAX_LITERALS, MAX_GROUPS, MAX_WIDTH, source_digest
)

def extract_bounded_mixed_xor(rows, n, *, max_groups=MAX_GROUPS):
    if type(n) is not int or not 1<=n<=MAX_N:
        return {"status":"ABSTAIN_INVALID_N"}
    if type(max_groups) is not int or not 1<=max_groups<=MAX_GROUPS:
        return {"status":"ABSTAIN_INVALID_SUPPORT_BUDGET"}
    if len(rows)>MAX_ROWS:
        return {"status":"ABSTAIN_ROW_BUDGET"}
    supports={}
    literals=0
    skipped_unindexed_clause_rows=0
    unsupported_or_repeated_clause_rows=0
    for index,row in enumerate(rows):
        literals+=len(row)
        if literals>MAX_LITERALS:
            return {"status":"ABSTAIN_LITERAL_BUDGET"}
        if any(type(x) is not int or not 1<=abs(x)<=n for x in row):
            return {"status":"ABSTAIN_INVALID_LITERAL"}
        if not 1<=len(row)<=MAX_WIDTH:
            unsupported_or_repeated_clause_rows+=1
            continue
        support=tuple(sorted(abs(v) for v in row))
        if len(set(support))!=len(support):
            unsupported_or_repeated_clause_rows+=1
            continue
        if support not in supports:
            if len(supports)==max_groups:
                skipped_unindexed_clause_rows+=1
                continue
            supports[support]={}
        negatives={abs(v) for v in row if v<0}
        mask=sum(1<<j for j,v in enumerate(support) if v in negatives)
        supports[support].setdefault(mask,[]).append(index)
    equations=[]
    consumed=set()
    for support,signs in sorted(supports.items()):
        width=len(support)
        for parity in (0,1):
            masks=[m for m in range(1<<width) if m.bit_count()%2==parity]
            if not all(m in signs for m in masks):
                continue
            indices=[signs[m][0] for m in masks]
            if any(i in consumed for i in indices):
                raise AssertionError("overlapping source allocation")
            for m,i in zip(masks,indices):
                wanted={(-v if (m>>j)&1 else v) for j,v in enumerate(support)}
                if len(rows[i])!=len(support) or set(rows[i])!=wanted:
                    raise AssertionError("source XOR sign-mask not identical")
            consumed.update(indices)
            equations.append({
                "variables":list(support),
                "rhs":1^parity,
                "original_clause_indices":indices
            })
    residual_indices=[i for i in range(len(rows)) if i not in consumed]
    if len(consumed)+len(residual_indices)!=len(rows):
        raise AssertionError("source clause lost during conservative partition")
    if len(consumed)!=sum(len(e["original_clause_indices"]) for e in equations):
        raise AssertionError("source clause allocated to more than one equation")
    return {
        "schema":"JANUS-TIME-SAT-004D4C-SUPPORT-CAPPED-LOSSLESS-PARTITION-V1",
        "status":"SOURCE_PARTITION_VERIFIED",
        "source_n":n,
        "source_clauses":len(rows),
        "source_logical_sha256":source_digest(rows,n),
        "complete_xor_equation_count":len(equations),
        "equations":equations,
        "xor_source_clause_indices":sorted(consumed),
        "residual_source_clause_indices":residual_indices,
        "residual_clauses":[list(rows[i]) for i in residual_indices],
        "source_xor_clauses":len(consumed),
        "source_residual_clauses":len(residual_indices),
        "indexed_unique_support_count":len(supports),
        "indexed_support_limit":max_groups,
        "index_exhausted":skipped_unindexed_clause_rows>0,
        "skipped_unindexed_source_clause_rows":skipped_unindexed_clause_rows,
        "unsupported_or_repeated_clause_rows":unsupported_or_repeated_clause_rows,
        "interpretation_when_index_exhausted":"PARTIAL_SCAN_NOT_PROOF_OF_ZERO_XOR_IN_SKIPPED_SOURCE",
        "SAT_or_UNSAT_verdict":"NOT_ATTEMPTED_SOURCE_ONLY",
        "original_clauses_unmodified":True,
        "production_C023":"UNCHANGED",
        "external_administrative_witness":"NOT_PERFORMED"
    }
