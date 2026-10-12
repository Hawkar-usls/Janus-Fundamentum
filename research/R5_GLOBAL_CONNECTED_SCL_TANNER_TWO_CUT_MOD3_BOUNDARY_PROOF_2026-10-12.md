# R5 — Connected SCL Tanner Minimal-Cut Arithmetic and Certified Expert Propagation

Date: 2026-10-12 Europe/Kyiv. Research branch for PR #516,
base on #515; main unchanged.

## Objective

UNIVERSAL deterministic `SolveLinearCubicXSAT` with SAT+witness
or UNSAT and a uniform `n^O(1)` worst-case bit runtime on EVERY
legal square+cubic+C4-free positive Exact-One input. At this
checkpoint this final goal is **NOT CONSTRUCTED** and `P vs NP`
remains **OPEN**.

The mathematical progress here applies to the exact ORIGINAL
square+cubic+linear input — not a heuristic relaxation, not a
graph-3-edge-colourability-only subclass, and not empirical
polynomial complexity.

## I. Exact all-input 1-cut and 2-cut theorems

Let G be the original bipartite Tanner graph: one vertex per
Exact-One ROW, one per variable COLUMN, and an edge for each
incidence 1. For any valid n-by-n SCL matrix every vertex has
degree exactly 3.

For an arbitrary vertex subset S let

   r = number of clause vertices in S,
   v = number of variable vertices in S,
   a = number of crossing incidences with ROW endpoint in S,
   b = number of crossing incidences with VARIABLE endpoint in S.

Double-counting internal incidence ends:

   3r = I + a,
   3v = I + b,

therefore EXACTLY:

   a - b = 3(r-v).

A single-edge cut would give a+b=1 and a-b=+/-1, impossible
modulo 3. Hence **EVERY connected cubic SCL Tanner graph is
bridgeless**. This does not mean it is 3-edge-connected.

For any 2-edge cut a+b=2, and since a-b is a multiple of 3,
the only possibility is

   a=b=1, r=v.

On BOTH sides we obtain one boundary row and one boundary
variable, and equal numbers of internal original rows and
columns. These cut-open fragments themselves have irregular
boundary degrees and are NOT silently valid independent
square/cubic/linear SCL sources; they require a correctly
designed boundary-signature solver.

A deterministic source-checked 2-cut recognizer can enumerate
all O(n²) edge pairs and perform O(n) reachability for each
(3-regular sparse graph), taking O(n³) time plus polynomial
source canonicalization. When no 2-cut exists, the connected
graph has edge connectivity exactly 3, since its degree is 3
and no bridge exists.

## II. New exact MOD-3 boundary identity for EVERY 2-cut

Take a certified side S of a two-edge cut with r original
rows and r internal variables. Name:

  u = internal variable whose 3rd incidence goes to an
      original clause OUTSIDE S.
  w = external variable whose 3rd incidence goes to an
      original clause INSIDE S.

Sum EXACTLY the r source Exact-One rows inside S, evaluated
on an arbitrary globally satisfying Boolean assignment x.
Each selected internal variable contributes 3 incidences,
except x_u contributes only 2 to the internal sum; x_w
contributes one external incidence. Thus:

  r = 3 * sum_(v internal S) x_v - x_u + x_w

and hence the universal integer identity

  3 * sum_(v internal S) x_v = r + x_u - x_w.

Since x_u,x_w in {0,1}, residue r mod 3 yields an **exact
boundary relation**, not a heuristic:

  r≡0 mod3 :   x_u = x_w .
  r≡1 mod3 :   x_u = 0 AND x_w = 1.
  r≡2 mod3 :   x_u = 1 AND x_w = 0.

This remains correct for SAT/UNSAT instances, arbitrary pins,
all sizes, any legal original SCL incidence geometry. The
proof also applies to every certified two-cut inside a larger
connected Tanner component, independent of nesting.

An original-input contradiction between any two independently
verified boundary consequences certifies UNSAT; no SAT model
could satisfy the required cut row sums. The same holds
when original caller pins conflict with a certified
boundary equality or forced unary value.

For residue-zero sides, the unpinned equality is not yet a
general source variable-contraction mechanism; it is
preserved as a certified relation and propagates both ways
once either boundary variable is fixed.

## III. Implemented proof-aware cooperation

Source-audited module:
`experiments/r5_universal_connected_scl_tanner_two_cut_proof_audit.py`

  `exact_tanner_graph`,
  `certified_tanner_edge_connectivity`,
  `certified_two_cut_mod3_rules`,
  `exact_connected_incidence_switch`.

The main `SolveLinearCubicXSAT_Portfolio` now accepts
`tanner_cut_max_n` (default 45, 0 disables this pass).

For ORIGINAL connected legal SCL source n<=cut guard, after
the previously verified general connected-component split
and shared proof-state replay:
  1. Enumerate and INDEPENDENTLY verify all 2-edge cuts
     and their 1-row/1-variable boundary orientations.
  2. Produce exact source-indexed equalities or forced pins
     under the modular identity.
  3. Combine with caller/shared-state pins, check certified
     conflicts and repeatedly propagate equalities.
  4. Forward ONLY newly proven pins to the existing root
     GF2/MOD9/ExactSupport, PC3 and complete exact fallback.
  5. Include `tanner_cut_provenance` and
     `tanner_cut_derived_pins` in the public solver result.
  6. If n>size guard, skip exactly, not a negative claim.

