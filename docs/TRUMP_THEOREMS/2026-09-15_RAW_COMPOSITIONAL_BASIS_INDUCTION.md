# TRUMP — Raw Compositional Basis Induction

Date: 2026-09-15

Authority: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_RAW_COMPOSITIONAL_BASIS_INDUCTION`

## Theorem

Given a raw Boolean constraint object with complete explicit allowed-tuple semantics and no trusted carrier labels, construct the bipartite variable-constraint incidence graph and its connected constraint components.

Distinct connected components have pairwise disjoint variable sets. Therefore the global conjunction is exactly a conjunction of variable-disjoint subinstances.

If every component is independently admitted by the sealed label-blind raw-relation basis inducer to one of the frozen six Schaefer bases, then the object admits an exact **compositional basis portfolio** consisting of the additive list of those component certificates.

No Cartesian product of local basis states is required for this basis explanation.

If any connected component has no admitted frozen local basis, the portfolio fails closed as `OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS`.

## Complexity

Canonical component discovery is polynomial in explicit scope incidence. The candidate uses union/find; the independent checker reconstructs the same partition by graph traversal.

Local basis induction contributes

`sum_components O(sum_{R in component} s_R^3 a_R)`.

Portfolio storage is additive in the component certificates.

Global variable-cube enumeration: `0`.

Cartesian products materialized: `0`.

SAT solver invocation in this gate: `0`.

## Strict scope

This theorem permits composition only across **variable-disjoint incidence components**. It does not authorize heuristic clustering or splitting any two constraints connected through a shared-variable path.

A bridge constraint touching two formerly independent components merges them before basis admission.

A connected mixed component outside the frozen local basis library remains OPEN.

## Source-bound receipt

Preregistration: `4139e1f15cf9fcc2355ba14cb8138e36c2dae60d`

Candidate: `1f1f2dcf7d4d2facd7649b078b79b9b161f8d130`

Independent checker: `133d0dfc60a303148073a84c826e117baea98fe7`

Workflow head: `06aa02c0cce7f0a6454b3a73900d0098fa7837fb`

Actions run: `34913439843`

Actions job: `104205791095`

## Controls

- disconnected raw OR2 + raw EVEN_XOR3:
  - one-global-basis gate: `OPEN_NO_SCHAEFER_BASIS`;
  - compositional gate: `ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO`;
  - local bases: `[BIJUNCTIVE, AFFINE]`.
- connected OR2 + EVEN_XOR3 sharing one variable: `OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS`.
- bridge between formerly independent blocks: exact merge, then OPEN.
- eight independent alternating OR2/AFFINE blocks: eight additive local certificates; zero Cartesian products.
- fake split of a connected mixed pair: independently rejected.
- surface permutation: identical semantic portfolio.

## Meaning for Inverted Pyramid

The lower basis of the pyramid can now be assembled automatically from multiple exact known local basis types when the raw incidence structure proves true independence.

Thus two scoped subproblems are now closed:

1. raw explicit relation semantics -> label-blind fixed-library basis recognition;
2. raw variable-disjoint structure -> additive composition of those locally recognized bases.

The remaining first-order blocker is no longer disconnected composition. It is:

`CONNECTED_MIXED_RAW_CORE_TO_EXACT_STRUCTURAL_EXPLANATION`

where no one frozen Schaefer basis applies and ordinary variable-disjoint decomposition is unavailable.

## Scientific firewall

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED = NO`

`ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`

`GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
