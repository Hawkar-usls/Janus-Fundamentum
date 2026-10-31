# R5 E9 — Bounded-Support Affine Kernel Descent Barrier

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_BARRIER_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Parents:
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_POLYSIZE_2GROUP_FIXED_GIRTH_COVER_THEOREM_2026-09-26_v1.0.md`
- `R5_E9_WDR_LEAN_NORMAL_FORM_SCHEDULER_CONTRACT_2026-09-23_v1.0.md`

Checker support:
`experiments/r5_e9_cubic_exact_one_affine_coset_minweight.py`

Scientific firewall:

```text
THIS BLOCKS ONLY BOUNDED-SUPPORT PARITY-PRESERVING REPAIR.
IT DOES NOT BLOCK NONLOCAL POLYNOMIAL REPAIR.
IT DOES NOT PROVE P!=NP.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Kernel vectors force incidence cycles

Let `H=(V,E)` be a 3-uniform hypergraph with minimum vertex degree at least two,
and let `A` be its edge-by-vertex incidence matrix over `F_2`.

Take a nonzero vector

```text
z in ker_F2(A)
```

and put

```text
S = {v in V : z_v=1}.
```

For every hyperedge `e`, parity gives

```text
|e intersect S| = 0 or 2,
```

because an even subset of a 3-set has size zero or two.

Consider the bipartite incidence graph restricted to:

- the selected variable vertices `S`;
- all clause/hyperedge vertices touching `S`;
- all incidence edges between them.

Every selected variable keeps all of its original incident edges and therefore
has degree at least two in this restricted graph.
Every touched hyperedge has degree exactly two because it contains exactly two
selected variables.

Thus the restricted finite graph has minimum degree at least two and therefore
contains a cycle.

If the full incidence graph has girth `g`, every such cycle has length at least
`g`.
A bipartite incidence cycle alternates selected variables and hyperedges, so a
cycle of length `2r` uses exactly `r` distinct selected variables.  Since the
cycle variables are contained in `S`,

```text
2 |S| >= g.
```

Therefore:

### Theorem BKD-1 — kernel distance from incidence girth

```text
for every nonzero z in ker_F2(A):
    |z| >= g/2.
```

Equivalently, the binary code `ker_F2(A)` has minimum distance at least half the
incidence girth.

No coding-theory black box is needed for this inequality; it is the direct
cycle argument above.

## 2. Consequence for bounded-support repair

Fix an integer `k>=1` and suppose

```text
g > 2k.
```

Then BKD-1 implies

```text
there is no nonzero z in ker_F2(A) with |z|<=k.
```

Hence no transformation

```text
x -> x XOR z
```

can move between two distinct parity solutions while changing at most `k`
Boolean coordinates.

This blocks not only a literal "flip one small kernel word" implementation.  Any
parity-preserving repair whose pre-state and post-state differ on at most `k`
variables has difference vector in `ker A`, and therefore must be the identity.

## 3. Satisfiable high-girth controls exist for every fixed support cap

Take any connected satisfiable cubic 3-uniform base instance, for example the
`AFFINE_3X3` control used by the companion checker.

Fix `k` and choose a fixed girth target

```text
g >= 2k+2.
```

The existing JANUS polynomial-degree 2-group fixed-girth cover theorem gives a
connected finite cover of the cubic bipartite incidence graph with

```text
girth >= g.
```

A graph cover preserves the bipartition and cubic degrees.  Pull an Exact-One
base witness back along the covering projection: every lifted clause sees the
same three Boolean values as its base clause, hence exactly one true value.
Therefore the lifted cubic 3-uniform instance remains satisfiable.

So for every fixed `k` there is a satisfiable cubic high-girth Exact-One
instance such that

```text
NO NONZERO PARITY-PRESERVING MOVE OF SUPPORT <= k EXISTS.
```

Yet a global descent still exists.

