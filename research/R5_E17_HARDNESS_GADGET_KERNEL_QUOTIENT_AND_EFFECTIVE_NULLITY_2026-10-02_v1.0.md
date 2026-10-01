# R5 E17 — Hardness-Gadget Kernel Quotient and Effective Nullity

Date: 2026-10-02

Status:
`EXACT_KERNEL_DECOMPOSITION_OF_R5_E12_REDUCTION__RAW_NULLITY_FIREWALL__EFFECTIVE_PORT_KERNEL_IDENTIFIED`

Scientific ceiling:

```text
THIS NOTE SHOWS THAT LARGE RAW NULLITY CAN BE PURELY LOCAL.
FOR THE R5 E12 RXC3 HARDNESS REDUCTION,

  nullity(target) = 2q + 2 nullity(source),

AND THE 2q TERM CONSISTS OF GADGET-LOCAL GAUGE MODES INVISIBLE ON THE PORTS.

QUOTIENTING THOSE MODES RECOVERS TWO COPIES OF THE ORIGINAL RXC3 KERNEL.
THIS IS A PREPROCESSING/STRUCTURAL RESULT, NOT A POLYNOMIAL SOLUTION OF RXC3.
P_VS_NP = OPEN.
```

## 1. Orientation

Use the natural exact-cover orientation of the R5 E12 target incidence matrix:

```text
rows    = target elements,
columns = target triples,
```

so a Boolean vector on target triples solves

```text
B x = 1.
```

For centered coordinates

```text
y = 3x - 1,
```

we have

```text
B y = 0,
y in {-1,2}^{17q}.
```

The matrix `B` is square, cubic and linear.

## 2. One gadget: port columns

For a source set

```text
C_j={x_1,x_2,x_3},
```

R5 E12 creates 17 target triples

```text
L_1,...,L_5,
L'_1,...,L'_5,
D_1,...,D_7.
```

Among these, the six triples touching global source-element rows are

```text
L_1,L_2,L_3,
L'_1,L'_2,L'_3.
```

Call their centered coordinates

```text
ell_1,ell_2,ell_3,
ell'_1,ell'_2,ell'_3.
```

The remaining 11 triple coordinates are purely internal to the gadget.

There are 15 internal element rows (`z,z',t`).

## 3. Exact local elimination

Let `J_int` be the `15 x 17` incidence matrix formed by the internal element rows of one gadget.
Exact rational elimination gives

```text
rank_Q(J_int)=13,
nullity_Q(J_int)=4.
```

Project `ker(J_int)` onto the six port coordinates.  The projected space has dimension two, and its exact defining equations are

```text
ell_1 = ell_2 = ell_3,
ell'_1 = ell'_2 = ell'_3.
```

Write the two common values as

```text
a_j = ell_1=ell_2=ell_3,
b_j = ell'_1=ell'_2=ell'_3.
```

For every chosen pair `(a_j,b_j)` there remain exactly two local kernel degrees of freedom supported in the internal gadget coordinates.

Therefore one gadget contributes:

```text
2 visible port dimensions (a_j,b_j),
2 invisible local gauge dimensions.
```

## 4. Global boundary equations recover the source kernel

Let `R` be the natural RXC3 source incidence matrix:

```text
rows    = source elements,
columns = source 3-sets C_j.
```

Every original source element belongs to exactly three source sets.
In the target, its global row sees exactly the corresponding three `L` port columns.
Therefore the unprimed boundary equations are precisely

```text
R a = 0.
```

The primed copy gives independently

```text
R b = 0.
```

Thus the visible global port kernel is

```text
ker(R) direct_sum ker(R).
```

Its dimension is

```text
2 d_source,
```

where

```text
d_source = nullity_Q(R).
```

## 5. Exact target-nullity formula

The `q` gadgets have disjoint internal coordinates, each contributing two independent zero-port gauge modes.
Hence the invisible local subspace has dimension

```text
2q.
```

Adding the two source-kernel copies gives

```text
boxed:
nullity_Q(B) = 2q + 2 nullity_Q(R).
```

This is an exact formula for the full R5 E12 reduction family.

Equivalently, after quotienting by the direct sum of all gadget-local zero-port modes,

