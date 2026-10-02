# R5 E9 — Maximum linear even-cover saturation theorem

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_EXTREMAL_BINARY_KERNEL_EQUIVALENCE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PARITY_DEFECT_SOURCE_SIGNED_EVEN_COVER_WGFP_2026-09-29_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_CIRCUIT_CONNECTED_CONTRACTION_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_maximum_linear_even_cover_saturation.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A POLYNOMIAL MAXIMUM-EVEN-COVER ALGORITHM.
IT COLLAPSES THE AFFINE-COSET TARGET TO ONE EXACT EXTREMAL KERNEL TEST.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A in {0,1}^{n x n}` be square, row/column-weight three. Assume the usual linear source promise when referring to the hypergraph/Levi geometry; the counting theorem itself needs only row/column cubicity.

Since every row has odd weight,

\[
A\mathbf1=\mathbf1\pmod2.
\]

Hence the full syndrome-one affine space is

\[
\boxed{\{x:Ax=\mathbf1\}=\mathbf1+\ker_{\mathbb F_2}A.}
\]

For `z in ker(A)` put `x=1 xor z`. Then

\[
\boxed{|x|=n-|z|.}
\]

Therefore minimizing syndrome-one Hamming weight is exactly maximizing binary-kernel Hamming weight.

## 2. Universal 2n/3 upper bound

Fix `z in ker_F2(A)` and let `S=supp(z)`. Every source row meets `S` evenly. Since row weight is three, every row meets `S` in exactly zero or two columns.

Let `a(z)` be the number of active rows, i.e. rows meeting `S` twice.
Count selected incidences in two ways:

- every selected column has degree three, giving `3|S|` incidences;
- every active row contributes two, giving `2a(z)` incidences.

Thus

\[
\boxed{3|z|=2a(z).}
\]

Since `a(z)<=n`,

\[
\boxed{|z|\le 2n/3.}
\]

Equality holds iff `a(z)=n`, i.e. every row contains exactly two selected kernel coordinates.

## 3. Saturation equals Exact-One

Let `x=1 xor z`. In a row with exactly two selected coordinates of `z`, the complement `x` has exactly one selected coordinate. Hence

\[
|z|=2n/3
\Longrightarrow
Ax=\mathbf1\text{ over the integers}.
\]

Conversely, if `x` is an Exact-One witness, `z=1 xor x` has exactly two ones in every row, is in `ker_F2(A)`, and has size `2n/3`.

### Theorem MLEC-1

\[
\boxed{
\text{Exact-One}(A)\text{ SAT}
\iff
\max_{z\in\ker_{\mathbb F_2}A}|z|=2n/3.
}
\]

Equivalently:

```text
SAT
iff
there is a binary even cover saturating every source row at degree two.
```

The reconstruction is linear time: `x=1 xor z`.

## 4. Exact deficiency identity

Define inactive-row count

\[
d(z)=n-a(z).
\]

Using `3|z|=2a(z)`,

\[
\boxed{
2n/3-|z|=\frac23d(z).
}
\]

Thus maximum-kernel deficiency is literally the number of unsaturated checks, up to the fixed factor `2/3`.

When `3|n`, `a(z)` is a multiple of three, so `d(z)` is a multiple of three and the kernel-weight gap from `2n/3` is an even integer.

## 5. Levi / General-Factor form

Select all three Levi incidences of variable `i` iff `z_i=1`. Then:

```text
variable shore degree: {0,3}
row shore degree:      {0,2}
```

for an arbitrary even cover.

Saturation requires

```text
variable shore degree: {0,3}
row shore degree:      exactly 2.
```

Taking the complement incidence factor gives

```text
variable shore degree: {0,3}
row shore degree:      exactly 1,
```

which is exactly the original Exact-One / parallel-class semantics. Therefore the saturation theorem is a representation identity, not a tractability claim.

## 6. Coding-theory boundary

For a general binary linear code, maximum-weight codeword is NP-hard and even hard to approximate. Those results do not by themselves classify the present 3-uniform, 3-regular, linear Tanner subclass.

Conversely, current regular-LDPC minimum-distance hardness does not automatically imply hardness under the additional 4-cycle-free/linear promise; current literature explicitly isolates the linear even-cover case as a separate open hardness frontier.

The JANUS exact Karp bridge already proves that the **saturation threshold** on this source class is P-vs-NP scale. Therefore generic codeword algorithms may be imported only with a source-preserving polynomial theorem.

## 7. Sharpened live gate

Freeze

```text
R5_E9_MAXIMUM_LINEAR_EVEN_COVER_SATURATION_GATE_V1
```

Required PASS:

```text
INPUT:
  square 3-uniform 3-regular linear incidence A.

OUTPUT in deterministic polynomial time:
  either z in ker_F2(A) with |z|=2n/3,
  or a polynomially checkable certificate that max kernel weight < 2n/3.

RECONSTRUCT:
  x=1 xor z.
```

Equivalent target currencies:

```text
maximum linear even cover,
minimum inactive-check deficiency,
shortest syndrome-one word,
shortest distinguished-f circuit in M([A|1]),
perfect transversal / parallel class.
```

Forbidden:
- generic maximum-codeword oracle;
- generic syndrome-decoding oracle;
- enumeration of the kernel;
- using parent-only high lift rank as a solver;
- dropping linearity or source provenance.

## 8. Ceiling

```text
SYNDROME-ONE COSET
= 1 + ker(A)

KERNEL EVEN-COVER IDENTITY
3|z| = 2 a(z)

UNIVERSAL KERNEL WEIGHT BOUND
|z| <= 2n/3

SATURATION
|z| = 2n/3
iff every row active
iff Exact-One witness exists

EXACT-ONE SAT
iff max kernel weight = 2n/3

UNIVERSAL POLYNOMIAL SATURATION ALGORITHM
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
