# R5 — q8 Delta Junction Witness and Recursive Delta-Hierarchy Firewall

Date: 2026-10-10

Status:
Q8_OVERLAP_JUNCTION_EXISTS__BINARY_RECURSIVE_DELTA_HIERARCHY_REFUTED

P_VS_NP = OPEN.

## 0. Starting point

E81 proved that the cyclic q=8 square-cubic-linear RXC3 Tanner graph has no
static disjoint partition into nonempty exact delta-boundary modules.

The present checkpoint asks two strictly broader questions:

1. can overlapping exact-delta bags cover q8 with a running-intersection tree?
2. can the instance nevertheless be built recursively from primitive Tanner
   vertices while every non-leaf intermediate induced bag has an exact
   delta-matroid boundary?

The answers are:

    (1) YES.
    (2) NO.

So overlap bypasses the static E81 obstruction geometrically, but delta closure
cannot be maintained throughout a binary bottom-up composition from atoms.

## 1. Complete induced-delta bag catalogue

Use the E81 q=8 source and its exact 200 connected delta bags.

A disconnected induced Tanner bag has exact boundary relation equal to the
direct product of the exact relations of its connected components.
Direct products of delta-matroids are delta-matroids, and every connected
component of a disconnected delta relation is recovered as a delta minor.

Therefore:

    disconnected bag is delta
    iff every connected component is one of the E81 connected delta bags.

Applying this criterion to all 2^16 induced vertex masks gives exactly

    448 delta masks including empty,
    447 nonempty delta masks.

Their size distribution is:

    size  1 :   8
    size  2 :  28
    size  3 :  56
    size  4 :  70
    size  5 :  56
    size  6 :  28
    size  7 :   8
    size  8 :   1
    size 12 :  48
    size 13 : 120
    size 14 :  24

The sizes 1..8 are exactly the nonempty subsets of the eight check vertices.

Hence:

    every delta bag containing at least one variable vertex has size >= 12.

There are exactly 192 such variable-containing delta bags.

## 2. Explicit q8 running-intersection delta junction path

Let Tanner vertices be C0..C7,V0..V7, encoded by bits 0..15.

Define:

    A = 0xdf3f
    B = 0x9fff
    C = 0xbfbe

with sizes

    |A|=13, |B|=14, |C|=13.

All three are connected exact-delta bags from the E81 catalogue.

Their adjacent intersections are

    A cap B = 0x9f3f, size 12,
    B cap C = 0x9fbe, size 12,

and both are connected exact-delta bags.

The nonadjacent overlap is

    A cap C = 0x9f3e, size 11,

which is connected and NON-delta.

Nevertheless

    A cap C subseteq B

and

    A union B union C = all 16 Tanner vertices.

Therefore the path

    A -- B -- C

satisfies the vertex running-intersection property, and every BAG and every
ADJACENT separator is exact-delta.

Thus E81's static-partition obstruction does NOT extend to arbitrary overlapping
vertex junction covers.

## 3. Why this does not yet give a solver

E78 boundary relations project away Tanner incidences internal to each bag.

For overlapping bags, an incidence can be internal to more than one bag.
Two bag extensions can therefore agree on the standard projected boundary while
using different hidden values on shared internal incidences.

Hence the static E78 equality-gluing proof does not automatically extend to
overlapping induced bags.

The q8 junction path is a structural positive witness, not yet an exact
polynomial composition theorem.

Any valid overlap solver must provide an ownership-compatible or enriched
interface that retains enough shared hidden state while preserving polynomial
representation.

## 4. Binary recursive delta-hierarchy firewall

Consider a full binary decomposition tree whose leaves are the 16 primitive
Tanner vertices.

Allow primitive variable leaves to be non-delta.
Require only that every internal node's induced Tanner vertex set have a
nonempty exact delta boundary relation.

No such tree exists.

### Structural proof

Choose a deepest internal node X whose subtree contains a variable vertex.

By depth maximality, neither child can be an internal subtree containing a
variable.

Therefore every child is either:

* a single variable leaf; or
* a subtree containing only check vertices.

There are only eight check vertices total.

Hence X contains at most

    1 variable + 8 checks = 9 vertices

if one child is the variable leaf, or at most two vertices if both children are
variable leaves.

But every exact-delta bag containing a variable has size at least 12.

Contradiction.

Therefore:

    NO binary bottom-up hierarchy from primitive Tanner vertices
    can remain inside the exact-delta class at every internal composition step.

## 5. Exact DP replay

An independent DP starts with all 16 singleton masks as primitive leaves.

A non-singleton mask is marked buildable iff:

1. its exact induced boundary is delta; and
2. it can be split into two disjoint already-buildable child masks.

Result:

    full 16-vertex q8 mask buildable = FALSE.

Stronger:

    number of variable-containing exact-delta bags = 192;
    number of variable-containing exact-delta bags buildable this way = 0.

Thus the structural argument is reproduced exactly.

## 6. Algorithmic consequence

The following universal route is refuted:

    primitive ExactOne_3 / Equality_3 Tanner atoms
      -> binary union/composition
      -> exact delta interface after every internal step
      -> E83 canonical matroid twist
      -> deterministic matroid intersection.

q8 forces any universal compositional solver to do at least one of:

A. pass through a genuinely non-delta intermediate interface;
B. use an interface class strictly stronger than delta-matroids;
C. use a nonlocal global representation that never exposes the forbidden
   bottom-up intermediate interface.

This identifies NONDELTA_INTERFACE_COMPRESSION as a genuine theorem gap, not
just an artifact of the static E81 partition formulation.

## 7. Relation to the new deterministic static terminal

The canonical-twist matroid-intersection theorem on this branch remains valid:
if a static represented-delta partition exists, gluing is deterministic
polynomial time and E78's randomized delta-sum construction is unnecessary.

q8 now gives two complementary facts:

    static disjoint delta partition: impossible;
    overlap delta junction geometry: possible;
    binary recursive delta closure from atoms: impossible.

So the next universal theorem cannot be another static/recursive delta-only
decomposition statement.

## Claim boundary

Q8_STATIC_DELTA_PARTITION = REFUTED_BY_E81.
Q8_DELTA_JUNCTION_COVER = EXISTS.
Q8_BINARY_RECURSIVE_DELTA_HIERARCHY = REFUTED.
NONDELTA_INTERFACE_COMPRESSION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
