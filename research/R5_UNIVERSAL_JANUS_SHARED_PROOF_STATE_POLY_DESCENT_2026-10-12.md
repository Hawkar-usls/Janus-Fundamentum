# R5 — JANUS Unified Proof-State, Certified Knowledge Descent and Coverage Gap

Date: 2026-10-12, Europe/Kyiv.
Repository: Hawkar-usls/Janus-Fundamentum.
Scientific authority: stacked draft PR #516, successor to #515.
Main stays unchanged.

## Scientific objective

Build ONE deterministic all-input `SolveLinearCubicXSAT` that returns
verified SAT+witness or rigorous UNSAT on EVERY legal square+cubic+linear
positive Exact-One instance in proved worst-case n^{O(1)} BIT time.
This milestone implements a proof-aware cooperation layer, NOT the
missing all-input complexity theorem.
`UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN`.

## 1. Concrete shared state and provenance rules

`experiments/r5_universal_certified_shared_proof_state.py` defines
`CertifiedSharedState` for a strict original immutable SCL matrix
and a scoped set of user-pinned literals. It maintains:

  - original source matrix / immutable context pins,
  - chronological list of logically forbidden assignments
    (nogoods of widths one and two),
  - exact proof authority + independently replayable certificates
    for every learned nogood,
  - forced variable values and a trace identifying the original
    Exact-One check or prior certified nogood that forced each value,
  - a strictly decreasing nonnegative integer progress potential,
  - counters and an explicit bounded probe scheduler,
  - optional SAT witness, verified against the original source.

An alleged expert fact is **never** accepted on heuristic confidence,
floating-point output, mere numerical rank observation, timeout,
or an unsupported mathematical assumption.

## 2. Three independently verified proof authorities

### A. GF2 Boolean polynomial-calculus degree 3

For each original 3-variable positive Exact-One row {a,b,c}
generate both exact Boolean-ring equations

  p=1+x_a+x_b+x_c = 0,
  q=x_a*x_b+x_a*x_c+x_b*x_c = 0.

Use all squarefree monomial multiples m*p of total degree <=3
and m*q of total degree <=3 in the quotient
F2[x]/(x_i^2-x_i). For a proposed forbidden partial assignment
N={(v_i,b_i)}, add the pin equations x_(v_i)+b_i=0 as
EXPLICIT hypothesis generators. Previously learned valid nogoods
are also legal generators:

  g_N(x) = product_(i in N) (x_i if b_i=1 else (1+x_i)) = 0.

Only if bit-exact GF2 elimination expresses constant 1 as a
linear combination of these polynomial generators does the
system learn the corresponding conditional nogood.
The complete specific combination is retained and replayed
by a second checker using direct polynomial arithmetic,
NOT using the elimination rank as an oracle.

Soundness proof: every actual Boolean solution of original
SCL+original context annihilates original p,q, all prior
already certified nogoods and all assignments in N. If it
satisfied N, evaluation of the derived identity would yield
0=1. Contradiction; therefore N is forbidden.
Induction over chronological proofs preserves this invariant.

Failure to derive 1 is UNKNOWN, never SAT.

### B. Exact bounded AND/OR residual-DAG proof

The existing `construct_unsat_proof` can search under proposed
pins with a guard. On a genuine UNSAT result it supplies an
AND/OR proof DAG; `verify_unsat_proof` replays all branches
against the original clauses independently. Its certified
negative response becomes a learned nogood in the SAME state.

A special sentinel from that pre-existing API means that the
assumptions contradict an original Exact-One clause at the
root, so there is no nonempty AND/OR DAG. The combined
knowledge engine explicitly recognizes it and independently
re-runs `residual_normalize` to verify the local contradiction.
It is not confused with budget exhaustion.

A genuine SAT answer to a bounded AND/OR query produces a
global original-input solution (any extra trial pins can be
discarded after independent source verification).
A budget exhaustion stays UNKNOWN.

