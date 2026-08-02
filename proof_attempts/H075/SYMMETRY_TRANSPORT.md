# H075 / H084 — exact signed-coordinate transport

## Status

`FORMALIZING`, reproducibility `R2`.

This artifact supplies a complete algebraic transport argument for the narrow
monomial-basis statement H084. It does **not** promote H075 or H084 to
`PROVED`; independent mathematical review and the final coefficient bound are
still required.

## Setup

Let

\[
z_k(x)
\]

be the column vector of all squarefree monomials in
\(x_1,\ldots,x_n\) of degree at most \(k\), including the constant monomial.

A signed coordinate permutation is specified by a permutation \(\pi\) and bits
\(c_i\in\{0,1\}\):

\[
\phi(x_i)=
\begin{cases}
x_{\pi(i)}, & c_i=0,\\
1-x_{\pi(i)}, & c_i=1.
\end{cases}
\]

## 1. Degree preservation

For a squarefree monomial \(x_S=\prod_{i\in S}x_i\),

\[
\phi(x_S)=
\prod_{i\in S,\;c_i=0}x_{\pi(i)}
\prod_{i\in S,\;c_i=1}(1-x_{\pi(i)}).
\]

Expanding the complemented factors produces only squarefree monomials on
subsets of \(\pi(S)\), hence every output term has degree at most \(|S|\le k\).

Therefore there is an integer matrix \(T_{\phi,k}\) satisfying

\[
z_k(\phi(x))=T_{\phi,k}^{\mathsf T}z_k(x).
\]

Every entry is in \(\{-1,0,1\}\).

## 2. Invertibility

The inverse substitution is another signed coordinate permutation:

\[
\phi^{-1}(x_j)=
\begin{cases}
x_{\pi^{-1}(j)}, & c_{\pi^{-1}(j)}=0,\\
1-x_{\pi^{-1}(j)}, & c_{\pi^{-1}(j)}=1.
\end{cases}
\]

Consequently

\[
T_{\phi,k}T_{\phi^{-1},k}
=
T_{\phi^{-1},k}T_{\phi,k}
=
I.
\]

`experiments/theta/symmetry_transport.py --self-test` constructs both matrices
over the integers and checks these identities for a deterministic grid of
small \(n,k\), permutations, and complement sets. Those finite checks validate
the implementation; the formulas above provide the universal argument.

## 3. Gram-certificate transport

Suppose

\[
p(x)=z_k(x)^{\mathsf T}Qz_k(x)
\]

with rational \(Q\succeq0\). Under substitution,

\[
p(\phi(x))
=
z_k(x)^{\mathsf T}
T_{\phi,k}Q T_{\phi,k}^{\mathsf T}
z_k(x).
\]

Congruence preserves positive semidefiniteness, so the transformed certificate
has the same degree bound. Applying the inverse substitution gives the reverse
transport.

This is the algebraic reason coordinate permutations and complementations
cannot by themselves change the minimum theta/SoS level.

## 4. Bit accounting

The basis dimension is

\[
D=\sum_{i=0}^{k}\binom{n}{i}.
\]

The transform matrix has integer entries of one bit plus sign. Computing
\(TQT^{\mathsf T}\) uses polynomially many rational additions and
multiplications in \(D\). The output numerator and denominator lengths grow by
at most the input bit length plus the logarithm of the number of accumulated
summands.

A final publication-quality proof must state the exact bit bound under one
fixed rational encoding. C010 therefore records attack `A220` as `WEAKENED`
rather than claiming the quantitative part is independently complete.

## Excluded operations

Nothing here proves preservation under:

- XOR substitutions involving products in real \(0/1\) coordinates;
- existential projection or variable forgetting;
- nonfunctional auxiliary fibers;
- unbounded-depth extension circuits.

Those are the active fronts H076, H077, H085, and H086.
