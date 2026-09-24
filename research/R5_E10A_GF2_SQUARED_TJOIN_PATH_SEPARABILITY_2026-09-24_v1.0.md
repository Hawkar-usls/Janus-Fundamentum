# R5 E10A — Exact Separability of GF(2)^2-Labelled T-Joins

Date: 2026-09-24

Authority:
\`JANUS_DERIVED_EXACT_STRUCTURE_AFTER_AUDIT__TJOIN_REDUCES_TO_PRESCRIBED_LABEL_SHORTEST_PATH__NO_DETERMINISTIC_SOLVER_CLAIM\`

Authorizing audit:
\`PA-0005-TWO-ROW-GRAPH-LIFT\`

Continuation of:
\`NM-0004-GF2-SQUARED-ZERO-SUM-CYCLE-COMPRESSION\`

Parent scope:
\`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1\`

Checker:
\`experiments/r5_e10a_gf2_squared_tjoin_path_separability.py\`

## 1. Setting

Let \`G=(V,E)\` be an undirected loopless multigraph with nonnegative edge
weights and labels \`lambda:E->GF(2)^2\`. Fix terminals \`u,v\` and target
\`g in GF(2)^2\`.

Let \`OPT_T(g)\` be the minimum weight of an edge set \`J\` with
\`boundary(J)={u,v}\` and label XOR \`g\`.

For each \`h in GF(2)^2\`, let \`P_h(u,v)\` be the minimum weight of a
**simple** u-v path of label \`h\`. For each nonzero label \`a\`, let \`C_a\`
be the minimum weight of a **simple** cycle of label \`a\`. Missing objects
have cost \`+infinity\`.

## 2. Source-bound parent theorem

The preceding zero-sum correction theorem proves that an optimum T-join can be
chosen as

\`\`\`
J = P dot-union C_1 dot-union ... dot-union C_q,
q<=2,
\`\`\`

with a simple u-v path, simple pairwise edge-disjoint cycles, and nonzero
linearly independent correction labels.

Therefore the correction-label sets are exactly

\`\`\`
{},
{01},{10},{11},
{01,10},{01,11},{10,11}.
\`\`\`

## 3. Exact separability theorem

For a correction set \`S\`, write \`xor(S)\` for the XOR of its labels. Then

\`\`\`
OPT_T(g)
=
min_S [
  P_{g XOR xor(S)}(u,v)
  +
  sum_{a in S} C_a
].
\`\`\`

### Lower bound

Take the canonical optimum edge-disjoint decomposition. Its correction labels
form one of the seven sets \`S\`, and its path label is \`g XOR xor(S)\`.
Each component is at least as expensive as the independently cheapest object
with that label, so its total weight is at least the displayed expression.

### Upper bound

Fix a correction set \`S\`. Choose independently a cheapest path of label
\`g XOR xor(S)\` and, for every \`a in S\`, a cheapest cycle of label \`a\`.
They need not be edge-disjoint.

Take the symmetric difference of all chosen edge sets. Boundaries add modulo
two, every cycle has zero boundary, and labels add by XOR, so the resulting
edge set is a feasible labelled T-join of target \`g\`.

Because weights are nonnegative, cancelling repeated edges under symmetric
difference can only decrease weight. Thus the T-join optimum is at most the
sum of independent minima. Together with the lower bound this proves equality.

This removes the mixed packing interaction entirely from the optimization.

## 4. Exact cycle-to-path reduction

For a nonzero target label \`a\`,

\`\`\`
C_a
=
min_{e=xy in E}
[
  w(e)
  +
  P^{G-e}_{a XOR lambda(e)}(x,y)
].
\`\`\`

Every simple cycle containing non-loop edge \`e=xy\` becomes a simple x-y path
after deleting \`e\`; conversely such a simple path in \`G-e\`, together with
\`e\`, forms a simple cycle. Weights and XOR labels add exactly.

If a representation contains graph loops, handle them separately as one-edge
cycle candidates and apply the formula to the non-loop edges.

## 5. Oracle consequence

A deterministic oracle for

\`\`\`
SHORTEST SIMPLE PATH
WITH ONE PRESCRIBED GF(2)^2 LABEL
\`\`\`

solves the whole two-row labelled T-join problem with polynomially many calls:

1. obtain the four terminal path costs;
2. obtain the three nonzero cycle costs using at most \`3|E|\` path calls;
3. evaluate the seven constant-size correction formulas;
4. symmetric-difference the returned witnesses.

Therefore the deterministic blocker is no longer labelled path-plus-cycle
packing. It is a single canonical path primitive.

## 6. Source status of that primitive

Bentert--Drange--Fomin--Golovach--Korhonen (ICALP 2024) define
**Xor-Constrained Shortest Path** exactly as a shortest simple s-t path whose
edge-label XOR equals a prescribed \`c in GF(2)^d\`. Their Theorem 2 gives a
one-sided-error randomized \`2^(d+p)(n+m)^O(1)\` algorithm. At \`d=2,p=0\`,
this is exactly the JANUS primitive.

Yamaguchi's weighted linear matroid parity line deterministically solves
shortest **non-zero** paths in finitely generated abelian groups, but in
\`GF(2)^2\` that objective minimizes over three labels and does not isolate one
target vector.

Kawase--Kobayashi--Yamaguchi distinguish prescribed-label feasibility from the
non-zero problem and cite Huynh's deterministic polynomial feasibility result
for fixed finite abelian groups. Feasibility does not supply minimum length.

Thus the located state is:

\`\`\`
PRESCRIBED GF(2)^2 SHORTEST SIMPLE PATH
=
RANDOMIZED POLYNOMIAL

DETERMINISTIC POLYNOMIAL
=
NOT LOCATED IN THE RE-AUDIT.
\`\`\`

## 7. Next gate

\`\`\`
R5_E10A_GF2_SQUARED_PRESCRIBED_LABEL_SHORTEST_PATH_GATE_V1
\`\`\`

Target a deterministic polynomial exact shortest simple path algorithm for
\`GF(2)^2\` prescribed labels, or a strict exact contraction/bypass.

Forbidden:

- promoting shortest-nonzero to prescribed-label;
- promoting feasibility to shortest optimization;
- full syndrome/trellis tables;
- generic Exact Matching derandomization as an assumption;
- quarantined Du-2026 as authority.

## 8. Scientific ceiling

\`\`\`
TJOIN SEPARABILITY INTO PATH/CYCLE COSTS
=
PROVED

CYCLE -> POLY MANY PRESCRIBED-LABEL PATH CALLS
=
PROVED

TWO-ROW GRAPH-LIFT -> PRESCRIBED-LABEL SHORTEST PATH ORACLE
=
PROVED

RANDOMIZED POLY PATH SOLVER
=
SOURCE-BOUND

DETERMINISTIC PATH SOLVER
=
NOT PROVED

D1
=
EMPTY

P_VS_NP
=
OPEN
\`\`\`
