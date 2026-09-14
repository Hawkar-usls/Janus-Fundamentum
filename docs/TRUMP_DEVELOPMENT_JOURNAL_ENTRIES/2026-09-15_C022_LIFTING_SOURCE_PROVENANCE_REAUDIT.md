# TRUMP Journal — C022 lifting-source provenance re-audit

Date: 2026-09-15
Authority: `HQ_CAPTAIN_OBVIOUS_PROVENANCE_AUDIT__NO_SCIENTIFIC_PROMOTION`

## Why this audit was opened

Captain Obvious re-evaluated the upstream obligations behind the C023R cache-fiber route. Any eventual transfer of the C022 no-cache lower bound to Policy-0A still depends on the C022 proof chain itself. The historical registry lists attack `A557` as `SURVIVED` and describes an external-theorem premise audit for ECCC TR26-018.

## Exact GitHub finding

The artifact named by historical `A557` is `registry/references-c020.json`. Its `R073` entry stores bibliographic metadata, an external ECCC URL and a short JANUS paraphrase:

- title: `Resolution Width Lifts to Near-Quadratic-Depth Res(⊕) Size`;
- authors: Dmitry Itsykson, Vladimir Podolskii, Alexander Shekhovtsov;
- year: 2026;
- source: ECCC TR26-018;
- internal note: base Resolution width `w` plus a constant-size 1-stifling gadget gives Res(⊕) depth `Omega(w^2/log S)` for proof size `S`, and MAJ3 is listed as an example.

The primary theorem text is not archived in `Janus-Fundamentum`, and GitHub code search did not locate a public GitHub copy containing the theorem statement. Under the current GitHub-first execution policy, HQ therefore cannot independently verify from primary bytes the exact hypotheses, encoding convention, proof-system convention, size convention, constants, or MAJ3 applicability.

## Historical A557 interpretation repair

Historical record `A557 = SURVIVED` is preserved unchanged as history. It is **not** rewritten.

For current authority, however, its evidence class is downgraded to:

`REGISTRY_SUMMARY_ONLY__PRIMARY_TEXT_NOT_ARCHIVED`

Current re-audit verdict:

`OPEN_RESOURCE_LIMIT__PRIMARY_LIFTING_THEOREM_TEXT_NOT_AVAILABLE_IN_GITHUB`

This is **not** a falsification of the lifting theorem and is **not** evidence that the theorem is inapplicable. It is a provenance/source-access blocker for scientific promotion of H137.

## Other upstream obligations after Captain Obvious review

### H135

`POLICY0T_NONAFFINE_SIMULATION_THEOREM.md` survived a new HQ formal red-team of restriction commutation, reverse unit reasons, branch combination without weakening, duplicate residual provenance and depth/size accounting.

Current status:

`SURVIVES_HQ_FORMAL_RED_TEAM__INDEPENDENT_EXTERNAL_REVIEW_STILL_OPEN`

No scientific promotion is made.

### H136

The old uniform dispatcher explanation needs a precise implementation correction:

- for local MAJ3 parity scopes of size `<=10`, the non-affine fibre-slice proof prevents affine recognition;
- for the frozen q=4 degree-5 family, each vertex scope has 15 gadget variables, while historical `exact_scope_relations` uses `max_scope=10`; therefore those clauses are not fully covered by the affine detector and `affine_answer=None` already follows from the detector scope cap.

The exact encoding identity can be proved symbolically for every fixed degree `d`: each falsifying base parity row has exactly `4^d` MAJ3 preimages, hence its lifted blocker family contains exactly those `4^d` width-`3d` blockers; over all `2^(d-1)` falsifying parity rows this gives exactly `2^(3d-1)` blockers, identical to the direct truth-table CNF for the parity-of-MAJ3 relation after canonicalization.

What remains source-blocked is the final identification of this clausewise construction with the exact primary theorem definition in TR26-018.

### Base family / width

The earlier q=4 Morgenstern binding remains closed and source-bound inside JANUS:

`C022_EXPLICIT_CONSTANT_DEGREE_EXPANDER_FAMILY_AND_LINEAR_WIDTH_BINDING = CLOSED`

## Claim ceiling

- H137 remains `FORMALIZING`.
- No Policy-0T scientific lower-bound promotion from this re-audit alone.
- No Policy-0A lower bound.
- No SAT-in-P or P-vs-NP conclusion.

## Captain Obvious branch decision

The primary-source audit is temporarily non-actionable under the GitHub-only execution policy. Therefore the nearest **internally actionable** missing link returns to C023R:

`C023R_DESCENDANT_DERIVED_CLAUSE_FINGERPRINT_PROPAGATION`

This gate must reason only from frozen Policy-0A transition semantics. Its purpose is to determine whether derived clauses can carry collision-history information far enough through descendants to prevent linearly many exact merge diamonds, or whether a symbolic collision template survives.

No finite asymptotic fitting is admissible.
