# 2025 Published P=NP Claim: Two Independent Constructive Counterexamples in the Exact SCL Class

Date: 2026-10-11.
Research branch: PR #515, `research/parity-isolation-trade-checkpoint-20261009`.
Status: EXACT GENERAL COUNTEREXAMPLE TO TREEWIDTH PROP. 4, PLUS
EXACT n=9 COUNTEREXAMPLE TO THE PUBLISHED DETERMINANT SHORTCUT.
P_VS_NP=OPEN. UNIVERSAL POLY SOLVER=NOT_CONSTRUCTED.

## External source and precise claim

Omar Kettani, *Cubic Monotone 1-in-3 SAT Problem is Polynomial Time
Solvable*, International Journal of Mathematics Trends and Technology,
71(9):36–46 (2025), doi:10.14445/22315373/IJMTT-V71I9P105.

PDF:
https://ijmttjournal.org/public/assets/volume-71/issue-9/IJMTT-V71I9P105.pdf

Page 39–43, Proposition 4 asserts that the column-conflict graph
of every cubic monotone 1-in-3-SAT matrix is induced-K1,4-free
and has bounded treewidth; the stronger claimed statement
(max degree 6, K1,4-free, >=3 triangles per vertex => tw<=6)
appears on p.40 and its conclusion on p.43.

Page 45, Table 2 Algorithm Step 2 says that if det(A)!=0,
return the unique solution x=A^{-1} 1, without validating
x is a {0,1} truth assignment.

These statements are not both valid. Counterexamples below are
fully within JANUS's SQUARE + CUBIC + LINEAR positive Exact-One
target, not arbitrary graph counterexamples.

## Theorem A. Infinite family of legitimate SAT carriers with tw(G)>=L-1

For any integer L>=9 with 3|L define variables indexed by
V=Z_L x Z_L, total n=L^2. For each (i,j) in V create exactly
one Positive Exact-One check:

    x_(i,j) + x_(i+1,j) + x_(i,j+1) = 1,

with modular indices. Call the n-by-n 0/1 incidence matrix A_L.
Its conflict graph G_L has n vertices (the variables) with
an edge exactly when two variables appear in the same check.

1. Every row has exactly three distinct ones for L>=4.

2. Every variable x_(i,j) occurs in exactly three checks,
   anchored at (i,j), (i-1,j), (i,j-1). A_L is square+cubic.

3. LINEARITY: each check support is a translate of
   S={(0,0),(1,0),(0,1)}. Its six nonzero ordered differences
   are (+/-1,0), (0,+/-1), (+/-1,mp1) in the paired
   diagonal orientations (+1,-1),(-1,+1).
   These are all distinct in Z_L^2 for L>=4.
   If two distinct translates had intersection size >=2,
   their translation displacement would be expressed by
   two distinct ordered differences of S, a contradiction.
   Hence every pair of checks shares at most one variable.
   A_L is precisely C4-free/linear.

4. Every vertex of G_L has six distinct neighbors, grouped into
   three disjoint PAIRS from its three incident checks. Each pair
   consists of adjacent vertices, because both are in the same
   Exact-One triangle. Consequently its neighborhood contains no
   independent set of size four. Thus G_L is 6-regular,
   induced-K1,4-free, and every vertex belongs to AT LEAST three
   triangles, exactly the hypotheses used in the published paper.

5. G_L contains the ordinary L-by-L grid as a SUBGRAPH:
   each horizontal (i,j)--(i+1,j) and vertical
   (i,j)--(i,j+1) grid edge occurs in a check anchored at (i,j).
   Delete wraparound and diagonal edges to see the grid.

