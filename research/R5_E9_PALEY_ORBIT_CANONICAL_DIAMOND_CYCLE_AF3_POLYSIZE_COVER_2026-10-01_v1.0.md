# R5 E9 — Paley-orbit canonical diamond-cycle AF3 polynomial-size cover

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY_ORBIT_AF3_POLYSIZE_COVER_FAMILY_THEOREM__REPRESENTATION_FRONTIER_CLOSED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PALEY_ORBIT_EXACT_F3_CONSTANT_GRADIENT_KERNEL_AFFINE_CHART_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY5419_DIAMOND_MACRO_BFS_EXACT_ORDER10_4CRITICAL_COVER_2026-10-01_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_GRADIENT_KERNEL_INFINITE_POST_RKPR_FAMILY_2026-09-29_v1.0.md`

Scientific ceiling:

```text
This theorem closes the AF3 coordinate-hyperplane cover problem for the already
frozen Paley-orbit family by an explicit polynomial-size constructor.

It is NOT a new universal SAT solver: the same Paley family already had a
polynomial UNSAT terminal through its rational gradient/cycle certificate.
The new contribution is a constructive AF3 reconciliation theorem which avoids
enumerating the 3^q affine potentials and exposes a transferable diamond-macro
mechanism.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen family and exact AF3 split

Let `q>3` be prime with

```text
q = 3 mod 8,
r = -2 mod q,
O = <r>,
L = ord_q(-2).
```

The exact F3 parent theorem proves

```text
ker_F3(A) = <1> direct-sum Grad(Z_q)
```

and

```text
A z = 1 is consistent iff 3 | L.
```

If `3` does not divide `L`, ordinary Gaussian elimination over `F3` is already a
polynomial terminal.  Hence only the consistent branch remains.

Assume from now on

```text
L = 3m.
```

With

```text
r0(r^k)=k mod 3,
```

every affine solution is exactly

```text
z = r0 + c + grad(p),
c in F3,
p:Z_q -> F3.
```

For traversal by a supported difference define

```text
phi_c(r^k)  = -k-c mod 3,
phi_c(-r^k) =  k+c mod 3.
```

Then the coordinate-zero hyperplane attached to a supported edge traversal
`x -> x+d` is

```text
p(x+d)-p(x)=phi_c(d).
```

## 2. Canonical cubic-root identity

Put

```text
zeta = r^m.
```

Since `r` has order `3m`, `zeta` has exact order three.  Therefore

```text
zeta^3 = 1,
zeta != 1,
1 + zeta + zeta^2 = 0 mod q.
```

Choose

```text
a = 1,
b = -zeta.
```

Then

```text
a in O,
b in -O,
b-a = -zeta-1 = zeta^2 in O.
```

So the four vertices

```text
x,
x+a,
x+b,
x+a+b
```

support the five edges of a `K4-e` diamond.

For every slice `c`,

```text
phi_c(a)       = -c,
phi_c(b)       = m+c,
phi_c(b-a)     = -2m-c.
```

Hence

```text
phi_c(b)-phi_c(a)
= m+2c
= -2m-c
= phi_c(b-a) mod 3,
```

because the difference is `3m+3c`.

Thus this same five-coordinate diamond is balanced in all three slices.

## 3. Exact diamond implication

Let

```text
A0 = a+b = 1-zeta,
mu = phi_c(a)+phi_c(b) = m mod 3.
```

Both `A0` and `mu` are independent of `c`, and `A0 != 0` because `zeta != 1`.

Switch the diamond by

```text
g(x)=0,
g(x+a)=phi_c(a),
g(x+b)=phi_c(b),
g(x+A0)=mu.
```

If a potential `p` avoids all five coordinate-zero hyperplanes of the diamond,
then `p-g` is a proper three-colouring of `K4-e`.  In every proper
three-colouring of a diamond the two nonadjacent degree-two tips have the same
colour.  Therefore avoidance forces

```text
p(x+A0)-p(x)=mu.
```

This implication can also be checked directly on all `3^4` local potentials;
the regression does so for every finite control.

The key point is that the selected five source coordinates do NOT depend on
`c`, while the induced macro relation `(A0,mu)` also does not depend on `c`.

## 4. Case mu != 0: one common q-diamond cycle covers all slices

Suppose

```text
m mod 3 != 0.
```

Translate the canonical diamond to the roots

```text
x_j = j A0,
j=0,...,q-1.
```

Because `q` is prime and `A0 != 0`, the `q` roots are all distinct and

```text
x_q = q A0 = 0.
```

If one affine solution avoided every selected coordinate hyperplane, the q
diamond implications would give

```text
p(x_{j+1})-p(x_j)=mu
```

