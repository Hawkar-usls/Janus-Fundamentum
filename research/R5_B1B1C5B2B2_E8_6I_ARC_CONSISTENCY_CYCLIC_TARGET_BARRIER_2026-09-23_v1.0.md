# R5 E8 6I — Arc-Consistency Cyclic-Target Barrier

Date: 2026-09-23

Authority: `PROVED_SOURCE_BOUND_ARC_CONSISTENCY_BARRIER__NO_D1_PROMOTION`

Parent gate:

`R5_E8_6I_THREE_SHEET_CONSISTENCY_TO_AFFINE_GATE_V1`

## 1. Source criterion

Dalmau--Oprsal, *Local consistency as a reduction between constraint satisfaction problems*,
Theorem 5.5:

```text
PCSP(A,A') <=_AC PCSP(B,B')
iff
there exists a minion homomorphism

omega(Pol(B,B')) -> Pol(A,A').
```

Their Definition 5.4 sets

```text
omega(M)^(X)
=
{(Y,f) : Y subseteq X, f in M^(Y)}
```

with minors

```text
(Z,f)^pi
=
(pi(Z), f^(pi|Z)).
```

The source explicitly notes that omega preserves precisely the balanced minor conditions
of the target minion. In particular, a cyclic identity is balanced because the cyclic
coordinate permutation is bijective.

## 2. Frozen source template

The frozen three-sheet Boolean identity is exact:

```text
OR3
=
M0 OR M1 OR M2.
```

When the union relation is interpreted extensionally on the visible Boolean prototype
coordinates, the source relational language is exactly the signed Boolean 3SAT language.

Already frozen source fact:

```text
Pol(Gamma_3SAT)
=
projection minion P.
```

Thus this theorem applies to the visible/extensional frozen three-sheet template.

It does not automatically apply to a richer instance-specific non-pp representation
whose polymorphism minion is genuinely different.

## 3. Cyclic obstruction lemma

Let B be a finite target template and assume Pol(B) contains an r-ary cyclic operation

```text
c(x1,...,xr)
=
c(x2,...,xr,x1)

r >= 2.
```

Let

```text
X = {1,...,r}
e = (X,c) in omega(Pol(B))^(X).
```

Let sigma be the cyclic shift permutation on X.

Because sigma(X)=X and c^sigma=c,

```text
e^sigma
=
e.
```

Suppose a minion homomorphism existed:

```text
xi :
omega(Pol(B))
->
P.
```

Naturality gives

```text
xi(e)^sigma
=
xi(e^sigma)
=
xi(e).
```

But every r-ary element of P is a projection p_i.

Under the full r-cycle sigma:

```text
p_i^sigma
=
p_{sigma(i)}
!=
p_i
```

for every i, since a full cycle of length r>=2 has no fixed coordinate.

Contradiction.

Therefore:

```text
NO MINION HOMOMORPHISM
omega(Pol(B))
->
P
```

whenever B has a nontrivial cyclic polymorphism.

By Dalmau--Oprsal Theorem 5.5:

```text
FULL SIGNED 3SAT
NOT <=_AC
CSP(B)
```

for every such finite target B.

## 4. Affine / XOR corollary

For Boolean XOR, the ternary operation

```text
m(x,y,z)=x XOR y XOR z
```

is cyclic.

More generally, for affine relations over a finite Abelian group of exponent e,
choose any prime r not dividing e. Multiplication by r is invertible on the group;
let r^{-1} denote the inverse endomorphism. Then

```text
c_r(x1,...,xr)
=
r^{-1}(x1+...+xr)
```

is idempotent, cyclic, and preserves every affine coset relation.

Hence:

```text
VISIBLE THREE-SHEET / SIGNED-OR3
<=_AC
FINITE AFFINE / XOR TARGET
=
IMPOSSIBLE.
```

This is algebraic and does not assume P != NP.

## 5. Taylor / Siggers scope

Finite CSP tractability is source-bound to nontrivial Taylor/Siggers/cyclic polymorphism
structure. In particular, standard finite affine, Mal'tsev, majority, bounded-width,
and few-subpowers tractable carriers possess nontrivial cyclic polymorphisms in the
relevant finite-core setting.

Therefore the same obstruction applies to any proposed arc-consistency target for which
a cyclic polymorphism is independently source-bound.

Do not overread this statement as a complexity-theoretic proof that no arbitrary
polynomial-time target can exist. The exact theorem is polymorphism/minion scoped.

## 6. Consequence for the compression-currency search

The first subgate is closed:

```text
ARC_CONSISTENCY REDUCTION
VISIBLE THREE-SHEET
->
XOR / FINITE AFFINE
=
BLOCKED
```

and, more generally,

```text
ARC_CONSISTENCY
VISIBLE THREE-SHEET
->
FIXED FINITE CYCLIC/TAYLOR TARGET
=
BLOCKED.
```

The remaining consistency-reduction search must therefore use at least one of:

1. genuine k-consistency with k>arc level;
2. a promise/infinite target whose relevant polymorphism minion evades this cyclic obstruction;
3. an instance-specific representation change before applying consistency reduction;
4. a non-cyclic global certificate architecture.

## 7. Next exact gate

Freeze:

```text
R5_E8_6I
FIXED_K_CONSISTENCY_CYCLIC_ESCAPE_GATE_V1
```

Question:

Does any fixed k>1 consistency reduction from the frozen three-sheet representation
to a polynomial-time target escape the cyclic-minor obstruction because the k-consistency
preprocessing changes the relevant source/minion interface in a way not captured by the
arc-level omega construction?

No PASS is claimed.

## 8. Ceiling

```text
ARC_TO_XOR
=
BLOCKED

ARC_TO_FINITE_AFFINE
=
BLOCKED

ARC_TO_SOURCE_BOUND_FINITE_CYCLIC_TARGET
=
BLOCKED

FIXED_K>ARC CONSISTENCY
=
OPEN

CLAP REPRESENTATION ROUTE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
