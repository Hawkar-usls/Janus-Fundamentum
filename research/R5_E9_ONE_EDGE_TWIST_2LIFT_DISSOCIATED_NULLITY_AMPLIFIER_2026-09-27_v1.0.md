# R5 E9 — One-Edge-Twist 2-Lift Trade-Free Nullity Amplifier

Date: 2026-09-27

Status:
`JANUS_DERIVED_ARBITRARY_N_STRUCTURAL_THEOREM_CANDIDATE__ROUTE_A_FALSIFIER__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_one_edge_twist_tradefree_nullity_amplifier.py`

Parent frontier:
`R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1`

Scientific firewall:

```text
THIS CLOSES ONE PROPOSED TRADE-FREE O(log n) SHORTCUT NEGATIVELY.
IT DOES NOT SOLVE THE TRADE-RICH / MIXED-CARRIER CORE.
IT DOES NOT SUPPLY A UNIVERSAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Carrier and terminology

Let

\[
A\in\{0,1\}^{n\times n}
\]

be a square incidence matrix with every row and every column of weight exactly
three. Its Tanner graph is therefore bipartite and 3-regular on both shores.

Call `A` **signed-trade-free** when

\[
\ker_{\mathbb Z}(A)\cap\{-1,0,1\}^n=\{0\}.
\]

For an incidence `(i,j)` with `A_ij=1`, define the **one-edge-twist 2-lift**
`Ahat` by lifting every incidence in parallel except `(i,j)`, which is lifted
crossed.

Write

\[
E=e_i e_j^T,\qquad P=A-E.
\]

After ordering the two sheets together, the lifted incidence matrix is

\[
\widehat A=\begin{pmatrix}P&E\\E&P\end{pmatrix}.
\]

The associated signed block is

\[
S=P-E=A-2E.
\]

## 2. Exact rational-nullity splitting

The invertible symmetric/antisymmetric coordinate change

\[
(u,v)\longmapsto(u+v,u-v)
\]

block-diagonalizes the lift over every field of characteristic different from
two:

\[
\widehat A\sim\operatorname{diag}(A,S).
\]

Hence

\[
\boxed{\nu_{\mathbb Q}(\widehat A)=\nu_{\mathbb Q}(A)+\nu_{\mathbb Q}(S).}
\]

Let

\[
K=\ker_{\mathbb Q}(A),\qquad k=\dim K.
\]

The coordinate hyperplane

\[
K_j^0=\{x\in K:x_j=0\}
\]

has dimension at least `k-1`. For every `x in K_j^0`,

\[
Sx=Ax-2e_i x_j=0.
\]

Therefore

\[
\nu_{\mathbb Q}(S)\ge k-1
\]

and thus

\[
\boxed{\nu_{\mathbb Q}(\widehat A)\ge 2k-1.}
\]

No satisfiability assumption is used in this inequality.

## 3. Signed-trade-freeness is preserved

Assume `A` is signed-trade-free. Suppose for contradiction that the lift has a
nonzero signed trade. Write its two variable sheets as

\[
p,q\in\{-1,0,1\}^n.
\]

All untwisted row-copy equations are ordinary copies of the base equations.
Only row `i` is changed by the crossed incidence `j`. The two lifted equations
at that row imply

\[
Ap=(p_j-q_j)e_i,\qquad Aq=-(p_j-q_j)e_i.
\]

Put

\[
d=p_j-q_j\in\{-2,-1,0,1,2\}.
\]

Because every column of `A` has sum exactly three,

\[
\mathbf1^T A = 3\mathbf1^T.
\]

Summing the entries of `Ap=d e_i` gives

\[
3\sum_{\ell=1}^n p_\ell=d.
\]

The left side is divisible by three, while `|d|<=2`; therefore `d=0`.
Consequently `Ap=0` and `Aq=0`. Signed-trade-freeness of the base forces
`p=q=0`, contradicting a nonzero lift trade.

### Theorem OET-1

For every square row/column-weight-three signed-trade-free incidence matrix,
every one-edge-twist 2-lift is again signed-trade-free.

The proof uses only the column sum `3`; it is not a finite-census statement.

## 4. Connectivity and linearity

Assume the Tanner graph of `A` is connected.

A connected 3-regular bipartite graph has no bridge. Indeed, if deleting a
bridge leaves a component whose bridge endpoint lies on the left shore, then,
counting internal edge incidences from the two shores,

\[
3|L_C|-1=3|R_C|,
\]

which is impossible modulo three. The right-shore case is symmetric.

Thus the twisted incidence edge lies on a base cycle. The signing with exactly
one crossed/negative edge makes that cycle negative. A standard 2-lift of a
connected signed graph is connected exactly when the signing is unbalanced
(equivalently, some cycle is negative). Hence the one-edge-twist lift is
connected.

If `A` is linear as a 3-uniform hypergraph, its Tanner graph has no 4-cycle. A
graph cover cannot create a cycle shorter than the base girth, so the lift is
also linear.

Therefore the operation preserves the connected cubic-linear carrier.

## 5. Exact-One satisfiability and uniqueness are preserved

If

\[
Ax=\mathbf1,\qquad x\in\{0,1\}^n,
\]

assign both lifted copies of variable `j` the same value `x_j`. Every lifted
row then sees the same three Boolean values as its base row, independent of
whether an incidence is parallel or crossed. Hence

\[
\widehat A(x,x)^T=\mathbf1.
\]

So SAT lifts upward.

Moreover, if `Ahat` is signed-trade-free and had two distinct Exact-One models
`u,v`, then `u-v` would be a nonzero vector in `{-1,0,1}^{2n}` with
`Ahat(u-v)=0`, a forbidden signed trade. Thus a satisfiable signed-trade-free
carrier has a unique Exact-One model.

## 6. Explicit 18x18 seed

Freeze the following row supports, using zero-based column labels:

```text
(0,15,17)
(1,4,12)
(2,10,14)
(3,4,11)
(4,8,9)
(3,5,13)
(1,6,10)
(2,7,15)
(1,8,14)
(3,7,9)
(9,10,16)
(7,11,13)
(5,12,17)
(0,13,16)
(0,12,14)
(5,8,15)
(2,6,16)
(6,11,17)
```

Direct exact checks give:

```text
row weight = 3
column weight = 3
Tanner connected = true
linear = true
rank_Q = 16
nullity_Q = 2
nullity_F2 = 2
```

One Exact-One model is

```text
(1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0).
```

A binary-kernel basis has supports

```text
Z1 = {4,5,6,8,10,11,12,13,14,16}
Z2 = {3,5,7,11,15,17}.
```

There are only three nonzero binary-kernel supports. Their contracted cubic
graphs contain the following explicit odd cycles:

```text
Z1        : 5-12-4-11-13-5
Z2        : 11-3-7-11
Z1 XOR Z2 : 13-3-7-13
```

A signed trade modulo two would give a nonzero binary-kernel support whose
contracted components admit a bipartition by the `+1/-1` signs. Each of the
three possible supports instead has a non-bipartite connected component, so the
seed is signed-trade-free.

Because it is SAT and trade-free, its displayed Exact-One model is unique.

## 7. Infinite trade-free linear-nullity family

Let `A_0=A_18` be the frozen seed above. Inductively choose any incidence of
`A_t` and take its one-edge-twist 2-lift `A_{t+1}`.

By Sections 3--5, every `A_t` is:

```text
connected
cubic
linear
Exact-One SAT
unique-model
signed-trade-free.
```

The dimensions satisfy

\[
n_t=18\cdot2^t
\]

and, with `k_t=nu_Q(A_t)`,

\[
k_{t+1}\ge2k_t-1,\qquad k_0=2.
\]

Therefore

\[
k_t-1\ge2^t(k_0-1)=2^t
\]

and hence

\[
\boxed{k_t\ge 2^t+1=\frac{n_t}{18}+1.}
\]

Thus this is an explicit infinite connected cubic-linear signed-trade-free
Exact-One-SAT family with **linear rational nullity**.

### Corollary OET-2

The proposed Route-A statement

```text
connected cubic-linear signed-trade-free
=> rational nullity O(log n)
```

is false.

More strongly, signed-trade-free instances can have `nu_Q(A)=Omega(n)` while
remaining satisfiable and unique-model.

This is a genuine arbitrary-size falsifier of that proposed shortcut.

## 8. Finite replay

The executable checker independently reconstructs the frozen 18x18 seed,
verifies the exact seed certificates, constructs the canonical lexicographic
one-edge-twist chain, and replays the first levels:

```text
n       18   36   72
nu_Q     2    3    5
nu_F2    2    4    8
trade    no   no   no
```

A separate offline extension also reached `n=144`, `nu_Q=9`; the CI replay is
deliberately capped at 72 because finite enumeration is not the proof.

The finite values are regression controls only. The arbitrary-size conclusion
is Sections 2--7.

## 9. Prior-art boundary

The following ingredients are source-bound prior art:

- graph 2-lifts and their signing formalism;
- old/new spectral or symmetric/antisymmetric decomposition of a 2-lift;
- balanced signed graphs and connectivity of the associated 2-lift;
- trades / null 3-hypergraphs as signed degree-zero objects.

Representative sources checked before materialization:

- Y. Bilu and N. Linial, *Lifts, Discrepancy and Nearly Optimal Spectral Gap*,
  Combinatorica 26 (2006), 495--519, DOI `10.1007/s00493-006-0029-7`.
- F. Martin, *Frustration and isoperimetric inequalities for signed graphs*,
  Discrete Applied Mathematics 217 (2017), 276--285,
  DOI `10.1016/j.dam.2016.09.015`.
- W. Kocay and P. C. Li, *On 3-Hypergraphs with Equal Degree Sequences*,
  Ars Combinatoria 82 (2007), 145--157.

The JANUS-derived step is the specialization combining a **single twisted
incidence**, column-sum divisibility, signed-trade-freeness, and rational-nullity
amplification. No world-priority claim is made.

## 10. New frontier after Route A is falsified

The dissociated-nullity split is no longer balanced between `A` and `B`:

```text
ROUTE A:
trade-free => O(log n) rational nullity
= FALSIFIED BY ARBITRARY-N FAMILY

