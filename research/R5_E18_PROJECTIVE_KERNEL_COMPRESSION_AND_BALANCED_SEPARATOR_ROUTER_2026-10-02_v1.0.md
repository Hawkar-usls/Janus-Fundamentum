# R5 E18 — Projective Kernel Compression and Balanced-Separator Exact Router

Date: 2026-10-02

Status:
`NEW_SOURCE_ALIGNED_UNSAT_CERTIFICATES__PROJECTIVE_KERNEL_FPT_COMPRESSION__BALANCED_EDGE_SEPARATOR_POLYNOMIAL_TERMINAL__P_VS_NP_OPEN`

Scientific ceiling:

```text
THIS NOTE ADDS TWO EXACT COMPLEMENTARY ROUTER BRANCHES.

(A) PROJECTIVE KERNEL COMPRESSION:
    zero kernel-evaluation coordinates and incompatible proportional
    kernel-evaluation coordinates give polynomial source-aligned UNSAT
    certificates; compatible forced projective classes reduce the
    exact kernel-enumeration exponent from d to a residual delta <= d.

(B) BALANCED-SEPARATOR GENERAL-FACTOR DP:
    recursively balanced constant-size edge cuts in the Levi graph
    give an exact deterministic polynomial algorithm.

THE TWO BRANCHES CLOSE DIFFERENT PREVIOUS FIREWALLS:
    R5 E17 frozen q=6 UNSAT -> projective/fixed-coordinate terminal;
    R5 E16 ring family       -> balanced 2-edge-separator terminal.

THEY DO NOT CLOSE THE GENERAL HIGH-ADHESION RESIDUAL CLASS.
P_VS_NP = OPEN.
```

## 1. Source class and centered kernel

Use the R5 E12 NP-complete carrier:

```text
A in {0,1}^{n x n},
row sum    = 3,
column sum = 3,
pairwise row overlap <= 1.
```

Exact-One asks for

```text
A x = 1,
x in {0,1}^n.
```

Because every row has sum three,

```text
A (1/3 * 1) = 1.
```

Put

```text
y = 3x - 1.
```

Then

```text
A x = 1, x in {0,1}^n
iff
A y = 0, y in {-1,2}^n.
```

Let

```text
K = ker_Q(A),
d = dim_Q(K).
```

Choose any rational basis of `K` and write it as the columns of

```text
N in Q^{n x d}.
```

Every centered rational solution is

```text
y = N alpha,
alpha in Q^d.
```

Write `b_i in Q^d` for row `i` of `N`.  Then the Boolean-alphabet
condition is exactly

```text
b_i alpha in {-1,2}   for every coordinate i.
```

Changing the basis of `K` right-multiplies all `b_i` by the same
invertible matrix.  Therefore the following are basis-invariant:

```text
b_i = 0;
b_i and b_j are proportional;
the proportionality scalar between b_i and b_j.
```

These invariants give the first E18 router branch.

## 2. K0 — kernel-fixed coordinate UNSAT terminal

### Theorem K0

If

```text
b_i = 0
```

for any coordinate `i`, then the Exact-One source is UNSAT.

### Proof

Every rational solution of `A x=1` has the form

```text
x = 1/3 * 1 + z,
z in ker_Q(A).
```

If the `i`th coordinate of every kernel vector is zero, then every
rational solution satisfies

```text
x_i = 1/3.
```

No Boolean solution can do this. QED.

### Source-aligned certificate

The condition

```text
z_i=0 for every z in ker(A)
```

is equivalent over `Q` to

```text
e_i in row_Q(A).
```

Thus one may provide `lambda in Q^n` with

```text
A^T lambda = e_i.
```

For any hypothetical Exact-One witness,

```text
x_i
= e_i^T x
= lambda^T A x
= lambda^T 1.
```

Multiplying `A^T lambda=e_i` by `1` and using `A1=3*1` gives

```text
3 lambda^T 1 = 1,
```

hence

```text
x_i = 1/3,
```

a contradiction.

So K0 has a short polynomially checkable source-aligned UNSAT
certificate.

### Spectral form

For a square+cubic+linear source,

```text
A^T A = 3I + Adj(G_A),
```

so `K` is the `-3` eigenspace.  K0 says:

```text
if the -3 eigenspace vanishes identically at any vertex,
then no Hoffman-tight coclique / Exact-One witness exists.
```

## 3. K1 — projective pair obstruction

Assume now that no `b_i` is zero.

Suppose

```text
b_j = c b_i
```

for some nonzero rational `c`.

Then every `y in K` obeys

```text
y_j = c y_i.
```

If `y_i,y_j in {-1,2}`, the only possible ratios are

```text
c in {1, -2, -1/2}.
```

Therefore:

### Theorem K1

