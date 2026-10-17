# R5 E9 — Primitive Nullity-2 Falsifier for the Naive Block-System Route

Date: 2026-09-27

Status:
`JANUS_EXACT_FINITE_STRUCTURAL_FALSIFIER__NO_D1_PROMOTION`

Scientific firewall:

```text
THIS FALSIFIES ONLY THE NAIVE IMPLICATION
  singular / nullity>=2 => imprimitive permutation action.

IT DOES NOT FALSIFY AN ASYMPTOTIC THEOREM WITH
  nullity_Q(A)=omega(log n)
OR OTHER ADDITIONAL HYPOTHESES.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parent:
- `R5_E9_LEVI_GENERAL_FACTOR_TWO_PERM_NORMAL_FORM_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_primitive_nullity2_falsifier.py`

## 1. Explicit carrier

Take `n=12` and define permutations in zero-based image notation

```text
p = [9,4,6,1,10,8,7,2,0,5,11,3]
q = [3,8,4,5,0,11,10,1,7,6,9,2]
```

Let `P,Q` be their permutation matrices and

\[
A=I+P+Q.
\]

Thus row `i` has support

\[
T_i=\{i,p(i),q(i)\}.
\]

The 12 row supports are

```text
0:  {0,9,3}
1:  {1,4,8}
2:  {2,6,4}
3:  {3,1,5}
4:  {4,10,0}
5:  {5,8,11}
6:  {6,7,10}
7:  {7,2,1}
8:  {8,0,7}
9:  {9,5,6}
10: {10,11,9}
11: {11,3,2}
```

Each symbol occurs in exactly three rows because `I,P,Q` are permutation matrices.
Every row has three distinct symbols.
Exhaustive pair checking shows that no unordered pair of symbols occurs in two rows. Hence `A` is a linear cubic square carrier, equivalently a `12_3` configuration.

## 2. Exact rational nullity

Exact Gaussian elimination over `Q` gives

```text
rank_Q(A) = 10
nullity_Q(A) = 2.
```

Therefore this is not a full-rank terminal and has a genuinely multidimensional rational kernel.

## 3. Exact-One witness

The Boolean vector

```text
x = [1,1,0,0,0,0,1,0,0,0,0,1]
```

satisfies

\[
Ax=\mathbf 1.
\]

Equivalently

```text
selected columns = {0,1,6,11}
```

meet every source row exactly once, and

\[
w=3x-\mathbf1\in\{-1,2\}^{12}
\]

lies in `ker_Q(A)`.

The executable checker additionally enumerates all `2^12` Boolean assignments and confirms that this witness is unique.

## 4. Primitivity certificate by exhaustive block rejection

Let

\[
\Gamma=\langle p,q\rangle.
\]

The action is transitive.

For a transitive action of degree 12, any nontrivial block containing 0 must have size dividing 12, hence size in

```text
{2,3,4,6}.
```

The checker enumerates every subset `B` containing 0 of each of these sizes. For each candidate it computes the orbit of `B` under `p,q,p^{-1},q^{-1}` and rejects `B` if some translate intersects `B` without being equal to `B`. Every candidate is rejected.

Therefore `Gamma` has no nontrivial block system:

\[
\boxed{\Gamma\text{ is primitive}.}
\]

As an optional independent diagnostic, a Schreier-Sims computation identifies the generated group as the full symmetric group `S_12`; that stronger identification is not needed for the theorem.

## 5. Falsified structural shortcut

The explicit carrier proves

\[
\boxed{
\text{linear cubic }A=I+P+Q,
\ \nu_{\mathbb Q}(A)=2
\ \centernot\Rightarrow\
\langle p,q\rangle\text{ imprimitive}.
}
\]

Since the example is SAT, neither satisfiability nor the existence of the special `{-1,2}` kernel point forces imprimitivity either.

Therefore the following proof-search shortcuts are now forbidden:

```text
singular => nontrivial permutation block system
nullity>=2 => nontrivial permutation block system
SAT + singular => nontrivial permutation block system
{-1,2} kernel witness => nontrivial permutation block system
```

## 6. What remains alive

This finite example does **not** settle the actual asymptotic residual

```text
nullity_Q(A)=omega(log n).
```

It leaves open stronger statements of the form

```text
large enough asymptotic nullity
+ exact linearity
+ OET-irreducibility
+ additional certified invariant
=> exact quotient/decomposition,
```

but any such theorem must use more than mere singularity or fixed positive nullity.

The next attack should therefore compare nullity growth against structural invariants that can scale with `n`, rather than trying to derive a block system from the existence of a kernel alone.

## 7. Ceiling

```text
EXPLICIT LINEAR 12_3 TWO-PERM CARRIER
= VERIFIED

rank_Q(A)=10
= VERIFIED

nullity_Q(A)=2
= VERIFIED

EXACT-ONE WITNESS
= VERIFIED

<p,q> TRANSITIVE AND PRIMITIVE
= VERIFIED

NAIVE nullity>=2 => imprimitive
= FALSIFIED

ASYMPTOTIC omega(log n) => quotient/decomposition
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
