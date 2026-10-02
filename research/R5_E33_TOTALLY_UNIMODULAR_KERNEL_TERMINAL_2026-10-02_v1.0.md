# R5 E33 — Totally-Unimodular Kernel Terminal

Date: 2026-10-02

Status:
`EXACT_TU_KERNEL_POLYNOMIAL_TERMINAL__E23_INTEGER_FEASIBLE_PLUS_TU_IMPLIES_SAT__NONREGULAR_HARD_CORE_REQUIRED`

Scientific ceiling:

```text
THIS NOTE GIVES AN EXACT POLYNOMIAL TERMINAL FOR EVERY EXACT-ONE SOURCE WHOSE
RATIONAL KERNEL HAS AN ORTHOGONAL TOTALLY-UNIMODULAR REPRESENTATION.

IF
  ker_Q(A) = ker_Q(R)
FOR AN INTEGER TOTALLY-UNIMODULAR MATRIX R,
THEN
  A IS EXACT-ONE SAT
IFF
  R*1 IS DIVISIBLE BY 3 ROWWISE.

IN PARTICULAR, AFTER THE R5 E23 INTEGER-SATURATION TERMINAL HAS PASSED,
ANY SUCH TU-REPRESENTABLE KERNEL IS AUTOMATICALLY SAT.

THEREFORE A POST-E23 INTEGER-FEASIBLE UNSAT SURVIVOR CANNOT HAVE A
TU-REPRESENTABLE ORTHOGONAL ROW SPACE.

P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic Exact-One incidence matrix, so

```text
A 1 = 3 1.
```

As usual, Exact-One is equivalent to

```text
y = 3x-1,
y in ker_Q(A) intersect {-1,2}^n.
```

Suppose there is an integer matrix

```text
R in Z^{r x n}
```

such that

```text
boxed:
ker_Q(R)=ker_Q(A)
```

and `R` is totally unimodular.

Equivalently,

```text
row_Q(R)=row_Q(A).
```

We call such an `R` a **TU kernel certificate**.

The equality of rational kernels is directly verifiable by exact rank / row-space
checks once `R` is supplied.

## 2. Centered alphabet equation

A Boolean witness has

```text
y=3x-1,
x in {0,1}^n.
```

Because `ker_Q(R)=ker_Q(A)`, the condition `y in ker_Q(A)` is equivalent to

```text
R(3x-1)=0.
```

Therefore

```text
boxed:
R x = (R 1)/3.
```

This is the exact Boolean system induced by the TU representation.

## 3. Immediate modular necessity

Since `R` and `x` are integral,

```text
R x
```

is integral.

Hence every Exact-One witness requires

```text
boxed:
R 1 == 0 mod 3
```

coordinatewise.

If any row sum of `R` is not divisible by three, the instance is immediately
UNSAT.

## 4. Fractional point always exists when the right side is integral

Assume now

```text
R 1 == 0 mod 3.
```

Put

```text
b=(R 1)/3 in Z^r.
```

The fractional vector

```text
x_* = (1/3) 1
```

satisfies

```text
R x_* = b
```

and

```text
0 <= x_* <= 1.
```

Thus the polytope

```text
P={x in R^n : R x=b, 0<=x<=1}
```

is nonempty.

## 5. Total unimodularity forces a Boolean vertex

Because `R` is totally unimodular, adjoining signed identity rows preserves total
unimodularity.  Hence the constraint matrix for

```text
R x=b,
0<=x<=1
```

is totally unimodular.

The right-hand side is integral.

Therefore every vertex of `P` is integral.

Since `P` is nonempty and bounded, it has a vertex.  Any integral point in the unit
box belongs to

```text
{0,1}^n.
```

Hence there exists

```text
x in {0,1}^n
```

with

```text
R x=b.
```

For this `x`,

```text
R(3x-1)=0,
```

so

```text
3x-1 in ker_Q(R)=ker_Q(A).
```

Using `A 1=3 1`,

```text
A(3x-1)=0
=>
3 A x - 3 1=0
=>
A x=1.
```

Thus `x` is an Exact-One witness.

## 6. Theorem TU-KERNEL

Combining Sections 3--5:

```text
boxed:
If ker_Q(A)=ker_Q(R) for an integer totally-unimodular matrix R, then

