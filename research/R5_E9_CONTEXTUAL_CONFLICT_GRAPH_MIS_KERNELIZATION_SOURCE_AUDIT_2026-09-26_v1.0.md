# R5 E9 — Contextual Conflict-Graph MIS Kernelization Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__KNOWN_MIS_REDUCTIONS_IMPORTED_AS_CONTEXTUAL_DOMINANCE_DONORS`

Immediate predecessors:

```
PA-0017-PERFECT-KERNEL-CONFLICT-GRAPH-SOURCE-AUDIT
NM-0022-CUBIC-CONFLICT-GRAPH-OBSTRUCTION
NM-0023-CONFLICT-ODD-HOLE-COVERAGE-SELECTOR-CONSERVATION
NM-0024-ODD-HOLE-FULL-BOUNDARY-DELTA-MATROID-BARRIER
PA-0020-ODD-HOLE-CONTEXTUAL-MULTISELECTOR-DOMINANCE
NM-0025-CUBIC-SOURCE-BOUNDARY-PINNING
```

## G0 — exact changed object

NM-0025 proves that a context-independent odd-hole state merge cannot be
justified by saying that the outside language is weaker than arbitrary CNF:
every complete boundary assignment can already be pinned by a cubic positive
Exact-One source context.

The surviving question is therefore instance-specific:

> Can the actual conflict graph / outside source context certify that one or
> more selector states are unnecessary, and delete them with exact witness
> reconstruction?

NM-0022 already gives the exact bridge

```
source Exact-One SAT
iff
alpha(C(A)) = n/3.
```

This audit asks what established maximum-independent-set reduction machinery
already supplies before JANUS invents a new contextual dominance rule.

## G1 — internal anti-duplication

Repository-first search covered the existing JANUS material on:

- witness dominance and grouped witness contraction;
- matching / linear autarkies;
- resolution-certified dominance barriers;
- odd-hole selector conservation;
- full-boundary delta-matroid / matching barriers;
- perfect-graph conflict P-island;
- Kettani bounded-treewidth falsification;
- rank-3 exact-cover / local matching-gadget barriers.

No current repository artifact source-binds the standard exact MIS
kernelization stack (domination / folding / unconfined / critical-set / crown
style reductions) back into the exact `alpha=n/3` conflict-graph semantics.

This is therefore a source reconciliation layer, not a claim that those graph
reductions are new.

## G2 — exact MIS reduction language is source-bound

### S1 — simple exact reductions and kernelization

Strash (COCOON 2016; arXiv:1608.00724), *On the Power of Simple Reductions for
the Maximum Independent Set Problem*, studies exact MIS kernelization and in
particular isolated-vertex / isolated-clique, vertex-folding and
critical-independent-set reductions.

Hespe--Schulz--Strash (ALENEX 2018; JEA 2019), *Scalable Kernelization for
Maximum Independent Sets*, develop a scalable exact kernelization pipeline
using the standard reduction family and matching-based machinery.

Classification:

```
EXACT MIS KERNELIZATION
=
SOURCE-BOUND DONOR.
```

### S2 — contextual branch deletion / unconfined style reductions

Akiba--Iwata, *Branch-and-reduce exponential/FPT algorithms in practice:
A case study of vertex cover*, TCS 609 (2016), use polynomially checkable
reduction rules and packing constraints that delete/fix vertices while
preserving optimum reconstruction.

The independent-set dual gives the same style of context-specific state
elimination.

Classification:

```
CONTEXT-SPECIFIC GRAPH REDUCTION
=
SOURCE-BOUND DONOR.
```

### S3 — critical independent sets / crowns

Butenko--Trukhanov, *Using critical sets to solve the maximum independent set
problem*, Operations Research Letters 35 (2007), show that the critical
independent-set problem is polynomially solvable and use a nonempty critical
independent set to reduce MIS exactly.

Crown / critical-set language is therefore an already established grouped
contraction mechanism.

Classification:

```
CRITICAL-SET / CROWN GROUPED CONTRACTION
=
SOURCE-BOUND DONOR.
```