If two nonzero coordinate evaluation rows of the rational kernel are
proportional with

```text
c not in {1,-2,-1/2},
```

then the source is UNSAT.

This is polynomially recognizable after one exact kernel computation.

### Source-aligned pair certificate

Since

```text
(e_j - c e_i)^T z = 0
```

for every `z in ker(A)`,

```text
e_j - c e_i in row_Q(A).
```

Hence there is a rational `lambda` such that

```text
A^T lambda = e_j - c e_i.
```

Every Exact-One witness would satisfy

```text
x_j - c x_i = lambda^T 1.
```

Evaluating this equality at the universal rational solution
`x=(1/3)1` gives

```text
lambda^T 1 = (1-c)/3.
```

Thus every hypothetical Boolean witness must satisfy the exact
two-coordinate source-aligned equality

```text
x_j - c x_i = (1-c)/3.
```

For `c not in {1,-2,-1/2}` none of the four Boolean pairs can satisfy
the centered relation `3x_j-1=c(3x_i-1)`.

The compatible cases have transparent semantics:

```text
c = 1      -> x_j = x_i;
c = -2     -> (x_i,x_j) = (0,1);
c = -1/2   -> (x_i,x_j) = (1,0).
```

So proportional kernel coordinates act as exact Boolean propagation,
not only as a rejection test.

## 4. Projective classes

Partition all coordinates into projective classes:

```text
i ~ j
iff
b_i = c b_j for some c != 0.
```

Fix a representative row `b_C` in a class `C`.  Write

```text
b_i = c_i b_C,
c_rep = 1.
```

Let

```text
t_C = b_C alpha.
```

The whole class is alphabet-compatible exactly when

```text
c_i t_C in {-1,2}  for every i in C.
```

Define the exact class target set

```text
T_C
=
intersection_{i in C} {-1/c_i, 2/c_i}.
```

Because the representative has `c=1`,

```text
T_C subseteq {-1,2}.
```

Therefore exactly three cases exist:

```text
T_C = empty       -> UNSAT;
T_C = {-1} or {2} -> forced projective class;
T_C = {-1,2}      -> flexible projective class.
```

Moreover `T_C={-1,2}` is possible only when every `c_i=1`, i.e. all
evaluation rows in that class are literally equal to the chosen
representative.

An empty projective class always contains an incompatible pair and
therefore admits a K1 certificate.

## 5. K2 — exact residual-dimension compression

Every forced class gives one rational linear equation in the kernel
parameter:

```text
b_C alpha = t_C,
t_C in {-1,2}.
```

Collect them as

```text
F alpha = t.
```

If this system is inconsistent, return exact UNSAT.

Otherwise let

```text
delta
=
dimension of {alpha : F alpha = t}
=
d - rank(F).
```

### Theorem K2

Exact-One can be decided in

```text
O(2^delta poly(n))
```

exact arithmetic after projective propagation.

In particular, if

```text
delta = O(log n),
```

this branch is deterministic polynomial time.

### Proof

Parameterize the forced affine space as

```text
alpha = alpha_0 + H beta,
beta in Q^delta,
```

where the columns of `H` span `ker(F)`.

Every remaining flexible projective class imposes

```text
b_C alpha in {-1,2}.
```

Consider the linear parts

```text
b_C H.
```

They span the full dual of the `delta`-dimensional residual parameter
space.  Otherwise there would be nonzero `beta` annihilated by every
flexible class.  It is already annihilated by all forced class rows
because `H beta in ker(F)`.  Hence every row of `N` would annihilate
`H beta`, so

```text
N H beta = 0.
```

Since `N` has full column rank and `H` has full column rank, this
forces `beta=0`, contradiction.

Choose `delta` flexible classes whose rows `b_C H` are independent.
For each of their at most

```text
2^delta
```

assignments from `{-1,2}`, solve the resulting `delta x delta` linear
system for `beta` and verify every remaining class.

A passing assignment reconstructs

```text
y=N alpha in {-1,2}^n
```

and therefore

```text
x=(y+1)/3 in {0,1}^n.
```

If all assignments fail, no alphabet vector exists in the full
kernel. QED.

### Relation to the old nullity terminal

R5 E10 gives

```text
O(2^d poly(n)).
```

E18 replaces `d` by

```text
delta <= d.
```

Thus K2 is never asymptotically worse than the old kernel enumeration
and can be strictly better when projective relations force kernel
coordinates.

## 6. Frozen controls for K0/K1/K2

### PG15_SAT

The frozen SAT source has

```text
d=4.
```

Its projective profile has no zero evaluation coordinate and no
forced/incompatible projective class.  Therefore

```text
delta=4.
```

E18 does not falsely simplify this control; the existing exact
`2^4` terminal remains available.

### PG15_UNSAT

