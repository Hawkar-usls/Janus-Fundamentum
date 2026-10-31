# R5 E9 — Rank-1 Stitched `TD(3,3)` High-Nullity Family

Date: 2026-09-27

Status:
`JANUS_EXACT_CONSTRUCTIVE_FAMILY_THEOREM__NO_D1_PROMOTION`

Scientific firewall:

```text
THIS NOTE PROVES AN EXPLICIT CONNECTED LINEAR CUBIC SQUARE FAMILY
WITH RATIONAL NULLITY n/9+1.

IT DOES NOT PROVE THAT THE FAMILY IS OET-IRREDUCIBLE.
IT DOES NOT PROVE AN ASYMPTOTIC PRIMITIVE TWO-PERMUTATION FAMILY.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL EXACT-ONE DECIDER.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parent checkpoint:
- `research/R5_E9_SEMANTIC_CHECKPOINT_OET_IRREDUCIBLE_HIGH_NULLITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_rank1_stitched_td33_high_nullity.py`

## 1. Base block `TD(3,3)`

Let the nine columns be

```text
X={x0,x1,x2}, Y={y0,y1,y2}, Z={z0,z1,z2}.
```

For `i,j in Z_3`, let

```text
L_ij = {x_i, y_j, z_{i+j mod 3}}.
```

The resulting `9 x 9` incidence matrix `B` is cubic on rows and columns and linear.

### Lemma 1 — exact rational kernel of one block

For a vector written as values `x_i,y_j,z_k`, the equation `Bv=0` is

```text
x_i + y_j + z_{i+j} = 0  for all i,j in Z_3.
```

Subtract the equations with `j` and `j+1`. For fixed `i`,

```text
y_j-y_{j+1} = z_{i+j+1}-z_{i+j}.
```

As `i` runs through `Z_3`, the three cyclic differences of the `z` values are equal. Their sum is zero, hence over `Q` each difference is zero. Therefore all `z_k` are equal. The equations then force all `x_i` equal and all `y_j` equal.

Thus

```text
ker_Q(B)
= { (a,a,a,b,b,b,c,c,c) : a+b+c=0 },
```

so

```text
rank_Q(B)=7,
nullity_Q(B)=2.
```

The same rank `7` remains after deleting row `L_00`, after deleting row `L_01`, and after deleting both. This finite local fact is independently replayed by the executable checker; equivalently, the remaining equations still force the same block-constant kernel law.

## 2. Chain construction

Take `m>=1` disjoint copies of `B`, indexed `t=0,...,m-1`. Before stitching, the block diagonal matrix has nullity `2m`.

For every boundary `t | t+1`, perform the incidence 2-switch

```text
remove (L_01^(t),   y_1^(t))
remove (L_00^(t+1), x_0^(t+1))

