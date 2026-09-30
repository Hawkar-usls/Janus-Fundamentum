# R5 E9 — Augmented Ternary Branch-Width Full-Support DP Router

Date: 2026-09-30

Status:
`JANUS_EXACT_FPT_ROUTER__FULL_SUPPORT_F3_FLOW_BY_BOUNDARY_SYNDROME_DP__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS NOTE GIVES AN EXACT 3^{O(k)} SOLVER ON A SUPPLIED WIDTH-k
BRANCH DECOMPOSITION OF THE AUGMENTED TERNARY MATROID.

FOR EVERY FIXED CONSTANT k, KNOWN FINITE-FIELD MATROID BRANCH-WIDTH
CONSTRUCTION ALGORITHMS TURN THIS INTO A DETERMINISTIC POLYNOMIAL ROUTER.

THIS NOTE DOES NOT PROVE THAT ALL SOURCE INSTANCES HAVE BOUNDED OR
O(log n) BRANCH-WIDTH, AND IT DOES NOT CLAIM A POLYNOMIAL GENERIC
DECOMPOSITION CONSTRUCTOR WHEN k GROWS AS O(log n).

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. From Exact-One to one full-support ternary flow

For a row-weight-three Exact-One source matrix

```text
A in {0,1}^{m x n},
```

form over `F3`

```text
H = [ A | -1_m ].
```

The parent theorem proves

\[
\boxed{
A\text{ Exact-One SAT}
\iff
\exists c\in(\mathbb F_3^*)^{n+1}: Hc=0.
}
\]

Thus the source problem is a full-support kernel / nowhere-zero `F3`-flow
problem on the represented matroid `M(H)`.

Write the columns of `H` as

\[
h_e\in\mathbb F_3^m,\qquad e\in E,
\]

where `|E|=N=n+1`.

## 2. Branch boundary spaces

Let `T` be a rooted binary branch decomposition whose leaves are the elements
of `E`.  For a node `t`, let `E_t` be the leaves below `t` and define

\[
U_t=\operatorname{span}_{\mathbb F_3}\{h_e:e\in E_t\},
\]

\[
V_t=\operatorname{span}_{\mathbb F_3}\{h_e:e\in E\setminus E_t\}.
\]

The exact boundary space is

\[
B_t=U_t\cap V_t.
\]

Its dimension is the ordinary represented-matroid connectivity value

\[
\dim B_t
=r(E_t)+r(E\setminus E_t)-r(E)
=\lambda_M(E_t).
\]

To avoid branch-width convention shifts by one, this note defines the
**interface width** of the supplied tree as

\[
k:=\max_t\dim B_t.
\]

Hence every boundary has at most

\[
|B_t|\le3^k
\]

vectors.

## 3. Exact DP state

For every node `t`, define

\[
D_t:=\left\{
\sum_{e\in E_t} a_e h_e:
 a_e\in\mathbb F_3^*\ \forall e,
\quad
\sum_{e\in E_t}a_e h_e\in B_t
\right\}.
\]

So a state is not an assignment table.  It is only the aggregate partial
syndrome that can cross the cut.

Because `D_t subseteq B_t`,

\[
\boxed{|D_t|\le3^k.}
\]

Store with every reachable syndrome one parent pointer sufficient to
reconstruct one choice of nonzero coefficients on the leaves below `t`.

## 4. Leaf rule

If `t` is a leaf labelled by element `e`, then

\[
\boxed{
D_t=\{h_e,2h_e\}\cap B_t.
}
\]

If `h_e` is a coloop relative to the rest, this set may be empty, which is
correct: no full-support kernel word can use a nonzero coefficient on a coloop.

## 5. Exact merge theorem

Let internal node `t` have children `u,v`, so

```text
E_t = E_u dot-union E_v.
```

### Theorem ATBW-1

\[
\boxed{
D_t=(D_u+D_v)\cap B_t.
}
\]

Here

\[
D_u+D_v=\{b_u+b_v:b_u\in D_u,b_v\in D_v\}.
\]

### Proof: right to left

Take `b_u in D_u` and `b_v in D_v`.  By definition there are nonzero
coefficient assignments on `E_u` and `E_v` whose partial sums are `b_u,b_v`.
Combining those assignments gives an all-nonzero assignment on `E_t` with sum

\[
b=b_u+b_v.
\]

If additionally `b in B_t`, then `b` satisfies the definition of `D_t`.

### Proof: left to right

Take any all-nonzero assignment on `E_t` whose sum

\[
b\in B_t.
\]

Let `b_u,b_v` be its child partial sums.  Then

\[
b=b_u+b_v.
\]

Certainly `b_u in U_u`.  Also

\[
b_u=b-b_v.
\]

Because `b in B_t subseteq V_t`, it lies in the span of `E-E_t`, while
`b_v` lies in the span of `E_v`.  Therefore

\[
b_u\in\operatorname{span}((E-E_t)\cup E_v)
=\operatorname{span}(E-E_u)=V_u.
\]

Hence `b_u in U_u cap V_u=B_u`, so `b_u in D_u`.  Symmetrically
`b_v in D_v`.  Thus `b in (D_u+D_v) cap B_t`. QED.

This proof is the key reason no hidden interior assignment table is needed.

## 6. Root criterion

At the root `r`,

```text
E_r=E,
V_r={0},
B_r={0}.
```

Therefore

\[
\boxed{
0\in D_r
\iff
\exists c\in(\mathbb F_3^*)^E:Hc=0.
}
\]

By the parent AF3 theorem,

\[
\boxed{
0\in D_r
\iff
A\text{ is Exact-One SAT}.
}
\]

Following the stored parent pointers reconstructs the full-support codeword.
Normalize its last coordinate to one and decode

```text
x_i = 1  iff  c_i/c_last = 2 in F3.
```

Direct integer multiplication verifies `Ax=1`.

## 7. Complexity

For every node there are at most `3^k` states.
At an internal node, brute-force merging examines at most

\[
3^k\cdot3^k=9^k
\]

state pairs.

Boundary bases `B_t` and membership tests are obtained by exact Gaussian
elimination over the fixed field `F3` in polynomial time.
There are `O(N)` tree nodes.

Thus, for a supplied decomposition of interface width `k`,

\[
\boxed{
T_{solve}(N,k)=O(9^k\,\operatorname{poly}(N,m)).
}
\]

Memory is

\[
O(3^k\,\operatorname{poly}(N,m))
\]

when state tables are released bottom-up, plus polynomial witness pointers.

Consequences:

```text
k = fixed constant
    => deterministic polynomial solve.

