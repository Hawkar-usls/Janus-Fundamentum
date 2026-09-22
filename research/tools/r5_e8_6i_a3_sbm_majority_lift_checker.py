#!/usr/bin/env python3
"""Exact 3-element semilattice-block-Mal'tsev lift positive control for 6I.

Algebra A3:
  domain D={0,1,2}
  congruence blocks B={0,1}, T={2}
  binary f:
      first projection inside B;
      2 absorbs cross-block inputs.
    Hence A3/sigma is the two-element join-semilattice.
  ternary m:
      XOR on B;
      trivial on T;
      first-block projection across mixed blocks.
    Hence every sigma block is Mal'tsev.

The checker enumerates every subalgebra of A3^3, every surjective decoder
pi:D->{0,1}, and every signed 3-clause.

Exact result:
  a clause has an exact decoded subalgebra lift for decoder triple
  (pi1,pi2,pi3) iff at least two signed values pi_j(2) satisfy the clause
  literals.

Thus decoder discovery over a 3-CNF is exactly a 2-SAT condition:
  AT_LEAST_2(l1,l2,l3)
  = (l1 OR l2) AND (l1 OR l3) AND (l2 OR l3).

This is a positive polynomial-lifecycle control, but not universal coverage.
"""
from __future__ import annotations

import collections
import itertools
import json

D=(0,1,2)
BITS=(0,1)
SIGNS=tuple(itertools.product((1,-1),repeat=3))
TUPLES=tuple(itertools.product(D,repeat=3))
INDEX={t:i for i,t in enumerate(TUPLES))


def block(a:int)->int:
    return 0 if a in (0,1) else 1


def f(a:int,b:int)->int:
    if block(a)==0 and block(b)==0:
        return a
    return 2


def m(a:int,b:int,c:int)->int:
    if block(a)==1:
        return 2
    if block(b)==0 and block(c)==0:
        return a ^ b ^ c
    return a


def verify_sbm()->None:
    # sigma is a congruence and quotient f is Boolean OR.
    for a,b in itertools.product(D,repeat=2):
        assert block(f(a,b))==(block(a)|block(b))

    # f is first projection on each sigma block.
    for B in ((0,1),(2,)):
        for a,b in itertools.product(B,repeat=2):
            assert f(a,b)==a

    # m is Mal'tsev on each block.
    for B in ((0,1),(2,)):
        for a,b in itertools.product(B,repeat=2):
            assert m(a,b,b)==a
            assert m(b,b,a)==a

    # sigma compatibility of m.
    for qa,qb,qc in itertools.product(BITS,repeat=3):
        values=set()
        for a in [x for x in D if block(x)==qa]:
            for b in [x for x in D if block(x)==qb]:
                for c in [x for x in D if block(x)==qc]:
                    values.add(block(m(a,b,c)))
        assert len(values)==1


FIDX=[
    [INDEX[tuple(f(x,y) for x,y in zip(TUPLES[i],TUPLES[j]))] for j in range(27)]
    for i in range(27)
]
MIDX=[
    [
        [
            INDEX[tuple(m(x,y,z) for x,y,z in zip(TUPLES[i],TUPLES[j],TUPLES[k]))]
            for k in range(27)
        ]
        for j in range(27)
    ]
    for i in range(27)
]


def closure(generators)->frozenset[int]:
    S=set(generators)
    changed=True
    while changed:
        changed=False
        cur=tuple(S)
        for i in cur:
            for j in cur:
                v=FIDX[i][j]
                if v not in S:
                    S.add(v);changed=True
        cur=tuple(S)
        for i in cur:
            for j in cur:
                for k in cur:
                    v=MIDX[i][j][k]
                    if v not in S:
                        S.add(v);changed=True
    return frozenset(S)


def all_subalgebras()->tuple[frozenset[int],...]:
    seen=set()
    queue=collections.deque()
    for i in range(27):
        C=closure({i})
        if C not in seen:
            seen.add(C);queue.append(C)
    while queue:
        S=queue.popleft()
        for i in range(27):
            if i in S:
                continue
            C=closure(set(S)|{i})
            if C not in seen:
                seen.add(C);queue.append(C)
    return tuple(sorted(seen,key=lambda s:(len(s),tuple(sorted(s)))))


def clause_relation(signs):
    out=[]
    for row in itertools.product(BITS,repeat=3):
        literals=[row[i] if signs[i]==1 else 1-row[i] for i in range(3)]
        if any(literals):
            out.append(row)
    assert len(out)==7
    return frozenset(out)


DECODERS=tuple(
    vals for vals in itertools.product(BITS,repeat=3)
    if set(vals)=={0,1}
)
assert len(DECODERS)==6


def decode_tuple(t,decoder_ids):
    return tuple(DECODERS[decoder_ids[j]][t[j]] for j in range(3))


def signed_top_majority(decoder_ids,signs)->bool:
    truths=[]
    for j in range(3):
        b=DECODERS[decoder_ids[j]][2]
        truths.append(b if signs[j]==1 else 1-b)
    return sum(truths)>=2


