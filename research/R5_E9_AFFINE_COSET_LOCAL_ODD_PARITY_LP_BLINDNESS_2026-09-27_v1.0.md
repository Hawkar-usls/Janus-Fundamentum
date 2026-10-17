# R5 E9 — Affine-Coset Local Odd-Parity LP Blindness

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_RELAXATION_BARRIER_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_affine_coset_local_parity_lp_blindness.py`

Parents:
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_BOUNDED_SUPPORT_AFFINE_KERNEL_DESCENT_BARRIER_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS BLOCKS THE BASIC LOCAL PARITY LP ONLY.
IT DOES NOT BLOCK STRONGER GLOBAL CUTS / HIERARCHIES / NONLOCAL QUOTIENTS.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Local odd-parity relation

For one 3-variable parity row

```text
x_a + x_b + x_c = 1 (mod 2),
```

the allowed Boolean triples are

```text
ODD_3 = {100,010,001,111}.
```

The standard local-codeword / parity LP replaces each Boolean row relation by
its convex hull

```text
conv(ODD_3).
```

For a whole 3-uniform incidence matrix, intersect these local parity polytopes
on the shared variable coordinates and minimize

```text
sum_v x_v.
```

This is the most direct LP relaxation of the affine-coset minimum-weight normal
form.

## 2. Universal one-third pseudocodeword

The local vector

```text
(1/3,1/3,1/3)
```

lies in `conv(ODD_3)` because

```text
(1/3,1/3,1/3)
=
(1/3)100 + (1/3)010 + (1/3)001.
```

Therefore for every 3-uniform instance, regardless of satisfiability, the global
uniform vector

```text
x* = (1/3) 1
```

is feasible in the intersection of all local odd-parity polytopes.

For a `d`-regular instance on `n` variables and `m` hyperedges,

```text
d n = 3m.
```

Every point of `conv(ODD_3)` has local coordinate sum at least one because all
four Boolean vertices have weight at least one.  Summing this inequality over
all hyperedges gives

```text
d sum_v x_v >= m.
```

Hence

```text
sum_v x_v >= m/d = n/3.
```

The uniform one-third vector attains equality.

### Theorem LPL-1

For every 3-uniform `d`-regular incidence instance,

```text
minimum local-parity-LP weight = n/3.
```

This value is independent of whether an Exact-One witness exists.

## 3. Consequence for the affine-coset representation

The companion exact theorem says

```text
Exact-One SAT
iff
minimum INTEGER parity-coset weight = n/3.
```

LPL-1 says the basic local parity LP always reports exactly the target lower
bound `n/3`.

Therefore the LP cannot distinguish

```text
integer optimum = n/3
```

from

```text
integer optimum > n/3.
```

The missing information is entirely global integrality / pseudocodeword
exclusion.

So the representation change

```text
Exact-One -> affine coset + minweight
```

does not become a solver merely by applying the local parity polytope.

## 4. Strong connected UNSAT control with 3 | n

The checker freezes the connected linear cubic instance

```text
(3,6,7)
(2,3,4)
(0,3,8)
(2,5,8)
(0,4,7)
(1,4,8)
(1,5,7)
(1,2,6)
(0,5,6)
```

on nine variables.

It has all of the following properties:

```text
3-uniform = YES
3-regular = YES
linear = YES
connected incidence graph = YES
n = 9, so n mod 3 = 0
Exact-One solution = NONE
```

Exhaustive offline validation further finds that the only integral odd-parity
solution is

```text
111111111,
```

of weight nine.

Thus

```text
integer parity optimum = 9,
local parity LP optimum = 3.
```

This removes the trivial objection that the LP failure is caused only by the
`n mod 3` filter.

The exhaustive enumeration is `OFFLINE_FALSIFIER_ONLY`; the arbitrary-size LP
theorem is Section 2.

## 5. Positive control

On the satisfiable `AFFINE_3X3` cubic-linear control, the checker finds

```text
integer parity optimum = 3,
Exact-One solution count = 3,
local parity LP optimum = 3.
```

Hence the same LP optimum occurs on both the SAT and UNSAT controls.

## 6. Coding-theoretic prior-art binding

LP decoding of LDPC / linear codes uses the intersection of local codeword
polytopes, often called the fundamental polytope.  Fractional pseudocodewords
are a standard limitation of this relaxation.

Relevant source-bound context includes Feldman-style LP decoding and subsequent
LDPC work.  For example, the literature defines the fundamental polytope as the
intersection of local single-parity-check codeword polytopes and distinguishes
it from the exact codeword polytope.

The JANUS result here is only the specialized exact observation that for the
3-uniform regular all-ones-syndrome carrier, the uniform `1/3` pseudocodeword
forces the optimum to equal `n/3` on every instance.

No novelty claim is made for LP decoding or pseudocodewords in general.

## 7. R5/R6 consequence

A nonlocal affine-coset route cannot use

```text
solve the local parity LP;
if optimum = n/3 then declare SAT.
```

That rule is unsound.

Any LP/polyhedral route must add globally valid inequalities or a stronger
representation capable of separating the connected UNSAT9 control from the SAT
control while keeping total construction and optimization polynomial.

A successful cut family must be synthesized without solving the original
Exact-One instance as a hidden separation oracle.

## 8. Updated active gate

Freeze:

```text
R5_E9_GLOBAL_AFFINE_COSET_CUT_OR_NONLOCAL_QUOTIENT_GATE_V1
```

Allowed PASS forms:

1. polynomially constructible global valid inequalities whose relaxation is
   exact on every cubic Exact-One instance;
2. a polynomial separation oracle with proof that it does not encode SAT/Exact
   Cover search internally;
3. a nonpolyhedral quotient/decomposition with strict polynomial progress and
   exact witness reconstruction;
4. a direct large-support kernel descent theorem.

Mandatory controls:

- connected linear cubic `UNSAT9` above;
- `AFFINE_3X3` SAT control;
- fixed-girth lifted SAT controls;
- large-nullity noncommuting `I+P+Q` survivors.

Forbidden:

- local parity polytope alone;
- treating fractional optimum `n/3` as an Exact-One witness;
- uncharged cutting-plane discovery;
- SAT/UNSAT or syndrome-decoding oracle calls.

## 9. Ceiling

```text
LOCAL ODD-PARITY LP OPTIMUM
= n/3 FOR EVERY 3-UNIFORM d-REGULAR INSTANCE

CONNECTED LINEAR CUBIC UNSAT9 WITH 3|n
= EXPLICIT CONTROL

SAT AND UNSAT CONTROLS SHARE LP OPTIMUM
= PROVED / CHECKED

BASIC LOCAL PARITY LP AS UNIVERSAL SOLVER
= CLOSED

GLOBAL CUT / NONLOCAL QUOTIENT / LARGE-SUPPORT DESCENT
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