This adds a polynomial-time **all-input sound gate** to a
deterministic cooperative solver. The size guard currently
limits where the gate is deployed for practical cost;
it does NOT limit validity of the underlying theorem.

When optional complete fallback is enabled its worst-case
complexity remains potentially exponential — discovering
the correct 2-port boundary relation is not sufficient to
solve arbitrary 3-edge-connected interiors.

## IV. Independent finite tests with explicit scientific scope

Source:
`experiments/r5_universal_connected_scl_tanner_two_cut_proof_audit.py`.
Workflow:
`.github/workflows/r5-tanner-two-cut-universal-audit.yml`.

Focused final CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38253716467
SUCCESS.

1. Fano SCL7 (Heawood Tanner graph) is certified 3-edge-
   connected: every removal of one or two incidence edges
   leaves the graph connected.
2. Start from two valid SAT K4 direct-edgecolour SCL18
   components and exchange exactly one incidence between
   a row/variable pair from each. The connected result
   is an ORIGINAL legal connected SCL36 with a genuine
   2-edge cut partitioning rows and variables 18+18.
   This construction independently verifies every row's
   size/variable degree and C4-free linearity.
3. For this connected SAT SCL36, residue r=18 mod3=0
   enforces `x_0=x_18`, with an independently verified
   full SAT witness. This is NONVACUOUS knowledge.
   Feeding original caller pin `x_0=1` to the
   common Portfolio derives and transmits `x_18=1`
   even when bounded ExactSupport states=0.
   Opposite caller pins `x_0=1,x_18=0` are rejected
   with certified UNSAT, without speculation or DAG.
4. Connected original SCL15 from the valid cyclic 7
   and cyclic 8 sources with one incidence exchange
   has r mod3 nonzero and leads to certified pins
   `x_0=0,x_7=1` with correct source mapping.
   A fully independent exhaustive enumeration of all
   2^15 Boolean assignments finds **ZERO SAT models**.
   Hence this n15 control tests the SOUNDNESS of a
   conditional deduction but is VACUOUS evidence of
   genuine model-forcing. No claim of SAT is permitted.
   The derived pins are nevertheless passed to the
   common Portfolio with exact proof provenance.
5. Setting `tanner_cut_max_n=0` disables the module
   and leaves no derived boundary pin; this is a
   resource guard, not a declared proof failure.
6. Existing root MOD9, PC3, mixed-component witness,
   complete AND/OR fallback and odd-symmetry
   integration regressions:
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38253635639
   SUCCESS;
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38253635480
   SUCCESS;
   https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38253635402
   SUCCESS.

The two failed intermediate CI checks are preserved for
provenance: a Tanner endpoint-indexing error (variables
already offset by n) and an incorrectly assumed existence
of a SAT witness on the n15 **UNSAT** finite test.
Both were corrected; successful CI verifies the finalized
claims above. Do not erase those failed history entries.

## V. Next decisive universal theorem gate

This step proves a new exact universal source-level
SEPARATOR CONSEQUENCE and implements certified transfer
to the original proof-state. It does not solve the general
connected 3-edge-connected SCL core.

The next worthwhile extension is a rigorous 2-port
**boundary-signature algebra** for arbitrary cut-open
irregular pieces, using independently verified SAT
witness construction and UNSAT proof composition.
For each 2-cut, only four assignments of (x_u,x_w)
exist; the theorem above filters them to two or one,
but computing whether each large side allows a given
state can still require exponential exact search.
A formally polynomial composition of bounded interface
signatures would be useful only if the atomic core
signatures were themselves polynomially computable.

The true missing all-input decision theorem is:

  Every CONNECTED original SCL source F, after all
  proven separator, symmetry, algebraic and shared
  fact reductions, reaches independently verified SAT
  witness or UNSAT in one uniform n^C bit bound.

No such theorem is proved. Neither constant-boundary
fact propagation nor polynomial accepted-knowledge
potential implies an all-input polynomial decision.

## Gate ledger

SCL_TANNER_BRIDGE_IMPOSSIBLE = PROVED_ALL_INPUT.
SCL_TANNER_2CUT_EXACT_BALANCED_PORTS = PROVED_ALL_INPUT.
SCL_TANNER_2CUT_MOD3_UNARY_EQUALITY_RULE = PROVED_ALL_INPUT.
SCL_TANNER_2CUT_DETECTION_POLYNOMIAL = PROVED.
SCL_TANNER_CUT_PROVENANCE_TO_PORTFOLIO = VERIFIED_CI.
SCL36_SAT_BOUNDARY_EQUALITY_AND_PIN_GLUE = VERIFIED_CI.
SCL36_PIN_CONTRADICTION_CERTIFICATE = VERIFIED_CI.
SCL15_MOD3_FORCED_PINS = PROVED_CONDITIONAL_BUT_ZERO_SAT_MODELS.
UNBOUNDED_TWO_PORT_ATOMIC_SIGNATURE_POLY_CONSTRUCTION = OPEN.
ALL_CONNECTED_SCL_POLYNOMIAL_EXPERT_COVERAGE = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