for every `j`.  Summing around the cycle yields

```text
0 = q mu in F3.
```

But `q != 3` is prime, so `q mod 3` is nonzero, and `mu` is nonzero by this
case assumption.  Contradiction.

Therefore the union of the q canonical diamonds covers the complete affine
solution space simultaneously for all three values of `c`.

It contains at most

```text
5q
```

distinct coordinate hyperplanes; overlaps can only reduce the size.

## 5. Case mu = 0: equality transport plus three closing coordinates

Suppose

```text
m = 0 mod 3.
```

The same q canonical diamonds force

```text
p(x+A0)=p(x)
```

at every root.  Since the nonzero step `A0` generates the additive prime group
`Z_q`, avoidance of all q diamonds forces `p` to be constant on all q
vertices.

For each `c in F3`, choose an exponent

```text
e_c = -c mod 3
```

with `0 <= e_c < L`, and put

```text
d_c = r^(e_c) in O.
```

Then

```text
phi_c(d_c) = -e_c-c = 0 mod 3.
```

Add the three source coordinates on the arcs

```text
0 -> d_0,
0 -> d_1,
0 -> d_2.
```

In slice `c`, constancy forces

```text
p(d_c)-p(0)=0,
```

while avoiding that coordinate-zero hyperplane requires the difference to be
nonzero.  Contradiction.

Thus the q canonical diamonds plus at most three closing coordinates cover the
complete affine space, using at most

```text
5q+3
```

distinct coordinate hyperplanes.

## 6. Family theorem

### PALEY-ORBIT-CANONICAL-DIAMOND-AF3-COVER

For every frozen Paley-orbit source with prime `q>3`, `q=3 mod 8` and
`L=ord_q(-2)`:

```text
if 3 does not divide L:
    A z=1 over F3 is inconsistent and is rejected by polynomial linear algebra;

if L=3m:
    the full 3^q affine solution space admits an explicit coordinate-hyperplane
    cover of size at most 5q+3, constructible in O(q) field operations once the
    orbit data are known.
```

For `m mod 3 != 0`, at most `5q` coordinates suffice.  For `m mod 3 = 0`, at
most `5q+3` suffice.

The constructor never enumerates affine potentials, assignments, critical graph
catalogues, or subsets of source coordinates.

## 7. Complexity accounting

The source itself has

```text
n = qL
```

coordinates.  Computing the `-2` orbit takes `O(L)` modular multiplications.
The cover construction then emits at most `5q+3 <= 5n+3` coordinate references.
All exponents and residues have `O(log q)` bits.

Hence construction and verification are polynomial in the explicit source
encoding size.

This is a genuine constructive terminal for the AF3 representation of this
family, not merely a polynomial certificate verifier with an unspecified
certificate-discovery step.

## 8. Anti-loop reconciliation

The rational parent theorem had already proved every member of this Paley-orbit
family UNSAT by a gradient-potential cycle argument.  Therefore this theorem
must not be promoted as a new overall solver for that family.

Its new content is instead:

```text
EXACT F3 CONSTANT+GRADIENT CHART
+
CANONICAL CHARACTER DIAMOND
+
O(q) AFFINE HYPERPLANE COVER CONSTRUCTOR.
```

This closes the live Paley AF3 gain-cover frontier and supplies a mechanism to
test on non-Paley prime/lift towers.

## 9. Next transfer gate

Freeze

```text
R5_E9_AF3_DIAMOND_MACRO_TRANSFER_TO_NONPALEY_PRIME_TOWERS_V1
```

Next test the same implication calculus against the existing prime SAT/UNSAT
lift towers.  The transferable sufficient condition is:

1. an exact F3 gain chart for the residual affine kernel;
2. a polynomially recognizable `K4-e` whose five inequalities force one affine
   endpoint equation;
3. a polynomial-size macro closure reaching either a nonzero cycle gain or a
   source coordinate with the forbidden endpoint value.

A failure must be frozen as an exact counterexample; no universal promotion is
allowed from the Paley family alone.

## 10. Ceiling

```text
Paley AF3 inconsistent branch                  = POLYNOMIAL LINEAR TERMINAL
Paley AF3 consistent branch                    = EXPLICIT <=5q+3 COVER
Paley AF3 cover construction                    = POLYNOMIAL
Paley affine-potential enumeration              = ELIMINATED
Paley family overall UNSAT terminal             = ALREADY KNOWN FROM RATIONAL GRADIENT
transfer to non-Paley prime towers              = OPEN
universal polynomial SAT solver                 = NOT PROVED
E8_D1                                           = EMPTY
P_VS_NP                                         = OPEN
```