The frozen singular UNSAT source has one-dimensional rational kernel
generated primitively by

```text
(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

All nonzero evaluation rows are in one projective class.  The class
contains ratio `4`, which is not in

```text
{1,-2,-1/2}.
```

K1 therefore rejects the source immediately, without enumerating the
two old free-coordinate states.

### R5 E17 frozen q=6 hardness target

The E17 target has

```text
n=102,
rank_Q=90,
d=12.
```

Exact kernel evaluation shows that **36 coordinates have zero row in
every rational kernel basis representation**.  They are precisely the
six port columns per each of the six E12 gadgets:

```text
L1,L2,L3,L'1,L'2,L'3.
```

Therefore all those coordinates are fixed to

```text
x_i=1/3
```

throughout the rational solution space.

K0 rejects the E17 UNSAT benchmark immediately.

This explains the E17 local-gauge observation in a stronger
source-level form:

```text
the 12-dimensional kernel moves only internal gadget coordinates;
the global port coordinates carrying RXC3 semantics are frozen.
```

No gadget labels are required by the K0 recognizer: one exact nullspace
basis exposes the zero evaluation rows directly.

### R5 E16 ring family

For the finite E16 ring controls,

```text
d = k+1,
```

and projective compression leaves

```text
delta = k+1.
```

So K0/K1/K2 do not fake-close the E16 firewall.  The next section
handles it by a genuinely different mechanism.

## 7. Levi general-factor representation

Let `H_A` be the bipartite Levi graph with:

```text
row vertices     R,
variable vertices V,
one edge rv iff A_{rv}=1.
```

Because the source is cubic, every vertex has degree three.

For a Boolean assignment `x`, select all three incidence edges at a
variable vertex when `x_v=1`, and select none when `x_v=0`.

Then Exact-One is equivalent to finding an edge set `F` with local
degree constraints

```text
deg_F(r) = 1       for every r in R,
deg_F(v) in {0,3}  for every v in V.
```

Conversely any such general factor reconstructs the Boolean assignment
by

```text
x_v=1 iff deg_F(v)=3.
```

This representation is exact.

## 8. Exact composition across an edge cut

Let

```text
delta(S)
```

be an edge cut of the current Levi subproblem and suppose

```text
|delta(S)| = s.
```

Enumerate all

```text
2^s
```

selected/unselected states of the cut edges.

For one fixed cut state, let `c_u` be the number of selected crossing
edges incident to vertex `u`.  If the current allowed total degree set
at `u` is `D_u`, the residual allowed degree set inside its side is

```text
D'_u = {d-c_u : d in D_u, d>=c_u}.
```

The two sides then share no unfixed edge.  Therefore:

### Cut composition lemma

For a fixed cut-edge state,

```text
the parent general-factor instance is feasible
iff
both residual side instances are feasible.
```

Taking the disjunction over the at most `2^s` cut states is exact.

This remains true recursively, because all information transmitted
across a cut is already contained in the selected/unselected status of
the crossing incidence edges.

## 9. BSEP-k — recursively balanced separator terminal

Fix constants

```text
k >= 0,
beta < 1,
```

for example `beta=2/3`.

Call a current subproblem `k`-balanced-separable if it has an edge cut
of size at most `k` whose two sides each contain at most `beta` times
the current number of vertices.

For fixed `k`, such a cut can be found or refuted in polynomial time:

```text
enumerate all edge subsets of size <= k;
delete them;
compute connected components;
enumerate the at most 2^(k+1) groupings of resulting components;
verify the actual crossing cut and the balance condition.
```

Define the recursive terminal:

```text
BSEP-k(H,D):
    if H is constant size:
        brute-force the remaining local factor exactly;

    find a balanced edge cut C with |C|<=k;
    if none exists:
        return UNROUTED;

    for every state sigma in {0,1}^C:
        derive the two exact residual degree-set instances;
        recursively solve both sides;

    SAT iff one state makes both children SAT;
    otherwise UNSAT.
