# R5 E10A — Multi-Interface / Decomposition-Tree Support-Accumulation Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__UNARY_RECURSION_SOURCE_BOUND__ACTIVE_INTERFACE_PER_STAR_GAP_SURVIVES`

Immediate predecessor:
`NM-0014-NONDISTINGUISHED-SINGLE-ROOT-BOUNDARY-LIFTING`

## G0 — exact changed scope

NM-0014 proves exact bounded boundary lifting through **one** rooted 2-sum,
ordinary Delta-3-sum, or dual Y-3-sum interface and reduces all standard
single-root conditioned costs to constant enumeration of ordinary T-joins.

The changed-scope question is whether those one-root bounds remain sufficient
through an entire source-valid decomposition tree.

Two representations of the same lineage must be kept distinct:

```
recursive minor / sum decomposition
    -> small local separators are explicit
    -> but repeated contraction/minor formation does not preserve
       the NM-0010 low-support star basis automatically;

flat/origin-real torso view
    -> puncturing the original NM-0010 star remains exact
    -> but one torso may have many virtual interfaces.
```

The audit therefore asks only:

```
Does public decomposition/tree-realization theory already prove
that the cubic-origin lineage can be processed with a uniformly
bounded number of live interfaces while retaining the exact
star-cocycle information needed by NM-0013/NM-0014?
```

## G1 — internal anti-duplication

No earlier Fundamentum artifact proves a multi-interface accumulation bound.

Already closed:

- one rooted interface: NM-0014;
- distinguished real torso: NM-0013;
- scalar conditioned-cost provenance: source-bound / exhausted;
- generic PA-0005 two-row optimization: broader than current lineage;
- arbitrary minor provenance: insufficient because contraction may destroy
  inherited low-support cocycles.

No internal `PA-0010`, active-interface, unaryization, or equivalent theorem
was found before this audit.

## G2 — canonical external language

### L1 — code-decomposition trees

Kashyap defines complete code-decomposition trees built from direct sums,
2-sums, ordinary 3-sums and dual 3-sums.

For almost-graphic families the stronger property is a
`(Gamma union D)-unary` decomposition tree: at every non-leaf node one
designated child is already a terminal/tractable piece.

For PAG families such a 3-homogeneous unary tree is constructible in polynomial
time.

### L2 — conditioned-cost recursion

Appendix B of Kashyap gives the exact dynamic-programming pattern.

For a 2-sum, the processed side is solved under the two possible connector
states and the result is encoded into one modified coefficient on the
continuing side.

For an ordinary 3-sum, the processed side is solved in exactly the four
admissible boundary states

```
000, 011, 101, 110,
```

and those four optima are converted into three interface coefficients on the
continuing side.

Thus

```
CHILD
-> FINITE CONDITIONED OPTIMA
-> MODIFIED INTERFACE COEFFICIENTS
-> CONTINUE RECURSION
```

is source-bound and must not be claimed as new JANUS machinery.

### L3 — tree realizations

Kashyap's minimal tree-realization theory and Forney's normal-graph realization
framework source-bind the broader fact that exact computation on a cycle-free
realization proceeds through finite state spaces on tree edges; complexity is
controlled by state/local-constraint dimensions, not by the number of tree
vertices alone.

This is adjacent to the present object but does not prove the JANUS
low-support-star propagation theorem.

## G3 — exact collision / gap split

### Known and source-bound

```
binary decomposition tree
finite 2/3-sum separator state spaces
child -> conditioned scalar costs
exact recursion on a tree
cycle-free tree realization / sum-product principle
PAG unary decomposition as a sufficient polynomial pattern
```

### Not located

No source located in this audit proves that the exact cubic-origin family

```
M([I+P+Q|1])
```

admits a lineage-preserving unary decomposition in which every residual
two-row solve continues to inherit the original NM-0010 star-cocycle promise.

Likewise no located source proves the alternative statement that, in a
non-unary tree, a fixed original 4-support star cocycle can carry nonzero state
on only O(1) incident interfaces at every torso.

This is the remaining scoped gap.

## G4 — why binary-tree structure alone is insufficient

A decomposition tree being binary does **not** by itself solve the JANUS
problem.

If one recursively replaces nodes by minors, contraction/shortening may destroy
the low-support cocycle generators used by NM-0013/NM-0014.

If instead one keeps the original-real restriction so that puncturing remains
valid, a flattened torso may expose many virtual separators.

Therefore the following inference is forbidden:

```
TREE HAS CONSTANT ARITY
=> ONLY CONSTANTLY MANY VIRTUAL INTERFACES MATTER
```

without an exact state/support theorem.

## G5 — new scoped target

Every original NM-0010 star cocycle satisfies

```
|D_i|=4.
```

Remove a torso node from a decomposition tree.  Its incident tree edges define
pairwise-disjoint branches of original real elements.

The natural candidate invariant is not a bound on torso degree.  It is:

```
for a fixed D_i,
only incident branches containing support(D_i)
may require a nonzero separator trace,
after choosing the canonical zero representative
on empty Y-branches.
```

Since the support has four original elements, this would imply at most four
active incident interfaces per star cocycle, independent of torso degree.

The literature located above supplies the tree/state language but not this
JANUS-specific consequence tied to the NM-0010 star and the separate
2/Delta3/Y3 kernel formulas of NM-0014.

## Audit decision

```
PA-0010-MULTI-INTERFACE-DECOMPOSITION-TREE-SUPPORT-ACCUMULATION
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_STAR_SUPPORT_ACTIVE_INTERFACE_TREE_PROPAGATION_GATE_V1
```

## First authorized killer test

For every original star cocycle `D_i` and every torso node `v`, prove or
falsify

```
# {
  incident decomposition interfaces e at v :
  the canonical local representative of D_i
  has nonzero trace on e
}
<= 4.
```

Proof obligations:

1. 2-sum empty branch -> unique zero trace;
2. Delta-3-sum empty branch -> unique zero trace;
3. Y-3-sum empty branch -> the `000` representative may be selected instead
   of the interface-only `111` representative;
4. those Y-kernel choices are simultaneously compatible across multiple
   distinct interfaces;
5. local representatives of the full NM-0010 star, together with any
   interface-only Y kernels, span the torso cocycle space needed for the
   two-row quotient;
6. conditioned-cost witness reconstruction survives the resulting flat
   multi-interface solve.

A failure of any item is the next obstruction atom.

## Mandatory anti-loop controls

Do not:

- claim unary recursion as new;
- assume the cubic lineage is PAG/almost-graphic without proof;
- infer bounded active interfaces from binary tree degree;
- recursively contract and silently retain the original star promise;
- reopen generic Bentert/PIT;
- conflate Delta and Y kernels;
- claim a full P=NP result from an active-interface lemma alone.

## Scientific ceiling

```
UNARY CODE-DECOMPOSITION RECURSION
=
SOURCE-BOUND

2/3-SUM CONDITIONED-COST PASSING
=
SOURCE-BOUND

CYCLE-FREE TREE REALIZATION
=
SOURCE-BOUND

CUBIC-LINEAGE UNARYIZATION
=
NOT PROVED

ACTIVE INTERFACES PER ORIGINAL 4-SUPPORT STAR COCYCLE
=
NO CLOSURE LOCATED

PA-0010
=
PASS_SCOPED_GAP_CONFIRMED

P_VS_NP
=
OPEN
```
