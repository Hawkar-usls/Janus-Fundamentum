# R5 E9 — UNSAT Prime Tower Augmented-Regularity Collapse

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_HOSTILE_FAMILY_COLLAPSE_TO_NEW_POLY_TERMINAL__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`
- `research/R5_E9_AUGMENTED_REGULAR_MATROID_SYNDROME_POLY_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_unsat_prime_tower_augmented_regularity.py`

Scientific ceiling:

```text
THIS PROVES THAT THE ENTIRE ARBITRARY-SIZE TWO-EDGE UNSAT PRIME TOWER
LIES INSIDE THE NEW AUGMENTED-REGULAR-MATROID POLYNOMIAL TERMINAL.

THE TOWER REMAINS A VALID HOSTILE CONTROL AGAINST RAW NULLITY,
SEPARATORS, BALANCEDNESS, AND LOCAL ODD-CYCLE ROUTES, BUT IT IS NO
LONGER A SURVIVOR AGAINST THE AUGMENTED-REGULAR-MATROID ROUTER.

THIS DOES NOT PROVE THAT EVERY SOURCE INSTANCE IS AUGMENTED-REGULAR.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen tower

Let `A_0` be the frozen `15_3` UNSAT seed from the parent prime-tower theorem.
The first two-edge twist uses

```text
F_0={(0,12),(2,9)}
```

and produces `A_1` of order 30.  The recursive tower for `t>=1` uses a
distinguished nonincident pair `F_t`; at level one it is

```text
F_1={(0,5),(1,1)},
```

and every next `F_{t+1}` is the pair of upper-right crossed copies of `F_t`.
The parent theorem already proves for every level:

```text
connected / linear / cubic / square,
UNSAT,
unbalanced,
no nontrivial <=3-edge cut,
rational nullity Omega(n),
SAT equivalence to the previous level under the exact left-kernel criterion.
```

The present theorem studies a different object: the binary augmented syndrome
matroid

```text
M_t^+ = M_F2([A_t | 1]).
```

## 2. Exact F2 base kernel at level one

Direct F2 elimination on the explicit `A_1` gives

```text
nu_F2(A_1)=2.
```

One kernel basis has supports

```text
k_1^0 = {0,3,7,9,11,13,14,17,21,22,24,27},
k_1^1 = {2,6,7,9,12,15,18,22,24,26,28,29}.
```

Both basis vectors are zero at the two distinguished columns of `F_1`:

```text
column 5 = 0 on ker_F2(A_1),
column 1 = 0 on ker_F2(A_1).
```

Since the displayed vectors form a basis, this is a statement about the full
kernel, not only about chosen generators.

## 3. Kernel doubling under every recursive lift

Let `A=A_t`, let `E` mark the two incidences in `F_t`, and form over the
integers

```text
Ahat = [[A-E, E],
        [E, A-E]].
```

Over `F2`, subtraction equals addition, so for a vector `(u,v)` the lifted
kernel equations are

```text
A u + E(u+v)=0,
A v + E(u+v)=0.
```

Adding them gives

```text
A(u+v)=0.
```

Assume the two distinguished column coordinates vanish on all of `ker_F2(A)`.
Then `s=u+v in ker(A)` implies

```text
E s = 0.
```

The two lifted equations therefore reduce exactly to

```text
A u=0,
A v=0.
```

Hence

\[
\boxed{
\ker_{\mathbb F_2}(A_{t+1})
=
\ker_{\mathbb F_2}(A_t)\oplus\ker_{\mathbb F_2}(A_t).
}
\]

Conversely every pair `(u,v)` of old kernel vectors satisfies the lifted
equations, so the equality is exact.

The next distinguished columns are crossed copies of the old distinguished
columns.  Their coordinates on `(u,v)` are old distinguished coordinates of
`v`, hence are again zero.  Thus the zero-coordinate hypothesis is inherited.

Starting from Section 2,

\[
\boxed{\nu_{\mathbb F_2}(A_t)=2^t\qquad(t\ge1).}
\]

More strongly, a kernel basis of `A_t` is the block-direct sum of
`2^{t-1}` disjoint copies of the two-dimensional basis of `A_1`.

## 4. Canonical dual representation of the augmented matroid

Every cubic source row has odd weight three, so over `F2`

```text
A_t 1 = 1.
```

Consequently the nullspace of the augmented matrix `[A_t|1]` is

```text
{(z,0): z in ker(A_t)}
  direct_sum
span{(1,1)}.
```

