# R5 E9 — Integer-lattice pair-projection 2-SAT terminal

Date: 2026-09-29
Status: PROVED POLYNOMIAL NECESSARY TERMINAL
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## 1. Motivation

The Smith/Hermite terminal tests only whether the affine Diophantine system

```math
Ax=\mathbf 1,\qquad x\in\mathbb Z^n
```

is nonempty.  RKPR extracts affine Boolean restrictions only when two rational-kernel coordinate functionals are projectively proportional.

There is a strictly stronger polynomial layer: project the **integer affine solution lattice** onto every one- and two-coordinate Boolean face.

---

## 2. Integer extendability relations

Let

```math
L_A=\{x\in\mathbb Z^n:Ax=\mathbf1\}.
```

For each coordinate `i` define

```math
D_i=\{a\in\{0,1\}:\exists x\in L_A,\ x_i=a\}.
```

For each pair `i<j` define

```math
R_{ij}=\{(a,b)\in\{0,1\}^2:\exists x\in L_A,\ x_i=a,\ x_j=b\}.
```

Each membership query is an integer linear-system feasibility test:

```math
Ax=\mathbf1,
```

plus one or two equations fixing coordinates to `0` or `1`.

By Smith/Hermite normal form, every such query is decidable in polynomial bit complexity.  There are only `2n+4*binom(n,2)=O(n^2)` queries.

---

## 3. Induced Boolean 2-CSP

Construct a Boolean formula `Phi_A` as follows.

- If `a notin D_i`, add the unit clause `x_i != a`.
- For every `(a,b) notin R_ij`, add the binary clause

```text
(x_i != a) OR (x_j != b).
```

Every Boolean Exact-One witness belongs to `L_A`, so it satisfies every one- and two-coordinate projection. Therefore

```math
Ax=\mathbf1,\ x\in\{0,1\}^n
\quad\Longrightarrow\quad
\Phi_A(x)=\mathrm{TRUE}.
```

`Phi_A` is a 2-CNF formula of polynomial size.  Hence:

### Theorem ILPP2-1

```text
if Phi_A is UNSAT:
    A is Exact-One UNSAT.
```

The complete construction and 2-SAT solve are deterministic polynomial-time, including bit complexity of the integer-feasibility queries.

If `Phi_A` returns an assignment, the assignment must still be checked against `Ax=1`.  A satisfiable projection formula is only a necessary relaxation, not a completeness theorem.

---

## 4. Relationship to existing terminals

### 4.1 Global Smith/Hermite membership

If `L_A` is empty, every coordinate state is nonextendable, so `Phi_A` is immediately inconsistent. Thus the pair-projection terminal subsumes the previous global integer-lattice rejection.

### 4.2 RKPR

For the cubic source carrier, `A 1 = 3 1`, so every rational solution is

```math
x=\frac13\mathbf1+y,\qquad y\in\ker_Q(A).
```

If two rational-kernel coordinate rows are projectively related by `b_i=lambda b_j`, then all rational solutions satisfy

```math
x_i-\frac13=\lambda\left(x_j-\frac13\right).
```

The RKPR compatibility cases `lambda in {1,-2,-1/2}` and all illegal-ratio/pinning consequences are therefore visible in the corresponding Boolean pair projection.  Integer pair projection can additionally impose restrictions caused by congruence/lattice structure even when the two rational-kernel rows are not projectively proportional.

---

## 5. Strict cubic control beyond SNF + RKPR

Define a connected square cubic source on `n=24` by

```text
A = I + P + Q
```

with zero-based permutations

```text
P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,1,21,22,11,3,12,15,20,5,0,9,8,14,18]
```

Exact arithmetic gives

```text
connected                 = true
row/column degree         = 3
rank_Q(A)                 = 21
nullity_Q(A)              = 3
1 in A Z^24               = true
rank_F2(A)=rank_F2([A|1]) = 21
rank_F3(A)=rank_F3([A|1]) = 20
```

The nonzero Smith invariant products of `A` and `[A|1]` are both `3`, so the global integer-lattice terminal passes.

The rational-kernel projective classes are

```text
{9,16,18}
{1,17}
{2,11}
{6,15}
{8,14}
{12,21}
```

plus eleven singletons.  Every nontrivial class has scalar ratio `+1`; there are no zero kernel rows, no `-2/-1/2` pins, and no illegal RKPR ratios.  Hence RKPR also passes after equality quotient.

This control is intentionally **not linear**: exactly four row pairs meet in two columns.  Therefore it falsifies a shortcut on the full cubic RX3C carrier, not a theorem restricted to linear cubic hypergraphs.

### 5.1 Pair-projection contradiction

Exact Smith/Hermite feasibility of the four Boolean states gives

```text
R_{5,12} = {(1,0)}
R_{3,5}  = {(1,0)}
```

(indices zero-based).

The first relation forces `x_5=1`; the second forces `x_5=0`.  Therefore `Phi_A` is UNSAT and the source has no Boolean Exact-One witness.

Coordinates `3`, `5`, and `12` are not members of a common RKPR projective class, so this contradiction is not a repackaging of the old proportional-row terminal.

Thus the pair-projection layer is **strictly stronger than global SNF + RKPR on the cubic source carrier**.

---

## 6. Algorithm

```text
INTEGER_LATTICE_PAIR_2SAT(A):
    if 1 not in A Z^n:
        return UNSAT

    for each i and a in {0,1}:
        test integer feasibility of Ax=1, x_i=a
        add a unit clause for every infeasible state

    for each i<j and (a,b) in {0,1}^2:
        test integer feasibility of Ax=1, x_i=a, x_j=b
        add clause (x_i!=a) OR (x_j!=b) when infeasible

    solve the resulting 2-CNF Phi_A

    if Phi_A is UNSAT:
        return UNSAT

    if a returned assignment satisfies Ax=1:
        return SAT + witness

    return UNRESOLVED
```

The router is sound and polynomial. It is not complete in this note.

---

## 7. Live conjecture boundary

A falsifier search on finite controls has not yet produced a **linear-cubic** UNSAT source which passes global SNF + RKPR.  This is only experimental evidence and is not promoted to a theorem.

The live gate is therefore:

```text
R5_E9_POST_SNF_RKPR_LINEAR_CUBIC_SUFFICIENCY_FALSIFIER_GATE_V1
```

Question:

```text
Does a connected square linear-cubic source exist that
passes integer-lattice membership and exhaustive RKPR,
but is still Exact-One UNSAT?
```

Until this is proved or falsified, no universal polynomial promotion is allowed.

---

## 8. Firewall

Proved:

```text
INTEGER-LATTICE PAIR PROJECTIONS ARE POLYNOMIALLY COMPUTABLE
THE INDUCED BOOLEAN 2-CSP IS A SOUND POLYNOMIAL UNSAT TERMINAL
THE TERMINAL IS STRICTLY STRONGER THAN GLOBAL SNF + RKPR ON AN EXPLICIT CUBIC CONTROL
```

Not proved:

```text
PAIR-PROJECTION 2-SAT IS COMPLETE
SNF + RKPR IS SUFFICIENT ON LINEAR CUBIC SOURCES
P = NP
```

Canonical state remains

```text
E8_D1   = EMPTY
P_VS_NP = OPEN
```
