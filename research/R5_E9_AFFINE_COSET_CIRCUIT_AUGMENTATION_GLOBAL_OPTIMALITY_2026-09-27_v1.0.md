# R5 E9 — Affine-Coset Circuit Augmentation and Global Optimality

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_AUGMENTATION_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_affine_coset_circuit_augmentation.py`

Parents:
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_BOUNDED_SUPPORT_AFFINE_KERNEL_DESCENT_BARRIER_2026-09-27_v1.0.md`
- `R5_E9_LOCAL_SWAP_BINARY_COSET_EXACTONE_CLASSIFICATION_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS AN EXACT GLOBAL-OPTIMALITY CHARACTERIZATION.
IT DOES NOT YET SUPPLY A POLYNOMIAL NEGATIVE-CIRCUIT FINDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A` be any binary matrix and let

```text
C = ker_F2(A).
```

Fix an affine point `x` in a coset `x0 + C` and use Hamming weight

```text
rho(x)=|x|.
```

For `z in C`, define the exact augmentation charge

```text
Delta_x(z)
= |x XOR z|-|x|
= |z|-2|supp(x) intersect supp(z)|.
```

Thus `z` is improving iff `Delta_x(z)<0`.

A **circuit** is the support of an inclusion-minimal nonzero vector of `C`, equivalently a minimal dependent column set of the binary matroid represented by `A`.

## 2. Disjoint circuit decomposition

### Lemma CAD-1

Every nonzero `z in C` is a disjoint union of circuit vectors.

### Proof

Let `S=supp(z)`. Since the columns indexed by `S` sum to zero, `S` is dependent. Choose an inclusion-minimal nonempty dependent subset `C1 subseteq S`; its indicator is a circuit vector and has zero column sum.

Over `F2`, subtracting the circuit is symmetric difference. Because `C1 subseteq S`, this simply removes `C1`:

```text
S1 = S \ C1.
```

The columns of `S1` still sum to zero because both `S` and `C1` do. If `S1` is nonempty, repeat. Finiteness terminates with pairwise disjoint circuits whose union is exactly `S`. QED.

## 3. Additivity of Hamming augmentation charge

If `z1,...,zk` have pairwise disjoint supports, then

```text
Delta_x(z1 XOR ... XOR zk)
= sum_i Delta_x(zi).
```

This follows directly from

```text
Delta_x(z)=sum_{j in supp(z)} (1-2 x_j).
```

Therefore the augmentation charge of a kernel vector is the sum of the charges of the disjoint circuits in any disjoint circuit decomposition.

## 4. Main theorem: circuit-local optimality is global

### Theorem CAD-2

For every affine point `x in x0+C`, the following are equivalent:

1. `x` has minimum Hamming weight in the entire affine coset `x0+C`.
2. No circuit `c in C` satisfies `Delta_x(c)<0`.

### Proof

`1 => 2` is immediate: an improving circuit is itself an affine-preserving move to a lower-weight coset point.

For `2 => 1`, suppose `x` is not globally minimum. Then there is `y in x0+C` with `|y|<|x|`. Put

```text
z = x XOR y.
```

Because `x,y` are in the same coset, `z in C`, and

```text
Delta_x(z)=|y|-|x|<0.
```

By CAD-1, decompose `z` into pairwise disjoint circuits

```text
z=c1 XOR ... XOR ck.
```

By charge additivity,

```text
Delta_x(z)=sum_i Delta_x(ci)<0.
```

Hence at least one circuit has negative charge, contradicting condition 2. QED.

This is exact: there are no Hamming-weight local minima with respect to all matroid circuits that are not global minima of the affine coset.

## 5. Exact greedy solver schema with one missing subroutine

Assume a subroutine

```text
NEGATIVE_CIRCUIT(A,x)
```

that returns either:

- a circuit `c in ker(A)` with `Delta_x(c)<0`, or
- `NONE`, certifying that no such circuit exists.

Then:

```text
x := any coset point
while True:
    c := NEGATIVE_CIRCUIT(A,x)
    if c is NONE:
        return x
    x := x XOR c
```

is an exact minimum-Hamming-weight coset solver.

