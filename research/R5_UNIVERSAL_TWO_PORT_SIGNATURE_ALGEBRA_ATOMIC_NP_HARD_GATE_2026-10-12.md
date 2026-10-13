# R5 — Exact Two-Port Signature Algebra and Atomic Interior NP-Hardness Gate

Date: 2026-10-12 Europe/Kyiv. Source branch:
`research/r5-cubic-flow-smith-pair-20261011`; draft PR #516.
Goal: deterministic, SAT-witness/UNSAT-certificate sound and
complete `SolveLinearCubicXSAT` on ALL legal square/cubic/linear
positive Exact-One inputs with proved UNIFORM n^O(1) bit time.

**UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.**

## A. Exact semantic algebra of the 2-port Tanner cut

For every certified two-edge cut (S,not-S) of the original
3-regular bipartite Tanner graph, each side S has the same number
r of original clauses and original internal source variables.
Exactly two edges cross, one row-end inside and one variable-end
inside. Let u be the inside variable whose original third
incidence goes to an outside clause; let w be the outside variable
appearing in an inside clause. For a Boolean pair (a,b), define

  sigma_S(a,b)=1  iff  there is a 0/1 assignment of ALL inside
  variables satisfying EVERY original clause with row vertex in S,
  subject to x_u=a and x_w=b.

The cut-open subproblem is NOT a legal original SCL matrix:
it has r rows but r+1 local variable names, one foreign column
of incidence degree1 and an inside source boundary variable
of local degree2. Its clauses remain EXACT positive triples.
A strict separate checker accepts precisely these irregular
3-literal instances and leaves the old full-SCL validator
unchanged by default.

Let S and T be the two cut-open sides. All original constraints
are partitioned between S and T, and the only shared original
variable IDs in their corresponding constraint sets are u,w.
Consequently the following equivalence is exact:

  SAT(original F)
    iff
  exists (a,b) in {0,1}^2:
       sigma_S(a,b)=1 and sigma_T(a,b)=1.

If a pair works, choose local witnesses, retain each own
side's ORIGINAL internal variables, invert original indices,
and INDEPENDENTLY evaluate all original n clauses and pins.
If every pair fails, select one side with verified UNSAT for
each pair and verify its source-relative contradiction.
The four-case exhaustion is a complete logical proof of
original F UNSAT. Resource exhaustion must remain UNKNOWN,
never negative evidence.

## B. Exact mod3 arithmetic compresses 4 cases to <=2 or <=1

Summing original Exact-One clauses inside S gives

  3 * sum_(v inside) x_v = r + x_u - x_w.

Therefore:

  r % 3 = 0: only (0,0) and (1,1) allowed.
  r % 3 = 1: only (0,1) allowed.
  r % 3 = 2: only (1,0) allowed.

Invalid states are now emitted as separate replayable
`CUT_MOD3_CONFLICT` authority with their original side count.
The verifier recomputes original source cut and residue, rejecting
forged residue values. Caller pin conflicts have a separate
`ORIGINAL_PIN_CONFLICT` authority.

These necessary boundary conditions do not establish internal
SAT feasibility of the remaining 1 or 2 assignments.

## C. Actual reused exact proof system and independent replay

Code:
`experiments/r5_universal_certified_two_port_signature_algebra.py`

Reused previous certificate system:
`experiments/r5_universal_exact_support_unsat_andor_certificate.py`

New opt-in `allow_irregular=True` is available only through
a checked, sorted, distinct-triple, valid-Boolean-column
validator. Without this explicit flag the original
`validate_sparse` strict SCL promise remains intact.

For a surviving boundary assignment, a cut-open side returns:
  SAT + internally verified full local model;
  UNSAT + independently replayed exact residual AND/OR DAG;
  UNSAT + independently validated root pin/row conflict;
  UNKNOWN if a strict residual-state budget is exhausted.

At the global level:
  SAT -> full original rows and caller pins rechecked;
  UNSAT -> all 4 cases exhaustively verified via independent
           original cut reconstruction, modular/caller conflicts,
           or original irregular source AND/OR DAG replay;
  UNKNOWN -> never promoted to SAT or UNSAT.

The independent global replay checks there is no missing
port assignment and rejects truncated local DAGs or forged
mod3 arithmetic certificates.

