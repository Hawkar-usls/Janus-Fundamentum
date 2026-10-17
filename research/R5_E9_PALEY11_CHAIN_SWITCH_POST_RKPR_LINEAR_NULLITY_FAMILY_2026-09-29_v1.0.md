# R5 E9 — Paley(11) chain-switch post-RKPR linear-nullity family

Date: 2026-09-29
Status: THEOREM / ROUTE FALSIFIER
Authority: non-authoritative research layer; `P_VS_NP=OPEN`

## 1. Scope

This note closes one specific prospective shortcut:

> `linear cubic + connected + exhaustive rational-kernel projective ratio pinning (RKPR) => rational nullity O(log n)`.

The shortcut is false.  There is an explicit infinite connected linear cubic family whose exhaustive RKPR quotient still has rational nullity linear in the instance size.

This does **not** prove `P=NP`, does not give a universal SAT algorithm, and does not falsify a stronger theorem that additionally assumes nontrivial small-cut irreducibility.  The family constructed here has a 2-edge interface cut between consecutive base blocks.

## 2. The 55 x 55 Paley(11) base block

Let

```text
V = Z_11
R = {1,3,4,5,9}
```

and orient every unordered pair by

```text
u -> v  iff  v-u in R (mod 11).
```

This is the Paley tournament `P(11)`.  Let `E` be its 55 directed arcs and let `T` be its 55 cyclic directed triangles.  Define the 0/1 incidence matrix

```text
A0[t,e] = 1  iff  arc e belongs to cyclic triangle t.
```

Exact finite verification gives:

```text
|E| = |T| = 55
row sum(A0) = 3
column sum(A0) = 3
rank_Q(A0) = 45
nu_Q(A0) = 10
```

Distinct cyclic triangles share at most one arc, so the corresponding cubic hypergraph is linear.  The Levi graph is connected.

### 2.1 Exact kernel model

Anchor a vertex potential by `p_0=0`.  For an arc `e=(u->v)` define

```text
g_e(p) = p_v - p_u.
```

For every cyclic triangle `u->v->w->u`,

```text
g_uv + g_vw + g_wu = 0.
```

Therefore the 10-dimensional gradient space lies in `ker_Q(A0)`.  Since exact row reduction gives `nu_Q(A0)=10`,

```text
ker_Q(A0) = { (p_v-p_u)_(u->v) : p in Q^11 / constants }.
```

Consequences used below:

1. every kernel-coordinate functional is nonzero;
2. two distinct arc-coordinate functionals are not proportional over `Q` (the tournament contains exactly one orientation of each unordered vertex pair);
3. the left nullspace has no coordinate that vanishes identically.  This also follows from the transitive affine automorphism action on cyclic triangles together with nonzero left nullity; the checker verifies it directly.

## 3. Chain-switch construction

Use the canonical lexicographic enumeration from the checker.  Intrinsically, choose the two incidences

```text
RIGHT: triangle {0,1,2}, arc 0->1
LEFT : triangle {0,1,6}, arc 1->6
```

Both are incidences of `A0`, and the two selected arc functionals are nonproportional.

For integer `t>=1`, start from

```text
D_t = diag(A0,...,A0)    (t copies).
```

For every interface `i | i+1`, perform one incidence 2-switch:

```text
remove (RIGHT-row_i, RIGHT-col_i)
remove (LEFT-row_{i+1}, LEFT-col_{i+1})
add    (RIGHT-row_i, LEFT-col_{i+1})
add    (LEFT-row_{i+1}, RIGHT-col_i).
```

Call the resulting `55t x 55t` matrix `A_t`.

Each switch preserves every row sum and column sum, and cannot create a repeated two-column intersection between rows.  Hence every `A_t` is square cubic and linear.  The cross incidences join consecutive Levi components, so the Levi graph is connected.

## 4. Rank-one form of every switch

For interface `i`, write

```text
u_i = e_(RIGHT-row_i) - e_(LEFT-row_{i+1})
v_i = e_(LEFT-col_{i+1}) - e_(RIGHT-col_i).
```

Then exactly

```text
A_t = D_t + sum_{i=1}^{t-1} u_i v_i^T.
```

Let `U=[u_1 ... u_{t-1}]` and `V=[v_1 ... v_{t-1}]`.

### 4.1 `U` is independent modulo `im(D_t)`

The cokernel of `D_t` is the direct sum of the `t` base cokernels.  The selected RIGHT/LEFT row classes are nonzero in the base cokernel.  In a relation

```text
sum alpha_i [u_i] = 0  in coker(D_t),
```

the first block contains only `alpha_1 [e_RIGHT]`; hence `alpha_1=0`.  Inducting along the chain gives all `alpha_i=0`.

Thus the image of `U` in `coker(D_t)` has rank `t-1`.

### 4.2 `V^T` has rank `t-1` on `ker(D_t)`

The kernel of `D_t` is the direct sum of `t` copies of the 10-dimensional gradient kernel.  Each constraint

