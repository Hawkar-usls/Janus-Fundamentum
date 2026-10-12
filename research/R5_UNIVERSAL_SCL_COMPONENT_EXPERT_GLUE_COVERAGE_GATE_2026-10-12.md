# R5 — Joint Certified Experts: Global SCL Component Theorem and Raw Algebraic Proofs

Date: 2026-10-12 (Europe/Kyiv).
Target remains ONE deterministic all-input polynomial-time
`SolveLinearCubicXSAT(A)` for every legal square/cubic/C4-free
positive Exact-One instance, with verified SAT witness or UNSAT
and ONE polynomial bit complexity bound.

**Scientific status:** global all-input polynomial coverage
NOT PROVED. Universal polynomial solver NOT CONSTRUCTED.
P vs NP OPEN.

## 1. Universal semantic decomposition of original SCL components

For any n x n valid square+cubic+linear incidence source A,
construct the bipartite Tanner graph whose clause vertices and
variable vertices each have degree exactly 3.

For a connected component H let r(H) be the number of rows
and v(H) the number of source variables. Count incidence ends
within H in two ways:

  3 r(H) = |E(H)| = 3 v(H).

Thus r(H)=v(H). Since every original row/variable has all
its three incidences inside its connected component and any
two rows share at most one variable in the original, each
component is itself an **exact legal square/cubic/linear**
Positive Exact-One source. No gadget assumption, rank
condition, or graph-isomorphism promise is needed.

Original formula F is a conjunction of constraints on
pairwise disjoint variable sets. Consequently

  F SAT iff EACH F_i SAT,

with a bijection between source witnesses and the
Cartesian product of component witnesses. One UNSAT
component proves the original formula UNSAT by restriction;
to assemble SAT witnesses, inverse-index each local column
into original source coordinates and independently evaluate
EVERY original check.

A connected component algorithm on bounded-degree Tanner
incidences performs O(n) graph traversal, then safe
canonical renaming/verification (polynomial, no loss of
literals or row cardinality). For uniformly p(n)=O(n^C)
bounded component experts, total cost
  sum_i p(n_i) <= O(n^C)
for fixed C>=1 and sum n_i=n, up to polynomial
input/output bookkeeping. If the expert uses complete
unbounded search, the assembly remains globally SOUND
and COMPLETE but retains exponential worst-case.

Proof-carrying implementation:
`experiments/r5_universal_certified_scl_component_decomposition.py`.
Main router now uses the decomposition before general root
algebra if the source Tanner graph has >1 component,
and recursively calls the SAME sound bounded-or-total
portfolio for each component. It distinguishes:
- ANY verified component UNSAT -> UNSAT with lifted
  component provenance even if earlier sibling was UNKNOWN.
- EVERY component SAT -> independently verified global
  witness SAT.
- UNKNOWN but no proven UNSAT -> UNKNOWN (no guess).
Pins are mapped to local indices exactly; an original
shared-state's independently verified global pins are
carried into each child. Whole-source odd-symmetry
hints are NOT unsafely copied into child coordinates.
All child proofs keep their own source-input authority.

Independent CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38249472880
SUCCESS, including full previously verified portfolio regression.

Controls:
- SAT K4 SCL18 + SAT K4 SCL18 = SAT SCL36; full
  exact child witnesses are lifted and re-evaluated
  globally. With zero residual state budget both
  components may remain UNKNOWN and the parent does
  not falsely report SAT.
- SAT K4 SCL18 + UNSAT Petersen SCL45 = UNSAT
  SCL63 (global 3|63). Under ZERO residual state
  budget, the K4 component returns UNKNOWN, but
  Petersen receives independently checked PC3
  contradiction; parent returns verified UNSAT
  by source-component restriction despite the
  undecided sibling.
- SAT K4 SCL18 + three Fano SCL7 components
  = UNSAT SCL39, with n divisible by3 globally.
  Each Fano source fails n_i%3=0 locally,
  demonstrating sound local cardinality stronger
  than the trivial whole-source divisibility check.
- Global pinned SAT witness on the second K4
  component is rechecked in the original coordinates.

This is a **universal theorem for preprocessing all SCL
sources**, not a universal polynomial solver: the remaining
single CONNECTED source may still require exponentially
many exact residual states.

## 2. Correct odd-order symmetrization with source row stabilizers

Previously a conditional PC3 shortcut refused automorphisms
that fixed an original row. That restriction was removed
by the verified algebraic theorem:

Let W3(A) be the degree<=3 Boolean polynomial-calculus
linear span of original exact-one parity and quadratic
generators. For every verified odd-order source automorphism
sigma of order h (currently 1<h<=n in code),

  1 in W3(A)  iff  1 in W3(A)^<sigma>.

