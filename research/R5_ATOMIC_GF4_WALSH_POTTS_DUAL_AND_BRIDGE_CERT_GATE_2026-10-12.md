# R5 — Atomic SCL: Exact GF(4) Cycle/Cut Fourier Algebra and a Genuine Bridge Certificate

Date: 2026-10-12 Europe/Kyiv. Source repository:
Hawkar-usls/Janus-Fundamentum, stacked research DRAFT PR #516.

## 0. Global scientific objective and authority ceiling

Goal: deterministic `SolveLinearCubicXSAT(A)` that on EVERY
legal square+cubic/linear positive Exact-One SCL input returns
SAT + ORIGINAL verified Boolean witness or verified UNSAT within
one proved uniform n^O(1) worst-case BIT time.

**UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.**

Prior source-checked all-input reduction proves that even the
promised 3-edge-connected *Tanner* atomic SCL class is NP-complete.
The polynomial 1/2-edge-cut gates do not remove all hard cores.
Here we attack these cores by exact FLOW-SPACE algebra, not another
finite-only width/rank terminal. No assertion of P=NP follows.

This exact Walsh/MacWilliams/Tutte transform is CLASSICAL;
what is new to this JANUS checkpoint is its unified original-
source derivation, independent three-way exact integer replay,
precise signed cancellation/provenance firewall, and a new
conditional proof-carrying bridge expert on actual atomic
3-edge-connected Tanner SCL instances.

## 1. Holyer image + binary nowhere-zero 4-flow equivalence

For a finite CONNECTED SIMPLE CUBIC graph G=(V,E), set
v=|V|, m=|E|=3v/2, r=m-v+1=v/2+1.
The exact JANUS Holyer gadget-free positive Exact-One SCL
embedding A_G has 3m original Boolean variables/rows and
is SAT iff G has a proper labelled 3-edge-colouring.

Let B be the UNORIENTED edge/vertex incidence over F2,
and C=ker(B) subset F2^m, a binary cycle space of dimension r.
Represent the nonzero elements of F2^2 as the three
edge colours (1,0),(0,1),(1,1).

At a cubic vertex with three incident edge colours,
the vector-flow equation
    (f_e1,g_e1)+(f_e2,g_e2)+(f_e3,g_e3)=0 in F2^2
and the requirement that NONE is (0,0) hold iff those
three nonzero colours are ALL DISTINCT.
Indeed in a 2-dimensional F2-vector space the sum of
three nonzero elements vanishes only when they are
exactly the three different nonzero elements.

Therefore, with
   h(a,b)=1 if (a,b)!=(0,0), else 0,
the EXACT number of labelled 3-edge-colourings is

  N3(G) = sum_{f,g in C} product_{e in E} h(f_e,g_e).

An original SAT certificate is recovered immediately by
mapping each nonzero pair to its corresponding one-hot
source variable X_(e,c) and validating every original
SCL Exact-One row. A zero result is logically UNSAT,
but producing that zero by the naive complete flow
enumeration costs 4^r pair states — exponential.

## 2. Exact 4-state Walsh/Fourier duality

Define the two-bit Walsh transform

  h_hat(s,t)=(1/4) sum_{a,b in F2}
                  h(a,b)(-1)^(as+bt).

A direct FOUR-entry computation yields

  h_hat(0,0)=3/4,
  h_hat(s,t)=-1/4 for (s,t)!=(0,0).

Expanding product_e h(f_e,g_e) in Walsh characters,
then applying character orthogonality over C, leaves
ONLY s,t in C^perp, the cut space of G:

  N3(G) = 4^r sum_{s,t in C^perp}
            product_e h_hat(s_e,t_e).

For connected G, each binary cut is the vertex
coboundary of exactly one vector after fixing
the root potential to 0. Thus a pair (s,t)
corresponds to a unique vertex 4-label assignment
sigma:V -> F2^2, sigma(root)=(0,0). For each edge uv,
(s_e,t_e)=sigma(u)+sigma(v).

Define the exact SIGNED integer numerator

  Z_G = sum_{sigma(root)=0}
          product_{uv in E}
            (3 if sigma(u)=sigma(v) else -1).

THEN THE UNIVERSAL IDENTITY:

  **N3(G) = Z_G / 4^(v-1).**

Consequences:
- Z_G is exactly divisible by 4^(v-1);
- the quotient is a NONNEGATIVE INTEGER despite positive
  and negative terms in Z_G;
