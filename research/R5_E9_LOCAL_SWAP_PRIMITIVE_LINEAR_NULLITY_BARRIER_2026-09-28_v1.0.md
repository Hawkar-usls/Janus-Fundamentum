# R5 E9 — Local-Swap Primitive Linear-Nullity Barrier

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_PRIMITIVE_OMEGA_NULLITY_TWO_PERM_BARRIER__PRE_RKPR_SCOPED__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_LOCAL_SWAP_LINEAR_NULLITY_PHASE_FAIL_BASE_FAMILY_2026-09-26_v1.0.md`

Checker:
- `experiments/r5_e9_local_swap_primitive_linear_nullity_barrier.py`

Scientific ceiling:

```text
THE FROZEN LOCAL-SWAP CUBIC TWO-PERMUTATION FAMILY IS PRIMITIVE FOR EVERY m>=3
WHILE ITS RATIONAL NULLITY IS AT LEAST n/3.

THEREFORE LARGE / LINEAR RATIONAL NULLITY DOES NOT FORCE A NONTRIVIAL
PERMUTATION BLOCK SYSTEM, EVEN ON AN EXPLICIT CONNECTED SAT TWO-PERMUTATION
CARRIER.

THIS IS A PRE-RKPR STRUCTURAL BARRIER.  IT IS NOT CLAIMED TO SURVIVE THE
RATIONAL PROJECTIVE RATIO/PINNING PREPROCESSOR, AND THE FAMILY IS NOT A
LINEAR-HYPERGRAPH HOSTILE FAMILY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Family

Let

```text
Omega_m = Z_3 x Z_m,   m>=3.
```

Define

```text
P(r,a)=(r+1,a)
```

and start from

```text
Q(0,a)=(2,a+1),
Q(1,a)=(0,a),
Q(2,a)=(1,a).
```

Put

```text
u=(0,0),
v=(2,2).
```

Swap only the two images `Q(u)=(2,1)` and `Q(v)=(1,2)` to obtain `Q'`:

```text
Q'(u)=(1,2),
Q'(v)=(2,1),
Q'=Q elsewhere.
```

The parent theorem proves for

```text
A'_m = I+P+Q'
```

that the source is connected and SAT, `P,Q'` do not commute, the Z3 phase fails,
and

```text
nu_Q(A'_m) >= m = n/3.
```

The new question is whether this high nullity forces a nontrivial block system
for the permutation group

```text
Gamma_m=<P,Q'>.
```

It does not.

## 2. The key permutation T=PQ'

Set

```text
T = P Q'.
```

Direct substitution gives the single cycle

```text
C = ((0,0), (2,2), (0,1), (0,2), ..., (0,m-1))
```

of length

```text
|C|=m+1.
```

Every remaining point is fixed by `T`.  Thus the fixed set

```text
F=Omega_m\C
```

has

```text
|F|=2m-1.
```

Since `Q'=P^{-1}T`,

```text
Gamma_m=<P,T>.
```

## 3. A proper block meets every P-fibre at most once

The `P`-orbits are the `m` fibres

```text
F_a={(0,a),(1,a),(2,a)}.
```

Let `B` be a block for the transitive action of `Gamma_m`.
Suppose a proper block contains two points of one `P`-fibre.  Those two points
are related by `P` or `P^2`, so

```text
B intersect P^k(B) != empty
```

for `k=1` or `2`.  The block property forces

```text
B=P^k(B).
```

Because `P` has order three, `B` is `P`-invariant and therefore contains the
entire fibre.  In particular it contains `(1,a)`, which is fixed by `T`.
Hence

```text
B intersect T(B) != empty,
```

so `B=T(B)` as well.  Therefore `B` is invariant under `<P,T>=Gamma_m`.
Transitivity then gives `B=Omega_m`, contradicting properness.

Thus every proper block satisfies

```text
|B intersect F_a| <= 1 for every a,
```

and consequently

```text
|B| <= m.
```

## 4. T separates the long cycle from its fixed points

If a block `B` contains a fixed point `f in F`, then

```text
f in B intersect T(B),
```

so `T(B)=B`.

If that same block also contained a point of the long cycle `C`, T-invariance
would force it to contain the whole orbit `C`, giving

```text
|B| >= m+1,
```

contrary to `|B|<=m`.

Therefore no proper block mixes the two T-orbit types:

```text
B subset C
or
B subset F.
```

All blocks in a transitive block system have the same size `b`.  Since the
blocks partition both `C` and `F`,

```text
b | (m+1),
b | (2m-1).
```

Hence

```text
b | gcd(m+1,2m-1)=gcd(m+1,3).
```

Thus a nontrivial proper block could only have

```text
b=3.
```

## 5. The size-three possibility is impossible

Assume `b=3` and let `B_*` be the block containing the unique non-layer-zero
point of the long cycle,

```text
s=(2,2) in C.
```

Because `B_* subset C`, its other two points are of the form

```text
(0,a), (0,b).
```

Apply `P`.  Then

```text
P(s)=(0,2) in C,
P(0,a)=(1,a) in F,
P(0,b)=(1,b) in F.
```

So the block `P(B_*)` mixes one point of `C` with two fixed points of `T`.
Section 4 proves that no proper block can do this.  Contradiction.

Therefore `b=3` is impossible.

### Theorem LSP-1

For every `m>=3`,

```text
Gamma_m=<P,Q'>
```

is primitive on `Omega_m`.

Combined with the parent nullity theorem,

```text
n=3m,
nu_Q(I+P+Q') >= m = n/3,
Gamma_m primitive.
```

Thus primitive action is compatible with arbitrary-size linear rational
nullity.

## 6. Exact scope correction

This theorem kills the shortcut

```text
high rational nullity
=> nontrivial permutation block system
=> recursive block decomposition.
```

on the general cubic two-permutation carrier.

It does **not** establish a post-RKPR hostile family.  Exact finite inspection
of the local-swap kernels shows large SAT-compatible `-1/2` projective classes,
so the newer rational projective ratio/pinning preprocessor acts before any
post-RKPR navigation theorem may cite this family.

It also does not claim that the row hypergraph of this family is linear: the
construction contains repeated/overlapping row supports.  Therefore it must not
be cited as a hostile family for a theorem whose premise explicitly requires
linear cubic incidence.

The admissible conclusion is exactly:

```text
PRIMITIVITY ALONE DOES NOT CONTROL RATIONAL NULLITY.
```

## 7. Algorithmic consequence

A universal P=NP route based on `A=I+P+Q` cannot use permutation primitivity as
the missing dichotomy by itself.  Any surviving decomposition theorem must use
additional post-RKPR/source structure, or the algorithm must attack the global
affine/cycle-syndrome coupling directly.

The current live universal objects remain:

```text
post-RKPR boundary direction / quotient,
and equivalently
matching-normalized affine parity intersect cycle-independence
with global endpoint syndrome.
```

## 8. Ceiling

```text
LOCAL-SWAP FAMILY CONNECTED + SAT
= PARENT-PROVED

RATIONAL NULLITY
>= n/3

T=PQ'
= ONE (m+1)-CYCLE + (2m-1) FIXED POINTS

<P,Q'> PRIMITIVE FOR EVERY m>=3
= PROVED

HIGH NULLITY => IMPIMITIVE
= FALSIFIED ON GENERAL CUBIC TWO-PERM CARRIER

POST-RKPR PRIMITIVE HIGH-NULLITY SURVIVOR
= NOT PROVED

LINEAR-HYPERGRAPH VERSION
= NOT PROVED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
