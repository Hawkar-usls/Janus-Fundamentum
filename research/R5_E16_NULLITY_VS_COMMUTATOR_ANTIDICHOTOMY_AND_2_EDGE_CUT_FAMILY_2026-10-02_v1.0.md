# R5 E16 — Nullity-vs-Commuting Anti-Dichotomy and the 2-Edge-Cut Family

Date: 2026-10-02

Status:
`EXPLICIT_CONNECTED_COUNTERFAMILY__LARGE_NULLITY_AND_LARGE_DISTANCE_TO_COMMUTING__SMALL_SEPARATOR_EXPOSED`

Scientific ceiling:

```text
THIS NOTE KILLS THE NAIVE DICHOTOMY
  LARGE RATIONAL NULLITY => SMALL DISTANCE TO COMMUTING.

THE COUNTERFAMILY REMAINS EXACT-ONE SAT AND HAS NONTRIVIAL 2-EDGE CUTS,
SO IT POINTS TO A REQUIRED THIRD ROUTER BRANCH: SEPARATOR DECOMPOSITION.

P_VS_NP = OPEN.
```

## 1. Base block

Let `B` be the `3 x 3` toroidal Exact-One source on indices

```text
(i,j) in Z_3 x Z_3
```

with permutations

```text
P(i,j)=(i+1,j),
Q(i,j)=(i,j+1),
```

and

```text
A_B = I + P + Q.
```

This is square, cubic and linear.  It is connected and commuting.

The rational nullity is exactly two:

```text
nullity_Q(A_B)=2.
```

It has exactly three Exact-One witnesses, the three color classes

```text
x_{i,j}=1 iff i-j == r mod 3,
r in Z_3.
```

## 2. k-block ring construction

Take `k>=2` disjoint copies `B_0,...,B_{k-1}` of the base block.
Keep `P` blockwise.

For each block `b`, let

```text
u_b=(0,0) in B_b,
v_b=Q(u_b)=(0,1) in B_b.
```

Replace the `Q` image on the special row by the next block's target:

```text
Q*(u_b)=v_{b+1 mod k}.
```

On every other row, keep

```text
Q*=Q.
```

Equivalently, this is obtained from the disjoint union by cyclically permuting the `k` target images `v_b` among the `k` special rows `u_b`.

Define

```text
A_k = I + P + Q*.
```

For `k=2` this is simply the two-image swap.

## 3. Structural audit

### Square and cubic

`P` and `Q*` are permutations, so every row and column of `A_k` has weight three.
The matrix has `9k` rows and `9k` columns.

### Linearity

Inside a block, replacing the one `Q`-target of the special row removes an old co-occurrence; the two retained local variables of that row occur together in no other row because the base block is linear.

The imported target lies in a different block, so it cannot create a second shared local variable with any row there.  Distinct imported targets `v_b` are different.  Hence no two rows share more than one column.

Thus `A_k` is square+cubic+linear.

### Connectedness

Each base Levi graph is connected.  The redirected `Q*` incidences link `B_b` to `B_{b+1}` cyclically, so the complete Levi graph is connected.

Therefore this is not a fake counterexample obtained by a disjoint union.

## 4. Exact rational nullity d=k+1

The base `3x3` torus has row rank seven, so its kernel has dimension two.
By translation symmetry every source row is redundant in the full set of nine row equations: deleting the special row `u_b` leaves the same rank seven.

Therefore, before inserting the redirected special equation, the eight unchanged equations in block `b` leave exactly the usual two-dimensional block kernel and already imply the original missing equation

```text
y(u_b)+y(Pu_b)+y(v_b)=0.
```

The redirected special equation is

```text
y(u_b)+y(Pu_b)+y(v_{b+1})=0.
```

Subtracting gives precisely the coupling condition

```text
y(v_{b+1})=y(v_b).
```

Across the `k` blocks these are the cyclic equalities

```text
y(v_0)=y(v_1)=...=y(v_{k-1}).
```

They have rank `k-1`.

Starting from `2k` independent block-kernel dimensions, the ring coupling removes `k-1`, hence

