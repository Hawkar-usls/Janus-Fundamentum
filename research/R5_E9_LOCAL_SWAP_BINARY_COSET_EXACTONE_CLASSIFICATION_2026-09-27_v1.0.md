# R5 E9 — Local-Swap Binary Coset and Complete Exact-One Classification

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_FAMILY_CLASSIFICATION__POLY_CONSTRUCTIVE_POSITIVE_ISLAND__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_local_swap_binary_coset_exactone_classification.py`

Parents:
- `R5_E9_LOCAL_SWAP_LINEAR_NULLITY_PHASE_FAIL_BASE_FAMILY_2026-09-26_v1.0.md`
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS SOLVES THE EXPLICIT LOCAL-SWAP BASE FAMILY.
IT DOES NOT SOLVE ARBITRARY CUBIC EXACT-ONE.
IT DOES NOT PROMOTE E8-D1.
P_VS_NP = OPEN.
```

## 1. Coordinates

Use the local-swap family

```text
Omega_m = Z_3 x Z_m,
m>=3,
A'_m = I + P + Q'.
```

Write the Boolean assignment coordinates as

```text
A_a = x_(0,a),
B_a = x_(1,a),
C_a = x_(2,a).
```

The unchanged `r=1` rows are

```text
A_a + B_a + C_a = 1.
```

For `r=2`, every row except `a=2` is the same unordered triple.  The swapped
row at `(2,2)` is

```text
C_2 + A_2 + C_1 = 1.
```

For `r=0`, every row except `a=0` is

```text
A_a + B_a + C_(a+1) = 1,
```

while the swapped row at `(0,0)` is

```text
A_0 + B_0 + B_2 = 1.
```

All indices in the `C_(a+1)` term are modulo `m`.

## 2. Complete F2 parity-coset parametrization

First interpret the row equations over `F_2`.

For every `a!=0`, XOR the `r=0` row with the `r=1` row at the same column:

```text
C_a + C_(a+1) = 0.
```

For

```text
a=1,2,...,m-1
```

these equalities form the chain

```text
C_1=C_2=...=C_(m-1)=C_0.
```

Hence there is one global bit

```text
c in F_2
```

such that

```text
C_a=c
```

for every `a`.

Now use the special `r=2,a=2` equation:

```text
C_2 + A_2 + C_1 = 1.
```

Since `C_1=C_2=c`, over `F_2` this reduces to

```text
A_2=1.
```

The ordinary column equation then gives

```text
B_a = 1 XOR A_a XOR c
```

for every `a`.

At `a=2`, this gives

```text
B_2=c.
```

The remaining swapped `r=0,a=0` equation is

```text
A_0+B_0+B_2=1,
```

which is automatically satisfied because

```text
A_0+B_0+c=1
```

is exactly the ordinary `r=1,a=0` parity equation and `B_2=c`.

Therefore the entire affine parity coset is parameterized by

```text
c free,
A_a free for every a!=2,
A_2=1,
C_a=c,
B_a=1 XOR A_a XOR c.
```

There are exactly

```text
1 + (m-1) = m
```

free bits.

### Theorem LSB-1

```text
rank_F2(A'_m)=2m,
dim_F2 ker(A'_m)=m=n/3,
|{x:A'_m x=1 mod2}|=2^m.
```

This is an arbitrary-`m` theorem; the checker verifies the rank law on
`m=3,...,20` and independently exhausts the ambient Boolean cube for `m=3,4,5`.

## 3. Exact integer equations kill the c=1 half

Now impose Exact-One over the integers rather than parity only.

The same subtraction of the ordinary `r=0` and `r=1` equations gives

```text
C_a=C_(a+1)
```

for every `a!=0`, so again

```text
C_a=c
```

for a single Boolean `c`.

But the special integer row is now

```text
C_2 + A_2 + C_1 = 1,
```

hence

```text
A_2 + 2c = 1.
```

Since `A_2,c` are Boolean, the only solution is

```text
c=0,
A_2=1.
```

Then every ordinary column row gives

```text
A_a+B_a=1,
```

so

```text
B_a=1-A_a.
```

The swapped `r=0,a=0` row becomes

