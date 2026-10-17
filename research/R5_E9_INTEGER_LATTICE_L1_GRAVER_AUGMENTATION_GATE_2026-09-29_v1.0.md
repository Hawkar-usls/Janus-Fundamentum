# R5 E9 — Integer-lattice L1 / Graver augmentation gate

Date: 2026-09-29
Status: THEOREM-LEVEL EXACT REFORMULATION; UNIVERSAL POLYNOMIAL STEP ORACLE OPEN
Scope: square cubic Exact-One source after the integer-lattice membership terminal; theorem itself holds for every integer matrix A with right-hand side 1.

## 1. Scientific firewall

This note does **not** prove P=NP and does **not** admit E8-D1.

What is proved here is an exact reformulation of Boolean Exact-One feasibility as separable convex integer minimization over the affine integer lattice, together with an exact gap-2 certificate. Known Graver-basis augmentation theory supplies polynomially many augmentation iterations when an appropriate Graver-best augmentation can be obtained. It does **not** supply, for the unrestricted source matrices in this program, a polynomial-time procedure for constructing that augmentation direction.

Accordingly the new live primitive is:

```text
LINEAR_CUBIC_GRAVER_BEST_STEP(A,z,l,u)
```

and its deterministic polynomial-time realizability remains OPEN.

## 2. Exact L1 reformulation

Let

```math
L_A := \{z\in\mathbb Z^n : Az=\mathbf 1\}
```

and define

```math
F(z):=\sum_{i=1}^n |2z_i-1|.
```

For every integer `k`, `2k-1` is a nonzero odd integer. Hence

```math
|2k-1|\ge 1,
```

with equality iff `k\in\{0,1\}`.

Therefore for every `z\in\mathbb Z^n`,

```math
F(z)\ge n,
```

and

```math
F(z)=n \iff z\in\{0,1\}^n.
```

Consequently, whenever `L_A` is nonempty,

```math
\boxed{
A x=\mathbf 1\text{ for some }x\in\{0,1\}^n
\iff
\min_{z\in L_A} F(z)=n.
}
```

If `L_A` is empty, the existing Smith/Hermite integer-lattice terminal already proves UNSAT.

## 3. Exact gap 2

Every summand `|2z_i-1|` is a positive odd integer. Its minimum is 1 and the next possible value is 3. Thus, if no Boolean point exists in `L_A`, every feasible integer point has at least one non-Boolean coordinate and

```math
\boxed{F(z)\ge n+2.}
```

Hence the optimum has a discrete exact dichotomy:

```text
OPT = n      <=> Exact-One SAT
OPT >= n+2   => Exact-One UNSAT
```

There is no `n+1` case.

## 4. Finite-box reduction from any lattice witness

Suppose the Smith/Hermite stage returns an integer feasible point `z^(0)` and let

```math
F_0 := F(z^{(0)}).
```

Any optimum `z*` satisfies `F(z*)\le F_0`. Therefore each coordinate individually obeys

```math
|2z_i^*-1|\le F_0,
```

so

```math
\frac{1-F_0}{2}\le z_i^*\le\frac{1+F_0}{2}.
```

Thus the unbounded-looking affine-lattice optimization is exactly reducible to a bounded separable convex integer program. When the initial lattice witness is returned with polynomial encoding length, these bounds also have polynomial encoding length.

## 5. Graver augmentation interface

`F` is separable convex on the integer lattice. Classical Graver-basis augmentation theory gives an exact optimality/augmentation framework for bounded separable convex integer minimization and shows that greedy Graver augmentation needs only polynomially many augmentation iterations under the corresponding oracle/access assumptions.

For this program the relevant prospective solver is:

1. Use Smith/Hermite membership to reject `L_A=\varnothing` or obtain `z^(0)\in L_A`.
2. Construct the finite box above.
3. Repeatedly call `LINEAR_CUBIC_GRAVER_BEST_STEP(A,z,l,u)`.
4. Stop when no improving Graver step exists; Graver optimality then gives a global optimum of `F`.
5. Return SAT iff the optimum is exactly `n`; otherwise return UNSAT (necessarily `>=n+2`).

This route is sound and complete **conditional on** a correct Graver-best-step implementation. It is not yet a polynomial algorithm because step 3 has not been proved polynomial on the unrestricted linear-cubic carrier.

## 6. Relation to the projection hierarchy

This is not another fixed-k local projection test. Unary/pair/triple lattice projections inspect low-dimensional shadows of `L_A`. The L1 objective instead asks for the globally closest affine-lattice point to the Boolean cube in the exact separable metric

```math
F(z)-n = 2\sum_i \operatorname{dist}(z_i,\{0,1\}).
```

Indeed, for integer `k`,

```math
|2k-1|-1=2\operatorname{dist}(k,\{0,1\}).
```

Therefore

```math
\boxed{
\frac{F(z)-n}{2}
=
\sum_i \operatorname{dist}(z_i,\{0,1\}).
}
```

The optimization target is exactly total integer-coordinate distance from the Boolean cube.

## 7. Frozen controls

### PG15 SAT control

For the frozen SAT incidence matrix, the known Boolean witness has support (0-based)

```text
{0,4,6,8,13}
```

and therefore `F=15=n`.

### PG15 UNSAT control

For the frozen UNSAT incidence matrix, the explicit integer lattice point

```text
z = [0,0,1,0,1,1,0,-1,0,0,1,0,1,1,0]
```

satisfies `Az=1` and has

```text
F(z)=17=n+2.
```

Exact Boolean enumeration on this n=15 control is UNSAT. The gap theorem then gives `OPT>=17`, while the displayed integer point gives `OPT<=17`, so

```math
\boxed{OPT=17.}
```

Thus the frozen SAT/UNSAT controls sit on the two closest possible objective levels, 15 and 17.

## 8. New exact frontier

The theorem isolates a single global algorithmic question:

```text
R5_E9_LINEAR_CUBIC_GRAVER_BEST_STEP_POLYTIME_GATE_V1

INPUT:
  connected square linear-cubic source A,
  integer feasible z,
  polynomial-bit box l <= z <= u,
  separable objective F(z)=sum_i |2 z_i-1|.

QUESTION:
  Can a best (or provably sufficient approximate greedy) feasible
  Graver augmentation be found deterministically in polynomial time
  from A,z,l,u, without enumerating an exponential Graver basis?
```

PASS would combine with the already established lattice membership layer and known augmentation-count theory to yield a polynomial solver for this Exact-One source carrier. FAIL must exhibit a rigorous obstruction to this specific primitive; generic NP-hardness rhetoric is not a substitute.

## 9. Epistemic status

```text
EXACT_L1_EQUIVALENCE          = PROVED
GAP_2                         = PROVED
FINITE_BOX_FROM_LATTICE_POINT = PROVED
PG15_SAT_CONTROL              = PASS
PG15_UNSAT_OPTIMUM_17         = PASS
GRAVER_AUGMENTATION_COUNT     = KNOWN_CONDITIONAL_TOOL
GRAVER_BEST_STEP_POLYTIME     = OPEN
E8_D1                         = EMPTY
P_VS_NP                       = OPEN
```

## 10. Prior-art boundary

Relevant prior art: R. Hemmecke, S. Onn, R. Weismantel, *A polynomial oracle-time algorithm for convex integer minimization*, Mathematical Programming 126 (2011), 97–117; arXiv:0710.3003. The paper establishes polynomially many greedy augmentation steps using suitable Graver directions for separable convex integer minimization and structured polynomial-time consequences. It is used here only for that augmentation framework; it is **not** cited as a polynomial constructor for Graver-best steps of arbitrary source matrices.