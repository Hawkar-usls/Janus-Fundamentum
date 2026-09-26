# R5 E9 — Filtered High-Nullity Graph-Cover Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__COVER_AND_NULLITY_DONORS_SOURCE_BOUND`

Immediate predecessors:

```
R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM
R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND
PA-0001-PERFECT-KERNEL
NM-0027-REGULAR-UNIFORM-CONFLICT-EXPANSION
PA-0024-ODD-HOLE-HIGH-GIRTH-ATTACHMENT
NM-0028-HIGH-GIRTH-ODD-HOLE-SPARSE-ATTACHMENT
```

## G0 — exact changed object

NM-0028 proves that untouched cubic source geometry plus 2-expansion does not
force useful local overlap around an odd hole.  Its finite Harries control is,
however, caught by the rational-nullity-zero polynomial lane.

The changed question therefore uses promises that NM-0028 deliberately did not:

```
connected cubic positive Exact-One source
+
incidence girth at least 10 / sparse odd-hole geometry
+
rational nullity beyond the low-nullity lane
+
normalized P,Q noncommuting
+
Z3 phase FAIL.
```

The audit asks whether public matrix-rank, graph-cover, spectral-lift, or
singular-regular-graph theory already forces tractability or a local structural
defect in this combined class.

## G1 — internal anti-duplication

Repository-first replay finds:

### Cubic kernel-word normal form

For the square cubic incidence matrix A,

```
Ax=1, x Boolean
iff
Az=0, z in {-1,2}^n.
```

The exact solver is

```
2^d poly(n),  d=dim_Q ker(A).
```

Thus `d=O(log n)` is already a polynomial island and any new large-nullity
construction must leave that lane asymptotically, not merely be singular.

### Z3 phase island

The phase test exactly captures the one-dimensional character zero-mode sector.
Phase PASS is a polynomial YES certificate, while phase FAIL removes only that
sector.

The repository already contains a noncommuting, linearly large-nullity,
phase-PASS easy family.  Therefore neither large nullity nor noncommutativity
alone is leverage.

### NM-0028

High-girth cubic source geometry can have a maximally sparse odd-hole
neighborhood, but the Harries finite control has rational nullity zero.

No internal artifact combines high girth, genuinely large rational nullity,
noncommuting normalization and phase FAIL in one source-valid family.

## G2 — canonical external language

The changed object intersects four standard subjects:

1. square 0/1 matrices with constant row and column sum three;
2. singular / high-nullity regular bipartite graphs;
3. graph covers / lifts and old-vs-new spectrum;
4. voltage lifts and prescribed girth.

For a square bipartite incidence matrix A, the adjacency matrix of the Levi
graph is

```
L = [ 0  A
      A^T 0 ].
```

Hence

```
nullity(L)=2 nullity(A).
```

So spectral nullity of the bipartite graph and rational nullity of the JANUS
incidence matrix are exactly linked.

## G3 — public-source exhaustion

### S1 — constant-line-sum rank flexibility is classical

Pullman--Stanford (1988), *Singular (0,1) matrices with constant row and column
sums*, explicitly construct n x n 0/1 matrices of constant line sum k and
prescribed rank.  Their abstract states that all possible singular ranks are
settled for k<=3.

Earlier minimum-rank work also obtains the exact minimum-rank behavior for
constant line sum three.

Therefore:

```
ROW/COLUMN SUM 3
+
LARGE RATIONAL NULLITY
```

is not, by itself, a new or rigid phenomenon.

The source theorem does not impose the JANUS combination of connectedness,
incidence girth>=10, phase FAIL and noncommuting P,Q.

### S2 — graph-nullity literature does not supply the combined local theorem

Fan--Qian (2009) determine broad nullity sets of bipartite graphs and
characterize some extremal regular-bipartite nullity cases.

General graph-nullity/girth results also bound or classify extremal adjacency
nullity.

These are source-bound donors and controls.  No located theorem converts
large nullity in the present cubic high-girth incidence setting into a bounded
local odd-hole attachment overlap or a polynomial Exact-One solver.

### S3 — 2-lift spectrum is source-bound

Bilu--Linial's 2-lift/signing framework and later signed-graph treatments give

