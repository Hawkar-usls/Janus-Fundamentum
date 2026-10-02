# R5 E19 — Paley 3-Lift Firewall for the Diagonal Schur-Power Hierarchy

Date: 2026-10-02

Status:
`CONNECTED_QINFINITY_FIREWALL__EXACT_KERNEL_EQUALITY_QUOTIENT__DIAGONAL_SCHUR_HIERARCHY_NOT_UNIVERSAL`

Scientific ceiling:

```text
THIS NOTE CONSTRUCTS A CONNECTED 165-VARIABLE SQUARE+CUBIC+LINEAR UNSAT SOURCE
FOR WHICH EVERY DIAGONAL SCHUR-POWER RELAXATION PASSES.

THE SAME INSTANCE IS CLOSED IMMEDIATELY BY THE R5 E18 KERNEL-PROJECTIVE EQUALITY QUOTIENT.

THEREFORE HIGHER DIAGONAL MOMENTS ALONE ARE NOT THE UNIVERSAL MISSING THEOREM.
P_VS_NP = OPEN.
```

## 1. Paley-11 base source

Let the vertex set be `Z_11`.  Orient the complete graph by

```text
i -> j  iff  j-i is a nonzero quadratic residue mod 11.
```

This gives the Paley tournament on 11 vertices.

There are

```text
55 directed arcs.
```

Take as source rows all cyclic directed triangles of the tournament.  The exact
checker verifies:

```text
55 cyclic triangles,
every arc lies in exactly 3 cyclic triangles.
```

Hence the base incidence matrix `A_55` is square and cubic.  Distinct directed
triangles share at most one directed arc, so it is linear.

The base source is Exact-One UNSAT for the trivial but exact cardinality reason:
if `S` were a witness, summing all 55 row equations would give

```text
3 |S| = 55,
```

which is impossible.

The base itself is therefore not yet a useful hard-core control because `3` does
not divide `55`.

## 2. Deterministic connected 3-lift

Replace every base arc by three copies labelled `c in Z_3`.

For base cyclic triangle number `t`, ordered as three base arcs `(a,b,c)`, create
three lifted rows indexed by `r in Z_3`:

```text
(a, r),
(b, r+t),
(c, r+2t+1),
```

with copy indices modulo three.

Thus every base triangle is replaced by three disjoint lifted triangles.

The companion checker verifies exactly:

```text
n = 165,
rows = 165,
every row has weight 3,
every column has weight 3,
linearity holds,
the Levi graph is connected.
```

So this is not a disjoint-union cardinality trick.

## 3. Exact rational kernel

For a Paley arc `i->j`, associate the root

```text
r_ij = e_i - e_j in Q^11.
```

Give all three lifted copies of the same base arc the same root vector.
Every lifted clause projects to one base cyclic triangle, hence its three root
vectors sum to zero.  Therefore the ten-dimensional `A_10` root space lies in the
rational kernel of the 165-variable lift.

Thus

```text
rank_Q(A_lift) <= 165-10 = 155.
```

The checker independently computes

```text
rank_F5(A_lift) = 155.
```

For an integer matrix,

```text
rank_F5(A_lift) <= rank_Q(A_lift),
```

so

```text
boxed:
rank_Q(A_lift)=155,
nullity_Q(A_lift)=10.
```

Hence the displayed copy-constant root space is the entire rational kernel.

## 4. Exact UNSAT certificate

Because the entire kernel is copy-constant, every centered rational solution has

```text
y_(arc,0) = y_(arc,1) = y_(arc,2)
```

for every base arc.

Therefore every Boolean Exact-One witness would satisfy

```text
x_(arc,0) = x_(arc,1) = x_(arc,2).
```

Apply the R5 E18 `KPROJ-EQUALITY` quotient and identify each triple of copies.
For each base triangle, its three lifted row equations collapse to the same base
row equation.  The quotient is exactly the 55-variable Paley base source.

