# R5 E9 — Exact F3 constant-plus-gradient kernel and affine chart for the Paley-orbit family

Date: 2026-10-01

Status:
`JANUS_EXACT_F3_KERNEL_AND_AFFINE_CHART_FAMILY_THEOREM__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY_ORBIT_GRADIENT_KERNEL_INFINITE_POST_RKPR_FAMILY_2026-09-29_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_AF3_CHARACTER_SPLIT_AND_K4_MOTIF_FALSIFIER_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_paley_orbit_exact_f3_constant_gradient_kernel.py`

Scientific ceiling:

```text
This theorem gives the exact mod-3 kernel and the complete affine chart for the
already frozen Paley-orbit control family.  It is not a universal SAT solver.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen family

Let `q>3` be a prime with `q=3 mod 8`, let

```text
r=-2 mod q,
O=<r> subset QR(q),
L=|O|=ord_q(-2).
```

Variables are `X(t,s)` with `t in Z_q`, `s in O`, and the homogeneous source equation attached to `(t,s)` is

```text
y_s(t)+y_s(t+s)+y_{rs}(t+2s)=0.
```

There are `n=qL` variables and `n` rows.

The rational theorem already frozen in the parent artifact proves that over characteristic zero the kernel is the `(q-1)`-dimensional gradient space.  Characteristic three has one additional mode because the all-ones edge signal becomes homogeneous.

## 2. Main theorem

Over `F3`,

```text
dim ker_F3(A)=q
```

and exactly

```text
ker_F3(A)
 = <1> direct-sum Grad(Z_q)
 = { c + p(t+s)-p(t) : c in F3, p:Z_q->F3 }.
```

The gradient space has dimension `q-1`; the constant mode is independent of it.

## 3. Fourier proof over an algebraic closure of F3

Because `q!=3`, the polynomial `X^q-1` is separable in characteristic three.  Translation by `t` is therefore diagonalizable after extending scalars from `F3` to an algebraic closure.  Rank and nullity of the source matrix do not change under this field extension.

Fix one additive frequency `chi`, a `q`-th root character, and write

```text
y_s(t)=a_s chi(t).
```

The source equation becomes

```text
(1+chi(s)) a_s + chi(2s) a_{rs}=0,
```

hence

```text
a_{rs} = -a_s (1+chi(s))/chi(2s).
```

The denominator never vanishes.  Since `O` is one multiplicative orbit under `r`, one amplitude determines all amplitudes in that frequency.  Thus every frequency contributes kernel dimension at most one.

### Zero frequency

For `chi=1`, characteristic three gives

```text
2 a_s + a_{rs}=0,
```

so, because `-2=1` in `F3`,

```text
a_{rs}=a_s.
```

This is consistent around every orbit and gives exactly one zero-frequency mode: the all-ones edge signal.

### Nonzero frequencies

For a nontrivial additive character, define

```text
a_s=chi(s)-1.
```

Since `q` is prime and `s!=0`, this amplitude is nonzero.  Put `z=chi(s)`.  Using `rs=-2s`,

```text
(1+z)(z-1) + z^2 (z^(-2)-1)
= (z^2-1)+(1-z^2)
=0.
```

Thus every nonzero frequency contributes at least one dimension, and the recurrence gives at most one.  There are `q-1` nonzero frequencies.

Therefore the total nullity over the algebraic closure, and hence over `F3`, is

```text
1+(q-1)=q.
```

## 4. Identification with constant plus gradients

For every potential `p:Z_q->F3`,

```text
y_s(t)=p(t+s)-p(t)
```

annihilates each source row by telescoping around the directed triangle.  The fixed-`s` arcs form a directed `q`-cycle, so the gradient map has kernel exactly the constant vertex potentials and hence image dimension `q-1`.

The all-ones edge vector is also in `ker_F3(A)` because every row has three ones.

It is not a gradient: summing a gradient around a fixed-`s` directed `q`-cycle gives zero, while summing the all-ones signal gives

```text
q != 0 mod 3
```

because `q>3` is prime.  Hence the constant mode is independent of the gradient space.

The resulting `q` dimensions exhaust the kernel dimensions proved by Fourier decomposition.

## 5. Exact affine consistency split

The inhomogeneous equation

```text
A z = 1
```

is consistent if and only if

```text
3 divides L.
```

Necessity follows from cubic column degree:

```text
1^T A = 0 over F3,
```

so consistency would imply `qL=0 mod 3`, and `q!=3`.

For sufficiency, if `L=3m`, define on the orbit

```text
r0(r^k)=k mod 3.
```

Then for every source row with differences `s,s,rs`,

```text
2 r0(s)+r0(rs)=2k+(k+1)=1 mod 3.
```

The definition closes around the orbit because `3|L`.

Combining this particular solution with the exact kernel theorem gives the full affine solution space:

```text
{ z : A z=1 }
 = { r0 + c + p(t+s)-p(t) : c in F3, p:Z_q->F3 }.
```

There are exactly `3^q` affine solutions when the branch is consistent.

## 6. Coordinate-hyperplane gain chart

For a coordinate belonging to the canonical oriented arc `u->v` with difference `s=v-u in O`, the forbidden coordinate-zero equation is

```text
r0(s)+c+p(v)-p(u)=0.
```

Equivalently,

```text
p(v)-p(u)=t_s-c,
t_s=-r0(s).
```

Thus the affine-hyperplane cover problem for every consistent Paley-orbit member is *exactly* a three-slice `Z3` gain-graph avoidance problem on the `q` potential vertices.  No hidden mod-3 kernel directions are omitted.

This validates source-specific gain obstructions such as the Paley19 gain-K4 cover and later q=331 critical-graph controls against the full affine solution space, not merely against a chosen chart.

## 7. Exact finite replay controls

The checker reconstructs the frozen source and performs sparse Gaussian elimination over `F3` on representative members:

```text
q=11:  n=55,   nullity_F3=11
q=19:  n=171,  nullity_F3=19
q=43:  n=301,  nullity_F3=43
q=67:  n=2211, nullity_F3=67
q=331: n=4965, nullity_F3=331
```

It also verifies the constant and gradient vectors directly and verifies the character particular solution on the consistent controls.

The finite replay is a regression guard.  The family theorem is the symbolic Fourier proof above.

## 8. Consequence for the live constructive search

The Paley branch now has an exact deterministic split:

```text
3 does not divide ord_q(-2)
    -> A z=1 is linearly inconsistent; immediate polynomial UNSAT terminal.

3 divides ord_q(-2)
    -> exact q-dimensional affine chart r0 + constant + gradient;
       attack the resulting Z3 gain-cover problem structurally.
```

The live positive target is therefore no longer “guess the kernel representation”.  It is:

```text
Given the exact character gain graph of a consistent member,
construct in polynomial time a small/full cover certificate,
or identify a new quotient that avoids enumerating 3^q potentials.
```

## 9. Ceiling

```text
ker_F3(A)                                  = CONSTANT + GRADIENT
nullity_F3(A)                              = q
A z=1 consistent                           iff 3 | ord_q(-2)
consistent affine solution count           = 3^q
full gain-chart representation             = PROVED
universal gain obstruction family          = OPEN
universal polynomial SAT solver            = NOT PROVED
E8_D1                                      = EMPTY
P_VS_NP                                    = OPEN
```
