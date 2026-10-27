# FARADAY–RAMANUJAN–EXACTONE: a falsifiable mathematical bridge

Date: 2026-10-28
Status: EXPLORATORY / FINITE EXACT CONTROLS / NO SOLVER CLAIM
Target: experiments/direct/ramanujan_mock_theta_exactone_probe.py
Relationship: independent research lane; no modification to admitted A3, mainline C023, or R5 PR #515.

## Research question

Can discrete cochain/cycle invariants or a rigorously proved modular, mock-modular,
or theta-series representation of the Exact-One energy partition polynomial yield a
new *polynomial-time constructible and evaluable* exact global-support invariant?

This is a testable question, not a claim that physical fields, quantum superposition,
Ramanujan's mock theta functions, or torsion fields solve NP-complete problems.

## Exact mathematical object

For a square+cubic+linear Exact-One incidence matrix A (n rows and n columns,
three ones in each row/column, pairwise row intersections <= 1), define for a
Boolean vector x:

    E_F(x) = sum_{i=1}^n (sum_j A_ij*x_j - 1)^2
    Z_F(q) = sum_{x in {0,1}^n} q^(E_F(x)) = sum_{k>=0} a_k*q^k

For every such F:
- a_k are nonnegative integers.
- a_0 counts exact solutions; a_0 > 0 if and only if SAT.
- Z_F(1) = 2^n.
- Z'_F(1) = n*2^n (because a random 3-bit row has expected squared
  Exact-One violation [1+3+4]/8 = 1).
- For any deleted check c, SUPPORT_c contains the incident ports chosen by
  at least one exact solution. Recovering it by exhaustive enumeration does
  NOT yield a polynomial-time algorithm.

This polynomial is an energy generating function. It is not shown to be a theta
or mock theta function. Equating arbitrary such polynomials with Ramanujan's
mock theta series without a valid transformation is unsound.

## Ramanujan comparison (deliberate negative control)

Use the third-order mock theta series:

    f(q) = sum_{r>=0} q^(r*r) / product_{k=1}^r (1+q^k)^2

Formal expansion to degree 12 produces:

    [1, 1, -2, 3, -3, 3, -5, 7, -6, 6, -10, 12, -11]

The negative coefficients disprove a direct unshifted, untransformed
coefficient-by-coefficient identification with Z_F, whose coefficients are
nonnegative. This does NOT rule out a valid nontrivial transform or a restricted
family, and does NOT prove such a transform exists.

References:
- Bruinier, Schwagenscheidt, "Completions and algebraic formulas for the
  coefficients of Ramanujan's mock theta functions":
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8599414/
- Dabholkar, Murthy, Zagier, "Quantum Black Holes, Wall Crossing,
  and Mock Modular Forms": https://arxiv.org/abs/1208.4074

The black-hole result applies to specific BPS-state generating functions; it
provides no reduction or complexity bound for Exact-One.

## Faraday/cochain boundary

The differential-form version of Faraday induction is dE = -d_t B.
On an oriented discrete cell complex the corresponding *kinematic*
cochain relation is C*e = -d_t*b. The identity C*G = 0
(discrete curl of a gradient = 0) follows from boundary-of-boundary = 0.
The finite test verifies this identity on a triangle.

No canonical cell complex or physical dynamical operator converting an
arbitrary Exact-One instance into a field problem with polynomial cost has
been established here. Physical signal propagation is not instantaneous;
superluminal "tracing/torsion information fields" are not a validated
computational resource; minimizing physical energy is not automatically a
polynomial-time exact global optimizer.

## Controls and expected findings

The script exhaustively enumerates every state for fixed circulant incidence
families with rows {i+s mod n: s in shifts}. Each fixture is verified to be
square, cubic and linear. An independent recursive exact-one search checks the
solution count. The connected bipartite incidence graph has 2n vertices,
3n edges, and cycle rank n+1.

  fixture                  n   shifts       SAT count   GF(2) rank   cycle rank
  n09_unsat                9   (0,1,3)      0           9            10
  n12_unsat               12   (0,1,3)      0          12            13
  n12_sat                 12   (0,1,5)      3          10            13
  n15_unsat_rank_deficient 15  (0,1,4)      0          11            16
  n15_sat                 15   (0,1,5)      3          13            16

The two n=12 instances have identical degree profiles, number of vertices,
edges, and graph-cycle rank, yet different SAT answers. Crucial confounder:
their GF(2) ranks DIFFER, so this pair does not defeat the existing affine
rank router. It only falsifies the sufficiency of those simpler invariants.

Easy theorem/negative control: for every square cubic Exact-One matrix, the
all-ones vector satisfies A*x=1 over GF(2). If A has full rank over GF(2),
it is the unique GF(2) solution; because every row contains three ones,
the all-ones vector is NOT an Exact-One solution. Thus full GF(2) rank
implies exact UNSAT. The n=15 (0,1,4) instance is a more informative finite
UNSAT control with a nontrivial GF(2) kernel; no hardness claim is made.

Exact enumeration costs 2^n assignments. The number of counted states,
verification work, and any representation/completion costs must be charged.

## Preregistered kill conditions

The universal solver route fails if any of the following is true:
1. Proposed invariant does not preserve a_0 or exact SUPPORT_c.
2. Required q-series or physical encoding takes exponential time, size,
   parallel hardware, energy, measurement precision, or readout.
3. A transform to a mock modular form only exists after computing a_0.
4. A purported global invariant is already subsumed by standard GF(2)
   elimination, XOR closure, branchwidth, or existing R5 polynomial terminals.
5. New finite positive cases are misreported as asymptotic evidence.
6. One family admits a short description while an unrestricted family does not.

## Next admissible gate

Find an *explicit* infinite family (ideally including post-E18-clean,
KLOC3-clean and nontrivial separator controls), and either:

(A) provide a polynomial-size, polynomial-time constructible symbolic
representation for Z_F or at least exact SUPPORT_c, with polynomial-time
evaluation / witness recovery on the full target class; OR
(B) prove a sharply scoped restricted-family theorem with a demonstrated
new capability beyond the current R5 routers; OR
(C) preserve a reproducible counterexample/obstruction that kills the route.

Do not claim mock modularity from a finite coefficient match.
Do not replace main, merge PR #515, alter the A3 frozen proof, or claim P=NP.

## Replay

    python experiments/direct/ramanujan_mock_theta_exactone_probe.py --self-test
    python experiments/direct/ramanujan_mock_theta_exactone_probe.py --json

Status:
    FINITE_TESTS = PASS (local, independent counts)
    MOCK_MODULARITY_OF_ZF = NOT_ESTABLISHED
    POLYNOMIAL_GLOBAL_SUPPORT = NOT_ESTABLISHED
    PHYSICAL_SPEEDUP = NOT_ESTABLISHED
    P_VS_NP = OPEN