```text
boxed:
nullity_Q(A_k)=2k-(k-1)=k+1.
```

Thus the rational nullity grows linearly with the size of the family.

## 5. Exact distance to the commuting centralizer t=k

Use the displayed normal form `A_k=I+P+Q*`.
The blockwise original `Q` commutes with `P` and differs from `Q*` exactly at the `k` special rows, so

```text
t <= k.
```

For the reverse inequality, inspect the `P`-cycle

```text
C_b={(0,0),(1,0),(2,0)}
```

inside each block.

Any permutation `R` commuting with `P` must map an entire `P`-cycle to another `P`-cycle with one common cyclic shift.  On `C_b`, the modified `Q*` agrees with the original within-block horizontal map at the two nonspecial points `(1,0),(2,0)`, but sends the special point `(0,0)` into the next block.

A commuting map can therefore:

```text
agree with the two nonspecial points by mapping C_b within B_b,
```

or

```text
agree with at most the one redirected special point by mapping C_b to B_{b+1},
```

but it cannot agree with all three.

Hence every commuting `R` disagrees with `Q*` at least once on every one of the `k` distinct cycles `C_b`:

```text
t >= k.
```

Therefore

```text
boxed:
distance_H(Q*, C(P)) = k.
```

Combining with Section 4:

```text
boxed:
nullity_Q(A_k)=k+1,
nearest-commuting distance t=k.
```

So both parameters are extensive.

## 6. Exact witness count

Inside one base block, the three Exact-One states are the three residue classes of `i-j mod 3`.
At the distinguished coordinate `v_b=(0,1)`, exactly one of these three states selects `v_b` and the other two do not.

In centered coordinates

```text
y=3x-1 in {-1,2},
```

this means:

```text
one local state has y(v_b)=2,
two local states have y(v_b)=-1.
```

The ring coupling from Section 4 requires all `y(v_b)` to be equal.

Thus either:

```text
all blocks use their unique y(v_b)=2 state: 1 global witness,
```

or

```text
every block independently chooses one of its two y(v_b)=-1 states: 2^k witnesses.
```

Therefore

```text
boxed:
#ExactOne(A_k)=2^k+1.
```

In particular the whole family is SAT.

## 7. Why the family does not defeat the overall router

The Levi graph of `A_k` has edge connectivity exactly two.
For each block, the two redirected incidences crossing its boundary form a nontrivial 2-edge cut separating that block from the rest of the ring.

So the family simultaneously has

```text
connected source,
large nullity,
large distance to commuting,
```

but also an obvious constant-size separator structure.

This shows that the hoped-for two-way theorem

```text
large nullity
=>
small distance to commuting
```

is false.

The structurally correct router must permit at least a third branch:

```text
large nullity
=>
small distance to commuting
OR small separator / exact decomposition
OR genuinely highly connected hard core.
```

## 8. General-factor separator interpretation

In the Levi/general-factor formulation, selected incidence edges obey local degree constraints

```text
clause vertex: degree exactly 1,
variable vertex: degree 0 or 3.
```

Across an edge cut of constant size `s`, one may enumerate the `2^s` selected/unselected states of the cut edges.  Each state leaves independent residual degree constraints on the two sides.

Therefore constant-size cuts are natural finite interfaces for exact dynamic programming.  The R5 E16 family is precisely of this decomposable type.

This observation does not solve an arbitrary highly connected component, but it explains why E16 is a firewall against an overstrong nullity/commuting conjecture rather than evidence against the larger router strategy.

## 9. Updated universal frontier

Any future universal theorem must survive the E16 counterfamily.  A plausible target is now:

```text
For an indecomposable / sufficiently edge-connected square+cubic+linear source
with large (-3)-multiplicity,
prove either

  (A) logarithmic distance to a tractable algebraic normal form,
  (B) a stronger polynomial obstruction,
  (C) a bounded-interface decomposition,
  (D) a constructive Hoffman-tight coclique.
```

Before promoting such a theorem, each implication must be attacked by explicit counterexample search.

P_VS_NP = OPEN.
