# R5 E9 — Paley(19) Gradient-Kernel Post-RKPR Control

Date: 2026-09-30

Status:
`JANUS_EXACT_FINITE_CONTROL__LINEAR_CUBIC_CONNECTED_POST_RKPR__NULLITY_18__GRADIENT_KERNEL__UNSAT`

Scientific ceiling:

```text
THIS IS A NEW EXACT POST-RKPR HARD CONTROL / POLYNOMIAL UNSAT TERMINAL.
IT DOES NOT YET GIVE AN INFINITE FAMILY.
IT DOES NOT PROVE A UNIVERSAL POLYNOMIAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Paley tournament on Z_19

Let

```text
Q = {1,4,5,6,7,9,11,16,17} subset Z_19^*.
```

Orient the complete graph on `Z_19` by

```text
u -> v  iff  v-u in Q (mod 19).
```

Because `19 = 3 (mod 4)`, exactly one of `d,-d` lies in `Q`; hence this is a tournament.

Its arc set has

```text
N = 19*18/2 = 171
```

arcs.

## 2. Selected cyclic-triangle translation orbits

For a triple `T={a,b,c}`, let its translation orbit be

```text
Orb(T) = { T+s : s in Z_19 }.
```

Use the following nine cyclic-triangle orbit representatives:

```text
(0,1,2)
(0,1,10)
(0,2,4)
(0,3,6)
(0,3,11)
(0,4,8)
(0,5,10)
(0,5,12)
(0,6,12)
```

Every orbit has size 19, so the selected row set has

```text
9*19 = 171
```

rows.

Columns are the 171 tournament arcs. A row has a 1 in the three tournament arcs induced by its cyclic triangle.

Thus the source matrix `A` is `171 x 171` with row weight exactly three.

### Degree certificate

Order the Paley differences as

```text
(1,4,5,6,7,9,11,16,17).
```

The nine orbit signatures, where one entry is the degree contribution to every arc of that difference class, are

```text
(0,1,2)   : (2,0,0,0,0,0,0,0,1)
(0,1,10)  : (1,0,0,0,0,2,0,0,0)
(0,2,4)   : (0,1,0,0,0,0,0,0,2)
(0,3,6)   : (0,0,0,1,0,0,0,2,0)
(0,3,11)  : (0,0,0,0,0,0,2,1,0)
(0,4,8)   : (0,2,0,0,0,0,1,0,0)
(0,5,10)  : (0,0,2,0,0,1,0,0,0)
(0,5,12)  : (0,0,1,0,2,0,0,0,0)
(0,6,12)  : (0,0,0,2,1,0,0,0,0)
```

Their componentwise sum is

```text
(3,3,3,3,3,3,3,3,3).
```

Hence every column also has weight exactly three.

Therefore `A` is a square cubic Positive 1-in-3 source.

## 3. Linearity and connectedness

Two distinct tournament triangles cannot share two tournament arcs: two shared arcs already determine the same three vertices, hence the same triangle. Therefore distinct rows intersect in at most one column, so the source is linear.

The exact checker performs a Levi-graph BFS and verifies that all

```text
171 row vertices + 171 column vertices = 342
```

vertices lie in one connected component.

Thus this is a connected linear cubic source.

## 4. Gradient kernel

Let `G` be the oriented arc-vertex incidence matrix of the tournament:

```text
G[e,u] = -1 at the tail of e,
G[e,v] = +1 at the head of e,
0 otherwise.
```

Each selected row of `A` is a directed 3-cycle. The sum of the three oriented incidence rows around a directed cycle is zero. Therefore

```text
A G = 0.
```

The underlying undirected tournament graph is complete and connected, hence

```text
rank_Q(G) = 19-1 = 18.
```

So

```text
nullity_Q(A) >= 18,
rank_Q(A) <= 153.
```

The exact checker then performs deterministic Gaussian elimination modulo the prime

```text
p = 1,000,003
```

and obtains

```text
rank_{F_p}(A mod p) = 153.
```

A nonzero `153 x 153` minor modulo `p` is an exact integer nonvanishing certificate, so

```text
rank_Q(A) >= 153.
```

Hence

```text
rank_Q(A) = 153,
nullity_Q(A) = 18,
ker_Q(A) = im_Q(G).
```

This is exact; no floating-point rank calculation is used.

## 5. RKPR-clean theorem

In the gradient kernel, the coordinate functional attached to an arc `u->v` is

```text
p |-> p_v-p_u.
```

For two distinct arcs, these functionals are nonzero. Two such functionals can be proportional only if they have the same unordered endpoint pair; then the scalar is `+1` for the same orientation or `-1` for the reverse orientation.

A tournament contains exactly one orientation of each unordered pair. Therefore distinct tournament-arc coordinates give no proportional rational kernel rows.

Consequently this source has

```text
zero zero-kernel rows,
zero proportional pairs,
zero RKPR pins,
zero RKPR equality merges.
```

It survives the entire rational kernel projective-ratio quotient unchanged.

Thus this is a genuine post-RKPR singular control with

```text
nullity_Q(A)=18.
```

## 6. Exact UNSAT terminal from the gradient kernel

Suppose, for contradiction, that

```text
A x = 1,
x in {0,1}^171.
```

Because every row has weight three,

```text
y = 3x-1
```

satisfies

```text
A y = 0,
y in {-1,2}^171.
```

Since `ker_Q(A)=im_Q(G)`, there exists a rational vertex potential `p` such that for every tournament arc `u->v`,

```text
y_{u->v} = p_v-p_u in {-1,2}.
```

Every unordered pair of tournament vertices has exactly one oriented arc. Hence for every distinct `u,v`,

```text
|p_u-p_v| in {1,2}.
```

In particular all 19 potentials are distinct. But a set of real numbers with every pairwise distance in `{1,2}` has size at most three: after translating the minimum to zero, every other point must lie in `{1,2}`.

Contradiction.

Therefore

```text
A is Exact-One UNSAT.
```

This is a polynomially checkable UNSAT certificate once the gradient-kernel equality has been certified.

## 7. What this kills

This single exact control falsifies any proposed theorem of the form

```text
connected + linear cubic + post-RKPR
=> full rational rank
```

or

```text
connected + linear cubic + post-RKPR
=> rational nullity bounded by a small absolute constant < 18.
```

It also shows that large nontrivial rational kernels can survive both linearity and RKPR simultaneously.

It does **not** by itself falsify an asymptotic theorem such as

```text
post-RKPR nullity = O(log n)
```

because this note freezes one finite `n=171` control only. An infinite family or unbounded sequence is still required for that promotion.

## 8. Relation to the commuting-nullity theorem

The source is connected and has nullity 18. By the already proved theorem

```text
connected + A=I+P+Q + PQ=QP
=> nullity_Q(A) in {0,2},
```

any matching-normalized two-permutation presentation of this source lies in the genuinely noncommuting branch.

Hence the control sits exactly inside the surviving hard regime:

```text
connected
+ linear cubic
+ post-RKPR
+ singular high-nullity
+ noncommuting.
```

## 9. Checker

Executable exact regression:

`experiments/r5_e9_paley19_gradient_kernel_post_rkpr_control.py`

It verifies:

- Paley tournament orientation;
- all nine base triples are cyclic;
- 171 distinct translated rows;
- row degree = column degree = 3;
- pairwise row intersection <= 1;
- Levi connectedness = 342/342;
- `A G = 0` over the integers;
- `rank(G)=18`;
- `rank(A mod 1,000,003)=153`;
- hence exact rational rank/nullity `(153,18)`;
- zero proportional gradient coordinate functionals;
- the potential-distance UNSAT contradiction.

## 10. Live frontier

The next genuine question is now sharper:

```text
CAN THIS PALEY/TOURNAMENT GRADIENT-KERNEL MECHANISM BE LIFTED
TO AN UNBOUNDED FAMILY OF SQUARE CUBIC POST-RKPR SOURCES?
```

A positive answer with nullity growing faster than `O(log n)` would kill that entire proposed post-RKPR nullity route. A negative structural theorem could instead expose a new polynomial quotient.

## 11. Ceiling

```text
q=19 square cubic design                 = PROVED
linear + connected                       = PROVED
rank_Q(A)                                = 153
nullity_Q(A)                             = 18
kernel_Q(A) = tournament gradients       = PROVED
RKPR-clean                               = PROVED
Exact-One UNSAT                          = PROVED
post-RKPR O(log n) asymptotic falsifier  = NOT YET PROVED
universal polynomial decider             = NOT PROVED
E8_D1                                    = EMPTY
P_VS_NP                                  = OPEN
```
