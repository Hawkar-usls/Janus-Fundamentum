# R5 E9 — Trade-Free Unique-Model Control and Dissociated-Nullity Gate

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_COUNTERCONTROL__TRADE_ONLY_COVERAGE_FALSIFIED__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_trade_free_unique_model_control.py`

Parents:
- `research/R5_E9_BINARY_KERNEL_BIPARTITE_TRADE_DONOR_2026-09-27_v1.0.md`
- `research/R5_E9_SIGNED_TRADE_POLYSIZE_BOUNDARY_PROJECTION_THEOREM_2026-09-27_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_CUBIC_LINEAR_GIRTH10_SPECTRAL_NULLITY_BOUND_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS FALSIFIES ONLY THE CLAIM
    SAT CUBIC-LINEAR EXACT-ONE => NONZERO SIGNED TRADE.

IT DOES NOT FALSIFY SIGNED-TRADE METHODS ON TRADE-RICH INSTANCES.
IT DOES NOT PROVE A HARDNESS LOWER BOUND.
IT DOES NOT PROVE P=NP OR P!=NP.

E8_D1 = EMPTY
P_VS_NP = OPEN
```

## 1. Exact 9x9 control

Let A be the clause-by-variable incidence matrix

\[
A=
\begin{pmatrix}
0&0&0&0&0&0&1&1&1\\
0&1&1&0&0&0&0&1&0\\
0&0&1&0&1&0&1&0&0\\
1&1&0&0&0&0&1&0&0\\
0&0&1&1&0&1&0&0&0\\
0&0&0&1&1&0&0&0&1\\
1&0&0&0&1&1&0&0&0\\
1&0&0&1&0&0&0&1&0\\
0&1&0&0&0&1&0&0&1
\end{pmatrix}.
\]

Every row and every column contains exactly three ones. Any two distinct rows
intersect in at most one column. The Tanner graph is connected. Hence this is a
connected square cubic-linear 3-uniform Exact-One carrier.

The vector

\[
x^\star=(1,0,1,0,0,0,0,0,1)^T
\]

satisfies

\[
Ax^\star=\mathbf 1.
\]

Therefore the instance is satisfiable.

## 2. Rational-kernel certificate

Exact rational elimination gives

```text
rank_Q(A) = 8
nullity_Q(A) = 1.
```

A primitive integer generator of the one-dimensional rational kernel is

\[
v=(2,-1,2,-1,-1,-1,-1,-1,2)^T.
\]

Direct multiplication gives

\[
Av=0.
\]

Moreover

\[
v=3x^\star-\mathbf1.
\]

This is exactly the rational-kernel word from the existing Exact-One normal
form.

### Unique-model theorem for this control

Every Exact-One model x would produce

\[
w=3x-\mathbf1\in\{-1,2\}^9\cap\ker_{\mathbb Q}(A).
\]

Because the kernel is one-dimensional, `w=t v` for some rational `t`.
The coordinates of `v` include both `2` and `-1`. Requiring every coordinate
of `tv` to lie in `{-1,2}` forces `t=1`. Hence

\[
w=v,\qquad x=x^\star.
\]

So the displayed Exact-One model is unique.

The executable checker independently enumerates all `2^9` Boolean assignments
as a finite regression and confirms the same result.

## 3. No signed trade

A signed trade would be a nonzero vector

\[
h\in\{-1,0,1\}^9,\qquad Ah=0.
\]

Again `ker_Q(A)=span_Q(v)`, so `h=t v`. Since `v` is primitive and has a
coordinate equal to `-1`, integrality of `h` forces `t` to be an integer.
If `t` is nonzero, a coordinate corresponding to a `2` in `v` has absolute
value at least two. This contradicts `h in {-1,0,1}^9`.

Therefore

\[
\boxed{
\ker_{\mathbb Q}(A)\cap\{-1,0,1\}^9=\{0\}.
}
\]

The checker also exhausts all `3^9-1=19682` nonzero signed vectors as a
redundant finite regression.

Thus the instance is simultaneously

```text
CONNECTED
CUBIC
LINEAR
EXACT-ONE SAT
UNIQUE-MODEL
SIGNED-TRADE-FREE.
```

## 4. Trade-only universal coverage is falsified

The existing binary-kernel donor proves that two distinct Exact-One models
always yield a nonzero signed trade by taking their difference.

The converse universal hope

```text
SAT => a useful nonzero signed trade exists
```

is false, even on connected cubic-linear Exact-One instances, by the exact
control above.

Hence a universal solver cannot route every satisfiable survivor solely by
first constructing a signed trade.

This does not weaken the signed-trade boundary-projection theorem. It narrows
its correct scope to the trade-rich branch.

## 5. Dissociated interpretation

Let `a_1,...,a_9` be the columns of A.

A nonzero signed relation

\[
\sum_i h_i a_i=0,\qquad h_i\in\{-1,0,1\},
\]

is equivalent to two distinct subsets of columns having the same integer sum.
Thus the absence of signed trades says exactly that the columns of A are
**dissociated** in the additive-combinatorial sense.

This terminology is source-bound prior art. General dissociated subsets of
`{0,1}^r` can have size much larger than their ambient dimension, so no
argument may infer small rational nullity from dissociation alone. Any such
bound must use the additional JANUS carrier structure:

```text
row weight = 3
column weight = 3
pairwise row intersection <= 1
connectedness / optional girth constraints.
```

## 6. Interaction with the rational-nullity router

This particular control is not a hard residual for the current exact front
end, because

```text
nullity_Q(A)=1.
```

The existing router solves nullity `k` in `2^k poly(n,L)`, and is polynomial
when `k=O(log n)`.

Therefore the true trade-free obstruction is not the 9x9 instance itself.
The live universal question is whether trade-free connected cubic-linear
carriers can have unbounded/high rational nullity.

## 7. New falsifiable gate

Freeze:

```text
R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1
```

For an unbounded connected cubic-linear family A_n with

\[
\ker_{\mathbb Q}(A_n)\cap\{-1,0,1\}^n=\{0\},
\]

determine which side is true:

### Route A — polynomial closure

Prove an arbitrary-size structural bound

\[
\nu_{\mathbb Q}(A_n)=O(\log n).
\]

Then the existing `2^k poly(n,L)` rational-kernel router decides every
trade-free instance in polynomial time.

Combined with a polynomially complete treatment of the trade-rich branch,
this would close one major representation-change split.

### Route B — falsifier

Construct an explicit connected cubic-linear trade-free family with

\[
\nu_{\mathbb Q}(A_n)=\omega(\log n).
\]

Then the proposed trade-free-nullity shortcut is dead and the universal route
must use a stronger invariant than signed trades plus small-nullity
enumeration.

Finite random census is only hypothesis generation and is not evidence for
Route A. Failure to find a counterexample is not proof.

## 8. Prior-art boundary

Checked source concepts include:

- W. Kocay and P. C. Li, *On 3-Hypergraphs with Equal Degree Sequences*:
  null 3-hypergraphs/trades as degree-preserving signed objects.
- V. F. Lev and R. Yuster, *On the Size of Dissociated Bases*,
  Electronic Journal of Combinatorics 18(1), P117 (2011),
  DOI `10.37236/604`: dissociated sets and distinct subset sums.
- A. Bjoerner and J. Karlander, *The mod p Rank of Incidence Matrices for
  Connected Uniform Hypergraphs*, European Journal of Combinatorics 14
  (1993), 151-155, DOI `10.1006/eujc.1993.1021`: source-bound incidence-rank
  context.

No novelty claim is made for trades, dissociated sets, or incidence rank.
The JANUS result is the exact 9x9 countercontrol and its routing consequence
inside the already frozen affine/kernel/trade stack.

## 9. Ceiling

```text
SAT CUBIC-LINEAR => SIGNED TRADE
= FALSIFIED

TRADE-FREE SAT INSTANCES
= EXIST

TRADE-FREE UNIQUE-MODEL CONTROL
= EXACT 9x9 CERTIFICATE

THIS CONTROL'S RATIONAL NULLITY
= 1
= ALREADY POLYNOMIAL UNDER EXISTING ROUTER

TRADE-FREE => O(log n) RATIONAL NULLITY
= OPEN

TRADE-FREE HIGH-NULLITY COUNTERFAMILY
= OPEN

TRADE-RICH GLOBAL MIXED-CARRIER CLOSURE
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
