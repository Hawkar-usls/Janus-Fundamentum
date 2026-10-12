# R5 — All-Source GF(2) Affine Witness Ledger and Unannotated Atomic Bridge Refutation

Date: 2026-10-12 Europe/Kyiv. Research branch:
`research/r5-cubic-flow-smith-pair-20261011`, stacked draft PR #516.
User's sole final objective: `SolveLinearCubicXSAT` on EVERY legal
square+cubic/linear Positive Exact-One instance, deterministic
uniform `n^{O(1)}` worst-case BIT time, SAT plus original Boolean
witness or UNSAT; **NOT CONSTRUCTED, P vs NP OPEN**.

## 1. Universal all-input polynomial proof ledger, exact not heuristic

Let A be ANY original valid SCL n-by-n incidence matrix.
Every original Exact-One constraint

   x_a+x_b+x_c=1  (as an INTEGER equation)

implies the GF2 affine equation

   x_a + x_b + x_c = 1 (mod 2).

Add any original caller pins x_j=b as further GF2 equations.
Gaussian eliminate the augmented system WITH independent
source-row provenance bits, producing explicit equations

   `XOR_{i in proofmask} original_equation_i`.

For each pivot coordinate j the exact row-reduced expression is

   x_j = b_j + XOR_{f free} t_(j,f) x_f.

For a free coordinate f its expression is exactly x_f.
If t_j is the ZERO coefficient vector, x_j=b_j is
**FORCED** in EVERY original Boolean Exact-One solution.
If t_i=t_j, then x_i XOR x_j=b_i XOR b_j is forced
and carries a one-row XOR certificate consisting of
the XOR of the source proofs for expressions i,j.

Proof and verification are entirely over finite F2 linear
algebra. The independent checker DOES NOT trust any
Gaussian pivot labels or the producer's reduced basis:
it XORs exactly the named ORIGINAL source rows and caller
pins, checks resulting variable mask and RHS, and rejects
a fabricated provenance mask. Proven literals and binary
relations are shared with the existing JANUS Portfolio
BEFORE modular/Tanner/PC3/residual experts.

A source-inconsistent augmented GF2 row `0=1` proves
UNSAT with its source-row combination. Even when GF2 is
consistent, if forced source bits make any ORIGINAL
Exact-One clause have at least TWO ones (or all zero),
the ORIGINAL exact-one semantics prove UNSAT. Independently
replay ALL the forced GF2 consequences, then check that
original Boolean clause. If all n variables are GF2 forced,
only a fully checked original Exact-One witness can claim SAT.
Every other algebraically consistent case returns UNKNOWN
or forwards proven pinned facts; it is NEVER promoted to SAT.

Safe worst-case complexity: input 2n-row augmented bit
matrix and O(n)-bit proof vectors; Gauss-Jordan and
grouping affine expressions use at most O(n^4)
bit operations (conservative). Certificates contain
O(n) forced literals and at most O(n) independent
star-basis parity relations, each O(n) proof bits:
polynomial construction, size and verification.
The full old exact fallback remains worst-case exponential.

### Universal GF2 negative-reading firewall

Every 3-literal original row has odd support, hence

  A*(1,1,...,1)^T = (1,1,...,1)^T over GF2.

Therefore for UNPINNED original SCL:
- the pure GF2 parity system is ALWAYS CONSISTENT;
- any algebraically FORCED coordinate necessarily equals 1;
- any algebraically forced binary XOR relation has parity 0,
  i.e. only `x_i=x_j` can be forced before pins.

Thus GF2 rank consistency alone has ZERO UNSAT
discriminating power on the unpinned original SCL.
The new effective all-input negative inference is the
COMBINATION of parity-implied FORCED ONES and integer
EXACT-ONE row semantics; 3 simultaneous parity-forced
ones cannot satisfy an original exact-one triple.