```text
ker(B) / K_local
cong
ker(R) direct_sum ker(R).
```

This quotient is the appropriate global/effective kernel for this reduction.

## 6. Centered Boolean semantics recovers RXC3 exactly

Suppose now

```text
y in ker(B) intersect {-1,2}^{17q}.
```

The local elimination forces

```text
ell_1=ell_2=ell_3=a_j
```

for every source set `C_j`, with

```text
a_j in {-1,2}.
```

For an original source element, exactly three source sets are incident, and its target row equation is

```text
a_{j_1}+a_{j_2}+a_{j_3}=0.
```

Three values from `{-1,2}` sum to zero iff exactly one is `2` and the other two are `-1`.

Therefore

```text
s_j=(a_j+1)/3 in {0,1}
```

selects exactly one incident source set at every source element:

```text
R s = 1.
```

So the unprimed port projection of every target Boolean kernel vector is an RXC3 exact cover.

The primed ports independently recover a second RXC3 exact cover.

Conversely, the eight-state local gadget theorem from R5 E12 supplies a target Boolean extension whenever the source exact-cover states are chosen consistently.

Thus the original NP-hard Boolean content lives in the quotient/port coordinates, while the `2q` raw gauge dimensions are not global combinatorial freedom.

## 7. Frozen 6-element hard benchmark

Use the R5 E12 checker fixture

```text
q=6,
C_i={i,i+1,i+3} mod 6.
```

Its natural source incidence matrix is

```text
[1 0 0 1 0 1]
[1 1 0 0 1 0]
[0 1 1 0 0 1]
[1 0 1 1 0 0]
[0 1 0 1 1 0]
[0 0 1 0 1 1]
```

with

```text
det(R)=-9,
rank_Q(R)=6,
nullity_Q(R)=0.
```

The fixture has no exact cover.

The E12 target has

```text
n=17q=102,
rank_Q(B)=90,
nullity_Q(B)=12.
```

The formula predicts

```text
2q + 2 d_source = 12 + 0 = 12,
```

so **every one of the twelve target kernel dimensions is a gadget-local gauge mode**.

Yet

```text
ker(B) intersect {-1,2}^{102} = empty,
```

because the source fixture is RXC3 UNSAT.

This is a strong warning against treating raw nullity as a proxy for useful Boolean freedom.

## 8. Connectivity / relaxation benchmark

For this same `102 x 102` target:

```text
Levi graph edge connectivity   = 3,
Levi graph vertex connectivity = 3.
```

The associated point graph in the natural exact-cover orientation is `K4`-free, so the universal fractional point `x=(1/3)1` satisfies every clique inequality; the clique-LP terminal therefore remains feasible while the Boolean instance is UNSAT.

A sampled set of 3-perfect-matching factorizations also gives very large distance to the commuting centralizer for the resulting `I+P+Q` normal forms.  This is useful empirical stress evidence only: it is **not** a proof that the minimum over all possible factorizations is large.

Hence this target is a valuable survivor benchmark for future router branches.

## 9. Effective-nullity lesson

R5 E16 showed that large nullity and large distance-to-commuting can coexist because of weakly glued global blocks.
R5 E17 shows a different failure mode:

```text
large raw nullity can also be generated by many independent local gauge modes.
```

A future structural parameter should therefore distinguish

```text
raw kernel dimension
```

from

```text
global / quotient / port kernel dimension after exact local-module elimination.
```

For a decomposition into modules with bounded interfaces, one can in principle:

```text
1. compute each module's internal zero-boundary kernel;
2. quotient it out;
3. retain only the finite/rational boundary relation;
4. solve the reduced global instance.
```

This is exact but does not automatically yield polynomial time when the reduced global interaction remains NP-hard, as it does here: the quotient is the original RXC3 source itself.

## 10. New hard-core requirement

A genuinely new universal theorem must now avoid being fooled by both E16 and E17.
The meaningful survivor should have:

```text
large effective/global kernel dimension after local quotient,
no cheap low-adhesion decomposition,
no clique-LP obstruction,
no known tractable algebraic normal form,
and still no {-1,2}-valued kernel vector in the UNSAT case.
```

Finding or ruling out such families is now a sharper target than merely maximizing raw `-3` multiplicity.

P_VS_NP = OPEN.