def build_receipt():
    verify_sbm()
    subs=all_subalgebras()
    assert len(subs)==2833

    allowed={}
    canonical_witness={}
    for signs in SIGNS:
        target=clause_relation(signs)
        rel=[]
        for decoder_ids in itertools.product(range(6),repeat=3):
            witness=None
            for S in subs:
                image=frozenset(
                    decode_tuple(TUPLES[i],decoder_ids)
                    for i in S
                )
                if image==target:
                    witness=S
                    break
            if witness is not None:
                rel.append(decoder_ids)
                canonical_witness[signs,decoder_ids]=witness

        expected=[
            d for d in itertools.product(range(6),repeat=3)
            if signed_top_majority(d,signs)
        ]
        assert sorted(rel)==sorted(expected)
        assert len(rel)==108
        allowed[signs]=rel

    # Strictness witness: original paired formula is satisfiable (NAE),
    # but no top-bit assignment satisfies >=2 true literals in both clauses.
    original_solutions=[]
    majority_lift_solutions=[]
    plus=(1,1,1)
    minus=(-1,-1,-1)
    for bits in itertools.product(BITS,repeat=3):
        if bits!=(0,0,0) and bits!=(1,1,1):
            original_solutions.append(bits)
        if sum(bits)>=2 and sum(1-b for b in bits)>=2:
            majority_lift_solutions.append(bits)
    assert len(original_solutions)==6
    assert majority_lift_solutions==[]

    # Each top bit has exactly three surjective decoder realizations.
    top_fibres={
        str(b):sum(1 for d in DECODERS if d[2]==b)
        for b in BITS
    }
    assert top_fibres=={"0":3,"1":3}

    return {
        "schema":"janus.r5_e8_6i.a3_sbm_majority_lift_positive_control.v1",
        "status":"PASS_EXACT_POLYNOMIAL_LIFT_POSITIVE_CONTROL",
        "algebra":{
            "domain":[0,1,2],
            "sigma_blocks":[[0,1],[2]],
            "quotient_f":"TWO_ELEMENT_JOIN_SEMILATTICE",
            "f_inside_nontrivial_block":"FIRST_PROJECTION",
            "m_inside_nontrivial_block":"BOOLEAN_XOR_MALTSEV",
            "sbm_axioms_checked":True
        },
        "enumeration":{
            "A3_cubed_tuple_count":27,
            "subalgebra_count":len(subs),
            "surjective_decoder_count":len(DECODERS),
            "decoder_triples_per_clause":216,
            "exact_lift_decoder_triples_per_signed_clause":108
        },
        "decoder_characterization":{
            "coarse_bit":"b(pi)=pi(2)",
            "exact_condition":"AT_LEAST_TWO_SIGNED_COARSE_BITS_SATISFY_THE_THREE_CLAUSE_LITERALS",
            "equivalent_2SAT":"(l1 OR l2) AND (l1 OR l3) AND (l2 OR l3)",
            "decoder_realizations_per_coarse_bit":top_fibres
        },
        "lifecycle":{
            "decoder_discovery":"2SAT_POLYNOMIAL",
            "lift_relation_lookup":"FINITE_CONSTANT_TABLE_AFTER_FIXED_A3_ENUMERATION",
            "lifted_relations":"SUBALGEBRAS_OF_A3_PRODUCTS",
            "lifted_solver":"SEMILATTICE_BLOCK_MALTSEV_POLYNOMIAL_ALGORITHM",
            "reconstruction":"COORDINATE_DECODER",
            "hidden_SAT_oracle":False
        },
        "strictness_control":{
            "formula":"(x OR y OR z) AND (NOT x OR NOT y OR NOT z)",
            "original_solution_count":6,
            "A3_majority_lift_coarse_solution_count":0,
            "verdict":"STRICT_SUBCLASS_NOT_UNIVERSAL"
        },
        "scientific_meaning":[
            "THIS_IS_A_COMPLETE_EXAMPLE_OF_THE_DESIRED_POLYNOMIAL_LIFT_ARCHITECTURE",
            "ITS_DISCOVERY_LAYER_IS_EXPLICIT_2SAT_NOT_HIDDEN_SAT",
            "ITS_COVERAGE_IS_ONLY_THE_TWO_TRUE_LITERALS_PER_CLAUSE_SUBCLASS",
            "THE_NEXT_TARGET_IS_TO_WEAKEN_THE_COARSE_THRESHOLD_FROM_TWO_TRUE_LITERALS_TO_ORDINARY_ONE_TRUE_LITERAL_WITHOUT_LOSING_TRACTABILITY"
        ],
        "firewall":{
            "P_VS_NP":"OPEN",
            "D1":"EMPTY",
            "SUCCESSOR_ALGORITHM":"LOCKED",
            "UNIVERSAL_3SAT_COVERAGE":False
        }
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),ensure_ascii=False,indent=2,sort_keys=True))