- Z_G=0 iff the exact original Holyer SCL A_G is UNSAT;
- evaluating the full Z_G by enumerating vertex
  4-labelings requires 4^(v-1) states, exponential.

This is NOT a polynomial decision algorithm just because
the final integer has only O(v) bits.

### Why this candidate does NOT give free compression

For connected cubic G, r=v/2+1.
The two exact direct enumeration sizes are

  PRIMAL binary cycle pairs:  4^(v/2+1).
  DUAL anchored cut potentials: 4^(v-1).

For v>4 the naive dual requires exponentially MORE
summands than primal. The transform is an exact
algebraic alternative and gives useful signed
certificates but does not justify a polynomial
flow-support Fourier evaluator. Polynomial-size
symbolic expression or matrix rank alone also
does not imply poly-time exact noncancellation testing.

## 3. Third INDEPENDENT representation: Tutte/FK expansion

In the dual product write edge weight as

    3 if equal else -1 = (4 * 1[equal] - 1).

Expand over selected edge subsets A subset E.
For fixed A, vertex labels are forced equal along A,
leaving 4^(c(V,A)-1) anchored labelings.
Therefore

  Z_G =
    sum_{A subset E} (-1)^(m-|A|)
                       4^(|A|+c(V,A)-1).

Divide by 4^(v-1):

  **N3(G) = sum_{A subset E}
            (-1)^(m-|A|) 4^(|A|-v+c(V,A)).**

The exponent is the nonnegative binary cycle rank
of the spanning subgraph (V,A). This is the ordinary
4-flow polynomial / Tutte special evaluation,
not a novel complexity breakthrough.

An independently implemented subset generator checks
the last formula without reusing cycle-flow or
Walsh vertex-label enumeration. It takes 2^m
subsets, also exponential. The three identities
are proved symbolically above for ALL connected
simple cubic graphs; finite CI checks detect
implementation/algebraic mistakes.

## 4. Original cubic bridge yields a SHORT certified UNSAT
##    even though its SCL Tanner graph is ATOMIC 3-connected

For a bridge e of any connected simple cubic G, remove e.
Consider a bridge side S. Cubic degree counting gives

  3|S| = 2|E(G[S])| + 1,

so |S| is ODD. Every colour class of a proper
3-edge-colouring is a PERFECT MATCHING. For a
perfect matching M_c and an odd vertex subset S,

  |M_c intersect delta(S)| = |S| (mod 2) = 1 mod 2.

Thus all THREE colours require at least one crossing
edge. But delta(S)={e} has only ONE edge.
Contradiction; G is NOT 3-edge-colourable and A_G is
UNSAT. This is a classical exact cut-parity lemma.

Implementation:
`experiments/r5_universal_atomic_gf4_cycle_cut_fourier_duality.py`
provides exact_bridge_witness, verify_bridge_witness,
and authenticated_holyer_bridge.

The SCL Portfolio has an OPTIONAL
`certified_holyer_edges` argument. It is **UNTRUSTED**:
the expert reconstructs EVERY original exact SCL
clause via make_scl(graph) and checks complete
canonical equality with original source rows/n.
A forged graph of the SAME source dimension raises
ValueError rather than pretending to prove UNSAT.
If a bridge exists, its concrete edge, side vertices
and oddness/cut cardinality are replayed by a separate
witness checker; only THEN does the common Portfolio
admit source-level
`UNSAT / HOLYER_CUBIC_BRIDGE_PARITY`
with `cubic_bridge_provenance`.

This graph bridge is NOT a bridge in the Tanner graph.
The previous universal Holyer theorem actually proves
that the input's Tanner graph is 3-edge-connected
for every connected simple cubic G, including bridged G.
Consequently this is a genuine polynomial-time
NEGATIVE expert applicable to some atomic SCL inputs.
It does NOT certify Petersen or other bridgeless snarks,
nor does it automatically discover Holyer decompositions
from arbitrary unlabelled SCL sources.

## 5. CI controls, exact provenance and falsification

Frozen independent tests:
`experiments/r5_universal_atomic_gf4_cycle_cut_fourier_duality.py`.
Workflow:
`.github/workflows/r5-atomic-gf4-cycle-cut-duality.yml`.
Confirmed CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38275702509
SUCCESS (first full integration).
Additional source-side independent Tanner 3-edge mincut
assertion added to a successor run.

