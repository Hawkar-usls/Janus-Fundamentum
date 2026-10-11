# R5 — Exact All-Cubic Two-Adic Cycle-Layer Filtration and Hamiltonian-Parity Base Gate

Date: 2026-10-12 (Europe/Kyiv).
Source: PR #516 successor to direct cubic graph -> legal SCL bridge
and 2-adic precision attack. **UNIVERSAL POLY SOLVER NOT CONSTRUCTED.**

## I. Exact all-cubic identity: fix colours at one vertex

Let G be a connected simple cubic graph on v=2h vertices.
Label the 3 colours 0,1,2, and fix a cubic vertex r with incident
edges e0,e1,e2. Require these three edges to have colours 0,1,2
respectively. S3 acts freely and transitively on the six local
colour assignments, so the number of colourings obeying these pins is

  C(G) := #labelled_3_edge_colourings(G)/6.

For every perfect matching M containing e0, remove M.
The complement G-M is a vertex-disjoint 2-factor with cycle lengths
l1,...,lc (every vertex has degree two).

It supports the pinned colours 1,2 precisely when all its cycles
are EVEN. If some cycle is odd, alternating 1/2 is impossible.
If all cycles are even, the unique cycle containing r has exactly
ONE valid alternation because the colours of e1 and e2 are pinned.
Each of the other c-1 cycles contributes exactly two alternations.

**Exact identity for ALL simple cubic G:**

  C(G) =
     sum_{M perfect matching, e0 in M,
          every cycle of G-M even}  2^(c(G-M)-1).       (1)

This is sound, complete, has no signs or cancellation,
and explicitly retains all proper colourings.
It does NOT yield a polynomial algorithm, since the number of
perfect matchings is unbounded and may be exponential.

## II. Exact 2-adic filtration, for any precision s>=1

Taking (1) modulo 2^s kills exactly those individual positive
summands whose complementary 2-factor contains at least s+1
connected cycles:

  C(G) mod 2^s =
     sum_{M includes e0, all residual cycles even,
          c(G-M)<=s} 2^(c(G-M)-1)   mod 2^s.          (2)

This is a nonnegative 2-adic layer decomposition.
**Do not mistake few layers for few contributing matchings.**
Already at s=1, the sum ranges over Hamiltonian cycles, and
there may be exponentially many of them.

## III. Base level s=1 equals parity of Hamiltonian cycles

When s=1, only c(G-M)=1 survives. A spanning 2-factor
with ONE cycle is precisely a Hamiltonian cycle H; its
complement is the unique perfect matching M=E-H.

Thus

  C(G) mod 2 =
    #{Hamiltonian cycles H of G with e0 NOT in H} mod 2.    (3)

By **Smith's theorem** (or Thomason's parity theorem), every
edge e of a cubic graph belongs to an EVEN number of
Hamiltonian cycles. Therefore, for every root edge e0,

  #{H: e0 not in H} == #{H: all} (mod 2).

Consequently:

  #labelled_3_edge_colourings(G)/6
        == #Hamiltonian_cycles(G)  (mod 2).               (4)

This parity connection is classical and discussed in
Leslie G. Valiant, `Observations on the Complexity of Counting
and a Characterization of the Determinant` (2017), Theorem 8:
https://people.seas.harvard.edu/~valiant/observations-8-1-17.pdf

Another source for Smith's theorem: Thomason's proof and
related survey, https://doi.org/10.1016/j.disc.2013.06.019.

**Anti-priority warning:** Equation (4) is NOT asserted as an
original novelty, and no claim is made that parity Hamiltonian
cycle counting is provably superpolynomial on cubic graphs.
The complexity of the relevant parity problem has been explored
as an open question (Valiant), so do not invent a hardness theorem.

Crucial point: a hypothetical polynomial evaluator of the LOWEST
bit of C(G) would provide the parity of Hamiltonian cycle counts;
but that lowest bit does NOT decide 3-edge-colourability universally.
The connected SAT graphs with C(G_t)=2^t from the predecessor
checkpoint have all lowest t bits zero. Even a correct polynomial
Hamiltonian-parity oracle would fail as a SAT decider on those
explicitly colourable inputs.

## IV. Polynomial evaluation gate, not achieved

The published Ivanov (2020) bound says for every connected cubic
G with v=2h, C(G)<2^h. Therefore ALL h bits of C(G) are enough
for a sound complete SAT zero test.

Equation (2) exposes an exact *lift tower*:
  s=1: Hamiltonian-cycle parity.
  s>1: even spanning 2-factors with up to s components, weighted
       2^(c-1) modulo 2^s.

The missing universal theorem would evaluate the cumulative
weighted sums for **s=h=Theta(v)** in deterministic poly(v)
BIT operations without enumerating exponentially many matchings,
cycles, or branch states.

The fact that 2^h has h+1 bits removes **large output size**
as a bottleneck; it does NOT remove the combinatorial difficulty
of calculating its residue.

## V. Reproducible checker

  python experiments/r5_universal_2adic_hamiltonian_parity_filtration.py

Tests independent exact count against rooted layer sums at
all three root incident edges. On n<=10, enumerates Hamiltonian
cycles separately by direct vertex-DFS (not matching enumeration).
On all cases, checks Smith even-incidence consequence and s=1,...,5
truncated sums against direct C mod 2^s.

Control graphs K4, K3,3, cube, odd prism P5,
Petersen, flower J5, and SAT20 have independently frozen
SAT or UNSAT status.

Finite checks are exponential and cannot serve as a
universal polynomial evaluation proof.

## VI. Gate ledger

ALL_SIMPLE_CUBIC_3EDGE_COLOUR_NORMALIZED_MATCHING_LAYER = PROVED.
ALL_SIMPLE_CUBIC_2ADIC_LAYER_TRUNCATION = PROVED.
ROOT_HAMILTONIAN_PARITY_IDENTITY = PROVED.
TOTAL_HAMILTONIAN_PARITY_IDENTITY = PROVED_USING_SMITH_THEOREM.
CUBIC_PARITY_HAMILTONIAN_POLYTIME_ALGORITHM = NOT_CONSTRUCTED.
UNIFORM_POLY_2ADIC_LIFT_ALL_PRECISIONS = NOT_CONSTRUCTED.
ALL_INPUT_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