Every successful augmentation lowers the integer potential `|x|` by at least one. Therefore there are at most `n` successful iterations. By CAD-2, termination at `NONE` is global optimality, not heuristic local optimality.

Hence if `NEGATIVE_CIRCUIT` is deterministic polynomial time and returns a polynomially checkable absence certificate, the whole minimum-weight solver is deterministic polynomial time.

## 6. Cubic Exact-One specialization

For the cubic 3-uniform Exact-One carrier, the companion affine theorem gives

```text
A 1 = 1 (mod 2)
```

and

```text
Exact-One SAT
iff
min{|x|: Ax=1}=n/3.
```

Start the circuit-descent algorithm at

```text
x0 = 1^n.
```

If a polynomial `NEGATIVE_CIRCUIT` procedure exists for every cubic incidence matrix, then at most `n` circuit augmentations find the exact affine-coset minimum. Accept iff the final weight equals `n/3`; otherwise reject.

Thus the universal cubic Exact-One frontier sharpens to one concrete subproblem:

```text
SIGNED_NEGATIVE_CIRCUIT_ON_CUBIC_BINARY_INCIDENCE_MATROIDS.
```

Because cubic monotone Exact-One is an NP-complete source class, a polynomial solution of this subproblem on the full carrier would be P=NP-level content. This note does not assume such a solution.

## 7. Why the high-girth barrier does not kill this route

The previous bounded-support theorem proves that high-girth satisfiable controls may have no nonzero kernel vector of support at most any fixed constant `k`.

CAD-2 does not require bounded support. The improving circuit may be large. In fact, if a lower-weight coset point exists, some improving circuit exists regardless of its support.

Therefore the correct lesson of the high-girth barrier is:

```text
CONSTANT-SUPPORT CIRCUIT SEARCH = INSUFFICIENT,
ALL-SUPPORT NEGATIVE-CIRCUIT SEARCH = STILL EXACT.
```

## 8. Structural bridge to the existing E10 matroid stack

The missing primitive is now a weighted circuit problem in the column matroid of `A` with signed element weights

```text
w_j(x)=1-2x_j in {-1,+1}.
```

An improving circuit is exactly a circuit of negative total signed weight.

This creates a direct bridge to the existing E10 work on graphic/regular-matroid, T-join, decomposition, and non-graphic obstruction lanes. The E9 affine-coset route and the E10 matroid route are therefore not separate search programs at this point: the matroid circuit oracle is the exact augmentation oracle required by E9.

No claim is made here that the existing E10 machinery already handles every binary matroid arising from arbitrary cubic Exact-One.

## 9. Mandatory next attack

Freeze:

```text
R5_E9_SIGNED_NEGATIVE_CIRCUIT_SYNTHESIS_GATE_V1
```

Input:

```text
cubic 3-uniform incidence matrix A,
parity point x with Ax=1,
signed weights w_j=1-2x_j.
```

PASS requires a deterministic polynomial algorithm that either:

1. constructs a circuit `c in ker(A)` with `sum_{j in c} w_j < 0`; or
2. certifies that every circuit has nonnegative signed weight.

The algorithm must charge construction, decomposition, comparison, and certificate verification. It may not enumerate the kernel or all circuits and may not call SAT / Exact-Cover / syndrome-decoding as an oracle.

Mandatory controls:

- connected cubic linear `UNSAT9`;
- `AFFINE_3X3` SAT;
- Fano-7 parity control;
- local-swap family `A'_m`;
- high-girth lifted satisfiable controls;
- noncommuting / large-nullity `I+P+Q` controls;
- regular-matroid positive islands already solved by E10.

## 10. Ceiling

```text
AFFINE COSET GLOBAL MINIMUM
iff
NO NEGATIVE CIRCUIT
= PROVED

GREEDY CIRCUIT DESCENT STEPS
<= n
= PROVED

UNIVERSAL CUBIC EXACT-ONE SOLVER
= REDUCED TO SIGNED NEGATIVE-CIRCUIT SYNTHESIS

POLYNOMIAL NEGATIVE-CIRCUIT SYNTHESIS ON ALL CUBIC BINARY INCIDENCE MATROIDS
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
