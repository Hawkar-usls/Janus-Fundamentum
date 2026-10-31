# R5 E9 — NAE transversal / minority copy-flow normal form

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_TRANSVERSAL_AND_COPY_FLOW_NORMAL_FORM__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_INTEGER_LATTICE_NAE_DEFECT_FLOW_POSITIVE_LAYER_BARRIER_2026-09-29_v1.0.md`
- `research/R5_E9_CONTINUOUS_L1_BARYCENTER_AND_CROSSING_PENALTY_BARRIER_2026-09-29_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_nae_transversal_copy_flow.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT REWRITES THE INTEGER-LATTICE FRONTIER AS A MINIMUM-TRANSVERSAL GAP
PLUS A NONNEGATIVE INTEGER ADD/COPY SYSTEM FOR A FIXED NAE THRESHOLD.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Cubic source and threshold NAE witness

Let `A` be the square incidence matrix of a 3-uniform 3-regular hypergraph `H`, and let

\[
z\in\mathbb Z^n,\qquad Az=\mathbf1.
\]

Define

\[
b_i=\mathbf1[z_i\ge1],
\qquad B=\{i:b_i=1\}.
\]

The NAE-defect theorem already proves that every row has Boolean weight one or two. Hence `B` and its complement both hit every hyperedge: `B` is a NAE transversal.

Let

\[
T=\{r:(Ab)_r=2\}.
\]

Counting selected incidences in two ways gives

\[
3|B|=\sum_r (Ab)_r=(n-|T|)+2|T|=n+|T|.
\]

Therefore

\[
\boxed{|T|=3|B|-n.}
\]

In particular every NAE transversal satisfies `|B|>=n/3`, with equality exactly when `T` is empty.

## 2. Exact-One equals the fractional transversal lower bound

For every transversal `S` of a 3-uniform 3-regular source,

\[
3|S|=\text{number of incidences from S}\ge n,
\]

because all `n` rows must be hit. Hence

\[
\tau(H)\ge n/3.
\]

The fractional assignment `x_i=1/3` has cost `n/3`, so this is the canonical fractional transversal lower bound.

If an integral transversal has size exactly `n/3`, its `n` incidences cover `n` rows at least once; therefore every row is covered exactly once. Conversely every Exact-One witness is a transversal of size `n/3`.

### Theorem NTCF-1

\[
\boxed{
\text{Exact-One}(A)\text{ SAT}
\iff
\tau(H)=n/3.
}
\]

Equivalently, on any NAE-satisfiable source the universal decision target is whether a NAE transversal can be driven all the way down to the fractional lower bound.

This is an exact equivalence, not an algorithmic claim: minimum transversal in the full source class is itself a P-vs-NP-scale object by the frozen Karp reduction.

## 3. Objective simplification

Write the exact NAE-defect decomposition

\[
z=b+p-q,
\qquad p,q\ge0,
\]

where `p_i` is supported on `b_i=1` and `q_i` on `b_i=0`.
The previous theorem gives

\[
F(z)-n=4\|p\|_1+\frac23|T|.
\]

Substituting `|T|=3|B|-n` yields

\[
\boxed{
F(z)=\frac n3+2|B|+4\|p\|_1.
}
\]

Thus the negative overshoot layer `q` disappears from the objective once feasibility is enforced. The exact costs are:

1. `2|B|` for the size of the NAE transversal;
2. `4||p||_1` for positive overshoot above Boolean value one.

At a Boolean Exact-One witness, `|B|=n/3` and `p=0`, giving `F=n`.

## 4. Minority copy-flow equations for fixed b

Fix a NAE threshold vector `b`. In every row there is a unique **minority** variable: the unique `1` in a weight-one row or the unique `0` in a weight-two row.

Define one nonnegative integer magnitude per source variable:

\[
r_i=
\begin{cases}
p_i,&b_i=1,\\
q_i,&b_i=0.
\end{cases}
\]

For a row with minority variable `m` and majority variables `u,v`, define

\[
\tau_r=\mathbf1[(Ab)_r=2].
\]

If the row has weight one, its integer equation is

\[
(1+r_m)-r_u-r_v=1,
\]

hence `r_m-r_u-r_v=0`.