```
Spec(lift)
=
Spec(base)
multiset-union
Spec(signed base).
```

In particular every old zero mode survives in every lift.

For a bipartite graph this statement can be read blockwise on the
biadjacency matrix: the invariant fiber-constant sector contains the original
kernel.

Thus:

```
GRAPH COVER / LIFT
PRESERVES OLD NULLSPACE
```

is source-bound and must not be claimed as JANUS novelty.

### S4 — arbitrary large girth via lifts is source-bound

The voltage-lift literature proves that any base graph can be lifted to graphs
of arbitrarily large girth.

Random-lift and residual-finiteness arguments give the same qualitative
message: covers can remove any fixed finite collection of short cycles.

Hence:

```
HIGH GIRTH BY PASSING TO A COVER
```

is a known donor.

What is not supplied by those theorems is the exact JANUS simultaneous
preservation of:

```
superlog rational incidence nullity
+
fixed-factorization Z3 phase FAIL
+
noncommuting two-permutation action
+
the exact cubic source semantics.
```

### S5 — phase persistence is not source-closed by the graph-cover papers

The JANUS phase obstruction is a labeled Z3 cocycle on the normalized
two-permutation action.

The located graph-cover/lift sources discuss covering geometry and spectrum;
they do not state the specific theorem that a phase obstruction survives
covers whose monodromy is a 2-group, nor do they connect that statement to
the exact {-1,2} kernel-word problem.

That is a legitimate scoped mathematical test after this audit.

## G4 — collision matrix

```
constant line-sum-3 singular matrices
=
SOURCE-BOUND FLEXIBLE RANK OBJECT

large graph / matrix nullity
=
SOURCE-BOUND SPECTRAL OBJECT
NOT A HARDNESS CERTIFICATE

2-lift old/new spectrum
=
SOURCE-BOUND

old kernel survives covers
=
SOURCE-BOUND COROLLARY

arbitrarily large girth by graph lifts
=
SOURCE-BOUND

large nullity + high girth + noncommuting + phase FAIL
inside the exact cubic source
=
NO SOURCE CLOSURE LOCATED

2-group-cover persistence of the JANUS Z3 phase obstruction
=
SCOPED GAP

explicit filtered high-nullity sparse-attachment survivor family
=
SCOPED GAP
```

This is a targeted source audit, not a legal novelty certification.

## G5 — exact permitted killer test

New mathematics is authorized only inside:

```
R5_E9_FILTERED_HIGH_NULLITY_COVER_SURVIVOR_GATE_V1
```

Allowed PASS/FALSIFIER target:

construct or rule out a polynomially explicit family of connected cubic
positive Exact-One incidence graphs satisfying simultaneously:

```
1. incidence girth >= 10;
2. rational nullity omega(log n);
3. normalized two-permutation action noncommuting;
4. Z3 phase test FAIL;
5. an induced conflict odd hole with the NM-0028 sparse local geometry.
```

The family need not yet survive every downstream MIS reduction; if it does
not, that fact must be recorded explicitly.

A useful intermediate theorem may establish that a 2-group cover cannot repair
a pre-existing Z3 phase obstruction.

## Mandatory anti-loop controls

Do not:

- call graph-lift kernel inheritance new;
- infer hardness from high nullity;
- infer high nullity from high girth;
- infer phase FAIL from singularity;
- promote a finite d>log2(n) sample to an asymptotic omega(log n) theorem;
- call a cover a full PA-0001 survivor without checking the exact normalized
  P,Q phase and noncommutativity conditions;
- use a cover construction whose size growth destroys the claimed nullity
  asymptotic without accounting for it.

## Audit decision

```
PA-0025
=
PASS_SCOPED_GAP_CONFIRMED

LARGE NULLITY / CONSTANT LINE SUM 3
=
SOURCE-BOUND FLEXIBLE MATRIX PHENOMENON

GRAPH LIFT SPECTRUM / OLD KERNEL
=
SOURCE-BOUND

ARBITRARILY LARGE GIRTH BY LIFTS
=
SOURCE-BOUND

EXACT FILTERED COMBINATION
=
SCOPED GAP SURVIVES

NEW MATH
=
R5_E9_FILTERED_HIGH_NULLITY_COVER_SURVIVOR_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
