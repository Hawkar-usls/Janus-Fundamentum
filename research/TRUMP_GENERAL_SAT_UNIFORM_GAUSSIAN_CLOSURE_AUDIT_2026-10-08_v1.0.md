# General SAT — Uniform Gaussian Implication Closure Audit

Date: 2026-10-08

Status:
`GAUSSIAN_IMPLICATION_CLOSURE_SOUND_AND_POLYNOMIAL__NOT_COMPLETE__LOW_NORMAL_RANK_RESIDUE_HAS_EXACT_POLYNOMIAL_TERMINAL`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE GENERAL SAT IN P OR P=NP.

IT AUDITS THE CURRENT UNIFORM-CLOSURE IDEA WITHOUT HIDING BRANCHING.

THE BRANCH-FREE CLOSURE
  Gaussian reduction
  + implication graph
  + SCC equalities
  + failed-lineral equations
IS SOUND AND POLYNOMIAL, BUT NOT COMPLETE.

A FROZEN 3-VARIABLE / 4-CLAUSE 2-XNF INSTANCE IS UNSAT WHILE THE CLOSURE
REACHES A FIXPOINT WITH NO LEARNED AFFINE EQUATION AND RETURNS OPEN.

THE CORRECT NEXT LAYER IS THE SAME AFFINE-FLAT / NORMAL-SPAN QUOTIENT
ALREADY DEVELOPED IN R5 E105-E111.

LOW NORMAL-SPAN RANK r=O(log L) IS A FULLY EXACT POLYNOMIAL TERMINAL.
THE HIGH-RANK CONNECTED RESIDUE REMAINS OPEN.
```

## 1. Repository/review context

The current default branch does not yet contain the uncommitted
`Uniform closure review` implementation described in the active review notes.

The older branch

```text
research/general-sat-universal-closure-v1
```

already preregisters the correct universal contract:

```text
* exact semantics;
* no final OPEN status;
* no hidden unbounded branching;
* total construction + discovery + solving + reconstruction + verification
  bounded by one fixed polynomial.
```

This audit is isolated on a new review branch so it does not overwrite or
pretend to see uncommitted work.

## 2. External anti-loop: 2-XNF already contains the same architecture

Andraschko, Danner and Kreuzer, *SAT Solving Using XOR-OR-AND Normal Forms*,
Mathematics in Computer Science 18, 20 (2024),
DOI 10.1007/s11786-024-00594-x, prove:

```text
* every CNF formula can be converted to equisatisfiable 2-XNF in polynomial
  time;
* consequently 2-XNF SAT is NP-complete;
* implication graph structures can be combined with Gaussian Constraint
  Propagation;
* SCC and failed-lineral in-processing learn new affine equations;
* their complete solver still uses DPLL decisions after closure.
```

Therefore the current repository gap is mathematically real:

```text
finite/polynomial closure != total branch-free solver.
```

A universal completion rule for arbitrary 2-XNF would itself be a P=NP
theorem.

## 3. Representation

A lineral is represented as

```text
L(x)=a dot x XOR c,
```

with a in GF(2)^n and c in GF(2).

A 2-XNF clause

```text
L1 OR L2
```

is false exactly on the affine fiber

```text
L1=0,
L2=0.
```

Hence every 2-XNF clause forbids one affine flat of relative codimension at
most two.

This is the exact same object isolated independently by R5 E105.

## 4. Uniform Gaussian implication closure

Maintain an affine equation system

```text
A x = b.
```

Repeat:

1. Gaussian-reduce every lineral modulo A x=b.
2. Delete clauses already true.
3. Convert a false/linear clause into a forced affine equation.
4. Build the implication graph
   ```text
   NOT L1 -> L2,
   NOT L2 -> L1.
   ```
5. If L and NOT L lie in one SCC, return UNSAT.
6. Mutual reachability of L and M gives the affine equality L=M.
7. A path L -> NOT L forces L=0.
8. A path NOT L -> L forces L=1.
9. Add all learned affine equations by Gaussian elimination and repeat.

Every strict learning round increases the affine rank.

Therefore there are at most n strict Gaussian-learning rounds.

This is a sound branch-free closure.

## 5. Polynomial resource bound

Let:

```text
n = number of base Boolean variables,
m = number of 2-XNF clauses,
q = O(m) distinct linerals in the active graph.
```

A deliberately conservative implementation bound is:

```text
Gaussian reduction / consistency per round:
  poly(n,m), e.g. O(m n^3) with non-incremental elimination;

graph construction:
  O(m);

SCC:
  O(q+m);

all-source reachability / failed-lineral audit:
  O(q(q+m)) <= O(m^2);

number of strict affine-rank rounds:
  <= n.
```

Thus even a simple implementation is bounded by a fixed polynomial such as

```text
O(n m n^3 + n m^2)
```

up to representation constants.

The exact exponent is not the scientific point here. The important property is:

```text
NO BRANCHING IS HIDDEN INSIDE THE CLOSURE.
```

## 6. Why XOR expressions may not be treated as independent Boolean nodes

Take

```text
y1=x1,
y2=x2,
y3=x1 XOR x2.
```

The abstract Boolean truth vector

```text
(y1,y2,y3)=(1,1,1)
```

is impossible.

Gaussian reconstruction sees

```text
x1=1,
x2=1,
x1 XOR x2=1
```

and immediately derives inconsistency.

Therefore any implication-graph assignment must be reconstructed in the
original affine variable space.

A graph-only model over independent lineral nodes is unsound.

The companion checker freezes this exact hazard.

## 7. Frozen closure obstruction

Use three base variables x1,x2,x3 and four clauses:

```text
C1:
  x3
  OR
  (x1 XOR x3)

