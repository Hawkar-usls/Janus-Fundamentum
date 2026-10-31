# R5 E9 — AF3 one-zero bipartite complement-graph polynomial terminal

Date: 2026-09-30

Status: `JANUS_CONSTRUCTIVE_POLYNOMIAL_SAT_TERMINAL__ONE_ZERO_AF3_PLUS_BIPARTITE_COMPLEMENT_GRAPH__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_AF3_ONE_ZERO_EXACT_MINUS2_BINARY_AUGMENTATION_THEOREM_2026-09-30_v1.0.md`

## 1. Input state

Let `A in {0,1}^{n x n}` be square row/column-cubic and linear. Suppose a polynomially constructed affine solution

\[
r\in\mathbb F_3^n,
\qquad Ar=\mathbf1
\]

has exactly one zero coordinate `i`.

Define

\[
b_j=\mathbf1[r_j=2],
\qquad
x^{(0)}=b+e_i.
\]

The parent theorem proves:

- `x^(0)` is a binary parity solution;
- the three rows through `i` have weight three and every other row has weight one;
- `|x^(0)|=n/3+2`.

Put

\[
S=\operatorname{supp}(x^{(0)}),
\qquad
U=[n]\setminus S.
\]

## 2. Complement graph G_U

Every nondefect row contains exactly one variable `s in S` and exactly two variables `u,v in U`.

Construct a graph `G_U` with vertex set `U` by adding edge `uv` for every nondefect row `{s,u,v}`.

### Lemma BCG-1

`G_U` is cubic. If the source hypergraph is linear, `G_U` is simple.

### Proof

A variable `u in U` is not in any defect row, because each defect row has `x^(0)`-weight three. Since every source column has degree three, all three rows through `u` are nondefect, and each contributes exactly one edge incident with `u`. Thus `deg_GU(u)=3`.

If two distinct source rows produced the same edge `uv`, they would share the two source variables `u,v`, contradicting linearity. QED.

Also

\[
|S|=n/3+2,
\qquad
|U|=2n/3-2,
\qquad
|E(G_U)|=n-3=3|U|/2.
\]

## 3. Bipartite construction theorem

### Theorem BCG-2

If `G_U` is bipartite, then `A` is Exact-One SAT and a witness is constructible in linear time after `r` is known.

### Construction

Choose one shore `W` from each connected component of `G_U`. Define a binary kernel move `z` by

```text
z_i = 0,
z_s = 1                  for every s in S-{i},
z_u = 1[u in W]          for every u in U.
```

### Proof that Az=0 over F2

For a defect row `{i,s1,s2}`, all three variables lie in `S` and the `z`-pattern is

```text
(0,1,1),
```

so the row parity is zero.

For a nondefect row `{s,u,v}`, the edge `uv` belongs to `G_U`. Bipartiteness makes exactly one of `u,v` lie in the chosen shore `W`, while `z_s=1`. Thus the row again contains exactly two `z=1` coordinates.

Hence

\[
Az=0\pmod2.
\]

Moreover all three defect rows are active and every active nondefect row is mixed `S-U`, so the parent statistics are exactly

```text
t=3,
w=0.
```

Therefore `z` is the unique allowed type of strict `-2` augmentation.

## 4. Exact-One witness

Set

\[
x=x^{(0)}+z\pmod2.
\]

On every defect row, `x^(0)` was `111` and `z` is `011`, leaving exactly one selected coordinate, namely `i`.

On every nondefect row, `x^(0)` was `100` in `(s,u,v)` order and `z` is either `110` or `101`; the result is respectively `010` or `001`.

Thus directly, over the integers,

\[
\boxed{Ax=\mathbf1.}
\]

No minimum-weight theorem or search oracle is needed once bipartiteness is known.

## 5. Deterministic polynomial entry test

The router need not search the whole affine space for a one-zero point.

1. Solve `Ar=1` over `F3` by Gaussian elimination. If inconsistent, AF3 already returns UNSAT.
2. Obtain one particular solution `r^(0)`.
3. Because `A1=0`, inspect the three solutions
   \[
   r^{(0)},\ r^{(0)}+\mathbf1,\ r^{(0)}+2\mathbf1.
   \]
4. If none has exactly one zero, return `NOT_IN_ONE_ZERO_BIPARTITE_BRANCH`.
5. For each one-zero shift, construct `G_U` and test bipartiteness by BFS/DFS.
6. If one is bipartite, construct `z`, return the Exact-One witness `x`, and verify `Ax=1`.
7. If all candidate `G_U` are nonbipartite, return `UNKNOWN`; nonbipartiteness is not an UNSAT certificate.

All operations are deterministic polynomial time; after elimination the graph step is linear.

## 6. Frozen controls

### PG15 SAT

The deterministic Gaussian particular solution has residue counts `(8,6,1)` up to ordering. The shift by `+1` gives

```text
r=(2,2,0,2,2,2,2,1,1,1,1,1,1,1,1).
```

The resulting `G_U` is cubic bipartite on eight vertices. One bipartition shore produces an exact kernel move and the witness

```text
{3,11,13,14,15}
```

in 1-based indexing (one of the four frozen PG15 models).

### Frozen singular UNSAT control

The same deterministic Gaussian/shift procedure produces

```text
r=(1,0,1,1,2,2,1,2,2,2,2,1,1,1,1).
```

Its eight-vertex cubic complement graph is nonbipartite. The router therefore returns `UNKNOWN`, never a false UNSAT conclusion. The existing rank-one exact terminal decides this control separately.

## 7. Meaning for the universal route

This is the first direct polynomial constructor extracted from the exact one-zero augmentation geometry:

```text
ONE ZERO AF3
+ BIPARTITE COMPLEMENT GRAPH
=> EXACT -2 GLOBAL MOVE
=> EXACT-ONE WITNESS.
```

It does not eliminate the all-or-none hard core when `G_U` is nonbipartite or when the Gaussian orbit has no one-zero representative.

The next legitimate gate is to extend the graph construction beyond bipartiteness by identifying a polynomially repairable odd-cycle obstruction, without branching on the all-or-none label classes.

## 8. Ceiling

```text
ONE-ZERO COMPLEMENT GRAPH = CUBIC / SIMPLE
= PROVED

G_U BIPARTITE => EXACT-ONE SAT
= PROVED CONSTRUCTIVELY

WITNESS CONSTRUCTION
= LINEAR AFTER F3 ELIMINATION

DETERMINISTIC GAUSSIAN + THREE-SHIFT ENTRY TEST
= POLYNOMIAL

PG15
= PASS / WITNESS CONSTRUCTED

UNSAT15
= SAFE REJECT TO UNKNOWN

NONBIPARTITE G_U UNIVERSAL REPAIR
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