Use the block-direct-sum kernel basis from Section 3 and let the final row be

```text
g=(1,...,1,1).
```

These rows form a binary representation `H_t` of the dual matroid `(M_t^+)^*`.
Let

```text
m=2^(t-1).
```

Name the two kernel coordinates in block `s` by `a_s,b_s`, and name the global
row `r`.

For every original column, all kernel evaluations vanish outside one block.
Inside that block the two evaluations are an arbitrary binary pair.  The global
row has value one.  Therefore every original column of `H_t` has support equal
to one of

```text
{r},
{r,a_s},
{r,b_s},
{r,a_s,b_s}
```

for one block `s`.  The distinguished syndrome column `1` itself has support
exactly `{r}`.

No other support type occurs.

## 5. Network-matrix realization

Construct a tree `T_m` as follows.

- one central tree edge `r` joins vertices `L` and `R`;
- for each block `s`, a leaf edge `a_s` is attached at `L`;
- for each block `s`, a leaf edge `b_s` is attached at `R`.

Orient the tree arbitrarily.  In a directed tree, the signed incidence vector
of the unique path between two vertices is a column of a network matrix after
adding the corresponding non-tree arc.

For block `s`, the four possible supports above are exactly the four tree paths

```text
L -- R                         -> {r},
leaf(a_s) -- R                 -> {a_s,r},
L -- leaf(b_s)                 -> {r,b_s},
leaf(a_s) -- leaf(b_s)         -> {a_s,r,b_s}.
```

Choose the usual +/- signs according to the tree orientation.  The resulting
signed real matrix is a submatrix of a network matrix, hence is totally
unimodular, and reducing it modulo two gives exactly `H_t` (parallel repeated
columns cause no problem).

Therefore `H_t` represents a regular matroid.  Regularity is closed under
duality, so

\[
\boxed{M_t^+=M_{\mathbb F_2}([A_t\mid\mathbf1])\text{ is regular for every }t\ge1.}
\]

## 6. Polynomial collapse of the entire hostile tower

The augmented-regular-matroid syndrome theorem now applies at every level.
Thus `mu(A_t)`, the minimum Hamming weight of a solution of

```text
A_t x = 1 mod 2,
```

is deterministically polynomial-time computable by minimum-weight circuit
optimization through the distinguished syndrome element.

Since every `A_t` is cubic,

```text
Exact-One SAT iff mu(A_t)=n_t/3.
```

The parent theorem proves every tower level is UNSAT.  Therefore the regular
matroid optimizer returns

```text
mu(A_t) > n_t/3
```

and certifies rejection in polynomial time for every `t`.

This is important scientifically: the same family that has

```text
rational nullity >= n/30+1,
no nontrivial <=3-edge cut,
unbalanced strong odd cycles,
```

is nevertheless easy in the new augmented-matroid currency.

## 7. Consequence for the active frontier

The arbitrary-size UNSAT prime tower is no longer an admissible counterexample
to a proposed solver that first tests augmented regularity.  It remains useful
against all earlier currencies, but future hostile residuals must satisfy

```text
M_F2([A|1]) NONREGULAR
```

in addition to whichever previous hard-core promises are being tested.

By Tutte's binary excluded-minor theorem, such a residual contains an `F7` or
`F7*` minor in its augmented syndrome matroid.

The next possible structural attack is therefore not raw nullity growth but
source-aware handling of these forbidden minors.  Merely locating an `F7/F7*`
minor is not progress unless the operation preserves the distinguished syndrome
semantics and decreases a polynomially bounded global potential without
branching exponentially.

## 8. Ceiling

```text
F2 KERNEL OF PRIME TOWER
nu_F2(A_t)=2^t
= PROVED

DISTINGUISHED KERNEL-ZERO COORDINATES
= INVARIANT

AUGMENTED DUAL SUPPORT NORMAL FORM
= ONE GLOBAL ROW + DISJOINT TWO-ROW BLOCKS
= PROVED

NETWORK-MATRIX / TU SIGNING
= EXPLICIT

AUGMENTED MATROID M([A_t|1])
= REGULAR FOR ALL t>=1

ENTIRE ARBITRARY-SIZE UNSAT PRIME TOWER
= POLYNOMIALLY DECIDED BY ARM-2

NONREGULAR SOURCE-GENERATED RESIDUAL
= OPEN

F7/F7* SEMANTIC CONTRACTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