add    (L_01^(t),   x_0^(t+1))
add    (L_00^(t+1), y_1^(t)).
```

Call the resulting `9m x 9m` incidence matrix `A_m`.

The matrix perturbation at one boundary is

```text
-e_r1 e_c1^T - e_r2 e_c2^T
+e_r1 e_c2^T + e_r2 e_c1^T
= (e_r1-e_r2)(e_c2-e_c1)^T,
```

hence each stitch is rank one as a matrix perturbation.

## 3. Cubic, square, linear and connected are preserved

A 2-switch preserves every involved row degree and column degree. Therefore every row and every column of `A_m` still has degree three, and the matrix remains square.

Linearity is preserved for this explicit switch. Inside each untouched block every unordered column pair occurred at most once. The removed incidences only delete old row-pairs. Each new cross-block incidence creates pairs whose endpoints previously lived in disjoint copies; those pairs did not occur before. Across distinct boundaries the copies/column labels are different, so no new unordered pair is duplicated.

The Levi graph is connected. Each `TD(3,3)` Levi block stays connected after removal of its designated boundary incidences (a finite local property checked exactly by the executable), and each boundary contributes the two new cross edges linking the adjacent blocks. Thus the chain of blocks is connected.

Consequently `A_m` is a connected linear cubic square carrier for every `m>=1`.

## 4. Exact nullity theorem

### Theorem R1-STITCH-TD33

For every `m>=1`,

```text
rank_Q(A_m) = 8m-1,
nullity_Q(A_m) = m+1.
```

Since `n=9m`, equivalently

```text
nullity_Q(A_m) = n/9 + 1.
```

### Proof

Because the non-switched seven source equations in every block already have rank seven and retain the base-block kernel, the restriction of any `v in ker_Q(A_m)` to block `t` has the form

```text
X_t = a_t,
Y_t = b_t,
Z_t = c_t,
a_t+b_t+c_t=0.
```

So before imposing stitched equations there are exactly two rational degrees of freedom per block: `2m` total.

Consider the boundary between blocks `t` and `t+1`.

The modified equation for `L_01^(t)` is obtained from

```text
a_t + b_t + c_t = 0
```

by replacing its `y_1^(t)` entry, value `b_t`, with `x_0^(t+1)`, value `a_{t+1}`. Since `a_t+b_t+c_t=0` already holds, the modified equation is exactly

```text
a_{t+1} = b_t.
```

The modified equation for `L_00^(t+1)` replaces its `x_0^(t+1)`, value `a_{t+1}`, by `y_1^(t)`, value `b_t`; after using `a_{t+1}+b_{t+1}+c_{t+1}=0`, it gives the same equality and no second independent constraint.

Thus boundary `t|t+1` contributes exactly one independent equation

```text
b_t - a_{t+1}=0.
```

The `m-1` boundary equations are independent: each one introduces the next variable `a_{t+1}` in a chain and no later equation can eliminate that first occurrence without using the same boundary relation.

Therefore

```text
nullity_Q(A_m)
= 2m - (m-1)
= m+1,
```

and, since `A_m` is `9m x 9m`,

```text
rank_Q(A_m)=9m-(m+1)=8m-1.
```

QED.

## 5. Why this matters to the current frontier

This family proves that linear-size rational nullity can arise from a mechanism different from the already-recognized one-edge-twist 2-lift tower:

```text
small singular modules
+ rank-1 degree-preserving stitching
=> connected linear cubic square carrier
+ nullity Theta(n).
```

Therefore high nullity by itself is not evidence that the remaining carrier is a globally irreducible spectral object.

The chain also exposes a small Levi separator at every module boundary: exactly two cross incidences join consecutive blocks. Hence this family should be stripped by a separator-aware exact router before using it as evidence about the genuinely irreducible high-nullity core.

This gives a new proof-search warning:

```text
PRIMITIVITY OF A CHOSEN TWO-PERMUTATION NORMALIZATION
!=
LEVI STRUCTURAL IRREDUCIBILITY.
```

A one-factorization may produce a transitive/primitive permutation presentation even when the underlying Levi graph has an obvious constant-size separator. Any theorem based on `Gamma=<p,q>` must therefore be checked against representation-independent Levi decomposability.

## 6. New admissible pre-gate

The next exact structural pre-gate is

```text
R5_E9_LEVI_SMALL_SEPARATOR_EXACT_COMPOSITION_GATE_V1
```

Target:

```text
recognize constant-size Levi edge separators;
compute the finite boundary signature for Exact-One / General-Factor {1}/{0,3};
compose the two sides exactly;
reconstruct a witness in polynomial time;
recursively strip all constant-separator modules;
then return to the primitive/high-nullity attack only on the separator-resistant core.
```

For a cut of size `c=O(1)`, exhaustive boundary-state composition has only a constant number of states (`2^c` edge-in/out patterns, augmented by the finite partial degree state at touched vertices). The exact state semantics and reconstruction theorem must be proved before promotion to a router.

## 7. Ceiling

```text
CONNECTED LINEAR CUBIC SQUARE FAMILY
= PROVED

n
= 9m

rank_Q(A_m)
= 8m-1

nullity_Q(A_m)
= m+1 = n/9+1

HIGH NULLITY FROM RANK-1 STITCHING
= PROVED

OET-IRREDUCIBLE
= NOT PROVED

ASYMPTOTIC PRIMITIVE TWO-PERM FAMILY
= NOT PROVED

LEVI SMALL-SEPARATOR POLYNOMIAL ROUTER
= NEXT PROOF OBLIGATION

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