supplied k <= c log N decomposition
    => deterministic polynomial solve stage.
```

The second line is deliberately only a **supplied-decomposition** statement.

## 8. Constructive recognition boundary

For matroids represented over a fixed finite field, branch-width is
fixed-parameter tractable and a bounded-width branch decomposition can be
constructed in polynomial time for every fixed constant `k`.
Therefore ATBW-1 yields a fully constructive polynomial router for every fixed
branch-width class.

Relevant external donors include:

- Petr Hlineny, *A Parametrized Algorithm for Matroid Branch-Width*, SIAM J.
  Comput. 35(2), 2005/2006;
- Petr Hlineny and Sang-il Oum, *Finding Branch-Decompositions and
  Rank-Decompositions*, SIAM J. Comput. 38, 2008;
- Mujin Choi, Tuukka Korhonen, Sang-il Oum, *Branch-width of represented
  matroids in matrix multiplication time*, arXiv:2605.14428, 2026.

The 2026 result gives an `O_{k,F}(N^2)+O(N^omega)` constructor/decision
algorithm, but its public asymptotic notation hides the dependence on `k`.
Accordingly this note does **not** infer that setting `k=c log N` makes generic
decomposition discovery polynomial.

A future logarithmic-width promotion must bind an explicit single-exponential
(or otherwise polynomial-at-log-width) decomposition constructor, or supply
the decomposition by a source-specific polynomial construction.

## 9. Relation to older routers

This router strictly changes the state currency:

```text
low nullity router:
    enumerate global kernel coordinates;

ATBW router:
    enumerate only cut-interface syndromes.
```

A code may have large global dimension while every decomposition interface is
small.  Conversely, source sparsity/degree three alone does not prove bounded
branch-width.

The router therefore composes naturally with the existing representation stack:
network / binet / TU / regular terminals can fire first, and ATBW can solve a
residual whenever its augmented ternary representation has a certified small
branch decomposition.

## 10. Anti-loop / universal ceiling

Do not promote any of the following:

```text
row/column degree three => bounded branch-width              NOT PROVED
linearity => bounded branch-width                            NOT PROVED
F3 nullity large => branch-width large                       FALSE IN GENERAL
F3 nullity small => ATBW needed                              NO, enumeration already works
FPT branch-width recognition => polynomial at k=O(log N)    NOT AUTOMATIC
ATBW => universal Exact-One solver                           FALSE
```

The exact promotion is:

```text
SUPPLIED WIDTH-k AUGMENTED TERNARY BRANCH DECOMPOSITION
=> Exact-One decision + witness reconstruction in 9^k poly(N).

FIXED CONSTANT AUGMENTED TERNARY BRANCH-WIDTH
=> deterministic polynomial Exact-One router.
```

The live universal question remains whether every residual can be contracted
into a solved representation/width class with polynomial total progress, or
whether a genuinely unbounded-width global constructor exists.

## 11. Ceiling

```text
AFFINE F3 / FULL-SUPPORT SOURCE NORMAL FORM = PROVED
BOUNDARY-SYNDROME MERGE RULE               = PROVED
STATE COUNT PER CUT                         <= 3^k
SOLVE TIME ON SUPPLIED DECOMPOSITION        = 9^k poly(N)
WITNESS RECONSTRUCTION                      = POLYNOMIAL OVER DP OUTPUT
FIXED-k CONSTRUCTIVE ROUTER                  = POLYNOMIAL VIA KNOWN DONORS
GENERIC O(log N)-WIDTH CONSTRUCTOR           = NOT CLAIMED
UNIVERSAL WIDTH BOUND                        = NOT PROVED
UNIVERSAL POLYNOMIAL SOLVER                  = OPEN
E8_D1                                       = EMPTY
P_VS_NP                                     = OPEN