### S4 — struction

Alexe--Hammer--Lozin--de Werra, *Struction revisited*, Discrete Applied
Mathematics 132 (2003), review a graph transformation applicable to an
arbitrary vertex that reduces the stability number by exactly one.

The key firewall is equally source-bound: unrestricted repeated struction can
increase graph size dramatically, so

```
ALPHA DROP
ALONE
!=
POLYNOMIAL TOTAL-STATE GUARANTEE.
```

This directly matches the JANUS cumulative-state firewall.

### S5 — claw-free polynomial island

Minty (1980) and Sbihi (1980) established polynomial algorithms for maximum
independent set on claw-free graphs; Nakamura--Tamura (2001) repair the
weighted Minty implementation.

More recent work continues to use claw-free MWIS as a standard polynomial
base class.

Therefore:

```
CONFLICT GRAPH CLAW-FREE
->
EXACT POLYNOMIAL SOURCE-BOUND ISLAND.
```

This island is not contained in the perfect-graph island: claw-free imperfect
graphs (for example graphs with an induced C5) exist.

The extension cannot be promoted to all `K1,4`-free graphs.  The current
cubic Exact-One conflict class is itself `K1,4`-free, while the source problem
remains the known cubic rank-3 hard layer.

## G3 — why every cubic conflict graph is K1,4-free

For a source variable x, its three source clauses have the form

```
{x,y_1,z_1},
{x,y_2,z_2},
{x,y_3,z_3}.
```

Every neighbor of x lies in one of the three pairs

```
{y_1,z_1}, {y_2,z_2}, {y_3,z_3},
```

and the two vertices within each pair are adjacent because they share the
same clause.

Hence an independent set in N(x) contains at most one vertex from each pair:

```
alpha(C(A)[N(x)]) <= 3.
```

So no induced `K1,4` can be centered at x.

Moreover, any induced claw centered at x uses exactly one leaf from each of
the three source-clause pairs.  This is the canonical source geometry of the
remaining contextual pivot.

## G4 — exact transfer to the JANUS decision target

Any source-backed graph reduction supplying

```
alpha(G) = delta + alpha(G')
```

together with polynomial reconstruction of a maximum independent set transfers
immediately to the cubic Exact-One decision:

```
SAT(source)
iff
alpha(G') = n/3 - delta.
```

If the reduced graph is solved and reconstructs an independent set of size
`n/3` in the original conflict graph, NM-0022 converts that set directly to
the true-variable set of an Exact-One witness.

This means the established MIS reductions are legitimate contextual
witness-dominance modules; they do not have to preserve the cubic graph class
after the reduction.

## G5 — what the sources do NOT provide

No checked source proves that exhaustive application of the known polynomial
MIS reductions empties every cubic Exact-One conflict graph, or even every
odd-hole survivor of PA-0020/NM-0025.

Likewise, general struction is not a free universal algorithm because its
intermediate graph can grow superpolynomially.

Therefore known MIS kernelization narrows the live residual but does not close
it.

## Audit decision

Freeze:

```
PA-0022
CONTEXTUAL CONFLICT-GRAPH MIS KERNELIZATION
=
PASS_SCOPED_GAP_CONFIRMED

DOMINATION / FOLDING / UNCONFINED / CRITICAL-SET / CROWN STYLE REDUCTIONS
=
SOURCE-BOUND CONTEXTUAL DOMINANCE DONORS

STRUCTION
=
SOURCE-BOUND ALPHA-REDUCTION DONOR
WITH POLYNOMIAL-STATE FIREWALL

CLAW-FREE CONFLICT GRAPH
=
SOURCE-BOUND P-ISLAND

GENERAL K1,4-FREE CUBIC CONFLICT GRAPH
=
NOT CLOSED

NEW MATH AUTHORIZED ONLY AFTER KNOWN REDUCTION CLOSURE
=
R5_E9_ODD_HOLE_CONTEXTUAL_MIS_KERNEL_LEAN_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
