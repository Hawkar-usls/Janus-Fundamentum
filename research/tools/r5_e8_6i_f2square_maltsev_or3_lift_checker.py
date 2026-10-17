#!/usr/bin/env python3
"""Exact F2^2 Mal'tsev OR3 lift classification for JANUS R5 E8 6I.

Carrier:
    A4 = F2^2
    m(x,y,z) = x XOR y XOR z
Every nonempty subalgebra of A4^3 is an affine subspace (coset) of F2^6.

For arbitrary surjective Boolean coordinate decoders pi_i:A4->{0,1},
the checker classifies when an affine subalgebra has exact decoder image OR3.

Symmetry reduction is exact:
AGL(2,2) has 24 elements and acts as S4 on the four carrier points.
Therefore decoder liftability depends only on the cardinalities
w_i = |pi_i^{-1}(1)| in {1,2,3}.

Result for positive OR3:
    exact affine lift exists iff at least two w_i are 3.

For a signed literal, complement the decoder if the literal is negated,
so the same theorem becomes:
    exact signed-clause lift exists iff at least two sign-adjusted
    decoder 1-fibres have size 3.

This gives a polynomial 2-SAT prototype layer, but only a strict subclass
of 3-SAT. No SAT oracle or heuristic search is used.
"""
from __future__ import annotations

import collections
import itertools
import json

BITS=(0,1)
V=tuple(range(4))  # F2^2 encoded as two-bit integers
POINTS=tuple(range(64))  # F2^6 = (F2^2)^3


def coord(point:int,j:int)->int:
    return (point>>(2*j))&3


def span_add(S:frozenset[int],v:int)->frozenset[int]:
    return frozenset(set(S)|{x^v for x in S})


def all_linear_subspaces()->tuple[frozenset[int],...]:
    zero=frozenset({0})
    seen={zero}
    q=collections.deque([zero])
    while q:
        S=q.popleft()
        for v in POINTS:
            if v in S:
                continue
            T=span_add(S,v)
            if T not in seen:
                seen.add(T)
                q.append(T)
    return tuple(sorted(seen,key=lambda s:(len(s),tuple(sorted(s)))))


def all_affine_subspace_masks(linear)->tuple[int,...]:
    masks=set()
    for S in linear:
        unseen=set(POINTS)
        while unseen:
            a=min(unseen)
            C={x^a for x in S}
            mask=0
            for x in C:
                mask|=1<<x
            masks.add(mask)
            unseen-=C
    return tuple(sorted(masks))


def mat_apply(rows:tuple[int,int],x:int)->int:
    xb=(x&1,(x>>1)&1)
    out=0
    for i,row in enumerate(rows):
        bit=((row&1)*xb[0]+(((row>>1)&1)*xb[1]))&1
        out|=bit<<i
    return out


def agl_permutations()->tuple[tuple[int,...],...]:
    perms=set()
    for r0 in range(4):
        for r1 in range(4):
            # invertible iff the two row vectors are independent/nonzero/distinct
            if r0==0 or r1==0 or r0==r1:
                continue
            rows=(r0,r1)
            image={mat_apply(rows,x) for x in V}
            if len(image)!=4:
                continue
            for b in V:
                perms.add(tuple(mat_apply(rows,x)^b for x in V))
    return tuple(sorted(perms))


def canonical_decoder(weight:int)->tuple[int,...]:
    assert weight in (1,2,3)
    return tuple(1 if x<weight else 0 for x in V)


def target_or_mask()->int:
    mask=0
    for row in itertools.product(BITS,repeat=3):
        if any(row):
            code=(row[0]<<2)|(row[1]<<1)|row[2]
            mask|=1<<code
    return mask


OR_MASK=target_or_mask()


def fibre_masks(weights:tuple[int,int,int])->tuple[int,...]:
    dec=[canonical_decoder(w) for w in weights]
    fibres=[0]*8
    for p in POINTS:
        row=tuple(dec[j][coord(p,j)] for j in range(3))
        code=(row[0]<<2)|(row[1]<<1)|row[2]
        fibres[code]|=1<<p
    return tuple(fibres)


def exact_or_lift_exists(affine_masks,weights):
    fibres=fibre_masks(weights)
    forbidden=fibres[0]
    wanted=fibres[1:]
    # Seven Boolean image tuples require at least seven carrier tuples.
    # Affine-subspace cardinalities are powers of two, hence only size >=8 matters.
    for S in affine_masks:
        if S.bit_count()<8:
            continue
        if S&forbidden:
            continue
        if all(S&F for F in wanted):
            return True,S
    return False,None


def verify_agl_decoder_symmetry(perms)->None:
    assert len(perms)==24
    # AGL(2,2) is all of S4 on the carrier.
    assert len(set(perms))==24
    all_subsets={
        w:{frozenset(C) for C in itertools.combinations(V,w)}
        for w in (1,2,3)
    }
    for w in (1,2,3):
        base=frozenset(x for x,b in enumerate(canonical_decoder(w)) if b)
        orbit={
            frozenset(p[x] for x in base)
            for p in perms
        }
        assert orbit==all_subsets[w]