A is Exact-One SAT
iff
R 1 == 0 mod 3 rowwise.
```

The decision step is polynomial once a TU representation is exposed and verified.
A Boolean witness can be reconstructed by solving any LP over

```text
R x=(R1)/3,
0<=x<=1
```

and returning an integral basic feasible solution.

No exponential kernel enumeration is required.

## 7. Relation to R5 E23 integer saturation

R5 E23 proves that `A x=1` has an integer solution if and only if every integral
vector in the saturated rational row space

```text
row_Q(A) cap Z^n
```

has coordinate sum divisible by three.

Every row `r` of the integer TU matrix `R` belongs to

```text
row_Q(R) cap Z^n
=
row_Q(A) cap Z^n.
```

Therefore, if the R5 E23 integer-feasibility gate passes, every row of `R` satisfies

```text
sum_j R_ij == 0 mod 3.
```

Equivalently,

```text
R 1 == 0 mod 3.
```

TU-KERNEL then gives an actual Boolean Exact-One witness.

Hence:

### Corollary E23+TU

```text
boxed:
INTEGER-FEASIBLE
+
TU-REPRESENTABLE ORTHOGONAL KERNEL SPACE
=>
EXACT-ONE SAT.
```

This sharply strengthens the post-E23 frontier.

## 8. Consequence for the hard core

Suppose a source is

```text
integer-feasible
```

but

```text
Exact-One UNSAT.
```

Then no integer totally-unimodular matrix `R` can satisfy

```text
ker_Q(R)=ker_Q(A).
```

Therefore every genuine post-E23 UNSAT survivor must have an orthogonal rational
space that is not TU-representable in this sense.

Informally:

```text
boxed:
THE INTEGER-FEASIBLE UNSAT HARD CORE IS FORCED OUTSIDE THE TU / REGULAR WORLD.
```

This statement is about existence of a TU representation of the rational orthogonal
space.  The note does not identify that existence with any stronger matroid notion
unless the corresponding representation theorem has separately been established.

## 9. Network and flow special case

Let `R` be an oriented vertex-edge incidence matrix of a directed graph.
Such matrices are totally unimodular.

Then

```text
ker_Q(R)
```

is the circulation / flow space.

TU-KERNEL says a centered Exact-One circulation exists exactly when

```text
R 1 == 0 mod 3.
```

Writing

```text
b=(R1)/3,
```

the Boolean witness is a `0/1` edge flow with node balance `b`.

This may be found by an ordinary unit-capacity feasible-flow computation.

Thus the whole graphic flow sector is polynomial.

## 10. Relation to the E32 root/tension terminal

R5 E32 treats the dual graphic language in which the kernel itself is a vertex
potential / tension space.

Whenever that tension space is supplied with a TU orthogonal cycle representation,
TU-KERNEL also applies.

E32 remains useful because it gives a much more explicit combinatorial algorithm:
mod-3 vertex propagation and direct witness reconstruction.

E33 provides the broader linear-programming envelope:

```text
root/tension,
flow/circulation,
network,
and any other exposed TU orthogonal representation
```

all collapse to polynomial Exact-One sectors.

## 11. Certificate / recognition caveat

The theorem is exact once a candidate integer matrix `R` with

```text
ker_Q(R)=ker_Q(A)
```

and certified total unimodularity is available.

The present note does not claim a new implementation of general TU-matrix
recognition or a universal procedure for discovering the best TU representation of
an arbitrary rational row space.

For known network / graphic / cographic constructions, the TU provenance is explicit
and easy to verify structurally.

A future router implementation may add a general TU-recognition layer separately.

## 12. Updated universal frontier

After E33, a true post-E23 hard core must satisfy all previous requirements and
also

```text
no exposed TU representation R with ker_Q(R)=ker_Q(A).
```

Thus the global-language hunt should now concentrate on genuinely non-TU kernel
languages.

The next natural targets are:

```text
1. bounded sums / low-rank perturbations of TU spaces;
2. near-regular representations;
3. exact decomposition across a small number of non-TU coordinates;
4. explicit non-TU high-width integer-feasible UNSAT carriers.
```

This suggests the next parameter:

```text
DISTANCE TO TU / REGULARITY DEFECT.
```

If deleting or fixing only `t` coordinates makes the orthogonal kernel space TU,
then branching over those `t` coordinates may give an FPT exact solver.

That is the next theorem target.

```text
P_VS_NP = OPEN.
```

Companion finite controls:

```text
experiments/r5_e33_tu_kernel_terminal.py
```