An earlier proof-state width2 saturation theorem still
warns that even ALL true unary/binary consequences need
not construct any SAT witness. This new polynomial source
ledger is not a global polynomial decision theorem.

## 2. ALL connected cubic Holyer source bridges caught automatically

Consider ANY connected simple cubic graph G with a BRIDGE
e={u,v}. Removing e yields an odd-vertex shore S because

   3|S| = 2|E(G[S])| + 1

and therefore |S| is odd.

Under the already verified Holyer source-to-SCL mapping,
for EACH colour c=0,1,2, sum ALL source vertex-colour
Exact-One rows R_(z,c) for vertices z in S modulo 2.
Each source variable X_(f,c) on an INTERNAL edge of S
occurs TWICE and cancels; the UNIQUE crossing-edge
variable X_(e,c) occurs ONCE. RHS is |S| mod2 = 1.
Hence each colour has a standalone original-source
GF2 XOR certificate

   X_(e,0)=1,
   X_(e,1)=1,
   X_(e,2)=1.

But the original SCL edge-row for e is

   ExactOne(X_(e,0),X_(e,1),X_(e,2)).

This is a genuine integer/Boolean contradiction.
The GF2 row space contains the three unit vectors
at these original source columns. Complete RREF
therefore discovers their forced value 1 WITHOUT
KNOWING G, its bridge, Holyer row types, or
even which variables are source edge-colours.
It then checks the original exact-one row and
publishes a polynomial-time UNSAT certificate.

This theorem applies to the INFINITE class of
ALL connected cubic graphs containing a bridge,
not merely one frozen benchmark.

Crucial structural contrast: by the previous
universal Holyer theorem T(A_G) is 3-edge-connected
as a Tanner incidence graph even when G has a bridge.
The new method works INSIDE the precise class that
survives 1-/2-edge Tanner decomposition.

## 3. Actual code and hard gates

New:
`experiments/r5_universal_certified_gf2_affine_forced_literals.py`

Functions:
- `source_equations`: original exact-one parity + checked caller pins
- `gf2_certified_source_closure`: exact Gaussian row/provenance
- `verify_xor_claim`, `verify_gf2_ledger`: independent raw replay
- `bridged_join_of_two_cubic_graphs`: source family controls

Main `experiments/r5_universal_certified_expert_portfolio.py`
now accepts `gf2_linear_propagation=True` by default.
It runs the GF2 closure before the old root experts,
replays the source proof ledger, attaches
`gf2_provenance` to the output, and either:
- issues a new verified UNSAT/SAT decision;
- shares source-proved forced values with downstream experts;
- preserves UNKNOWN whenever undecided.

The prior `certified_holyer_edges` bridge expert is
still available for explicit independent source
bridge verification, but this new path needs NO
input metadata or Holyer hint. Wrong or forged
source-row certificate is checked and rejected.

The previous isolated MOD9 provenance test
**temporarily disables** the new GF2 proof producer
to check MOD9's own original annihilator; likewise
isolated two-port/Tanner tests disable GF2 to
test their own proof-lifting. This is not a bypass
in the default combined solver: multiple sound
UNSAT routes may return in different order, so
the identity of the FIRST proof is not a
semantic invariant.

## 4. Independent cross-family and ablation evidence

Frozen new GF2 CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38278073557
SUCCESS on the first five-family control.
Ablation final:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38278300069
SUCCESS.

| Independently connected cubic bridge family | SCL dimension | GF2 forced bits | Decision |
|---|---:|---:|---|
| K4 subdivided + K4 subdivided + bridge | 45 | 3 | UNSAT |
| K4 + K3,3 | 54 | 3 | UNSAT |
| K3,3 + K3,3 | 63 | 3 | UNSAT |
| K4 + cube | 63 | 3 | UNSAT |
| K4 + Petersen | 72 | 3 | UNSAT |