def build_receipt():
    perms=agl_permutations()
    verify_agl_decoder_symmetry(perms)

    linear=all_linear_subspaces()
    affine_masks=all_affine_subspace_masks(linear)
    assert len(linear)==2825
    assert len(affine_masks)==26387

    pattern_results={}
    witnesses={}
    for weights in itertools.product((1,2,3),repeat=3):
        exists,S=exact_or_lift_exists(affine_masks,weights)
        expected=sum(1 for w in weights if w==3)>=2
        assert exists==expected
        key="".join(map(str,weights))
        pattern_results[key]=exists
        if S is not None:
            witnesses[key]={
                "size":S.bit_count(),
                "points":[p for p in POINTS if (S>>p)&1],
            }

    good_patterns=[k for k,v in pattern_results.items() if v]
    assert len(good_patterns)==7

    # Count all concrete surjective decoder triples.
    multiplicity={1:4,2:6,3:4}
    concrete_positive_count=0
    for weights in itertools.product((1,2,3),repeat=3):
        if pattern_results["".join(map(str,weights))]:
            prod=1
            for w in weights:
                prod*=multiplicity[w]
            concrete_positive_count+=prod
    assert concrete_positive_count==544

    # Strictness witness: positive and all-negative clauses cannot both have
    # threshold-2 coarse certificates because each variable can be POS, NEG or NEUTRAL.
    strict_coarse=[]
    for states in itertools.product(("P","N","Z"),repeat=3):
        plus=sum(s=="P" for s in states)>=2
        minus=sum(s=="N" for s in states)>=2
        if plus and minus:
            strict_coarse.append(states)
    assert strict_coarse==[]

    return {
        "schema":"janus.r5_e8_6i.f2square_maltsev_or3_lift_classification.v1",
        "status":"PASS_EXACT_FIXED_CARRIER_CLASSIFICATION",
        "carrier":{
            "domain":"F2^2",
            "domain_size":4,
            "basic_operation":"m(x,y,z)=x XOR y XOR z",
            "maltsev":True,
            "A4_cubed_identification":"F2^6",
            "subalgebras":"NONEMPTY_AFFINE_SUBSPACES"
        },
        "symmetry":{
            "AGL_2_2_size":len(perms),
            "acts_as_full_S4_on_carrier":True,
            "surjective_decoder_orbits_by_one_fibre_size":[1,2,3],
            "concrete_decoder_counts":{"1":4,"2":6,"3":4}
        },
        "enumeration":{
            "linear_subspaces_F2_6":len(linear),
            "affine_subspaces_F2_6":len(affine_masks),
            "canonical_weight_triples_checked":27,
            "good_weight_triples":len(good_patterns),
            "concrete_surjective_decoder_triples":14**3,
            "concrete_positive_OR3_liftable_decoder_triples":concrete_positive_count
        },
        "exact_positive_OR3_characterization":{
            "iff":"AT_LEAST_TWO_DECODERS_HAVE_ONE_FIBRE_SIZE_3",
            "good_weight_patterns":good_patterns,
            "canonical_witnesses":witnesses
        },
        "signed_clause_characterization":{
            "sign_adjustment":"NEGATED_LITERAL_REPLACES_WEIGHT_w_BY_4_MINUS_w",
            "iff":"AT_LEAST_TWO_SIGN_ADJUSTED_DECODER_ONE_FIBRES_HAVE_SIZE_3",
            "coarse_decoder_states":{
                "P":"weight_3__active_for_positive_literal_only",
                "N":"weight_1__active_for_negative_literal_only",
                "Z":"weight_2__active_for_neither_sign"
            },
            "prototype_encoding":"2SAT_WITH_P_x_N_x_MUTEX_AND_PAIRWISE_AT_LEAST_TWO_CLAUSE_CONSTRAINTS"
        },
        "lifecycle":{
            "prototype_discovery":"2SAT_POLYNOMIAL",
            "local_lift_lookup":"FINITE_FIXED_A4_TABLE",
            "lifted_relations":"AFFINE_SUBSPACES_OF_POWERS_OF_F2^2",
            "lifted_solver":"MALTSEV_CSP_POLYNOMIAL",
            "reconstruction":"COORDINATE_BOOLEAN_DECODER",
            "hidden_SAT_oracle":False
        },
        "strictness_control":{
            "formula":"(x OR y OR z) AND (NOT x OR NOT y OR NOT z)",
            "original_formula_satisfiable":True,
            "coarse_prototype_count":0,
            "verdict":"STRICT_SUBCLASS_NOT_UNIVERSAL"
        },
        "source_bound_algorithm_donor":{
            "title":"A Simple Algorithm for Mal'tsev Constraints",
            "authors":["Andrei Bulatov","Victor Dalmau"],
            "doi":"10.1137/050628957",
            "url":"https://doi.org/10.1137/050628957"
        },
        "scientific_meaning":[
            "PURE_F2SQUARED_MALTSEV_IS_A_SECOND_COMPLETE_POLYNOMIAL_LIFT_ARCHITECTURE_CONTROL",
            "MORE_DECODER_STATES_AND_A_PURE_MALTSEV_SOLVER_STILL_REPRODUCE_THRESHOLD_TWO",
            "THIS_IS_A_FIXED_CARRIER_CLASSIFICATION_NOT_A_GENERAL_MALTSEV_LOWER_BOUND"
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
