# HQ review — APMA Trinity bounded-interface unicyclic transfer

Verdict:

`PASS_SCOPED_BOUNDED_INTERFACE_UNICYCLIC_TRANSFER`

Authority class:

`SCOPED_EXACT_ALGORITHM_THEOREM__NOT_GENERAL_SAT__NOT_P_VS_NP`

## Reviewed lineage

- preregistration: `32a29969ca85259aff23c411396289f4e6a938c2`
- candidate initial implementation: `b82c747206f158787800a091f76b0355e09e9fa9`
- independent checker: `8bb602c4a4db9fbcad0a6e8bc6c53f241e2f220d`
- preregistered gate workflow commit: `9781df20ac000e7f55cf2931d765f4ad27fdb77d`
- gate run: `34906067621`
- hostile falsifier workflow commit: `7d6c3fcbba5b7e9de1935c1a07706d2da108ec63`
- hostile falsifier run: `34906259278`
- formal proof commit: `fa7b1d61104adbb66b2d9a7c0661a4a5853443d9`

Frozen Trinity v1.0 remains unchanged.

## Formal obligation review

### P1 — PASS

For a connected simple graph with `|E|=|V|`, cyclomatic number is exactly one. The chosen edge is required by the implementation to be a non-bridge; deleting it preserves connectivity and leaves `|V|-1` edges, hence a tree.

### P2 — PASS

For the complete cut separator `S`, every root assignment induces exactly one `sigma=A|S`, and every satisfying assignment of a conditioned formula extends with the same sigma to a satisfying root assignment. Thus

`SAT(F) iff exists sigma SAT(F | S=sigma)`.

No-hyperedge admission ensures cut variables occur in no third module, so conditioning both cut endpoints removes exactly the semantic interaction represented by the removed graph edge.

### P3 — PASS

The conditioned tree DP has the standard exact existential-message invariant: a parent-separator key is present iff the entire rooted module subtree has a satisfying extension under that key and the fixed cut assignment. Leaves follow from exact native typed-carrier solving; the inductive step follows by exact enumeration of the module boundary and equality matching on every child separator.

Keeping one row per parent key is exact for SAT existence because rows with identical parent key are existential alternatives; absence is established only after all enumerated boundary rows inducing the key fail.

### P4 — PASS

Reconstruction follows stored exact separator keys. Tree-adjacent witnesses agree on complete edge separators. The two endpoints of the removed cycle edge agree on the same explicitly fixed sigma. Under no-hyperedge admission there are no hidden cross-module overlaps. Final witness replay is performed on the unchanged root CNF.

### P5 — PASS

If all sigmas are rejected, P3 gives `UNSAT(F | S=sigma)` for every sigma. P2 then implies `UNSAT(F)`. This obligation was additionally exercised by hostile finite UNSAT falsifiers but does not depend on those finite tests.

### P6 — PASS

With `w=floor(log2 L)`:

- outer cut assignments: `2^|S| <= L`;
- rows per module per sigma: `<= 2^w <= L`;
- modules `M <= L`;
- total exact local solves: `<= M L^2`;
- each native 2CNF/Horn/Dual-Horn solve is polynomial in `L`;
- extraction, recomposition, module discovery, interaction construction, cut discovery, reconstruction, and root replay are polynomial.

Therefore the full frozen-scope lifecycle is polynomial in the root encoding size.

## Counterexample attack

The finite runs were used only as falsifiers/implementation checks.

Preregistered gate:
- historical cycle OPEN cases: 128;
- successor OPEN on the same 256-orientation product: 0;
- exact mismatches: 0;
- multi-cycle control: remains OPEN;
- width-overflow control: remains OPEN;
- v1.0 regression checker: PASS.

Hostile augmentation attack:
- tested augmentations: 8,128;
- admitted unicyclic instances: 1,477;
- exact mismatches: 0;
- genuine UNSAT/all-sigma-rejection cases found and passed;
- attached-tree unicyclic cases found and passed;
- multi-variable cut-separator cases found and passed.

These counts are **not** asymptotic evidence and are not part of the mathematical proof.

## Important proof-carrying caveat

The semantic algorithm and polynomial replay theorem are admitted. However, the current UNSAT output serializes the tested/rejected cut assignments but does not serialize a full local rejection trace/table for every sigma. A verifier can independently recompute the exact polynomial DP, so semantic verification remains polynomial; nevertheless this successor should **not** yet be described as introducing a new compact standalone UNSAT certificate format.

Authorized wording:

`exact polynomial deterministic replay within the frozen scope`

Not yet authorized wording:

`new compact proof-carrying UNSAT certificate language`.

## Remaining OPEN regimes

1. `MULTICYCLE / GROWING_FEEDBACK_INTERFACE`: OPEN.
2. `WIDER_INTERFACE_EXACT_POLYNOMIAL_REPRESENTATION`: OPEN.
3. `UNIVERSAL_DISCOVERY`: NOT CLAIMED.
4. `GENERAL_SAT_IN_P`: NOT PROVED.
5. `P_VS_NP`: OPEN.

## HQ promotion boundary

This review promotes only the theorem:

> Exact polynomial SAT decision for the frozen class of exactly typed, no-hyperedge, connected unicyclic module-interaction instances whose complete per-module boundary is at most `floor(log2 L)`.

No broader scientific frontier is unlocked automatically.