All families are checked as exact simple cubic graphs,
source Holyer legal square/cubic/C4-free SCL matrices,
all three original bridge colour variables are
independently proven 1 by the row-XOR ledger,
and the same source Exact-One row is certified
inconsistent with these three forced values.
A modified proof mask is intentionally rejected.

**Decisive controlled ablation**, original legal SCL45
with the same zero PC3/zero DAG/Tanner/2port budgets,
WITHOUT supplying `certified_holyer_edges`:

  gf2_linear_propagation = False:
      status=UNKNOWN, expert=ALL_BOUNDED_EXPERTS_EXHAUSTED.

  gf2_linear_propagation = True:
      status=UNSAT,
      expert=CERTIFIED_GF2_SOURCE_CLAUSE_CONFLICT,
      original proof independently replayed.

This establishes a NEW effective proof route not previously
covered by the exact same configured polynomial portfolio.
It is not evidence that other previously implemented
algorithms could NEVER derive the same contradiction
under different settings. A user-supplied bridge
witness could also already prove it.

SAT controls direct Holyer K4 and K3,3 return
UNKNOWN, NEVER a false UNSAT. Petersen no-bridge
also returns UNKNOWN in this GF2-only lane:
this is an explicit unsolved atomic core witness
against treating all GF2 affine facts as a universal
SAT/UNSAT algorithm.

The earlier first combined CI failures were due
to assertions demanding a particular MOD9 or
two-port PROVENANCE LANE even though the new valid
GF2 lane refuted first. Focused independent old
proof-lane regressions now disable the new gate
only for those route-specific tests; default combined
execution retains the GF2 gate. Preserve failed
history, and only report final green one-HEAD CI
after checking its actual run conclusion.

## 5. NEXT GLOBAL POLYNOMIAL PROOF OBLIGATION

We must still construct polynomial termination for
EVERY SCL, including bridgeless NP-complete atomic
Holyer images such as Petersen and arbitrary cubic
snarks. The new GF2 proof ledger cannot force a
SAT witness or UNSAT after its affine saturation
on all such sources: parity relaxation accepts
the all-one vector for every original unpinned SCL.
Higher-order Exact-One compatibility is therefore
the genuinely hard remaining Boolean obstruction.

A scientifically legitimate next candidate would be
a uniform polynomial-time, globally source-valid
lifting of these certificate-carrying affine
relations to an exact BOOLEAN closure/normal form
that provably yields SAT witness or UNSAT on EVERY
source. Polynomial-time GF2 linear deduction
by itself is insufficient: to claim P=NP one
must prove the subsequent exact consistency
decision terminates at uniform polynomial bit cost.

## Gate ledger

SOURCE_GF2_ORIGINAL_ROW_PROVENANCE = PROVED_ALL_INPUTS.
UNPINNED_ODD_ROW_ALL_ONE_GF2_GAUGE = PROVED_ALL_INPUTS.
UNPINNED_GF2_FORCED_LITERALS_ONLY_ONE = PROVED.
UNPINNED_GF2_FORCED_PAIRS_ONLY_EQUALITIES = PROVED.
SOURCE_GF2_FORCED_BOOL_EXACTONE_CONTRADICTION = PROVED_ALL_INPUTS.
CONNECTED_CUBIC_BRIDGE_HOLYER_GF2_UNSAT = PROVED_ALL_BRIDGED_GRAPH_SOURCES.
FIVE_CUBIC_BRIDGE_SOURCE_FAMILIES = VERIFIED_CI.
DEFAULT_PORTFOLIO_NO_HINT_BRIDGE_UNSAT = VERIFIED_CI.
BASELINE_SAME_ZERO_BUDGET_WITH_GF2_OFF_UNKNOWN = VERIFIED_CI.
GF2_GAUSSIAN_CLOSURE_ALL_SCL_COMPLETE = FALSE_AS_CLAIM.
UNIVERSAL_SCL_POLYNOMIAL_WITNESS_OR_REFUTATION = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