**Complexity:** the Tanner cut finder is deterministic
polynomial (conservatively O(n^3)); at most 8 partial
side queries across four port states are made, reduced
by mod3 to at most 4 or 2 nontrivial side queries.
With at most B(n) visited residual proof states per query,
the total bounded implementation costs

  O(n^3 + B(n) * poly(n))

in standard bit arithmetic including all local certificate
verification (for polynomial B(n)). But when the source
is not decided within the guard it returns UNKNOWN.
With max_states=None, the signature algorithm is exact
and total for a source carrying the requisite 2-cut, but
the number of internal AND/OR proof states can be exponential.

Integration into the existing common
`SolveLinearCubicXSAT_Portfolio`:
  `two_port_max_n=45` (default, 0 disables),
  `two_port_states=64` (default fixed upper bound per
     partial side query, not a completeness guarantee).

A sound SAT witness or exhaustive UNSAT certificate from
the boundary expert is independently replayed before
admission into the main router. The high-level source result
contains certificate provenance; absence of a cut or budget
exhaustion leaves the previous experts/fallback available.

## D. Reproducible CI evidence

Focused final signature/algebra CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38256070084
SUCCESS. Additional high-level portfolio + corruption checks:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38255866245
SUCCESS. Final tampering and atomic gate replay on latest
revision: check current branch actions.

- Connected original SCL36 (two joined SAT K4 sources) yields a
  global SAT witness that passes every original Exact-One row;
  the actual shared Portfolio invokes the new certified
  boundary-signature expert and returns source-level SAT.
- Caller pins that contradict x_u=x_w produce UNSAT with
  **ZERO internal search** using the verified mod3 cut-row
  identity; all four pairs are explicitly excluded.
- Without initial pins, budget 0 returns UNKNOWN because at
  least one arithmetically allowed pair has no decided
  internal signature. This is correct, not UNSAT.
- Connected original SCL25 (K4 and Fano joined by an
  exact incidence swap) yields source-level UNSAT with
  independent irregular local AND/OR proof replay
  (one nontrivial DAG node after mod3 pruning).
- Destroying an actual local UNSAT AND/OR proof is detected
  by the independent checker. Forging the modular residue
  is also explicitly rejected.
- Truly 3-edge-connected atomic Tanner Fano SCL7 is not
  assigned a fictitious 2-port gate; adapter returns
  UNKNOWN with `NO_TANNER_TWO_CUT` (other experts can
  separately solve Fano).

Earlier test run with an invalid demand for a proven UNSAT
when the local budget was ZERO failed. The requirement was
fixed (UNKNOWN is legitimate on unsolved signature tasks),
and later green CI verifies sound handling. Preserve the
historical failed run for full provenance.

## E. CRITICAL NEW NEGATIVE GATE: arbitrary atomic signatures
carry the full original NP-complete problem

Source and CI:
`experiments/r5_universal_two_port_atomic_signature_nphard_graft.py`,
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38256756465
SUCCESS.

**Exact general embedding theorem.** For ANY connected legal
square/cubic/linear Positive Exact-One SCL source A of size n,
choose a source clause C and a source variable u in C.
Take the FIXED SAT direct Holyer image of K4
(legal SCL18, exactly 6 labelled edge-colourings),
a gadget clause D and its variable w.
Take their disjoint union, then EXCHANGE the two
incidence edges (C,u),(D,w) for (C,w),(D,u).

The resulting matrix A' has size n+18, remains square,
cubic (every row and every variable still degree 3)
and linear (formerly disjoint variable sets, so any
new row pair intersections across sides are at most
one). The input Tanner graph is connected when
the original A is connected, via exactly two crossing
incidence edges, a genuine 2-edge cut. This is a
polynomial-time transformation.

The cut-open A side has internal original rows/variables
of cardinality n and outer port w. If x_u=x_w=b,
replacing w with u in the one changed source row
is literally the original source A under x_u=b.
Thus for ALL n:

   SAT(A) iff sigma_A(0,0) OR sigma_A(1,1).