```

### Theorem BSEP

For every fixed `k` and fixed `beta<1`, BSEP-k is an exact
deterministic polynomial-time algorithm on the class of instances for
which every nonconstant recursive subproblem admits such a balanced
cut.

### Complexity

Let `T(N)` be the worst-case running time on this recursively
separable class.  A cut has at most `k` edges and both sides have size
at most `beta N`, so

```text
T(N)
<=
2^k (T(N_1)+T(N_2))
+ N^{k+O(1)},
N_1,N_2 <= beta N.
```

The recursion depth is `O(log N)`.  For fixed `k` and fixed `beta`,
this recurrence is

```text
T(N)=N^{O(k)}.
```

SAT reconstruction stores the successful cut state and child
backpointers.  An UNSAT execution tree is also polynomial-size on this
class.

Thus BSEP is a real polynomial terminal, not only a certificate
verifier.

## 10. E16 is closed by BSEP-2

R5 E16 constructs a connected `k`-block ring with

```text
nullity_Q(A_k)=k+1,
distance-to-commuting t=k.
```

So neither small-nullity nor near-commuting handles the family.

However the Levi graph is a ring of constant-size blocks linked by the
redirected incidences.  Cutting the two ring incidences at appropriate
positions separates two contiguous block intervals.  Choosing the cut
positions near opposite sides of the ring gives a balanced 2-edge cut.

The same property recurs inside each interval.

Therefore the E16 family belongs to the recursively balanced
`k=2` separator class and is decided exactly in polynomial time by
BSEP-2.

The companion checker verifies balanced 2-edge cuts on finite controls
`k=2,...,6`.

## 11. Why E18 does not solve the E12 carrier

The two branches are deliberately incomplete.

Projective compression can leave

```text
delta = Theta(n).
```

Balanced constant-size cuts can be absent in a highly connected Levi
graph.

R5 E17 also warns that identifying local gauge modes does not by itself
remove the global NP-hard quotient: for the general E12 reduction the
port quotient recovers two copies of the original RXC3 kernel.

Therefore E18 does **not** claim:

```text
large raw nullity => small projective residual;
large raw nullity => balanced separator;
or
every E12 target is solved after local quotient.
```

Those statements would contradict the existing firewalls.

## 12. Updated exact router

The source-level stack can now safely include:

```text
T0  cardinality / structural checks

T1  full Q-rank
      -> UNSAT

T2  K0 kernel-fixed coordinate
      -> source-aligned UNSAT

T3  K1 incompatible projective ratio
      -> source-aligned pair UNSAT

T4  K2 projective propagation
      residual delta=O(log n)
      -> exact polynomial enumeration

T5  old small-nullity terminal
      -> O(2^d poly(n))

T6  clique-LP / weighted source-aligned certificate
      infeasible -> UNSAT

T7  commuting I+P+Q
      -> polynomial exact

T8  distance-to-commuting t=O(log n)
      -> O(2^(3t) poly(n))

T9  BSEP-k for fixed k
      recursively balanced Levi decomposition
      -> polynomial exact

otherwise
      -> HIGH-ADHESION PROJECTIVELY-FREE EFFECTIVE CORE
```

The router should choose the cheapest applicable exact terminal.

## 13. New universal hard-core conditions

An unresolved family must now evade all of the following:

```text
no kernel-fixed coordinate;
no incompatible proportional kernel evaluations;
projective residual delta = omega(log n);
no recursively balanced constant-size Levi cut;
large effective/global kernel after local quotient;
clique LP feasible;
far from every already certified tractable commuting normal form;
no reconstructed {-1,2} kernel vector.
```

For the square+cubic+linear carrier, the point-graph language is:

```text
the -3 eigenspace has nonzero evaluation at every vertex,
its projective evaluation rows are alphabet-compatible,
its residual Boolean freedom remains large,
and the Levi source has high adhesion.
```

This is strictly narrower than the E17 frontier.

## 14. Next attack surface

The next natural layer is no longer raw nullity.

It is the first place where genuinely ternary coupling remains after
all unary/projective-pair propagation and all cheap balanced
decomposition:

```text
HIGH-ADHESION EFFECTIVE KERNEL
+
NO UNARY FIXED COORDINATE
+
NO PROJECTIVE PAIR OBSTRUCTION
+
LARGE PROJECTIVE RESIDUAL
```

Two exact directions remain aligned with the current program:

```text
(A) higher-order source-aligned projection/rank obstructions;
(B) bounded-interface decompositions beyond literal small edge cuts.
```

Any claimed universal theorem must be stress-tested against E12,
E16, E17 and the frozen PG15 controls before promotion.

## 15. Global verdict

```text
NEW EXACT RESULT:
    kernel-fixed coordinate -> polynomial source-aligned UNSAT.

NEW EXACT RESULT:
    incompatible projective kernel ratio -> polynomial
    source-aligned pair UNSAT.

NEW EXACT RESULT:
    projective forced-class propagation reduces the old
    O(2^d poly(n)) terminal to O(2^delta poly(n)), delta<=d.

NEW EXACT RESULT:
    recursively balanced constant-size Levi edge separators
    admit exact deterministic polynomial general-factor DP.

FROZEN FIREWALLS:
    PG15_SAT passes safely;
    PG15_UNSAT is caught by K1;
    E17 q=6 UNSAT is caught by K0 with 36 fixed coordinates;
    E16 survives K0/K1/K2 but is caught by BSEP-2.

UNRESOLVED:
    high-adhesion, projectively-free, large-effective-kernel core.

P_VS_NP = OPEN.
```
