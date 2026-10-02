# R5 E31 — Tripartite High-q / High-Width Firewall

Date: 2026-10-02

Status:
`EXACT_SQUARE_CUBIC_LINEAR_HIGH_PROJECTIVE_DIVERSITY_HIGH_TREEWIDTH_SAT_FIREWALL__VERTEX_POTENTIAL_KERNEL_NORMAL_FORM`

Scientific ceiling:

```text
THIS NOTE CONSTRUCTS AN EXPLICIT INFINITE SQUARE+CUBIC+LINEAR FAMILY WITH

  n = 3m^2,
  nullity_Q = 3m-1 = Theta(sqrt(n)),
  q = n,
  projective-quotient treewidth = Omega(m) = Omega(sqrt(n)).

SO LARGE EFFECTIVE NULLITY, MAXIMAL PROJECTIVE DIVERSITY, AND GROWING
PROJECTIVE-QUOTIENT WIDTH CAN ALL OCCUR SIMULTANEOUSLY ON THE TARGET CARRIER.

NEVERTHELESS THE WHOLE FAMILY IS EXACT-ONE SAT BY A GLOBAL THREE-PARTITE
POTENTIAL NORMAL FORM.

THEREFORE HIGH-q + HIGH-WIDTH IS NOT BY ITSELF A HARDNESS CERTIFICATE.
P_VS_NP = OPEN.
```

## 1. Construction

Fix an integer

```text
m >= 4.
```

Let

```text
A = B = C = Z_m.
```

Create three variable families

```text
X_ab,  a,b in Z_m,
Y_bc,  b,c in Z_m,
Z_ca,  c,a in Z_m.
```

Thus the total number of variables is

```text
n = 3m^2.
```

For every

```text
a,b in Z_m,
s in {0,1,2},
```

put

```text
c = a+b+s mod m
```

and add the Exact-One row

```text
X_ab + Y_b,c + Z_c,a = 1.
```

There are exactly

```text
3m^2 = n
```

rows.

## 2. Square, cubic and linear

Every row contains exactly three variables.

For fixed `X_ab`, the three values `s=0,1,2` give exactly three incident rows.

For fixed `Y_bc`, and for each `s in {0,1,2}`, there is a unique

```text
a = c-b-s mod m,
```

so `Y_bc` also occurs in exactly three rows.

Similarly every `Z_ca` occurs in exactly three rows.

Hence the incidence matrix is square and cubic.

For linearity, suppose two rows share two variables. Any two of

```text
X_ab,
Y_bc,
Z_ca
```

determine the same triple `(a,b,c)`. Since

```text
s = c-a-b mod m
```

and the allowed residues `0,1,2` are distinct for `m>=4`, that triple determines a
unique source row. Therefore distinct rows cannot share two variables.

Thus

```text
boxed:
A_m is square+cubic+linear.
```

## 3. Immediate SAT witness

Set

```text
X_ab = 0,
Y_bc = 0,
Z_ca = 1
```

for all indices.

Every row then contains exactly one selected variable. Therefore

```text
boxed:
A_m is Exact-One SAT for every m>=4.
```

In centered coordinates

```text
y=3x-1,
```

this witness is simply

```text
X=-1,
Y=-1,
Z=2.
```

## 4. Exact rational kernel

Write a centered kernel vector as

```text
U_ab,
V_bc,
W_ca.
```

The kernel equations are

```text
U_ab + V_b,c + W_c,a = 0,

c=a+b+s,
s=0,1,2.
```

For fixed `a,b`, compare the equations for `s=0` and `s=1`.  At

```text
c=a+b
```

we obtain

```text
Delta_c V_b,c + Delta_c W_c,a = 0.
```

Compare `s=1` and `s=2`; at

```text
c=a+b+1
```

we obtain the same difference identity.

Now fix arbitrary `b,c`.

Using the first comparison with

```text
a=c-b
```

gives

```text
Delta V_b,c + Delta W_c,c-b = 0.
```

Using the second comparison with

```text
a=c-b-1
```

gives

```text
Delta V_b,c + Delta W_c,c-b-1 = 0.
```

Therefore

```text
Delta W_c,a = Delta W_c,a-1
```

for every `a,c`, so for fixed `c` the `c`-difference of `W` is independent of `a`.
Consequently the `c`-difference of `V` is independent of `b`.

Hence there are functions

```text
beta_b,
gamma_c,
alpha_a
```

such that

```text
V_bc = beta_b - gamma_c,
W_ca = gamma_c - alpha_a.
```

Substituting back gives

```text
U_ab = alpha_a - beta_b.
```

Thus every rational kernel vector has the vertex-potential form

```text
boxed:
U_ab = alpha_a-beta_b,
V_bc = beta_b-gamma_c,
W_ca = gamma_c-alpha_a.
```

Conversely every vector of this form satisfies every row equation telescopically.

There are `3m` potential parameters and adding the same constant to all
`alpha,beta,gamma` changes no edge difference. Therefore

```text
boxed:
nullity_Q(A_m)=3m-1.
```

Since

```text
n=3m^2,
```

we have

```text
nullity_Q(A_m)=Theta(sqrt(n)).
```

The companion checker independently verifies for `m=4,...,8` that rank modulo
`1009` is exactly

```text
n-(3m-1),
```

