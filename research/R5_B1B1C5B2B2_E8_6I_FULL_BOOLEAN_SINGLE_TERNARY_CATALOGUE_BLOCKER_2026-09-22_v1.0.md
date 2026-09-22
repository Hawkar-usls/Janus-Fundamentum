# R5 E8 6I — Full Boolean Single-Ternary Tractable-Algebra Blocker

Date: 2026-09-22

Authority: EXACT_FINITE_DOMAIN_CLASSIFICATION_BLOCKER__NO_GLOBAL_PROMOTION

## Source-bound classification

For Boolean CSPs, Schaefer/Post imply that a non-essentially-unary polymorphism generates one of the canonical tractable Boolean operations (min/max/majority/minority), while the projection-only idempotent regime is NP-complete.

This permits an exact finite classification of one-signature ternary Boolean algebra donors.

## Frozen catalogue

There are exactly 256 ternary Boolean operations.

Among them, 248 depend on at least two arguments.

Add CONST_0 and CONST_1, which are trivially tractable algebras.

Exclude the six nonconstant essentially-unary ternary operations x, y, z, NOT x, NOT y, NOT z.

Thus the frozen maximal single-ternary Boolean tractable catalogue has |B_all| = 250.

## Exact paired-clause test

Freeze the two relations on one scope:

    R_plus  = x OR y OR z
    R_minus = NOT x OR NOT y OR NOT z

Their conjunction is Boolean NAE(x,y,z).

For every ordered triple (A_f,A_g,A_h) in B_all^3, the checker tests by the literal definition of preservation whether the mixed coordinate-wise operation tuple preserves both relations.

Checker:
research/tools/r5_e8_6i_full_boolean_single_ternary_catalogue_checker.py

Receipt:
research/R5_B1B1C5B2B2_E8_6I_FULL_BOOLEAN_SINGLE_TERNARY_CATALOGUE_BLOCKER_2026-09-22_v1.0.json

## Exact result

The complete surviving induced relation contains 1494 ordered algebra-label triples.

Breakdown:

    0 constant labels = 0
    1 constant label  = 0
    2 constant labels = 1488
    3 constant labels = 6

Every surviving triple contains both CONST_0 and CONST_1.

With exactly two constants:

    choose nonconstant coordinate = 3
    choose orientation of CONST_0 / CONST_1 = 2
    choose arbitrary nonessential ternary operation = 248
    3 * 2 * 248 = 1488

With three constants, exactly the six non-monochromatic Boolean triples survive.

Therefore the paired induced relation is exactly: every scope contains at least one CONST_0 and at least one CONST_1.

## Prototype core

Restrict the induced-label domain to {CONST_0,CONST_1}. The paired relation becomes exactly Boolean NAE.

Conversely, map every nonconstant label to CONST_0. Every surviving triple already contains both constants, so this map is a retraction of the paired induced relation.

Hence the paired induced prototype template is homomorphically equivalent to Boolean NAE.

Monotone NAE-3SAT is NP-complete by the Boolean CSP dichotomy.

Therefore the prototype layer on this paired-clause sublanguage is NP-complete unless P=NP.

## Meaning for 6I

This closes much more than B4:

    ALL single basic ternary Boolean tractable algebras
    = INSUFFICIENT

The failure mechanism is exact: nonconstant tractable algebra labels cannot jointly preserve the paired NAE clause gadget; surviving prototypes must expose Boolean constants, and the prototype core retracts to the original NAE choice.

Thus the induced layer has not removed semantic choice; it has relabeled it.

## What is still open

This result does not rule out:

    MULTI-OPERATION ALGEBRAS
    MULTI-SORTED SIGNATURES
    LIFTED DOMAINS
    NON-BOOLEAN AUXILIARY DOMAINS
    INSTANCE-GENERATED PROOF-CARRYING ALGEBRA FAMILIES
    RECURSIVE ALGEBRAIC LIFTS WITH A PROVED DECREASING POTENTIAL

These are now the legitimate descendants of 6I.

## Claim ceiling

    P_VS_NP = OPEN
    D1 = EMPTY
    SUCCESSOR_ALGORITHM = LOCKED
    SINGLE_TERNARY_BOOLEAN_6I = BLOCKED
    NEXT EXACT TARGET = MULTI_OPERATION / LIFTED DOMAIN COVERAGE_DISCOVERY BRIDGE