### C. Exact-One / learned nogood unit propagation

Given a verified scoped assignment:
- Exactly one 1 in a source row forces its other two values 0.
- Exactly two 0s force its third value 1.
- For a learned width-1/2 nogood, when all but one forbidden
  literal are fixed to their forbidden values, the remaining
  literal is forced to the opposite value.

Each added literal records its precise rule and reference to
a source clause / certified nogood. The independently
implemented sequential trace checker replays these
implications using only PREVIOUS pins; no trust in the forward
propagation implementation is needed.

On a conflict, the bounded scheduler does NOT silently publish
UNSAT: it requires an independently replayable root proof.
This conservative rule avoids provenance gaps.

The router `SolveLinearCubicXSAT_Portfolio` has an OPTIONAL
`shared_state` adapter. It checks the original matrix and
context-pin identity, replays the entire nogood certificate
ledger and literal propagation trace, then forwards ONLY
verified strengthened pins to its existing algebraic, PC3,
bounded exact and full exact experts. Every SAT result is
rechecked against the original SCL input.

## 3. A genuine monotone global progress theorem

For a legal n-variable original source, the chosen language
of width <=2 Boolean nogoods has at most

  2n                   unary forbiddances,
  4*C(n,2)             binary forbiddances.

At most n variable values can be fixed. Define the integer

  M(n) = n + 2n + 4*C(n,2) = 2n^2+n.

