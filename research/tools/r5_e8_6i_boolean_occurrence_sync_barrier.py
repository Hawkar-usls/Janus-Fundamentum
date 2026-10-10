#!/usr/bin/env python3
"""Exact Boolean B4 occurrence-synchronization / domain-permutation checker.

It checks the finite algebra identities behind the symbolic theorem:
EQ preserves (f,g) iff f=g;
NEQ preserves (f,g) iff g=dual(f);
B4 is closed under Boolean conjugation;
and exhaustive occurrence orientations cannot rescue the NAE3 two-clause witness.

No SAT solving is used.
"""
from __future__ import annotations

import itertools
import json

D=(0,1)
LABELS=("AND3","OR3","MAJ3","XOR3")


def op(label,a,b,c):
    if label=="AND3": return a & b & c
    if label=="OR3": return a | b | c
    if label=="MAJ3": return int(a+b+c>=2)
    if label=="XOR3": return a ^ b ^ c
    raise KeyError(label)


def table(label):
    return tuple(op(label,*x) for x in itertools.product(D,repeat=3))


def dual_table(label):
    out=[]
    for x in itertools.product(D,repeat=3):
        nx=tuple(1-v for v in x)
        out.append(1-op(label,*nx))
    return tuple(out)


TABLE_TO_LABEL={table(l):l for l in LABELS}
DUAL={l:TABLE_TO_LABEL[dual_table(l)] for l in LABELS}


def pair_preserved(relation,label_a,label_b):
    allowed=set(relation)
    rows=tuple(relation)
    for r0,r1,r2 in itertools.product(rows,repeat=3):
        out=(
            op(label_a,r0[0],r1[0],r2[0]),
            op(label_b,r0[1],r1[1],r2[1]),
        )
        if out not in allowed:
            return False
    return True


def transform_relation(relation,orient):
    # orient_i=1 means complement coordinate i.
    return tuple(sorted({
        tuple((1-row[i]) if orient[i] else row[i] for i in range(len(row)))
        for row in relation
    }))


def preserves(relation,labels):
    allowed=set(relation)
    for rs in itertools.product(relation,repeat=3):
        out=tuple(op(labels[j],rs[0][j],rs[1][j],rs[2][j]) for j in range(len(labels)))
        if out not in allowed:
            return False
    return True


def normalize_label(local_label,orientation):
    # Pull local operation back through the Boolean coordinate permutation.
    return DUAL[local_label] if orientation else local_label


def clause(signs):
    out=[]
    for row in itertools.product(D,repeat=3):
        vals=[row[i] if signs[i] else 1-row[i] for i in range(3)]
        if any(vals):
            out.append(row)
    return tuple(out)


def build_receipt():
    eq=((0,0),(1,1))
    neq=((0,1),(1,0))
    eq_pairs=[]
    neq_pairs=[]
    for a,b in itertools.product(LABELS,repeat=2):
        if pair_preserved(eq,a,b): eq_pairs.append((a,b))
        if pair_preserved(neq,a,b): neq_pairs.append((a,b))

    assert set(eq_pairs)=={(x,x) for x in LABELS}
    assert set(neq_pairs)=={(x,DUAL[x]) for x in LABELS}
    assert DUAL=={"AND3":"OR3","OR3":"AND3","MAJ3":"MAJ3","XOR3":"XOR3"}

    # Exhaustive conjugation identity for all 8 signed clause relations,
    # all 8 Boolean coordinate orientations and all 64 B4 label triples.
    conjugation_checks=0
    for signs in itertools.product((0,1),repeat=3):
        rel=clause(signs)
        for orient in itertools.product((0,1),repeat=3):
            transformed=transform_relation(rel,orient)
            for local_labels in itertools.product(LABELS,repeat=3):
                normalized=tuple(normalize_label(local_labels[i],orient[i]) for i in range(3))
                assert preserves(transformed,local_labels)==preserves(rel,normalized)
                conjugation_checks+=1

    # Occurrence-split NAE witness: two clause copies, each occurrence may be
    # independently oriented. Synchronization then forces local labels to be
    # equal/dual, which is exactly one normalized label per original variable.
    pos=clause((1,1,1))
    neg=clause((0,0,0))
    split_solutions=0
    combinations_checked=0
    for orient_pos in itertools.product((0,1),repeat=3):
        rpos=transform_relation(pos,orient_pos)
        for orient_neg in itertools.product((0,1),repeat=3):
            rneg=transform_relation(neg,orient_neg)
            for normalized in itertools.product(LABELS,repeat=3):
                labels_pos=tuple(DUAL[normalized[i]] if orient_pos[i] else normalized[i] for i in range(3))
                labels_neg=tuple(DUAL[normalized[i]] if orient_neg[i] else normalized[i] for i in range(3))
                combinations_checked+=1
                if preserves(rpos,labels_pos) and preserves(rneg,labels_neg):
                    split_solutions+=1
    assert split_solutions==0

    return {
      "schema":"janus.r5_e8_6i.boolean_occurrence_sync_barrier.v1",
      "status":"PASS_EXACT_GENERAL_IDENTITY_PLUS_NAE_CONTROL",
      "library":list(LABELS),
      "dual_map":DUAL,
      "equality_preserving_label_pairs":[list(x) for x in sorted(eq_pairs)],
      "disequality_preserving_label_pairs":[list(x) for x in sorted(neq_pairs)],
      "symbolic_identities":{
        "EQ":"PRESERVED_IFF_LOCAL_OPERATIONS_EQUAL",
        "NEQ":"PRESERVED_IFF_SECOND_OPERATION_IS_BOOLEAN_DUAL_OF_FIRST",
        "coordinate_permutation":"PRESERVATION_AFTER_BOOLEAN_RENAMING_IFF_ORIGINAL_RELATION_PRESERVED_BY_CONJUGATED_OPERATIONS"
      },
      "exhaustive_checks":{
        "signed_clause_relations":8,
        "coordinate_orientations_per_relation":8,
        "label_triples_per_orientation":64,
        "conjugation_equivalences_checked":conjugation_checks,
        "nae_split_orientation_pairs":64,
        "nae_normalized_label_triples":64,
        "nae_split_combinations_checked":combinations_checked,
        "nae_split_prototype_count":split_solutions
      },
      "consequence":{
        "BOOLEAN_OCCURRENCE_SPLITTING_WITH_EQ_NEQ_AND_ID_NOT_RENAMING_CAN_RESCUE_B4":False,
        "meaning":"SUCH_A_LIFT_IS_ONLY_BOOLEAN_DOMAIN_CONJUGATION_OF_THE_ORIGINAL_VARIABLEWISE_B4_PROTOTYPE",
        "next_required_class":"RICHER_LIFTED_DOMAIN_OR_NON_BIJECTIVE_AUXILIARY_RELATIONS_OR_GENUINELY_NONLOCAL_PREPROCESSING"
      },
      "firewall":{
        "P_VS_NP":"OPEN","D1":"EMPTY","SUCCESSOR_ALGORITHM":"LOCKED",
        "scope":"BOOLEAN_BIJECTIVE_OCCURRENCE_REFORMULATION_WITH_EQ_NEQ_SYNCHRONIZATION"
      }
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),indent=2,sort_keys=True))