All counts are labelled proper 3-edge colourings:

| Graph | v | m | source SCL n | r | N3 | Signed anchored Z |
|---|---:|---:|---:|---:|---:|---:|
| K4 | 4 | 6 | 18 | 3 | 6 | 384 |
| K3,3 | 6 | 9 | 27 | 4 | 12 | 12288 |
| Cube | 8 | 12 | 36 | 5 | 24 | 393216 |
| Triangular prism | 6 | 9 | 27 | 4 | 6 | 6144 |
| C5 prism | 10 | 15 | 45 | 6 | 30 | 7864320 |
| Petersen | 10 | 15 | 45 | 6 | 0 | 0 |
| Simple cubic with bridge | 10 | 15 | 45 | 6 | 0 | 0 |

Each row is checked by THREE independently coded
algorithms (binary cycle-space pair count,
anchored four-state vertex Potts signed sum, and
Fortuin-Kasteleyn spanning subgraph expansion).
On the bridged graph, the common
`SolveLinearCubicXSAT_Portfolio` returns independently
verified `UNSAT` with ZERO residual/PC3 states.
A same-dimension forged graph hint is rejected.
A no-bridge graph never gets a false negative
from this bridge-only expert.

Notably Petersen and C5 prism have the same
original graph size / cycle dimension and the
same Holyer-SCL Smith Normal Form (predecessor
SNF checkpoint) but signed Potts Z equals 0 vs
7864320. Merely reading ranks/Smith invariant
factors does not decide the Boolean source.

## 6. Current targeted literature

Recent relevant surface-restricted result:
Y. Inoue, K. Kawarabayashi, A. Miyashita,
B. Mohar, T. Sonobe, `Three-edge-coloring
(Tait coloring) cubic graphs and nowhere-zero
4-flow for graphs on the torus`, SODA 2026,
pp 6133–6165; published January 7, 2026;
DOI 10.1137/1.9781611978971.218,
https://epubs.siam.org/doi/10.1137/1.9781611978971.218.

Their classification and quadratic-time algorithm
apply to cubic graphs embedded on a TORUS (genus 1),
with exceptions/Petersen-like structure treated
under their precise hypotheses. It is important
current external mathematics on the same 4-flow
structure, but does NOT furnish a polynomial
method for arbitrary (unbounded genus) cubic
graphs or JANUS's unrestricted SCL promise.
Do not import its results without checking the
surface preconditions and implementing verified
embedding/certificate adapters.

## 7. The one true next theorem

Find and prove a deterministic polynomial-bit
evaluation (or ZERO/nonzero test with verified
SAT witness extraction) of the exact full-support
cycle-pair coefficient or equivalently the
signed four-state Potts sum for ALL connected
simple cubic graphs, including arbitrary
unbounded-genus snarks; transfer the result by
the Holyer source-equivalent mapping.
A valid uniform n^C method would prove P=NP.
Neither writing an exponential partition function
as a compact formal expression nor fixing
one constant number of Walsh moments gives that
algorithm.

Alternatively discover an entirely different
all-input polynomial-certified family-union
mechanism, but it must handle the NP-complete
3-edge-connected Tanner atomic subclass proved
in the immediately preceding checkpoint.

## Gate ledger

GF4_CYCLE_PAIR_COLOUR_BIJECTION = PROVED.
GF4_WALSH_CUT_POTTS_DUALITY = PROVED.
GF4_ANCHORED_SIGNED_NUMERATOR_DIVISIBILITY = PROVED.
TUTTE_SPANNING_SUBGRAPH_4FLOW_FORMULA = PROVED_CLASSICAL.
THREE_INDEPENDENT_EXACT_INTEGER_COMPUTATIONS = VERIFIED_CI.
DUAL_SUM_BETTER_THAN_PRIMAL_ON_GENERAL_CUBIC = FALSE_BY_DIMENSION.
AUTHENTICATED_HOLYER_ORIGINAL_SOURCE_MATCH = VERIFIED_CI.
CUBIC_BRIDGE_PERFECT_MATCHING_PARITY_UNSAT = PROVED.
ATOMIC_TANNER3_GRAPH_BRIDGE_UNSAT_ADAPTER = VERIFIED_CI.
GLOBAL_POLYNOMIAL_FOUR_FLOW_NONZERO_TEST = OPEN.
GLOBAL_POLYNOMIAL_SAT_WITNESS_EXTRACTION = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