This equivalence of the A fragment does NOT require
n divisible by 3. For n%3!=0 the original A is
trivially UNSAT and both diagonal signatures empty.
For n%3==0 the global cut mod3 identity furthermore
forces every possible A' solution onto the diagonal.
The K4 gadget can realize either port value b in a
genuine Boolean witness by a global permutation of
the three edge-colour labels. Therefore

   SAT(A') iff SAT(A)

with n+18 new variables and a source-checkable
witness reconstruction in both directions.

The general SCL SAT problem is NP-complete via the
existing certified cubic 3-edge-colouring Holyer
embedding. If all connected SCL instances were
solvable in deterministic polynomial time, original
arbitrary SCL instances could be split into connected
components and solved polynomially. Thus connected
SCL decision is hard under polynomial-time Turing
reductions; extracting every exact two-port
signature of a connected atomic fragment is at
least this hard. More precisely, the decision
predicate `sigma_A(0,0) OR sigma_A(1,1)` for the
constructed legal cut-open fragment is NP-hard
under the same source reduction, and belongs to NP.

The exact signature table has constant four-bit size,
but computing it in deterministic polynomial time
for ALL arbitrary atomic sources would already imply
P=NP. Thus an unproved statement 'bounded boundary
=> polynomial interior signature' cannot be used as
a step in a proof of P=NP. It is a reformulation
of the same essential open computational difficulty.

This theorem does NOT establish P != NP; it is a
precise complexity preservation and no-free-lunch
gate for JANUS expert composition.

Finite independent source-aligned witnesses confirm
the graft equivalence:

| Source A | n | Joined size | Diagonal SAT b-values |
|---|---:|---:|---|
| K4 SAT | 18 | 36 | 0,1 |
| K3,3 SAT | 27 | 45 | 0,1 |
| Petersen UNSAT | 45 | 63 | none |
| Fano UNSAT | 7 | 25 | none |

All connected graphs and transformed source rows
were validated exactly; each returned positive
cut-open witness restricts to a source witness
checked against ALL original rows.

## F. Next genuinely decisive universal proof obligation

We have proven:
1. an exact constant-width compositional algebra;
2. polynomial arithmetic pruning of its interface;
3. independent original-level SAT and UNSAT replay;
4. an explicit general reduction showing that
   *unrestricted atomic signature computation itself
   is as difficult as original SCL SAT*.

Therefore the next acceptable 'global coverage' theorem
must go BEYOND constant boundary width alone. It
must construct a uniform polynomial mechanism for
ATOMIC connected sources with Tanner edge connectivity
3 (or prove that some other verified expert covers them),
and build original SAT witnesses and UNSAT decision
at a single uniform n^C bit budget.

One speculative research route is a globally valid
algebraic compression/rank-invariant of atomic
boundary truth functions that avoids enumerating
their exponentially many internal exact residuals;
this remains a conjectural avenue, not a theorem.
Do not promote finite E118/Fano/Petersen/snark
controls or fixed-degree PC3 into all-input authority.

## Scientific gates

TWO_PORT_ORIGINAL_CUT_SOURCE_SEMANTICS = PROVED_ALL_INPUTS.
TWO_PORT_FOUR_STATE_EXHAUSTIVE_COMPOSITION = PROVED_ALL_INPUTS.
TWO_PORT_MOD3_RESIDUE_4_TO_2_OR_1 = PROVED_ALL_INPUTS.
TWO_PORT_SAT_ORIGINAL_WITNESS_REPLAY = VERIFIED_CI.
TWO_PORT_UNSAT_FOUR_CASE_DAG_REPLAY = VERIFIED_CI.
TWO_PORT_FORGED_MOD3_AND_DAG_PROOFS_REJECTED = VERIFIED_CI.
TWO_PORT_POLY_GUARDED_PORTFOLIO_ADAPTER = VERIFIED_CI.
TWO_PORT_ATOMIC_SIGNATURE_SAT_HARDNESS = PROVED_REDUCTION.
CONNECTED_SCL_GRAFT_N_PLUS_18_EQUIVALENCE = PROVED_REDUCTION.
TWO_PORT_ARBITRARY_ATOMIC_POLY_SIGNATURE = OPEN_EQUIVALENT_LEVEL_P_NP.
ALL_ATOMIC_CONNECTED_SCL_POLYNOMIAL_COVERAGE = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
