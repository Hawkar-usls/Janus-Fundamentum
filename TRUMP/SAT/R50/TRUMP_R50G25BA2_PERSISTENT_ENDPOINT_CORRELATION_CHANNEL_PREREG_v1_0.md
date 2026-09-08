# R50G25BA2 — PERSISTENT ENDPOINT CORRELATION CHANNEL — PREREG v1.0

Status: FROZEN BEFORE IMPLEMENTATION/TESTING
Parent: sealed BA1-D UNARY_PAYLOAD_TOO_WEAK
Parent source head: a5d4229b25a7f00465a825548cb668f6ee95381e

## Scope / nonclaims
BA2 studies only whether a minimal source-dependent endpoint correlation can create a nonzero persistent directional residual channel through the frozen block/bridge chain. It does NOT study arbitrary-CNF coverage, SAT in P, or P=NP.

## Exact endpoints and orientation
Within the sealed real U block:
- q := x2 (incoming boundary endpoint)
- p := x30 (outgoing endpoint)
- next-block boundary r := x32 = shifted copy of x2 in the next block.

Relation matrices use ROW=input, COLUMN=output, in order 0,1.
R_U(q,p) is to be independently reconstructed from real U before any promotion. Expected from sealed BA0/BA1 evidence: [[1,1],[1,1]].

Frozen bridge clause: (p OR r), i.e. literals (30,32) in the first unshifted bridge.
Expected Boolean relation B(p,r), rows p=0,1 and columns r=0,1:
B = [[0,1],[1,1]].
F1 if actual source semantics differs.

## Boolean relation composition
For Boolean relations R(x,y), S(y,z):
(R o S)(x,z) := OR_y (R(x,y) AND S(y,z)).
This is Boolean relation composition, NOT arithmetic matrix multiplication.
For an endpoint carrier C(q,p): T := C o B. Persistence is studied by Boolean powers T^k.

## Persistence criterion
Directional information persists iff there exist a != b in {0,1} such that for every required k>=1, row_a(T^k) != row_b(T^k). Record N_local, N_after_1, N_after_k, eventual stable classes. Local distinguishability alone is insufficient.

## Frozen controls/candidates
### Equality negative control
C_EQ = [[1,0],[0,1]], realized by q=p (two CNF clauses if materialized).
Preregistered expectation: T_EQ=B and T_EQ^2=ALL_RELATION. If confirmed: LOCAL PERFECT COPYING != PERSISTENT CHANNEL.

### Minimal one-clause candidate
Add exactly one endpoint clause (NOT q OR NOT p), i.e. (-2,-30) in the unshifted real U block.
Because parent U is expected to realize all four endpoint pairs, projected candidate relation expected:
C_STAR = [[1,1],[1,0]].
Preregistered predicted transport:
T_STAR = C_STAR o B = [[1,1],[0,1]], the implication relation q -> r.
Test/prove T_STAR o T_STAR = T_STAR. If true, T_STAR^k=T_STAR for all k>=1.
Allowed success wording only: PERSISTENT_ONE_POLARITY_CONSTRAINT_CHANNEL; semantic signal expected FORCE_1 -> FORCE_1 while FORCE_0 -> TOP. This is NOT a two-polarity/full Boolean copy channel.

### XOR control
C_XOR = [[0,1],[1,0]], q != p, normally two clauses. Compare T_XOR with candidate transport. If same persistent semantics, freeze redundancy.

## Complete 2x2 audit / minimality
Enumerate all 16 Boolean binary endpoint relations C exactly. For each:
1. classify whether q=0 and q=1 are both admissible; otherwise unary-kill/degenerate;
2. T=C o B;
3. compute Boolean powers until fixed point/cycle;
4. determine whether input rows remain distinguishable for arbitrary k;
5. determine minimum CNF clause cost over q,p needed to impose C on full R_U.
Classify RESET / ONE_STEP_ONLY / FINITE_HORIZON / PERSISTENT_ONE_POLARITY / PERSISTENT_TWO_POLARITY / UNSAT_OR_DEGENERATE.
Minimality success requires no zero-clause persistent directional relation and no cheaper clause-set than the candidate.

## Real-CNF materialization
No relation-matrix result counts unless realized inside the actual sealed U. For every allowed endpoint pair of C_STAR, provide an extension to all internal U variables satisfying U plus (-q OR -p). For the forbidden pair (1,1), independently verify exclusion by the added clause. Reconstruct actual B from the CNF bridge.

## Generic carrier family
Define carrier mode by adding only the preregistered clause (-q_j OR -p_j) to each active carrier block, where q_j=2+30j and p_j=30+30j, while bridges remain frozen positive clauses (p_j OR q_{j+1}). Neutral mode adds no carrier clauses and must equal sealed F_g exactly.
No g-specific/post-hoc/hindsight choice is allowed.

## Generalized invariant
pi_carrier := SAT_DECISION_PRESERVATION + PERSISTENT_DIRECTIONAL_BOUNDARY_RESIDUAL_SEMANTICS + CONSTRUCTIVE_RETURN + SOURCE_VALIDATION.
A matrix-only endpoint statement does not pass unless actual CNF materialization and reconstruction pass.

## Reconstruction
For every SAT carrier instance, reconstruct a model of the original generalized CNF and independently verify all U clauses, all carrier clauses, and all bridges. If the persistent signal is FORCE_1, every boundary claimed to carry it must equal 1 in the reconstructed witness.

## Complexity quantities
Measure/derive exact deltas from AZ/BA1:
- C_g, L_g, V_g;
- certificate record/bit size;
- construction and verification/reconstruction time;
- primal/separator width under the actual added binary correlation clause.
Old w<=13 is NOT inherited automatically; recompute and prove the new generic bound. DAG sharing allowed only with independently verifiable referenced content; hash reference != proof.

## Falsifiers
F1 actual bridge matrix != preregistered B.
F2 C_STAR not realizable inside real U.
F3 T_STAR != predicted implication relation.
F4 row distinction merges at finite Boolean power.
F5 endpoint algebra persistence fails in actual CNF composition.
F6 reconstruction ignores/violates propagated signal.
F7 g-specific/hindsight choice required.
F8 certificate/verification/reconstruction becomes super-polynomial.
F9 zero-clause or weaker relation already gives persistence, invalidating minimality.
F10 neutral mode does not recover sealed F_g exactly.

## Outcome states
BA2-A PERSISTENT_ONE_POLARITY_CHANNEL_CERTIFIED
or a restricted/falsified outcome naming the first broken obligation. If BA2-A succeeds: STOP. Do not start arbitrary-CNF coverage or a two-polarity study automatically.

Firewalls: P_VS_NP=OPEN; SAT_IN_P=NOT_PROVED; TRUMP_finished=false.
