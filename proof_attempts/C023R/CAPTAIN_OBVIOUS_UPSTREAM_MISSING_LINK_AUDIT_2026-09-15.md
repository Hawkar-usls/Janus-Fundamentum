# Captain Obvious — C023R upstream missing-link audit

Date: 2026-09-15
Authority: `DIAGNOSTIC_GATE_SELECTION__NO_PROOF_AUTHORITY_BY_ITSELF`
Mechanism: `JANUS-CAPTAIN-OBVIOUS-NEAREST-MISSING-LINK-DIAGNOSTIC-MECHANISM-2026-09-11-v1.0`

## CO01 — STATUS_FIRST_SNAPSHOT

Established for this route:

- historical C022 no-cache target and MAJ3 route exist;
- explicit q=4 Morgenstern degree-5 family and linear base Resolution-width binding are frozen;
- C023R exact cache-fiber identity: multiplicity equals root-to-key path count in the unique-key execution DAG;
- exact merge-surplus upper bound `m(v) <= 2^mu(v)`;
- MAJ3 semantic restriction/cycle-space collisions exist, but semantic preimages are not execution fibers;
- exact historical two-step diamond requires byte-key commutation under frozen transitions.

Not established:

- H135 has only an internal complete proof draft plus finite replay; independent mathematical review remains open;
- H136's old detector explanation does not exactly match the degree-5 implementation path because `exact_scope_relations` has `max_scope=10`;
- independent audit of the registered lifting theorem premise remains open;
- C023 cached-policy lower bound remains open.

## CO02 — FROZEN TARGET CLAIM

Target `T` for this historical route:

> Establish or refute an exponential charged-work lower bound for exact Policy-0A on the frozen q=4 MAJ3-lifted Tseitin family, without importing stronger reason-caching or clause-learning resources.

This is a policy lower bound only. It is not a SAT lower bound and does not imply `P != NP`.

## CO03 — CLAIM-OBLIGATION DAG

One admitted route:

1. `H135_POLICY0T_TRACE_TO_RESOLUTION_SIMULATION` — OPEN / FORMALIZING.
2. `H136_MAJ3_DISPATCH_AND_EXACT_ENCODING` — OPEN / FORMALIZING, but algebraically repairable.
3. `EXPLICIT_Q4_BASE_WIDTH_BINDING` — ESTABLISHED.
4. `REGISTERED_2026_LIFTING_PREMISE_AUDIT` — OPEN.
5. `C022_POLICY0T_EXPONENTIAL_LOWER_BOUND` — depends on 1–4.
6. `C023R_CACHE_FIBER_TRANSFER_OR_FALSIFIER` — OPEN.
7. `POLICY0A_EXPONENTIAL_LOWER_BOUND` — depends on 5 and 6.

The current cache theorem is therefore not the nearest unresolved prerequisite to the final target.

## CO04 — NEAREST ACTIONABLE MISSING LINKS

Selected order:

1. H135 formal red-team review, because failure destroys the C022 bridge immediately.
2. H136 exact algebraic repair/proof, because it is local and cheap.
3. independent lifting-premise audit.
4. only then return to the expensive C023R cache-fiber theorem.

## CO05 — RED_TEAM FIRST: H135

Attacks independently replayed from the theorem text and frozen core semantics:

- restriction/Resolution commutation under a consistent partial assignment;
- witness-choice independence when canonical residual clauses have more than one root-derived witness;
- reverse unit-reason elimination in reverse chronological order;
- opposite-unit and empty-resolvent terminal cases;
- branch combination without weakening;
- dependency-path depth accounting.

No logical counterexample was found in these obligations. In particular, any witness `D` with `D|alpha=C` contains no literal satisfied by `alpha`; therefore choosing a different valid witness cannot introduce an assigned complementary pair. A proof-dependency path through branch-combination selects one child at every branch and hence corresponds to one execution root-to-leaf path, supporting the stated depth accounting.

HQ diagnostic verdict:

`H135_SURVIVES_HQ_FORMAL_RED_TEAM__EXTERNAL_OR_INDEPENDENT_MATHEMATICAL_REVIEW_STILL_OPEN`

This is not an external review and does not silently change historical authority.

## H136 correction and proof

The non-affinity lemma itself is valid: each MAJ3 fibre is non-affine, and fixing blocks 2..d restricts the parity-of-MAJ3 relation to one non-affine MAJ3 fibre.

However the current detector has `max_scope=10`. Therefore the implementation consequence must be split:

- for degree `d <= 3`, scope `3d <= 9` is inspected and non-affinity prevents affine coverage;
- for degree `d >= 4`, scope `3d > 10` is not inspected at all, so those clauses remain uncovered and `visible_affine_root_decision` returns `None`;
- the frozen q=4 route has degree 5, so the scope-cap case alone already guarantees `affine_answer=None`.

The exact encoding identity also has a general symbolic proof for every `d >= 1`:

- base parity has `2^(d-1)` falsifying output rows `y`;
- the blocker of one falsifying row is lifted clause-wise;
- for each block, the fibre CNF contributes exactly four blockers of gadget inputs whose MAJ3 output falsifies the corresponding base literal;
- disjoint blocks make every product selection one width-`3d` blocker;
- the `4^d` selections are in bijection with gadget assignments whose MAJ3 output vector equals `y`;
- over all falsifying `y`, this gives `2^(d-1) * 4^d = 2^(3d-1)` clauses, exactly one blocker for every falsifying lifted assignment.

Hence, relative to the registered clause-wise lift definition, canonical clausewise lift and direct exact-relation CNF are identical for all degrees, not only the finite audit degrees 1..4.

HQ diagnostic verdict:

`H136_INTERNAL_ALGEBRAIC_PROOF_COMPLETE_WITH_DETECTOR_PATH_CORRECTION__EXTERNAL_LIFTING_SOURCE_PREMISE_AUDIT_SEPARATE`

## CO06 — CLAIM CEILING

No Policy-0A lower bound is promoted yet.

H135 remains awaiting genuinely independent/external mathematical review if that standard is retained. H136 no longer needs finite-size extrapolation, but the external lifting theorem's exact syntax/premises remain a separate source-bound obligation.

## CO07 — ONE NEXT GATE

Freeze next gate:

`C022_REGISTERED_2026_LIFTING_THEOREM_PREMISE_AUDIT`

Before returning to cache-fiber work, verify from the registered primary theorem statement that:

1. MAJ3 satisfies the theorem's exact gadget hypothesis;
2. the theorem applies to the exact clause-wise CNF construction used here;
3. the base width parameter is the one already bound on the q=4 family;
4. the proof-size/depth convention supports the algebraic rearrangement used in H137;
5. there is no hidden bounded-degree, encoding-size, or proof-system mismatch.

Forbidden: infer the theorem from the existing JANUS summary alone, run new finite SAT experiments, or reinterpret a source mismatch as a repaired theorem after seeing it.

## CO08 — PROMOTION FIREWALL

Current outcome:

`NEXT_LINK_IDENTIFIED`

No global frontier change. No `SAT_IN_P`. No `P != NP`. C023R cache theorem remains preserved but temporarily downstream of the selected upstream audit.