C2:
  NOT x1
  OR
  NOT(x1 XOR x2)

C3:
  (x1 XOR x2)
  OR
  NOT(x1 XOR x2 XOR x3)

C4:
  NOT x2
  OR
  (x1 XOR x2 XOR x3).
```

Exact enumeration gives:

```text
SAT assignments = 0.
```

Deleting any one clause gives at least one satisfying assignment.

So the witness is irredundantly UNSAT under clause deletion.

## 8. Exact affine-cover structure of the obstruction

Each clause forbids exactly two of the eight points of GF(2)^3.

In integer encoding x1+2x2+4x3, the four forbidden sets are:

```text
B1={0,2}
B2={1,5}
B3={4,7}
B4={3,6}.
```

They are pairwise disjoint and

```text
B1 union B2 union B3 union B4
=
GF(2)^3.
```

Thus UNSAT is a global exact affine cover.

No one clause is locally contradictory and no pairwise overlap is needed.

## 9. Closure result on the obstruction

The Gaussian implication closure reaches a fixed point with:

```text
learned affine rank = 0,
active clauses       = 4,
SCC contradiction    = none,
failed lineral       = none,
verdict               = OPEN.
```

Yet exact semantics is UNSAT.

Therefore:

```text
boxed:
GAUSSIAN + SCC + FAILED-LINERAL CLOSURE IS NOT COMPLETE FOR 2-XNF.
```

This is the required firewall against promoting the current closure merely
because it solves the saved examples.

## 10. The bridge to R5 E105-E111

The remaining 2-XNF problem after Gaussian implication closure is exactly an
affine-flat avoidance problem.

This matches the independent R5 pipeline:

```text
E105:
  one forbidden affine fiber per check;

E106:
  polynomial rank-0/rank-1 affine propagation;

E108:
  quotient by the span of active flat normals;

E109:
  direct-sum normal-matroid component decomposition;

E110:
  exact branch-DP on a supplied low-width rank-2 subspace arrangement;

E111:
  constructive polynomial terminal for sufficiently small branchwidth.
```

So these two research lanes should be unified rather than duplicated.

## 11. Branch-free low-normal-rank terminal

At the closure fixed point, let W be the span of all active affine-flat
normals and let

```text
r=dim W.
```

Every active clause depends only on the quotient by W-perp.

Therefore the complete residual decision factors through exactly

```text
2^r
```

quotient states.

This is exact, not heuristic.

Hence:

```text
r <= C log_2 L
=> 2^r <= L^C
=> exact residual solving is polynomial.
```

The frozen four-clause obstruction has

```text
r=3,
2^r=8,
```

and is therefore solved immediately by this branch-free quotient terminal.

## 12. What remains genuinely OPEN

The universal closure gap is now sharpened.

A hard residual must survive all of:

```text
1. Gaussian equation reduction;
2. implication/SCC closure;
3. failed-lineral closure;
4. exact assignment reconstruction;
5. rank-0/rank-1 affine propagation;
6. low-normal-rank quotient solving;
7. normal-matroid direct-sum decomposition;
8. any polynomially constructible low-width subspace DP terminal.
```

What remains is:

```text
HIGH-RANK,
MATROID-CONNECTED,
HIGH-BRANCHWIDTH
2-XNF AFFINE-FLAT AVOIDANCE
AT A CLOSURE FIXPOINT.
```

For arbitrary 2-XNF this class cannot be dismissed by finite testing because
2-XNF SAT is NP-complete.

## 13. Correct next experiment

Do not add another unrestricted branch fallback.

Build a generator/search for closure-fixed residuals and classify them by

```text
normal rank,
normal-matroid components,
subspace branchwidth,
SAT/UNSAT,
minimum affine-cover multiplicity,
number of forced equations under one hypothetical decision.
```

The target theorem is a genuine dichotomy:

```text
UNIFORM CLOSURE DICHOTOMY

Every closure-fixed 2-XNF residual either

A. has a polynomially bounded normal-span / branchwidth decomposition;

or

B. satisfies a new globally forced affine equality discoverable without
   branching;

or

C. belongs to an explicit high-rank obstruction family.
```

Only A or B with a universal symbolic resource bound would advance the
P=NP route.

C would precisely identify why branching is still necessary.

Scientific status:

```text
UNIFORM_GAUSSIAN_IMPLICATION_CLOSURE = SOUND_POLYNOMIAL_INCOMPLETE.
LOW_NORMAL_RANK_RESIDUE = EXACT_POLYNOMIAL_TERMINAL.
HIGH_RANK_CONNECTED_RESIDUE = OPEN.
GENERAL_SAT_IN_P = NOT_PROVED.
P_VS_NP = OPEN.
```
