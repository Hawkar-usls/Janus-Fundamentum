# R5 E8 6I — Clause-Local Sound-Cut Dichotomy

Date: 2026-09-23

Authority: PROVED_GENERAL_LOCAL_INTERFACE_BARRIER__REPRESENTATION_INDEPENDENT_WITHIN_SCOPE__NO_D1_PROMOTION

Parent: R5_E8_6I_NONLOCAL_GROUPED_RANK1_OBSTRUCTION_CURRENCY_GATE_V1

## 1. Frozen local semantic fact

For one signed clause, after sign normalization, the visible Boolean boundary is (a,b,c).

The genuine satisfying boundary relation is

    OR3 = {0,1}^3 minus {000}.

Thus OR3 contains seven of the eight possible boundary assignments.

## 2. Sound clause-local refinement

Let Y be any finite or succinct local auxiliary state for the clause. Let G subseteq {0,1}^3 x Y be the genuine local-lift relation, with projection

    proj_abc(G) = OR3.

Let C be any clause-local refinement predicate, in any representation/language, satisfying the sole soundness requirement

    every genuine local lift in G satisfies C.

Equivalently, G is a subset of C when C is viewed as an allowed set on the same local coordinates (possibly after adding witness coordinates existentially).

Let R_C be the visible boundary relation after imposing the local abstraction plus C and existentially eliminating all clause-local state.

Because all genuine lifts survive,

    OR3 subseteq R_C.

Because R_C is a Boolean ternary relation,

    R_C subseteq {0,1}^3.

There is exactly one tuple outside OR3, namely 000.

Therefore exactly two outcomes are possible:

    R_C = OR3
or
    R_C = TRUE3.

QED.

## 3. Consequence

Any sound clause-local refinement that communicates with the rest of the instance only through the original three Boolean boundary variables has an all-or-nothing semantics:

- TRUE3: it communicates no clause restriction;
- OR3: it reactivates the full original clause.

There is no third intermediate relation that could gradually transmit a new tractable compatibility summary.

This theorem is independent of whether the local cut is affine, Horn, nonlinear, polyhedral, polynomial-calculus-derived, or an arbitrary computable predicate.

## 4. Relation to the product-cut checker

The exhaustive 256-history product-cut checker is now a concrete positive replay of the general theorem:

- 254 histories realize TRUE3;
- 2 histories realize OR3.

The general dichotomy explains why no other projected relation could have appeared.

## 5. Global RAIL barrier

Any RAIL instantiation satisfying all of the following:

1. cuts are generated independently within individual clauses;
2. every cut is sound for every genuine local lift;
3. clause-local auxiliaries are existentially eliminated before the recursive/global solver;
4. the only exported interface is the original (a,b,c) boundary;

reduces globally to choosing a subset of original clauses to reactivate.

Thus it is clause-subformula refinement, not a new compression currency.

At full activation it returns the original 3CNF.

## 6. Exact escape condition

A surviving obstruction currency must violate at least one premise above. In practice it must use one of:

- a cut spanning multiple clauses / original variables;
- a richer exported interface whose state has a separately proved polynomial bound;
- a quotient/syndrome invariant that identifies many boundary assignments before projection;
- a recursive representation with a strictly decreasing global invariant.

Therefore the active target can be sharpened to:

    NONLOCAL CROSS-CLAUSE COMPRESSION CURRENCY.

## 7. Ceiling

    ANY SOUND CLAUSE-LOCAL PROJECTED CUT = TRUE3 OR OR3
    CLAUSE-LOCAL REFINEMENT = NO NEW INTERMEDIATE SEMANTICS
    CROSS-CLAUSE / RICH-INTERFACE CURRENCY = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
