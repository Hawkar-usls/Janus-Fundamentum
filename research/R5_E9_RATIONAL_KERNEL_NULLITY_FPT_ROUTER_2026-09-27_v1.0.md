# R5 E9 — Rational-Kernel Nullity FPT Router for Cubic Exact-One

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_FPT_ROUTER_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_rational_kernel_nullity_fpt_router.py`

Parents:
- `R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS AN EXACT PARAMETERIZED ROUTER.
IT IS POLYNOMIAL ONLY WHEN RATIONAL NULLITY IS O(log n).
IT DOES NOT SOLVE THE HIGH-NULLITY UNIVERSAL CORE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact rational kernel word

Let `A` be the square incidence matrix of a cubic 3-uniform Exact-One instance.
For a Boolean assignment `x`, define

```text
w = 3x - 1.
```

Coordinatewise,

```text
w_i in {-1,2}.
```

Because every row of `A` has exactly three ones,

```text
A 1 = 3 1.
```

Hence

```text
A x = 1  over the integers
iff
A(3x-1)=0
iff
A w = 0 over Q.
```

Therefore

```text
Exact-One SAT
iff
ker_Q(A) contains a vector w in {-1,2}^n.
```

This is exact, not a relaxation.

## 2. Nullity-zero terminal

Let

```text
k = dim_Q ker(A).
```

If `k=0`, then the only rational kernel vector is zero, but zero is not in
`{-1,2}^n`. Therefore

```text
k=0 => UNSAT.
```

This immediately classifies any nonsingular cubic incidence matrix.

## 3. Coordinate information set for the kernel

Compute a rational basis of `K=ker_Q(A)` and write it as an `n x k` matrix

```text
B=[b_1 ... b_k],
```

so every kernel vector is uniquely

```text
w = B alpha,
alpha in Q^k.
```

Because `B` has column rank `k`, there exists a set of coordinate indices

```text
I subseteq {1,...,n}, |I|=k,
```

such that the `k x k` row submatrix `B_I` is nonsingular.
Such an `I` is constructible by ordinary Gaussian elimination on the rows of
`B`.

Consequently the coordinate projection

```text
pi_I : K -> Q^k,
w -> w_I
```

is an isomorphism: a kernel vector is uniquely determined by its values on the
`k` information coordinates.

## 4. Exact 2^k algorithm

Every desired Exact-One kernel word has

```text
w_I in {-1,2}^k.
```

Enumerate the `2^k` vectors `s in {-1,2}^k`. For each:

1. solve

```text
B_I alpha = s;
```

2. reconstruct

```text
w=B alpha;
```

3. accept iff every coordinate of `w` belongs to `{-1,2}`;
4. reconstruct

```text
x=(w+1)/3
```

and verify `Ax=1` exactly.

### Theorem RKN-1

Cubic Exact-One with rational nullity `k` is decidable and witness-constructible in

```text
2^k poly(n,L)
```

bit operations, where `L` is the input bit length.

The arithmetic bit lengths remain polynomial: `A` has tiny integer entries and
Gaussian elimination / rational linear solving has polynomial-size exact
numerators and denominators under standard fraction-free or exact rational
algorithms.

## 5. Polynomial island

If

```text
k = O(log n),
```

then

```text
2^k poly(n)=poly(n).
```

Therefore every genuine universal hard survivor after this router must satisfy

```text
nu_Q(A)=omega(log n)
```

along an unbounded family.

This is a rigorous routing statement, not a hardness theorem.

## 6. Why the binary and rational representations must be combined

The binary affine-coset representation alone may leave a large parity coset
on an instance that is already trivially UNSAT over `Q`.

The frozen connected linear cubic `UNSAT9` control from the local-parity-LP
barrier is exactly such an example. Its incidence matrix has

```text
rank_Q(A)=9,
det(A)=27,
nu_Q(A)=0.
```

So the rational router rejects it before any affine-coset minimum-weight search.

This does not weaken the LP-blindness theorem; it shows that a universal solver
must route across representations rather than require one representation to do
all work.

## 7. Controls

The checker freezes:

- `CONNECTED_LINEAR_CUBIC_UNSAT9`: rational nullity `0`, terminal UNSAT;
- `AFFINE_3X3`: rational nullity `2`, exact enumeration recovers its Exact-One witnesses;
- small local-swap `I+P+Q'` controls: nonzero/high relative nullity and successful kernel-word reconstruction, showing that large nullity need not mean hardness.

All exhaustive enumeration in the checker is finite validation only. The
arbitrary-size theorem is the information-coordinate argument above.

## 8. Combined router

For a cubic Exact-One instance, the current exact front end is now:

```text
1. compute k = nullity_Q(A);
2. if k=0: return UNSAT;
3. if 2^k is polynomially bounded by the declared input budget:
       run the exact information-coordinate enumerator;
4. otherwise:
       pass to the high-nullity nonlocal carrier:
       affine-coset circuit augmentation / global quotient / other exact route.
```

No step calls SAT, Exact-Cover, syndrome decoding, or an uncharged oracle.

## 9. New live frontier

Freeze:

```text
R5_E9_HIGH_RATIONAL_NULLITY_GLOBAL_QUOTIENT_OR_AUGMENTATION_GATE_V1
```

The universal residual must simultaneously survive:

- rational nullity `omega(log n)`;
- binary affine-coset exact-weight routing;
- bounded-support kernel descent barriers;
- local parity LP blindness;
- all previously frozen WDR reductions.

The target is a polynomially constructible quotient or augmentation rule on
that high-nullity core.

## 10. Ceiling

```text
RATIONAL NULLITY 0
= EXACT UNSAT TERMINAL

RATIONAL NULLITY k
= EXACT 2^k poly(n) SOLVER

k=O(log n)
= POLYNOMIAL ISLAND

HIGH-NULLITY UNIVERSAL CORE
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