But the base source is UNSAT by

```text
3 |S| = 55.
```

Therefore

```text
boxed:
A_lift is Exact-One UNSAT.
```

This proof is structural and does not depend on brute-force search or MILP.

## 5. Why every diagonal Schur-power level passes

Let `K` be the ten-dimensional lift kernel.  Because all kernel vectors are
copy-constant, every Schur power lies in the 55-dimensional space

```text
W = {vectors constant on the three copies of each base arc}.
```

The checker forms all pairwise Schur products of the root coordinate vectors on
the 55 base arc types and verifies

```text
rank_F5(K^(star 2)) = 55.
```

Since `dim W=55`, this proves over characteristic zero that

```text
boxed:
K^(star 2)=W.
```

There is also a kernel vector that is nonzero on every base arc: use potentials

```text
t_i=i,
```

so

```text
y_ij=i-j != 0.
```

Coordinatewise multiplication by this vector is an invertible diagonal map on
`W`.  Therefore, inductively,

```text
boxed:
K^(star r)=W  for every r>=2.
```

## 6. Firewall against the diagonal moment strategy

The alphabet relation

```text
y^2 = y + 2
```

implies for a true witness that every coordinate power is affine in `y`:

```text
y^r = a_r y + b_r 1.
```

A diagonal Schur-power hierarchy asks for compatible vectors in

```text
K, K^(star 2), K^(star 3), ...
```

satisfying these coordinate-power recurrences.

On the 165-variable lift, choose first moment

```text
m_1 = 0 in K.
```

For every `r>=2`, the recurrence produces a constant vector `m_r`, and all
constant vectors lie in

```text
W = K^(star r).
```

Thus every diagonal Schur-power level passes, including the unbounded union of
these diagonal tests.

Yet the instance is UNSAT.

Therefore:

```text
boxed:
NO DIAGONAL SCHUR-POWER HIERARCHY, BY ITSELF, IS A UNIVERSAL EXACT-ONE SOLVER.
```

What is missing is non-diagonal/global compatibility, not another coordinate
power.

## 7. Why R5 E18 survives the firewall

The R5 E18 kernel-projective branch sees immediately that the three copies of
each base arc have identical kernel rows:

```text
b_(arc,0)=b_(arc,1)=b_(arc,2).
```

Hence they are exact Boolean equality classes and may be quotient-identified.
The 165-variable connected source collapses to the 55-variable base source, where
the cardinality contradiction is immediate.

Thus this firewall kills the Schur hierarchy while validating the stronger
router order:

```text
kernel projective quotient
BEFORE
higher moment relaxations.
```

## 8. Router update

The algebraic branch should now be ordered as follows:

```text
K0  exact rational kernel
K1  zero kernel-row UNSAT
K2  forbidden projective-ratio UNSAT
K3  forced projective assignments
K4  equality-class quotient
K5  rerun all cheap exact terminals on the quotient
K6  bounded-interface/local-gauge quotient
K7  Schur-square or stronger moment obstructions as optional UNSAT terminals
```

Moment feasibility is never promoted to SAT without reconstruction of an actual
`{-1,2}` kernel vector.

## 9. New universal frontier

A true remaining hard core must now have, after repeated exact quotienting:

```text
all kernel rows nonzero,
no forbidden projective ratios,
no large equality classes,
no forced projective assignments,
large effective kernel,
no bounded-interface decomposition,
no source-aligned/clique obstruction,
no commuting or near-commuting structure,
and no actual {-1,2}-valued kernel vector in UNSAT cases.
```

The next useful theorem must therefore exploit relations among multiple distinct
kernel rows, not only one-coordinate powers.

A natural next object is the bounded-rank kernel-circuit CSP:

```text
minimal linear dependencies among rows b_i
+
finite alphabet {-1,2}
```

with exact propagation on low-rank circuits and quotienting of forced classes.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e19_paley_3lift_schur_hierarchy_firewall.py
```