If the row has weight two, its equation is

\[
-r_m+(1+r_u)+(1+r_v)=1,
\]

hence `r_m-r_u-r_v=1`.

Therefore every fixed-threshold fiber is exactly

\[
\boxed{
r_m-r_u-r_v=\tau_r\quad\text{for every row }r,\qquad r\in\mathbb Z_{\ge0}^n.}
\]

Conversely, any nonnegative integer solution `r` of these equations reconstructs an integer point `z` by

\[
z_i=
\begin{cases}1+r_i,&b_i=1,\\-r_i,&b_i=0.
\end{cases}
\]

So this is a bijective representation of the integer lattice fiber with threshold `b`.

### Theorem NTCF-2 — add/copy normal form

For fixed NAE `b`, integer-lattice feasibility and optimization are an exact nonnegative integer **add/copy system**:

```text
one scalar r_i per source variable,
three uses of the same scalar because every variable has degree 3,
row law: minority = majority_1 + majority_2 + tau,
tau in {0,1}.
```

The local addition is elementary. The non-network coupling is the fanout/equality requirement that the same `r_i` must be reused on all three incidences of variable `i`.

## 5. Oriented-Levi conservation identity

Orient each row-node toward its minority variable and orient the two majority incidences from their variables toward the row.
Let `m_i in {0,1,2,3}` be the number of incident rows in which variable `i` is the minority.

Using `r_i` as the common magnitude on all three incidences, the signed divergence at variable `i` is

\[
(3-2m_i)r_i.
\]

Summing the row equations gives

\[
\boxed{|T|=\sum_i(2m_i-3)r_i.}
\]

This is the copy-flow form of the earlier identity

\[
|T|=3(\|q\|_1-\|p\|_1).
\]

Ordinary min-cost flow would be polynomial if the three incidences of a variable could carry independent values. The source semantics instead requires exact three-way equality/fanout, which is precisely the surviving global coupling.

## 6. Prior-art boundary

Real-valued generalized flow has polynomial algorithms, but **integral** generalized flow is NP-hard in general, and remains NP-complete on restricted graph classes; thus generic generalized-flow theory cannot be imported as a polynomial oracle for the integer add/copy system.

The present source is more structured than arbitrary integral generalized flow, so that hardness result is only a firewall, not an exact hardness theorem for this JANUS subclass.

Likewise, the tractable promise CSP direction `(1-in-3, NAE)` constructs a NAE assignment when a 1-in-3 assignment is promised to exist. It does not solve the reverse optimization problem of converting an available NAE threshold to an Exact-One witness.

## 7. Sharpened live gate

Freeze

```text
R5_E9_NAE_MIN_TRANSVERSAL_COPY_FLOW_GLOBAL_GATE_V1
```

A PASS must provide a deterministic polynomial mechanism that, on the exact source class, does one of the following without hidden SAT search:

1. lowers the NAE transversal / overshoot objective and reconstructs the new integer point; or
2. certifies that no source trade can reduce it; or
3. contracts the add/copy system exactly with a strict polynomial progress measure.

A universal PASS closes the frozen NP-complete linear-cubic Exact-One carrier and therefore, with the existing Karp bridge, implies `P=NP`.

Forbidden shortcuts:
- ordinary real flow with independent incidence values;
- dropping the three-way copy/equality constraint;
- assuming the NAE threshold itself is close to Exact-One;
- enumerating NAE assignments or source trades;
- generic integer generalized-flow oracle;
- fixed local consistency as a completeness claim.

## 8. Ceiling

```text
NAE DEFECT COUNT
|T| = 3|B| - n
= PROVED

EXACT-ONE SAT
iff transversal number = n/3
= PROVED

L1 OBJECTIVE
F = n/3 + 2|B| + 4||p||_1
= PROVED

FIXED-b INTEGER FIBER
r_minority - r_majority1 - r_majority2 = tau
= PROVED EXACT / BIJECTIVE

LOCAL ADDITION
= EASY

THREE-WAY VARIABLE COPY/FANOUT
= SURVIVING GLOBAL COUPLING

UNIVERSAL POLYNOMIAL COPY-FLOW / TRANSVERSAL AUGMENTATION
= OPEN

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