For any consistent proof state, define

  Phi = M(n) - (#distinct certified nogoods)
             - (#distinct fixed variables).

Then Phi is nonnegative and cannot increase. Each ACCEPTED
previously unknown nogood decreases Phi by exactly one.
Each newly forced literal decreases Phi by exactly one.
Duplicate information is rejected, so there is no artificial
progress from re-adding the same assertion. Thus there can
be at most 2n^2+n substantive knowledge additions.

This is an all-input polynomial BOUND ON ACCEPTED UPDATES
in the restricted proof-state language. The bound is
mathematical, independent of the tested graph family and
independent of runtime measurements.

For a full deterministic schedule, enumerate all 2n+4*C(n,2)
potential nogoods, restarting after a strict update. There
are at most M(n) updates plus a final no-progress scan, and
at most O(M(n)^2)=O(n^4) PC3 queries. Each fixed-degree PC3
call is deterministic polynomial bit time (previous memo
conservatively O(n^9)), so this entire bounded-width,
bounded-degree **closure algorithm** has a polynomial
worst-case bit bound (conservatively O(n^13)).

The executable `run_bounded_descent(max_queries=B)` additionally
supports a hard user-supplied query guard. It returns only an
accurate resource/saturation/needs-proof diagnostic; no
unchecked final SAT/UNSAT verdict can leak.

### CRITICAL THEOREM THAT IS *NOT* OBTAINED

The polynomial potential bound does NOT prove that saturation
forces either a SAT witness or an UNSAT certificate.

Already an unpinned SAT K3,3 carrier reaches the original
Exact-One unit-propagation fixed point with no assigned
literals, and the logical status has not been proved by
that fixed-point computation. Other experts can still
solve it by search, but the fact of stagnation itself is
NOT a decision procedure.

Proving that the *joint closure* always decides every
legal SCL instance, or that the remaining exact
AND/OR fallback always visits only polynomially many
states after closure, is EXACTLY the unresolved
P vs NP-level global coverage/compression question.
A strictly decreasing polynomial-sized vocabulary alone
cannot settle that implication.

Full fixed-width local CSP consistency and bounded-degree
polynomial calculus are established proof-complexity
concepts; no originality is asserted for their existence.
Published PC degree lower bounds on Tseitin CNFs
(Buss-Grigoriev-Impagliazzo-Pitassi, JCSS 62, 2001)
cannot be transferred automatically to this precise
square-cubic-linear Exact-One encoding without proving
a degree-preserving reduction.

## 4. CI evidence and graph-independent controls

Main replay:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38188393743
and the earlier verified state-to-router integration:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38188219557
both SUCCESS.

  K3,3 direct legal SCL n=27:
    M=1485; exact PC3 proof of a binary forbidden assignment
    using five GF2 generator terms; Phi 1485 ->1484.
    Same no-good cannot be counted twice.
    Independent bounded AND/OR / original-clause local
    contradiction and independent GF2 PC3 evidence coexist
    in a chronological ledger and are replayed together.

  A separate K3,3 caller-pinned branch:
    PC3 proves a new nogood; closure derives six extra
    source-checked variable values; derived scoped
    assignments go directly into the already connected
    certified portfolio; the returned SAT witness is
    independently checked against the ORIGINAL source.
    Phi=1477 in this scoped run.

  E61 original SCL SAT12 (NOT cubic graph embedding):
    degree3 PC refutes one false assignment to a variable,
    establishing a forced original Boolean literal;
    shared state n=12: M=300, Phi=298 after certifying
    the unary nogood and performing exact implication.
    The whole SCL constraint matrix is independently
    verified legal before the proof.

  Bounded scheduler on K3,3 with query budget=2:
    RETURNS UNKNOWN_RESOURCE_GUARD after two valid
    inconclusive polynomial PC3 probes, zero new facts.
    Never falsely upgrades UNKNOWN to SAT/UNSAT.

The initial integration with the bounded AND/OR adapter
discovered a real expert-contract mismatch:
`construct_unsat_proof` represents an immediate pin
contradiction as (None,None), whereas guarded UNKNOWN
uses ('UNKNOWN',None). The adapter was fixed to verify the
direct original-clause conflict separately, with its own
proof-authority tag, before accepting the nogood.
A failed intermediate CI run is preserved for provenance;
the corrected run listed above is SUCCESS.

## 5. Exact remaining target and next legal experiment

**To justify CONSTRUCTED, require simultaneously:**

(a) Every SAT source reaches a VERIFIED witness in n^O(1)
    time through one or several cooperating experts.

(b) Every UNSAT source reaches an independently verifiable
    complete contradiction certificate in n^O(1) time.

(c) The global dispatcher and all failed/negative queries
    obey ONE worst-case polynomial bit-operation bound.

(d) The theorem applies to EVERY legal square+cubic+linear
    input, with no leftover irreducible snark, graph
    width, phase, proof-degree, odd symmetry or boundary case.

None of (a)-(d) has yet been proved globally.
The next research gate is therefore a **coverage theorem or
verified counterexample** for the fixed-point state:
can ANY true UNSAT legal SCL instance remain jointly
consistent under these polynomially bounded experts,
or does a structural theorem force polynomial refutation?
Independently, can a SAT witness always be generated from
the saturated state without exponential search?
One cannot assume either conclusion merely from the
potential descent theorem.

## Gate ledger

SHARED_PROOF_STATE_CANONICALIZATION = IMPLEMENTED.
PC3_NOGOOD_CERTIFICATE_INDEPENDENT_REPLAY = VERIFIED_CI.
ANDOR_AND_DIRECT_CONFLICT_NOGOOD_PROVENANCE = VERIFIED_CI.
SOUND_LITERAL_PROPAGATION_INDEPENDENT_TRACE = VERIFIED_CI.
ROOT_SCL_PIN_SCOPING_AND_EXPERT_HANDOFF = VERIFIED_CI.
MONOTONE_PHI_O_N2_ACCEPTED_ADDITIONS = PROVED.
COMPLETE_BOUNDED_WIDTH_2_PC3_CLOSURE_POLY_RUNTIME = PROVED.
CLOSURE_FIXEDPOINT_IMPLIES_EXACT_SAT_OR_UNSAT = NOT_PROVED.
UNIVERSAL_CERTIFIED_POLYNOMIAL_EXPERT_COVERAGE = OPEN.
UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
