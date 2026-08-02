# H092 — rational LDL certificate completeness

## Status

`FORMALIZING`, reproducibility `R2`.

This note records the exact algebraic induction implemented by
`experiments/theta/rational_ldl.py`. It does not promote H092 to `PROVED`:
the universal binary bit-complexity bound and independent mathematical review
remain open obligations.

## Statement under examination

For a symmetric rational positive-semidefinite matrix \(Q\in\mathbb Q^{n\times n}\),
there should exist a permutation matrix \(P\), a rational unit-lower-triangular
matrix \(L\), and a nonnegative rational diagonal matrix \(D\) such that

\[
PQP^{\mathsf T}=LDL^{\mathsf T}.
\]

Unlike an ordinary Gram factor \(Q=B^{\mathsf T}B\), this representation does
not require square roots of rational pivots.

## Exact induction

Assume the active Schur-complement block is rational and PSD.

1. If every diagonal entry is zero, PSD implies every row and column is zero.
   Indeed, for a PSD matrix \(M\), the \(2\times2\) principal minor on indices
   \(i,j\) gives

   \[
   M_{ii}M_{jj}-M_{ij}^2\ge0.
   \]

   With both diagonal entries zero, this forces \(M_{ij}=0\).

2. Otherwise choose a positive diagonal pivot \(d=M_{pp}>0\), permute it into
   the leading position, and define

   \[
   \ell_i=M_{i0}/d.
   \]

3. The remaining block is the rational Schur complement

   \[
   S=M_{1: ,1:}-d\,\ell\ell^{\mathsf T}.
   \]

   Since \(d>0\) and \(M\succeq0\), \(S\succeq0\).

4. Recurse on \(S\). All operations are rational additions, multiplications,
   divisions by a positive rational pivot, and symmetric permutations.

This yields a rational permuted LDL decomposition with nonnegative diagonal.

## Exact verification

The verifier checks:

- the permutation is a bijection;
- \(L\) is unit lower triangular;
- every diagonal entry of \(D\) is nonnegative;
- the exact rational identity \(PQP^{\mathsf T}=LDL^{\mathsf T}\).

No eigenvalue approximation or floating-point tolerance is used.

## Bit-complexity boundary

The code establishes exact construction on finite inputs, but it does not by
itself prove the asymptotic claim that all intermediate numerators and
denominators have polynomial encoded length.

A publication-quality proof should express every elimination entry as a ratio
of signed minors and apply determinant-size bounds under a fixed binary
rational encoding. Until that argument is independently reviewed, attack
`A260` remains `WEAKENED`.

## Reproduction

```bash
python experiments/theta/rational_ldl.py --self-test
```

The test suite includes singular PSD matrices, a zero leading pivot requiring
permutation, a graph-Laplacian fixture, and indefinite matrices that must be
rejected.
