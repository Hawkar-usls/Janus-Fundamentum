# R5 E9 — Local-Swap Primitive Linear-Nullity SAT Family

Date: 2026-09-27

Status:
`JANUS_DERIVED_ARBITRARY_SIZE_PRIMITIVITY_THEOREM__ASYMPTOTIC_BLOCK_SYSTEM_ROUTE_FALSIFIED`

Parent:
- `R5_E9_LOCAL_SWAP_LINEAR_NULLITY_PHASE_FAIL_BASE_FAMILY_2026-09-26_v1.0.md`
- `R5_E9_PRIMITIVE_NULLITY2_BLOCK_SYSTEM_FALSIFIER_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_local_swap_primitive_linear_nullity.py`

Scientific ceiling:

```text
THIS FALSIFIES A STRUCTURAL SHORTCUT.
IT DOES NOT SUPPLY A UNIVERSAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen family

For `m>=3` let

```text
Omega_m = Z_3 x Z_m.
```

Define

```text
P(r,a) = (r+1,a)
```

and the original permutation

```text
Q(0,a) = (2,a+1),
Q(1,a) = (0,a),
Q(2,a) = (1,a).
```

Let

```text
u=(0,0),
v=(2,2).
```

The old images are

```text
Q(u)=(2,1),
Q(v)=(1,2).
```

Define `Q'` by swapping exactly these two images and leaving every other image unchanged.

The parent theorem already proves for

```text
A'_m = I+P+Q'
```

that the carrier is connected and cubic Positive Exact-One, has an explicit Exact-One witness, satisfies `PQ' != Q'P`, fails the Z3 phase condition, and obeys

```text
nullity_Q(A'_m) >= m = n/3,
where n=3m.
```

The only new question here is the permutation block structure.

## 2. A long commutator cycle

Use the convention

```text
c = [P,Q'] = P Q' P^{-1} (Q')^{-1}.
```

A direct substitution in the definitions gives one nontrivial orbit

```text
C = (
 (0,0),
 (2,2),
 (2,1),
 (1,2),
 (2,0),
 (2,m-1),(2,m-2),...,(2,3),
 (0,1),(0,2),...,(0,m-1)
)
```

with the obvious omission of an empty `(2,m-1),...,(2,3)` range when `m=3`.

Thus

```text
|C| = 2m+1.
```

Every remaining point is fixed by `c`; the fixed set is exactly

```text
F = {(1,a): a != 2},
|F| = m-1.
```

Hence `c` has cycle type

```text
(2m+1)(1)^(m-1).
```

In particular

```text
|C|=2m+1 > 3m/2 = n/2.
```

## 3. Block lemma for a long cycle plus fixed points

Let `G=<P,Q'>`.  The parent connectedness proof is exactly transitivity of this action on `Omega_m`.

Assume for contradiction that `G` has a nontrivial block `B` of size `b`.  Since the action is transitive,

```text
1 < b <= n/2
and
b divides n=3m.
```

### Lemma 1

No block that meets the long orbit `C` can also meet the fixed set `F`.

### Proof

Suppose `x in B intersect C` and `f in B intersect F`.
Because `f` is fixed by every power of `c`, every translate `c^j(B)` contains `f`.  Two blocks in the same block system are either disjoint or equal, so

```text
c^j(B)=B for every j.
```

Since `B` contains `x` and is `c`-invariant, it contains the entire `c`-orbit `C`.  Hence

```text
b >= |C| = 2m+1 > n/2,
```

contradicting properness. QED.

Therefore every block meeting `C` lies wholly in `C`.  Since blocks partition the transitive point set, `C` is a disjoint union of whole blocks.  Consequently

```text
b divides |C|=2m+1.
```

Together with `b | 3m`,

```text
gcd(3m,2m+1) | 3
```

because

```text
3(2m+1)-2(3m)=3.
```

Thus a nontrivial block is possible only when

```text
b=3
and
3 | (2m+1),
```

i.e. only when

```text
m = 1 mod 3.
```

## 4. The exceptional arithmetic case also collapses

Assume now

```text
m=3k+1.
```

Then

```text
L=|C|=2m+1=3(2k+1).
```

Consider the unique block `B` containing `(0,0)`.  Restricted to the regular cyclic action of `<c>` on `C`, a block of size three must be a coset of the unique subgroup of order three.  Hence

```text
B = {
 (0,0),
 c^(L/3)(0,0),
 c^(2L/3)(0,0)
}.
```

Put

```text
d=L/3=2k+1.
```

From the explicit cycle in Section 2:

- if `k=1` (`m=4`), `c^d(0,0)=(1,2)`;
- if `k>=2`, `c^d(0,0)` lies in the `(2,a)` portion of the long cycle.

In either case

```text
P(c^d(0,0)) in C.
```

But

```text
P(0,0)=(1,0) in F.
```

Therefore the image block `P(B)` meets both `C` and `F`, contradicting Lemma 1.

Hence the arithmetic exception is impossible as well.

## 5. Main theorem

For every `m>=3`,

```text
G_m=<P,Q'>
```

is transitive and primitive on `3m` points.

Combining with the parent theorem gives the arbitrary-size family

```text
connected,
linear/cubic Positive Exact-One,
SAT with explicit witness,
primitive permutation action,
PQ' != Q'P,
Z3 phase FAIL,
nullity_Q(I+P+Q') >= m = n/3.
```

Thus

```text
boxed(
primitive action
DOES NOT imply
O(log n) rational nullity
)
```

even on an explicit connected satisfiable linear-cubic family.

This strictly strengthens the earlier finite `12_3` nullity-two falsifier.

## 6. Consequence for the endgame

The proposed structural dichotomy

```text
primitive <p,q>
=> low nullity
=> polynomial kernel router,

imprimitive
=> recurse on block systems
```

is false and must not be reopened.

Any group-action route must use an invariant stronger than permutation primitivity and raw kernel multiplicity.  In particular, `S_n/A_n`-scale mixing of the generated action is compatible with linear rational nullity after the local swap construction; the solver cannot equate group primitivity with algebraic rigidity of `I+P+Q`.

The active universal routes remain exact global semantic compression of the affine-cycle form or a polynomial semantic lift of structural reductions.

## 7. Verdict

```text
LOCAL-SWAP FAMILY TRANSITIVE
= PREVIOUSLY PROVED

COMMUTATOR CYCLE TYPE
= (2m+1)(1)^(m-1)

NONTRIVIAL BLOCK SIZE
= FORCED TO 3, THEN CONTRADICTED

<P,Q'> PRIMITIVE FOR EVERY m>=3
= PROVED

RATIONAL NULLITY
>= n/3

EXACT-ONE
= SAT

PRIMITIVE => O(log n) NULLITY
= FALSIFIED ASYMPTOTICALLY

PRIMITIVE/IMPRIMITIVE UNIVERSAL ROUTER
= CLOSED AS STATED

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