which matches the symbolic theorem.

## 5. Maximal kernel-projective diversity

In the potential model each coordinate functional is a root vector between two
vertices of different parts:

```text
X_ab : alpha_a-beta_b,
Y_bc : beta_b-gamma_c,
Z_ca : gamma_c-alpha_a.
```

Two nonzero root functionals

```text
e_u-e_v
```

and

```text
e_r-e_s
```

are rationally proportional only when they use the same unordered endpoint pair.
The construction contains exactly one oriented variable for each such cross-part
pair and never its opposite copy.

Therefore no two distinct kernel coordinate rows are projectively proportional.
There are no zero rows either.

Hence after R5 E18 KPROJ preprocessing,

```text
boxed:
q(A_m)=n=3m^2.
```

This is maximal projective diversity.

## 6. The projective quotient is the original CSP

Because every coordinate is its own free projective class, the R5 E28 projective
quotient introduces no compression:

```text
Q(A_m)=A_m.
```

Its interaction graph has one vertex for every `X`, `Y`, `Z` variable and a triangle
for every Exact-One source row.

The family therefore directly tests whether high projective diversity can coexist
with genuinely growing quotient width.

## 7. Explicit grid subdivision

Take the `X` variables

```text
X_(2i,2j)
```

with

```text
0 <= 2i < m,
0 <= 2j < m.
```

There are

```text
t = ceil(m/2)
```

chosen coordinates in each direction.

### Horizontal edges

For every adjacent pair

```text
X_(a,b), X_(a+2,b)
```

use the intermediate variable

```text
Y_(b,a+b+2).
```

Indeed

```text
X_(a,b)
```

shares the `s=2` source row with this `Y`, while

```text
X_(a+2,b)
```

shares the `s=0` source row with the same `Y`.

Thus the interaction graph contains the path

```text
X_(a,b) -- Y_(b,a+b+2) -- X_(a+2,b).
```

### Vertical edges

Likewise

```text
X_(a,b) -- Z_(a+b+2,a) -- X_(a,b+2).
```

The intermediate `Y` and `Z` vertices used by these paths are pairwise distinct.
They are also disjoint from all chosen `X` grid vertices.

Hence the interaction graph contains a subdivision of the

```text
t x t
```

square grid.

Treewidth is monotone under taking subgraphs and subdivisions preserve the grid
minor. Since the `t x t` grid has treewidth `t`,

```text
boxed:
tw(Q(A_m)) >= ceil(m/2).
```

Equivalently,

```text
boxed:
tw(Q(A_m)) = Omega(m) = Omega(sqrt(n)).
```

Therefore every exact elimination order has width at least `Omega(sqrt(n))`.
The R5 E28 width branch is not polynomial on this family.

## 8. Why this is an important firewall

Before E31 the known controls separated the two high-description axes:

```text
E25 torus:
  q=O(1).

E16 / E27 ring:
  q=Theta(n),
  but quotient width=2.
```

E31 shows both can be large simultaneously:

```text
nullity_Q = Theta(sqrt(n)),
q = n,
quotient treewidth = Omega(sqrt(n)).
```

Yet the instance remains trivial SAT through the global part-type assignment

```text
X=0,
Y=0,
Z=1.
```

So the implication

```text
high q + high quotient width => hard core
```

is false.

Large description complexity can still hide a very short global normal form.

## 9. Relation to KLOC

Because the whole instance has a global centered alphabet witness

```text
X=-1,
Y=-1,
Z=2,
```

every coordinate projection of the rational kernel contains the corresponding
alphabet projection.

Therefore

```text
boxed:
KLOC-s passes for every s, including the full radius n.
```

This is stronger than merely surviving KLOC-3 or KLOC-4.

Thus E31 is a clean SAT-side firewall against interpreting local consistency,
projective diversity, or quotient width as hardness evidence.

## 10. Interaction with E29 and E30

The family has growing rational nullity, so by R5 E29 it cannot belong to the
connected commuting sector.

It also has a growing base parameter `m`, so it lies outside the fixed-base uniform
cyclic-lift regime excluded by R5 E30.

Hence it occupies a genuinely new region of the router landscape:

```text
connected,
noncommuting,
large effective nullity,
q=n,
high projective-quotient width,
KLOC-clean,
SAT by a compact global type normal form.
```

## 11. Updated universal frontier

After E31, a true unresolved hard core must not only have

```text
large effective nullity,
large q,
large quotient width,
high adhesion,
no KPROJ/KLOC obstruction,
integer feasibility,
```

but must also avoid a compact global polarity/type/potential normal form like the
one above.

The next useful parameter is therefore not merely graph width.  It is the complexity
of the **global quotient language** after all exact algebraic reductions.

A sharper next target is:

```text
GLOBAL-LANGUAGE COMPRESSION DICHOTOMY

For every projectively reduced integer-feasible carrier with large quotient width,
either
  (A) expose a polynomial-size global type/potential normal form,
  (B) expose an exact polynomial UNSAT certificate,
  (C) decompose/quotient further,
  or
  (D) produce an explicit high-width instance whose quotient language remains
      genuinely unconstrained by all known global normal forms.
```

Branch (D) is now the correct post-E31 firewall target.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e31_tripartite_highq_highwidth_firewall.py
```