6. PROVED TREEWIDTH LOWER BOUND WITHOUT A BLACK-BOX SOLVER:

   In the ordinary L-by-L grid form the crosses

       C_(i,j) = (all vertices of grid row i)
                 union (all vertices of grid column j).

   Every two crosses intersect (row i of the first meets column
   j' of the second), and every cross is a connected subgraph.
   Any hitting set T with fewer than L vertices misses some full
   row AND some full column, hence misses their cross altogether.
   Therefore every set hitting all crosses has size >=L.

   In any tree decomposition of G_L, bags touching any fixed
   cross form a connected subtree: the vertices in that cross
   induce a connected subgraph, and the bag subtrees for its
   vertices are connected via its grid edges.

   As crosses pairwise intersect, their associated subtrees
   pairwise intersect. Subtrees in a tree have the Helly property,
   so a common bag intersects ALL crosses. It must contain at
   least L vertices by the preceding hitting-number argument.

   Hence every tree decomposition of G_L has a bag size >=L:

       tw(G_L) >= L-1.

   Already L=9 gives n=81 and tw(G_L)>=8>6.
   For arbitrary multiples of three L, this is UNBOUNDED width,
   refuting not only the numerical <=6 assertion but any
   claimed universal constant treewidth of this associated G.

7. This family is even SAT, not merely locally UNSAT:

       x_(i,j) = 1 iff (i-j) mod 3 = c,  for c=0,1,2.

   Since L is a multiple of 3, assignments are well-defined on
   the torus. Each check's three residues are r,r+1,r-1 mod3,
   and therefore exactly one selected value is 1.
   There are at least THREE explicit exact satisfying witnesses,
   each with n/3 selected variables. Thus the paper cannot
   rescue the universal tw claim by excluding hard UNSAT cases.

This directly disproves Proposition 4's structural implication
on matrices of EXACTLY the class addressed in the paper.

## Theorem B. Every invertible cubic carrier is BOOLEAN UNSAT

Let A be any n-by-n 0/1 matrix with exactly three ones in
every row. The vector u=(1/3) 1 is a rational solution of

    A u = 1.

If det(A)!=0, that rational solution is UNIQUE; therefore
the equation Ax=1 has **NO Boolean solution**, because all
coordinates of u equal 1/3, not 0 or 1.

The 2025 paper's Algorithm 2, Step 2 instead returns this
non-Boolean vector when det(A)!=0 and thereby incorrectly
treats a rational solution as the Exact-One witness.

A SMALL legitimate n=9 linear cubic instance makes the error
completely explicit: take row i's 1 entries at columns

    (i, i+1, i+3) mod 9,  for i=0,...,8.

This n=9 matrix is square, cubic in both rows and columns,
C4-free (ordered differences +/-1, +/-2, +/-3 mod9 all
distinct), and exact integer Bareiss elimination gives

    det(A)=27 != 0,

so its *only* rational solution is u=(1/3)1 and the
Boolean formula is UNSAT. This is not a numerical
rounding counterexample; determinant 27 is verified
in exact integer arithmetic.

The general all-invertible-unsat theorem is already part
of the previous E129/E61 JANUS work. New scientific
contribution here is the external paper audit and a
minimal n=9 exact example.

## Independent structural mistakes visible in the published proof

Page 40 argues that a separator in an induced subgraph G[C]
is automatically a separator of the WHOLE G. This implication
is false in general: for a 4-cycle a-b-c-d-a, in
G[{a,b,c}] the vertex b separates a and c, but it does NOT
separate a and c in G, because a-d-c is a path avoiding b.

The paper also treats being simplicial within G[C] as forcing
all triangles of that vertex in G to lie in C; this is not
justified without an extra property of C.

These observations flag proof gaps, while Theorem A and
Theorem B are direct falsifications of its decisive universal
mathematical and algorithmic assertions.

## Provenance versus E125 (anti-duplicate)

JANUS Fundamentum E125 already uses a toroidal 3-regular
incidence SKELETON to glue 63-variable UNSAT blocks and proves
unbounded LEVI treewidth of that block-splice family. That
precedent is credited, not rediscovered.

This report's narrowly distinct result is:

* use the **bare skeleton itself** as a legal n=L^2 square,
  cubic, linear SAT-positive Exact-One carrier;
* prove its COLUMN CONFLICT GRAPH (the exact graph used in the
  external paper) has unbounded treewidth, with a complete
  crossed-grid bramble/Helly proof;
* audit external Proposition 4 and independently its
  determinant shortcut with a 9x9 invertible carrier.

This neither proves a universal SAT solver nor disproves the
possibility of an entirely different polynomial algorithm.

## Exact runnable witness

    python experiments/r5_universal_kettani_2025_toroidal_treewidth_counterexample.py

No external mathematics package. Replay verifies n9 determinant
by exact Bareiss elimination, and for L=9,12,15 checks:
every row/column degree 3, unique row pairs (=linearity),
conflict 6-regularity, K1,4-free neighborhood pairing,
three triangles per variable, 3 explicitly SAT models,
and every edge of the ordinary grid inside the conflict graph.
It checks that all grid cross subgraphs pairwise intersect and
exhibits a hitting set of size exactly L; the lower bound is
proved for all L in the mathematical argument, NOT calculated
by a treewidth heuristic.

## Scientific result and next allowed move

PUBLISHED_2025_TW_LE_6_FOR_CONFLICT_GRAPHS = REFUTED.
PUBLISHED_2025_ALGORITHM_STEP2_NONBOOLEAN_OUTPUT = REFUTED.
EXACT_SCL_SAT_HIGH_CONFLICT_TREEWIDTH_FAMILY = PROVED.
QUADRATIC_GAUSS_MOD4 = SOUND_PARTIAL_ONLY.
SINGLE_PRIMITIVE_PHASE_ENCODING = EXACT_NP_HARD_EVALUATION_TARGET.
UNIFORM_POLYNOMIAL_PHASE_EVALUATOR = STILL OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.

Do NOT cite this external paper as established P=NP or as a
valid polynomial routing theorem in later Fundamentum work.
Proceed only if a new genuinely ALL-INPUT compression/
phase-evaluation theorem supplies soundness, completeness,
worst-case polynomial bit complexity and witness recovery.
