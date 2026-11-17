# R5 Universal Solver Attack — Exact Pinned-LP Distance-Shell Obstruction

Date: 2026-10-10
Repository: Hawkar-usls/Janus-Fundamentum, PR #515.
Verified predecessor on branch: `9a57a5c0cabbf9c07c4236e8bd6893f557e8afc3`.
Fixed E129 structural-validator dimension bug at
`c28b77c52b5f00db94bf43ae4c0c5224f25f44d9`.
Complete integrated R5 run `38066950581`: SUCCESS, 92/92 steps;
Validate JANUS registry run `38066950539`: SUCCESS.
No new positive P=NP theorem is claimed.

## 1. Universal algorithm attempt

A deterministic LP-guided self-reduction for all square/cubic/linear
positive Exact-One inputs would repeatedly select a check c, try three
states (1,0,0), and use polynomial-time linear programming to eliminate
branches for which

    Ax = 1; 0 <= x <= 1;
    x_chosen = 1; x_other_two = 0

is infeasible. LP feasibility is a necessary Boolean condition. One
could hope that exact fixed-point affine closure plus polynomial LP
consistency catches enough false supports to guarantee a polynomial
number of surviving recursion nodes.

There is NO proved global polynomial shrink theorem. The present
reproducible obstruction tests this hope at the first branching level
on the strongest frozen q63 E123 UNSAT control, with **exact rational
witnesses** rather than floating LP approximations.

## 2. Fully explicit LP solution for all 189 one-check pins

Let R be the source-oriented q63 Tutte-12/GH(2,2) incidence matrix from
E64/E123. Its connected cubic bipartite Levi graph has 63 check
vertices and 63 variable vertices, girth 12.

Fix **any** variable vertex j as the selected variable. Let d(v,j)
be the shortest Levi-graph distance between variables v and j
(an even integer). The exact distance-shell populations are

    d=0:   1 variable
    d=2:   6 variables
    d=4:  24 variables
    d=6:  32 variables.

For every j define

    x_v(j) = 1        when d(v,j)=0,
             0        when d(v,j)=2,
             1/2      when d(v,j)=4,
             1/4      when d(v,j)=6.

All coordinates lie in [0,1]. Every check sees one and only one of
the following distance triples:

    (0,2,2) : 1 + 0 + 0       = 1,
    (2,4,4) : 0 + 1/2 + 1/2   = 1,
    (4,6,6) : 1/2 + 1/4+1/4 = 1.

The checker independently rebuilds all Levi shortest-path distances
for each of the 63 roots, verifies every shell population, and
evaluates all 63 Exact-One **linear** equations over Fraction without
floating errors. Consequently

    R x(j) = 1;   0 <= x(j) <= 1;
    x_j(j)=1;    x_v(j)=0 for every v sharing a check with j.

Column j occurs in exactly three checks c. Therefore x(j) satisfies
the required Boolean (1,0,0) pin on **each** of these three checks,
and supplies three valid fractional pinned certificates. Since
there are 63 choices of j, all

    63 * 3 = 189 one-check pinned supports

admit exact rational LP extensions; the LP-support mask of every check
is 111, while its true Boolean SUPPORT is 000.

This is strictly stronger than E127's survival of local
unit/XOR/affine closure and its rational linear-consistency test:
we enforce nonnegative **and upper-bounded** x at the same time,
for the entire original system.

## 3. Independent Boolean UNSAT check

The checker imports only E64's canonical Tutte-12 matrix constructor
and E65's GF2 exact kernel basis. It enumerates its complete 2^14
binary kernel space (not an asymptotic algorithm). Every candidate
Exact-One solution must have binary parity representation x=1+k and

    |k| = 2n/3 = 42.

Instead the maximum observed exact GF2 kernel-word Hamming weight
is 40 (consistent with E65's min selected parity weight 23), proving
the q63 carrier UNSAT.

Thus 189 LP-feasible pinned states coexist with zero Boolean
solutions, without relying on SciPy, floating LP feasibility,
random restarts or SAT-oracle answers.

## 4. Uniform all-input theorem not obtained

The exact distance-shell construction works on this specific
strongly symmetric GH(2,2) carrier; it is NOT asserted to apply to
arbitrary square/cubic/linear matrices. It is a *counterexample*
to a would-be universal support inference of the form:

    pin(c,j) LP feasible  =>  pin(c,j) has a Boolean completion,

and to any recursion argument claiming its first branching step
will automatically prune at least one false branch whenever UNSAT.

It does not prove exponential lower bounds against every
LP-guided recursive algorithm, and it does not rule out
higher-order convex relaxations or genuinely global integrality
certificates.

The **required constructive theorem** for this algorithm family
remains: find a deterministic polynomially constructible global
Boolean-support certificate or polynomial-size recursion potential
for *every* cubic square linear carrier. In particular, it must
distinguish the 189 pinned LP-feasible but unsatisfiable E123
states from the SAT transpose control. No such theorem is proved.

## 5. Executable exact reproduction

    python experiments/r5_universal_lp_distance_shell_attack.py

Expected report:
    q63 GF2 nullity 14, max kernel weight 40 < 42;
    63 exact fractional root vectors;
    each variable shell counts [1,6,24,32];
    189 pinned LP supports;
    0 global Boolean Exact-One solutions.

The scientific claim is derived from the exact constructive shell
vectors and the exhaustive small negative control. A sample
floating SciPy LP feasibility check may support an exploratory
interpretation, but is unnecessary for the permanent certificate.

## Final claim boundary

E123_ALL_189_PINNED_LP_FEASIBLE = PROVED_BY_EXACT_REPLAY.
E123_ALL_189_PINNED_BOOLEAN_UNSAT = PROVED_BY_EXACT_REPLAY.
E123_DISTANCE_SHELL_LP_FORMULA = PROVED_BY_EXACT_REPLAY.
LP_FIRST_PIN_BRANCH_PRUNING_IMPLIED_BY_UNSAT = REFUTED.
GENERAL_POLYNOMIAL_RECURSION_SHRINK = OPEN.
UNIVERSAL_POLYNOMIAL_SUPPORT_CONSTRUCTOR = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