Proof: group-average the identity 1, using
`sum_(t=0)^(h-1) sigma^t(1)=1` over F2. Conversely
any invariant span vector is already in W3. An
individual generator orbit of size d dividing h
is repeated h/d times in its full group sum,
and h/d remains ODD, so there is no cancellation.
The same applies to variable/monomial/row fixed
orbits (d=1). Every monomial orbit remains a
valid coordinate in the invariant polynomial subspace.

The upgraded verifier now independently expands each
selected orbit generator in the ORIGINAL Boolean
polynomial ring, NOT the invariant coordinates,
and checks raw monomial symmetric difference is
EXACTLY {0} (constant 1). This is a second
checker independent of rank, orbit-coordinate mapping,
and original `poly_row` arithmetic. Conditional UNSAT
is accepted only if raw certificate verification succeeds.

Important separate CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38249010839
SUCCESS, legal SCL39 with n divisible by3:
K4 SCL18 + 3 rotated Fano SCL7 components.
The order3 automorphism FIXES all 18 K4 rows
and cycles the 21 Fano clauses.
25 row representatives; invariant degree3 dimension 3970,
rank 3895; independently replayed 20-term orbit-sum UNSAT.
Also K4 SAT18 with one fixed vertex and 3-cycle variable
symmetry correctly remains PC3 inconclusive and yields
a validated SAT witness.
Prior J5/J7 and E118 regressions still pass:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38248672358
SUCCESS;
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38248784460
SUCCESS.

This certificate improvement does NOT provide a
polynomial-time odd automorphism discovery algorithm
for arbitrary legal SCL sources, or imply such
automorphisms always exist.

## 3. Global coverage theorem attack — what DID and DID NOT advance

The connected-component theorem removes redundant
search on disconnected SCL sources in a provably
exact and cost-preserving manner. It is a universal
structural preprocessing step. The strengthened
symmetry method extends the certified conditional
UNSAT domain and protects against false orbit
projection certificates.

But on CONNECTED legal SCL source F, neither theorem
shows that any current bounded expert produces
SAT or UNSAT. Disconnected SAT witness gluing cannot
create a witness for a connected component without
a solver for that component.

The actual missing statement is:

  forall connected legal SCL F of every dimension n:
    some deterministic polynomial-budget sequence of
    certified expert calls produces a verified original
    SAT witness or a verified original UNSAT certificate,

  with uniformly n^C total bit cost, including
    recognition, transformations, proof discovery,
    source-coordinate reconstruction and verification.

This statement remains OPEN. A complete exact
fallback gives final correctness but no polynomial
worst-case guarantee. The shared-state O(n²)
knowledge potential counts accepted facts only;
even the K3,3 full-width2 semantic nogood oracle
can saturate without a forced literal or SAT
witness (already independently certified in
earlier checkpoint).

The recent discussion of bounded-degree Groebner
3-edge-coloring at MathOverflow
(https://mathoverflow.net/questions/515541/)
likewise has no proved bounded-degree completeness:
its authors explicitly seek counterexamples and
test on finite graph families. It concerns a
different F3 3-edge-coloring ideal, so neither
success nor failure directly determines the
specific Boolean F2 SCL PC3 proof degree.

## 4. Research authority ledger

FULL_SCL_TANNER_COMPONENTS_ARE_SCL = PROVED_ALL_INPUTS.
COMPONENT_SAT_WITNESS_PRODUCT = PROVED_ALL_INPUTS.
ONE_COMPONENT_UNSAT_IMPLIES_GLOBAL_UNSAT = PROVED_ALL_INPUTS.
BOUNDED_POLY_EXPERT_COMPONENT_TOTAL_COST = PROVED_CONDITIONAL.
SCL36_SAT_COMPONENT_WITNESS_REPLAY = VERIFIED_CI.
SCL63_UNSAT_PC3_LIFT_WITH_UNKNOWN_SIBLING = VERIFIED_CI.
SCL39_LOCAL_CARDINALITY_WHEN_GLOBAL_N_DIV3 = VERIFIED_CI.
ODD_SYMMETRY_FIXED_ROW_ORBITS = PROVED.
ODD_SYMMETRY_RAW_ORIGINAL_PC3_CERTIFICATE = VERIFIED_CI.
ALL_CONNECTED_SCL_POLY_EXPERT_COVERAGE = OPEN.
ALL_CONNECTED_SCL_POLY_SAT_WITNESS = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Do not merge draft PR #516 into main or mark universal
proof gates passed until all connected-source cases
and worst-case bit bounds are established.