ROUTE B:
explicit trade-free high-nullity family
= CONSTRUCTED
```

Therefore the universal algorithm cannot rely on low rational nullity to
dispose of the trade-free residue.

The active representation-change frontier becomes:

```text
R5_E9_TRADE_FREE_HIGH_NULLITY_UNIQUE_MODEL_CONTRACTION_GATE_V1
```

together with the already-open trade-rich mixed-carrier closure:

```text
R5_E9_SIGNED_TRADE_POLY_DISCOVERY_OR_MIXED_CARRIER_CLOSURE_GATE_V1.
```

A universal P=NP route must cover both branches by deterministic polynomial
construction with polynomial total intermediate size and witness
reconstruction.

## 11. Ceiling

```text
ONE-EDGE-TWIST TRADE-FREE PRESERVATION
= PROVED

ONE-EDGE-TWIST CONNECTED CUBIC-LINEAR PRESERVATION
= PROVED

RATIONAL NULLITY RECURRENCE
k' >= 2k-1
= PROVED

EXPLICIT SAT UNIQUE-MODEL TRADE-FREE FAMILY
n_t=18*2^t
k_t >= n_t/18+1
= PROVED

TRADE-FREE O(log n) ROUTE A
= FALSIFIED

TRADE-FREE HIGH-NULLITY POLYTIME CONTRACTION
= OPEN

TRADE-RICH MIXED-CARRIER GLOBAL CLOSURE
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
