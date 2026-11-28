# R5 — Canonical-Twist Matroid-Intersection Deterministic Gluing Terminal

Date: 2026-10-10

Status:
PROVED CONDITIONAL DETERMINISTIC POLYNOMIAL TERMINAL

P_VS_NP = OPEN.

## 0. Anti-loop

This theorem combines two already-proved mainline facts rather than opening a
new representation lane.

* E78: for a Tanner-vertex partition into exact boundary relations D_t,
  global consistency is equality of the two copies of every cut incidence.
* E83: whenever an exact Tanner boundary relation D_t is a delta-matroid,
  twisting by all variable-side boundary coordinates P_t turns D_t into an
  ordinary matroid basis family.

E81 remains decisive: such a static delta partition does not exist for every
square-cubic-linear RXC3 instance (cyclic q=8 is a counterexample).

The new point is that, WHEN such a partition exists, E78 does not need
randomized delta-sum representation at all.

## 1. Duplicate the cut ground

Let M_1,...,M_s be a Tanner-vertex partition.

For every cut Tanner incidence e=uv, create two formal copies:
one in the boundary ground of the module containing the check endpoint and one
in the boundary ground of the module containing the variable endpoint.

Thus the duplicated boundary ground is the disjoint union

    U = disjoint_union_t E_t.

Every original cut incidence e induces one pair

    pi_e={e^C,e^V}.

## 2. Canonical twist of every module

Let D_t=(E_t,F_t) be the exact boundary relation of module t and assume D_t is
a delta-matroid.

Let P_t subseteq E_t be exactly the boundary copies whose endpoint inside the
module is a variable vertex.

By E83,

    K_t := D_t * P_t

is an ordinary matroid in basis-family presentation.

Thus for each local feasible boundary state F_t,

    B_t := F_t xor P_t

is a basis of K_t, and conversely every basis B_t gives
F_t=B_t xor P_t.

Let

    K = direct_sum_t K_t

on the duplicated ground U.

Then B=disjoint_union_t B_t is a basis of K iff every module chooses a locally
feasible exact boundary state.

## 3. Equality gluing becomes exactly-one-per-pair

Fix one cut incidence e.

Exactly one of its two boundary copies is variable-side, because every Tanner
incidence joins one check vertex to one variable vertex. Therefore

    1_{e^C in P} xor 1_{e^V in P} = 1,

where P=disjoint_union_t P_t.

Global consistency in the original boundary bits is

    1_{e^C in F} = 1_{e^V in F}.

Substitute F=B xor P. The equality becomes

    1_{e^C in B} xor 1_{e^V in B} = 1.

Since the bits are Boolean, this is exactly

    |B intersect pi_e| = 1.

Therefore every globally consistent tuple of local exact states corresponds
bijectively to a set B that is simultaneously:

1. a basis of K; and
2. a basis of the partition matroid Q whose blocks are the pairs pi_e and whose
   capacity is one in every block.

## 4. Deterministic polynomial algorithm

Hence

    GLOBAL EXACT-ONE SAT
    iff
    K and Q have a common basis.

Ordinary matroid intersection is deterministic polynomial time given
polynomial-time independence oracles. If every K_t is supplied by a linear
representation (as in the represented-linear-delta premise of E78), then K has
an explicit block-diagonal linear representation and Q has a trivial partition
oracle/representation.

So:

    POLYNOMIALLY CONSTRUCTIBLE STATIC REPRESENTED LINEAR-DELTA PARTITION
        =>
    DETERMINISTIC POLYNOMIAL EXACT-ONE SOLVER.

This strengthens the E78 terminal from randomized to deterministic without
constructing any delta-sum representation and without polynomial identity
testing.

## 5. Rank consistency

Q has rank equal to the number m of cut incidences.

K has rank sum_t r(K_t).

If these ranks differ, there is immediately no common basis and hence no global
solution. If they agree, ordinary maximum-cardinality matroid intersection
decides whether a common independent set of that rank exists and recovers it.

The recovered common basis gives every B_t, hence every exact boundary state
F_t=B_t xor P_t; local witnesses may then be recovered by the module extension
procedures assumed by the decomposition.

## 6. Why this does not prove P=NP

E81 proves that the universal static-partition premise is false: the cyclic q=8
square-cubic-linear source admits no disjoint Tanner-vertex partition into
nonempty exact delta boundary modules.

Therefore the new theorem removes RANDOMIZATION/PIT as a blocker on the static
delta lane, but it does not repair universality.

The genuine surviving universal obstruction is now:

    cross a non-delta interface (or avoid static interfaces entirely)
    while retaining polynomial-size exact state.

Any proposed universal solver that only searches for a static delta partition
is ruled out by E81.

## 7. Consequence for the parity branch

The Kronecker exactification of E78 remains mathematically correct, but
STRUCTURED E78 PFAFFIAN PIT is no longer the preferred static-partition
frontier: canonical twist + ordinary matroid intersection is strictly simpler
and deterministic whenever E78's static represented-delta premise holds.

The next admissible attack must therefore address the E81 q=8 obstruction,
for example via recursive/non-static elimination, overlap, or a different
global algebraic representation.

## Claim boundary

STATIC_REPRESENTED_DELTA_GLUING_RANDOMNESS = REMOVED.
STATIC_REPRESENTED_DELTA_GLUING_PIT = NOT_NEEDED.
STATIC_REPRESENTED_DELTA_PARTITION_UNIVERSALITY = REFUTED_BY_E81.
NONDELTA_INTERFACE_COMPRESSION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
