# R5 E9 — Paley {1,2,-3} Infinite Post-RKPR Square-Root Nullity Barrier

Date: 2026-09-30

Status:
`JANUS_EXACT_INFINITE_FAMILY__CONNECTED_LINEAR_CUBIC_POST_RKPR__NULLITY_OMEGA_SQRT_N__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS THEOREM FALSIFIES THE ROUTE
POST-RKPR LINEAR-CUBIC RESIDUAL => nullity_Q = O(log n).

IT DOES NOT SOLVE THE REMAINING SOURCE CLASS.
IT DOES NOT PROVE A UNIVERSAL POLYNOMIAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Infinite prime set

Let `q` be a prime satisfying

```text
q = 7 (mod 24),
q > 7.
```

There are infinitely many such primes by Dirichlet's theorem on primes in arithmetic progressions.

Because `q = 7 (mod 8)`, quadratic reciprocity gives

```text
(2/q)=+1.
```

Because `q = 7 (mod 12)`,

```text
(-1/q)=-1,
(3/q)=-1,
```

and therefore

```text
(-3/q)=+1.
```

Hence both

```text
2 and -3
```

are nonzero quadratic residues modulo `q`.

Let `Q` denote the multiplicative subgroup of nonzero quadratic residues in `F_q`, and let

```text
H = <2,-3> <= Q.
```

Fix any multiplicative coset

```text
C = a H subset Q.
```

Write

```text
h = |H|.
```

## 2. Paley tournament restricted to one difference coset

Use the Paley tournament on `F_q`:

```text
u -> v  iff  v-u in Q.
```

Columns are the tournament arcs whose difference belongs to `C`:

```text
E_C = { (s -> s+d) : s in F_q, d in C }.
```

Hence the number of columns is

```text
n = q h.
```

For every `d in C` and `s in F_q`, define one directed triangle row

```text
R(d,s):
  s      -> s+d        difference d,
  s+d    -> s+3d       difference 2d,
  s+3d   -> s           difference -3d.
```

The three differences lie in `C` because `2,-3 in H`, and

```text
1 + 2 - 3 = 0.
```

Thus every row is a directed 3-cycle in the Paley tournament.

There are exactly

```text
q h = n
```

candidate rows.

## 3. Distinctness of all rows

The multiplicative signature of `R(d,s)` is

```text
{d,2d,-3d} = d {1,2,-3}.
```

Suppose two row orbits had the same signature. Then for

```text
t = d'/d in H
```

we would have

```text
t {1,2,-3} = {1,2,-3}.
```

The multiplicative stabilizer of a three-element set has order dividing three. If it were nontrivial, `{1,2,-3}` would be a coset of a subgroup of order three. Since it contains `1`, it would itself be that subgroup. Then `2` would have order three and its square would be the third element:

```text
4 = -3 (mod q),
```

forcing `q | 7`, hence `q=7`, excluded.

Therefore the signature stabilizer is trivial and distinct `d in C` give distinct translation orbits.

For fixed `d`, translation by nonzero `s` cannot stabilize a three-point subset of `F_q` when prime `q>3`. Hence all `q h` rows are distinct.

Thus the source matrix `A_C` is square `n x n`.

## 4. Cubic column degree

Each row has exactly three columns.

Fix a column arc

```text
E(c,u) = (u -> u+c),
c in C.
```

It occurs in exactly the following three rows:

```text
R(c, u)                    [first edge],
R(c/2, u-c/2)              [second edge],
R(-c/3, u+c)               [third edge].
```

All three row differences remain in `C` because `2,-3 in H` and inverses lie in `H`.

For `q>7` these three row labels are distinct. Therefore every column has degree exactly three.

Hence

```text
A_C is square cubic:
row degree = 3,
column degree = 3.
```

## 5. Linearity

Rows are distinct directed triangles of a tournament. Two distinct directed triangles cannot share two arcs: two shared arcs determine the same three vertices, and the tournament orientation on those vertices is unique.

Therefore any two distinct source rows intersect in at most one column.

So `A_C` is linear cubic.

## 6. Levi connectedness

Ignoring translation coordinates, row difference labels and column difference labels both range over the coset `C`.

From row difference `d`, the source incidence directly reaches column differences

```text
d,
2d,
-3d.
```

Since `H=<2,-3>`, the quotient incidence graph on difference labels is connected on `C`.

It remains to show the translation lift does not split.

Define two row-to-row two-edge moves through a shared column:

```text
A_move: R(d,s) -> R(2d, s+d),
B_move: R(d,s) -> R(-3d, s+3d).
```

Compare the two length-four paths:

```text
A_move then B_move:
R(d,s) -> R(-6d, s+7d),