```text
A_0+B_0+B_2=1.
```

Here `A_0+B_0=1` and `B_2=0` because `A_2=1`, so it is automatic.

Thus every choice of the remaining `m-1` bits

```text
A_a, a!=2
```

gives an Exact-One witness, and there are no others.

### Theorem LSB-2 — complete Exact-One classification

For every `m>=3`, the Exact-One witnesses of the local-swap family are exactly

```text
C_a=0                  for every a,
A_2=1,
B_2=0,
B_a=1-A_a              for every a,
A_a arbitrary          for a!=2.
```

Therefore

```text
#ExactOne(A'_m)=2^(m-1).
```

## 4. Linear-time direct solver

A canonical witness is obtained without search:

```text
A_2=1,
A_a=0 for a!=2,
C_a=0 for all a,
B_2=0,
B_a=1 for a!=2.
```

This is exactly the previously recorded witness set

```text
S_m = {(0,2)} union {(1,a):a!=2}.
```

The new theorem explains that witness as one point in a full affine-size family
of `2^(m-1)` exact solutions.

Construction and verification are `O(n)`.

## 5. Why the binary nullity does not itself solve the family

The new affine-coset normal form gives

```text
dim_F2 ker(A'_m)=m=n/3,
```

so the generic low-binary-nullity algorithm would still cost

```text
2^(n/3) poly(n).
```

The family is easy for a stronger structural reason: the local swap collapses
the parity system to one global `C` bit plus independent complementary
`A/B` pairs, and the exact integer row forces that global bit to zero.

Thus this is a useful example where

```text
large nullity != hard.
```

That distinction matters for the universal solver search.

## 6. Consequence for the phase-FAIL stress family

The local-swap family remains valuable as a structural negative control:

```text
connected,
noncommuting P,Q',
Z3 phase FAIL,
large rational nullity,
large binary nullity.
```

But as a decision/search problem on the explicit base family it is now fully
classified and directly solvable.

Therefore those structural diagnostics cannot by themselves be treated as
hardness evidence.

The correct interpretation is:

```text
PHASE FAIL + NONCOMMUTING + LARGE NULLITY
DO NOT PREVENT A SIMPLE GLOBAL COORDINATE CLASSIFICATION.
```

This is a positive lesson for the universal route: search for a polynomially
synthesizable global coordinate/quotient before assuming that a large kernel is
an adversary.

## 7. Covers

The existing fixed-girth cover theorem lifts any base Exact-One witness
fiber-constantly.  Therefore every JANUS-generated cover of this base family
comes with a polynomially constructible satisfying witness from the known
cover projection and the canonical base witness above.

This does **not** claim that an arbitrary unlabeled input graph is polynomially
recognizable as one of those covers, nor that the complete `2^(m-1)` base
classification lifts unchanged.

It only means that the generated high-girth positive-control lineage is never a
mystery SAT/UNSAT instance to JANUS: its construction provenance carries a
witness.

## 8. Updated scientific frontier

This result removes the explicit local-swap base family from consideration as a
candidate decision-hard survivor.

The universal frontier remains arbitrary cubic Exact-One / arbitrary 3-CNF,
where the affine-coset form is

```text
A x = 1 (mod 2),
minimize |x|,
Exact-One iff optimum=n/3.
```

The next useful positive mechanism is therefore not another statistic such as
nullity alone.  It is a **global quotient/coordinate theorem** that can be
synthesized on arbitrary noncommuting survivors and reduces the minimum-weight
coset problem without exponential kernel enumeration.

Freeze:

```text
R5_E9_GLOBAL_BINARY_COSET_QUOTIENT_SYNTHESIS_GATE_V1
```

## 9. Ceiling

```text
LOCAL-SWAP GF2 NULLITY
= m=n/3

LOCAL-SWAP PARITY COSET
= COMPLETE m-BIT PARAMETRIZATION

LOCAL-SWAP EXACT-ONE SOLUTIONS
= EXACTLY 2^(m-1)

DIRECT WITNESS
= O(n)

LOCAL-SWAP BASE FAMILY AS DECISION-HARD CORE
= CLOSED

ARBITRARY CUBIC AFFINE-COSET MINWEIGHT
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
