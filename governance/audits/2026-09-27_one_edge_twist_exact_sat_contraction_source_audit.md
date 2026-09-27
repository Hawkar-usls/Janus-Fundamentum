# Source audit — One-Edge-Twist 2-Lift Exact SAT Contraction

Date: 2026-09-27

Scope: `R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1` continuation / exact representation-contraction discovery.

## Internal anti-loop

Checked against the current JANUS affine/kernel/trade stack before materialization, including:

- `R5_E9_ONE_EDGE_TWIST_2LIFT_DISSOCIATED_NULLITY_AMPLIFIER_2026-09-27_v1.0.md`;
- `R5_E9_TRADE_FREE_UNIQUE_MODEL_DISSOCIATED_NULLITY_GATE_2026-09-27_v1.0.md`;
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`;
- `R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`;
- the current pre-math supplements and stream/context cache.

The one-edge-twist amplifier already established nullity amplification and trade-free preservation, but did not contain the stronger exact Boolean model-space identity

`Mod(Ahat) = {(u,v): Au=1, Av=1, u_j=v_j}`

or a polynomial recognition/contraction route for the hidden base.

## External prior-art check

Source-bound ingredients:

1. Y. Bilu and N. Linial, *Lifts, Discrepancy and Nearly Optimal Spectral Gap*, Combinatorica 26 (2006), 495–519, DOI `10.1007/s00493-006-0029-7`.
   - binds the standard 2-lift/signing formalism;
   - no novelty claim for 2-lifts.

2. E. M. Luks, *Isomorphism of Graphs of Bounded Valence Can Be Tested in Polynomial Time*, Journal of Computer and System Sciences 25(1) (1982), 42–65, DOI `10.1016/0022-0000(82)90009-5`.
   - binds polynomial colored/marked isomorphism recognition for the degree-three components;
   - no novelty claim for bounded-degree graph isomorphism.

3. F. Martin, *Frustration and isoperimetric inequalities for signed graphs*, Discrete Applied Mathematics 217 (2017), 276–285, DOI `10.1016/j.dam.2016.09.015`.
   - binds signed-graph balance/connectivity language used by the parent 2-lift work;
   - no novelty claim for signed-graph lift connectivity.

Searches for an exact off-the-shelf theorem combining a single crossed incidence in a cubic Exact-One incidence matrix with the Boolean model-space identity and the resulting SAT contraction did not locate that exact formulation. This is not a world-priority or novelty claim; it records only the checked scope.

## Derived delta authorized for candidate status

The candidate adds two scoped mathematical steps:

1. **Exact model-space identity.** From lifted equations and column sum three,
   `3 sum(u-v) = 2(u_j-v_j)` forces `u_j=v_j`, after which both sheets individually satisfy the base Exact-One system.

2. **Polynomial recognition/contraction composition.** The crossed incidences form a 2-edge cut; deletion exposes two marked degree-three components. Enumerating edge pairs plus source-bound bounded-valence colored GI recognizes the quotient in polynomial time. Iterated OET towers contract in logarithmically many successful steps.

## Collision status

```text
TWO_LIFT_SIGNING
= SOURCE_BOUND_PRIOR_ART

BOUNDED_DEGREE_GRAPH_ISOMORPHISM
= SOURCE_BOUND_PRIOR_ART

SIGNED_LIFT_BALANCE_CONNECTIVITY
= SOURCE_BOUND_PRIOR_ART

ONE_EDGE_TWIST_EXACT_ONE_MODELSPACE_IDENTITY
= SCOPED_DERIVED_CANDIDATE__NO_PRIORITY_CLAIM

OET_TWO_EDGE_CUT_PLUS_GI_EXACT_CONTRACTION
= SCOPED_COMPOSITION_CANDIDATE__NO_PRIORITY_CLAIM
```

## Decision

`PASS_SCOPED_GAP_CONFIRMED`

Authorized only as a theorem candidate / contraction donor. It does not authorize `E8_D1`, `P=NP`, or a universal SAT claim.