B_move then A_move:
R(d,s) -> R(-6d, s).
```

They reach the same difference label but translation coordinates differ by

```text
7d != 0 (mod q)
```

because `q>7` and `d!=0`.

Their concatenation yields a closed quotient walk with nonzero additive voltage `7d`. Since the additive group of `F_q` has prime order, any nonzero voltage generates all translations.

Therefore the full Levi graph of `A_C` is connected.

## 7. A forced `(q-1)`-dimensional rational kernel

Let `G_C` be the oriented arc-vertex incidence matrix of the column digraph `E_C`:

```text
G_C[e,u] = -1 at the tail,
G_C[e,v] = +1 at the head.
```

Every source row is a directed triangle, so the oriented incidence vectors telescope around the cycle:

```text
A_C G_C = 0.
```

The underlying undirected column graph is connected. Indeed, choose any `d in C`; the edges

```text
s -- s+d
```

alone form one cycle through all `q` vertices because `q` is prime and `d!=0`.

Hence

```text
rank_Q(G_C)=q-1.
```

Therefore

```text
nullity_Q(A_C) >= q-1.
```

No claim of equality is needed for the barrier theorem.

## 8. RKPR-clean despite the large kernel

The rational-kernel projective-ratio quotient (RKPR) looks for zero or proportional coordinate functionals on `ker_Q(A_C)`.

But `im_Q(G_C)` is a subspace of `ker_Q(A_C)`.

For a column arc `e=(u->v)`, the coordinate functional restricted to this gradient subspace is

```text
p |-> p_v-p_u.
```

This functional is nonzero.

For two distinct tournament arcs `e,f`, the two gradient coordinate functionals are proportional only if the oriented incidence covectors are proportional. Two nonzero incidence covectors of simple directed edges are proportional only when they have the same unordered endpoint pair. A tournament contains at most one orientation of each pair, so distinct columns cannot be proportional on the gradient subspace.

Consequently they cannot become zero or proportional on the larger full kernel either.

Therefore every member of the family is exactly RKPR-clean:

```text
zero zero-kernel rows,
zero proportional kernel-row pairs,
zero ratio pins,
zero equality merges.
```

The family survives RKPR unchanged.

## 9. Square-root nullity lower bound

The source size is

```text
n = q h.
```

Since `H <= Q` and `|Q|=(q-1)/2`,

```text
n <= q(q-1)/2.
```

Let `r=q-1`. Then

```text
2n <= r(r+1),
```

so

```text
q-1 = r >= (sqrt(1+8n)-1)/2.
```

Combining with the gradient kernel,

```text
nullity_Q(A_C)
>= q-1
>= (sqrt(1+8n)-1)/2
= Omega(sqrt(n)).
```

Because there are infinitely many admissible primes `q`, this is an unbounded infinite family.

Therefore the proposed route

```text
connected
+ linear cubic
+ post-RKPR
=> nullity_Q = O(log n)
```

is false.

This is an asymptotic falsifier, not merely a finite counterexample.

## 10. q=31 exact control

The first admissible prime after the excluded `q=7` is

```text
q=31.
```

Here

```text
H=<2,-3>=Q,
h=15,
n=31*15=465.
```

The deterministic checker constructs the full `465 x 465` source and verifies:

```text
row degree = column degree = 3,
linear = true,
Levi connected = true,
A G = 0,
rank_Q(G)=30,
RKPR-clean = true.
```

For this particular `q=31` control it additionally verifies

```text
rank(A mod 1,000,003)=435.
```

Since the gradient kernel already gives `rank_Q(A)<=435`, this proves

```text
rank_Q(A)=435,
nullity_Q(A)=30,
ker_Q(A)=im_Q(G)
```

for the frozen `q=31` member.

This exact equality is a finite control only; the infinite barrier uses only the universal lower bound `nullity>=q-1`.

## 11. Prior-art / anti-loop boundary

Cyclic directed triple systems and Mendelsohn difference families are classical design-theory objects, and Paley tournaments are standard. The present JANUS use is deliberately narrower: the selected `{1,2,-3}` difference-coset construction is bound to the rational-kernel/RKPR source pipeline and used to prove a post-quotient nullity lower bound.

A targeted open-literature search found general cyclic Mendelsohn difference-family constructions (for example Mishima, *J. Stat. Plann. Inference* 106 (2002), 105-115, DOI `10.1016/S0378-3758(02)00206-9`) and standard Paley-tournament definitions, but did not establish a novelty claim for the exact construction above.

Accordingly:

```text
NO LITERATURE-NOVELTY CLAIM IS MADE.
THE INTERNAL MATHEMATICAL STATEMENT IS SELF-CONTAINED.
```

## 12. Consequence for the universal algorithm program

The following shortcut is now closed:

```text
RKPR
-> connected linear residual
-> prove rational nullity O(log n)
-> enumerate 2^nullity
-> polynomial universal solver
```

The family above survives the first three structural premises while retaining

```text
nullity = Omega(sqrt n).
```

Therefore the universal program must use additional structure beyond rational nullity and pairwise projective kernel-row relations.

The live target returns to a genuinely global quotient/selection mechanism, especially the matching-normalized cycle-2-factor plus affine-syndrome coupling.

## 13. Ceiling

```text
INFINITE ADMISSIBLE PRIME SET q=7 mod24, q>7  = PROVED (Dirichlet)
SQUARE CUBIC FAMILY                            = PROVED
LINEAR                                         = PROVED
LEVI CONNECTED                                 = PROVED
RATIONAL NULLITY >= q-1                       = PROVED
RKPR-CLEAN                                     = PROVED
NULLITY = Omega(sqrt n)                        = PROVED
POST-RKPR nullity O(log n) ROUTE               = FALSIFIED
q=31 exact nullity = 30                        = CHECKED/PROVED
UNIVERSAL POLYNOMIAL DECIDER                   = NOT PROVED
E8_D1                                          = EMPTY
P_VS_NP                                        = OPEN
```
