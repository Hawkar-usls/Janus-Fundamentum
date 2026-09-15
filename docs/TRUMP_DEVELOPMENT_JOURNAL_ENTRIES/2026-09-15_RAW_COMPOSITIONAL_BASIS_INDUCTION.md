# 2026-09-15 — Raw Compositional Basis Induction

Parent scoped result: `PASS_SCOPED_RAW_RELATION_SCHAEFER_BASIS_INDUCTION`.

Gate: `TRUMP_RAW_COMPOSITIONAL_BASIS_INDUCTION`.

## Question

Can the Inverted-Pyramid basis layer be assembled automatically from multiple different known exact basis types using only raw structural independence, rather than demanding one global basis label?

## Freeze

Preregistration commit: `4139e1f15cf9fcc2355ba14cb8138e36c2dae60d`.

Candidate commit: `1f1f2dcf7d4d2facd7649b078b79b9b161f8d130`.

Independent checker commit: `133d0dfc60a303148073a84c826e117baea98fe7`.

Workflow head: `06aa02c0cce7f0a6454b3a73900d0098fa7837fb`.

No implementation code was changed after the revealed run.

## Result

GitHub Actions run `34913439843`, job `104205791095`: `success`.

Verdict:

`PASS_SCOPED_RAW_COMPOSITIONAL_BASIS_INDUCTION`.

The candidate's union/find decomposition matched an independently reconstructed graph-traversal partition.

## Exact structural result

Constraints connected by shared variables belong to the same component. Distinct components therefore use pairwise disjoint variable sets, so the global conjunction is exactly the conjunction of those independent subinstances.

Each component may be fed to the already sealed label-blind raw-relation basis inducer. If every component is admitted, the basis explanation is stored as an additive portfolio. There is no need to materialize a Cartesian product merely to represent the basis explanation.

## Controls

- disconnected OR2 + EVEN_XOR3:
  - one global basis classifier: OPEN;
  - compositional basis: admitted;
  - local basis sequence: `[BIJUNCTIVE, AFFINE]`.
- same two relation types connected through a shared variable: one component, OPEN.
- adding a bridge between two formerly independent blocks: exact merge followed by OPEN.
- eight independent alternating OR2/AFFINE blocks: eight admitted local records, zero Cartesian products.
- deliberately fake partition splitting a shared variable: rejected independently.

## Complexity

Component discovery is polynomial in explicit scope incidence. Local basis induction remains polynomial in the explicit allowed-tuple surface. Portfolio storage is additive.

`cartesian_products_materialized = 0`

`full_variable_cube = 0`

`solver_invocations = 0`

## Learned

The Inverted-Pyramid basis layer can be synthesized compositionally from raw structure for **truly independent variable-disjoint blocks**, even when the union of relation types has no one common Schaefer basis.

This closes another representation/discovery artifact: global mixed-language classification need not force OPEN when the raw formula itself proves exact independence into locally tractable basis blocks.

## Remaining blocker

The first unresolved object is now sharply localized:

`CONNECTED_MIXED_RAW_CORE_TO_EXACT_STRUCTURAL_OR_NOVEL_BASIS_EXPLANATION`.

There, ordinary variable-disjoint decomposition is unavailable and no one frozen Schaefer basis applies. Future work must either derive another exact structural explanation (separator/quotient/provenance/backdoor/etc.) with complete polynomial admission, or fail closed.

## Firewall

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED = NO`

`ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`

Global APMA frontier unchanged.