Indeed the all-ones vector is always a parity solution.  If `y` is any lifted
Exact-One witness, then

```text
z_global = 1 XOR y
```

lies in `ker A` and sends the all-ones state to `y`.
For a cubic instance on `n` variables,

```text
|y| = n/3,
|z_global| = 2n/3.
```

Thus the obstruction is genuinely locality/support, not absence of a descent
direction.

## 4. WDR R5/R6 interpretation

After the affine-coset representation change, consider an `R5` structural
dominance or `R6` ranked/SR macro whose certified action:

1. stays inside the parity coset `A x=1 (mod 2)`;
2. changes at most a fixed `k` coordinates of the current assignment/state;
3. is expected to obtain strict Hamming-weight / defect descent.

For the high-girth satisfiable instance constructed above, no such nonidentity
move exists at all.

Therefore:

```text
FIXED-SUPPORT AFFINE REPAIR
!=
UNIVERSAL R5/R6 CURRENCY.
```

The next viable affine-coset mechanism must be nonlocal in support, or must use
a quotient/decomposition that is not equivalent to a bounded coordinate flip.

## 5. Why this is stronger than a finite counterexample

This is a quantified theorem schema:

```text
for every fixed k
there exists a satisfiable cubic Exact-One instance
on which every parity-preserving <=k-coordinate move is identity.
```

The construction route is source-bound to the already established fixed-girth
cover theorem.  It is not an empirical claim from a few random instances.

It still does not rule out:

- support growing with input size;
- a large-support kernel direction synthesized in polynomial time;
- global algebraic quotienting;
- decomposition into polynomial carriers;
- a representation change that does not preserve the affine parity state at
  each intermediate step.

Those remain the live routes.

## 6. Connection to local-search traps

The companion affine theorem gives the exact potential

```text
rho(x)=|x|,
t(x)=(3|x|-n)/2
```

on cubic parity solutions.

High girth now proves that this potential can have no admissible small-support
neighbor at all, even though a much lower global state exists on satisfiable
instances.

So a proof of universal progress cannot take the form

```text
if rho(x)>n/3,
then some constant-size kernel repair lowers rho.
```

That statement is false.

Any valid universal descent theorem must explicitly synthesize a nonlocal
object.

## 7. New active gate

Freeze:

```text
R5_E9_NONLOCAL_AFFINE_COSET_DESCENT_OR_QUOTIENT_GATE_V1
```

Input:

```text
connected cubic incidence A,
A x = 1 (mod 2),
current parity solution x,
minimum target n/3.
```

Allowed PASS forms:

1. construct a possibly large-support `z in ker A` with certified strict weight
   decrease in deterministic polynomial time;
2. compute a polynomial quotient of the coset/weight objective with exact
   witness reconstruction and strict dimension/size progress;
3. decompose the noncommuting `I+P+Q` overlay into independently solvable
   pieces with polynomial total cost;
4. enter another already proved polynomial carrier.

Mandatory adversaries:

- fixed-girth lifted satisfiable controls from this theorem;
- the current high-nullity / phase-FAIL family and its covers;
- Fano UNSAT control;
- `AFFINE_3X3` SAT control;
- noncommuting large-nullity `I+P+Q` survivors.

Forbidden:

- bounded-support local flip as the only progress theorem;
- existential "there is a better coset point" without polynomial synthesis;
- exhaustive search over kernel basis coefficients;
- syndrome-decoding / SAT oracle calls;
- uncharged certificate discovery.

## 8. Ceiling

```text
NONZERO BINARY KERNEL SUPPORT
>= incidence_girth/2

FOR EVERY FIXED k
HIGH-GIRTH SAT CONTROL WITH NO <=k MOVE
= PROVED FROM COVER THEOREM

CONSTANT-SUPPORT R5/R6 AFFINE DESCENT
= CLOSED AS UNIVERSAL ROUTE

NONLOCAL LARGE-SUPPORT DESCENT / QUOTIENT
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
