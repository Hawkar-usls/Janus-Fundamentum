# Fixed-M trade compatibility: chordality counterexample

Date: 2026-10-10
Status: CHORDALITY_REFUTED
P_VS_NP = OPEN

Use the E119 PERFECT-SAT9 component with clauses
(A_i,B_j,C_{i+j mod 3}) for i,j in Z_3.

Fix the perfect matching M_A={A_0,A_1,A_2}.

There are two distinct connected fixed-M_A trades:
T_B: replace M_A by {B_0,B_1,B_2};
T_C: replace M_A by {C_0,C_1,C_2}.

Both trades remove the same M-support {A_0,A_1,A_2}, so they are incompatible.
Each trade graph is K_{3,3}, hence connected.

Now take the disjoint union of two copies X,Y of PERFECT-SAT9 and fix
M=M_A^X union M_A^Y.

Let T_B^X,T_C^X,T_B^Y,T_C^Y be the four connected fixed-M trades.
Trades from different components are compatible; the two trades inside the
same component are incompatible.

Therefore the compatibility graph induced by these four trades is exactly
K_{2,2}=C_4.

Hence the universal claim
  "the fixed-M trade compatibility graph is chordal"
is false even for square, cubic, linear Positive Exact-One instances.

This does not refute perfectness: C4 is perfect.

Next surviving target:
  PERFECTNESS OF THE TRADE COMPATIBILITY GRAPH,
or a weaker polynomial optimization theorem for its exact graph class.

No universal polynomial Exact-One solver is established.