```text
v_i^T x = x_(LEFT-col_{i+1}) - x_(RIGHT-col_i)
```

is a nonzero coordinate-functional difference between two consecutive blocks.  The same endpoint induction shows that these `t-1` constraints are independent on `ker(D_t)`.

## 5. Exact nullity theorem

Suppose `A_t x=0`.  Modulo `im(D_t)`,

```text
[U] V^T x = 0.
```

Because `[U]` is injective, `V^T x=0`.  Therefore the perturbation term vanishes and `D_t x=0`.

Conversely every `x in ker(D_t)` satisfying `V^T x=0` is visibly in `ker(A_t)`.

Hence

```text
ker(A_t) = ker(D_t) intersect ker(V^T)
```

and therefore

```math
\boxed{\nu_{\mathbb Q}(A_t)=10t-(t-1)=9t+1.}
```

Since `n_t=55t`,

```math
\frac{\nu_{\mathbb Q}(A_t)}{n_t}\to \frac{9}{55}>0.
```

So connectedness plus linearity alone do not force small rational nullity.

## 6. Exact RKPR behavior

Let `ell_{i,e}` denote the base gradient coordinate functional of arc `e` in block `i`.  Restricting to `ker(A_t)` imposes exactly

```text
ell_(i,RIGHT) = ell_(i+1,LEFT),   i=1,...,t-1.
```

In the dual description, restriction to `ker(A_t)` quotients the direct sum of the block dual spaces by

```text
W = span{ ell_(i,RIGHT) - ell_(i+1,LEFT) }.
```

The two selected base arc functionals RIGHT=`0->1` and LEFT=`1->6` are nonproportional.  Support-chasing along the path now gives:

- no coordinate functional becomes zero;
- within one block, no two distinct arc functionals become proportional;
- between nonadjacent blocks, proportionality would force an intermediate linear relation between the nonproportional LEFT and RIGHT functionals, impossible;
- between adjacent blocks, the only proportional pair is the intended switch pair, with ratio exactly `1`.

Therefore exhaustive RKPR finds exactly `t-1` nontrivial projective classes, all equality classes:

```text
RIGHT-col_i == LEFT-col_{i+1}.
```

There are no `-2`, `-1/2`, illegal-ratio, or zero-row RKPR terminals.

After merging those equality pairs, RKPR preserves kernel dimension, so the quotient has

```text
q_t = 55t-(t-1) = 54t+1
nu_Q = 9t+1.
```

Thus

```math
\boxed{\nu_{\mathbb Q}=\Theta(q_t)\quad\text{after exhaustive RKPR}.}
```

This is the promised falsifier of the proposed `post-RKPR + linear + connected => O(log n)` route.

## 7. Divisibility firewall

The single Paley block has `n=55`, so its Exact-One UNSAT status is already caught by the global count `3|S|=55`; it must **not** be advertised as a hard Exact-One instance.

For the chain family, choose for example

```text
t = 3s.
```

Then

```text
n_t = 165s
```

is divisible by 3, so the elementary global `n mod 3` necessary condition no longer rejects the source family.

This observation does not assert SAT, UNSAT hardness, or survival of every other polynomial preprocessing rule.

## 8. Small-cut firewall

A single 2-switch contributes two cross Levi edges between consecutive blocks.  Hence the prefix/suffix separation at every interface is a nontrivial 2-edge cut.

Therefore this theorem does **not** falsify a stronger statement whose hypotheses include, for example,

```text
NO_NONTRIVIAL_CUT_OF_SIZE_LE_3.
```

The next admissible target is to replace each interface by a cut-robust multi-switch/4-join while retaining a linear lower bound on rational nullity and then re-run exhaustive RKPR.

## 9. Regression values

The exact checker verifies, among other cases:

```text
t=1: n=55,  rank_Q=45,  nu_Q=10, intended RKPR equalities=0
t=2: n=110, rank_Q=91,  nu_Q=19, intended RKPR equalities=1
t=3: n=165, rank_Q=137, nu_Q=28, intended RKPR equalities=2
t=4: n=220, rank_Q=183, nu_Q=37, intended RKPR equalities=3
```

For `t=3`, the only proportional kernel-row pairs are exactly

```text
(block 0, arc 0->1) == (block 1, arc 1->6)
(block 1, arc 0->1) == (block 2, arc 1->6).
```

## 10. Scientific consequence

Closed route:

```text
LINEAR
+ CONNECTED
+ RKPR_EXHAUSTED
=> RATIONAL_NULLITY_O_LOG_N
```

is **FALSE**.

Still open:

```text
3-CUT-IRREDUCIBLE / stronger separator-reduced variants
cycle-endpoint syndrome global quotient
signed negative-circuit synthesis under source restrictions
universal deterministic polynomial Exact-One/SAT algorithm
P_VS_NP
```

No claim in this file changes `E8_D1=EMPTY` or `P_VS_NP=OPEN`.
