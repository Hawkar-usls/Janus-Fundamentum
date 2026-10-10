# R5 E8 6I — Projected-Linear OR3 Delta-Parity Bridge and Fanout Frontier

Date: 2026-09-23

Authority:
JANUS_DERIVED_THEOREM__PROJECTED_LINEAR_OR3_PASS__TWO_OCCURRENCE_PARITY_PASS__HIGH_FANOUT_DIRECT_ROUTE_BLOCKED__PAIR_GADGET_OPEN

Scientific ceiling:

    D1       = EMPTY
    P_VS_NP  = OPEN
    P_EQ_NP  = NOT_PROVED

This artifact corrects the scope of the earlier delta-matroid negative control.
The obstruction ALL_EQUAL_d for d>=3 blocks a direct occurrence-equality
delta-matroid, but it does not block the clause side. In fact the full signed
3-clause relation has a constant-size projected-linear delta-matroid
representation.

## 1. Exact projected-linear representation of OR3

Use visible coordinates x1,x2,x3 and one hidden coordinate h.

Over GF(3), let A be the skew-symmetric matrix, in order

    x1 x2 x3 h

given by

    [ 0  0  1  1 ]
    [ 0  0  1  2 ]
    [ 2  2  0  1 ]
    [ 2  1  2  0 ].

Let D(A) contain exactly those subsets S for which the principal submatrix
A[S] is nonsingular.

Twist by

    T = {x1,x2}

and existentially project h.

The nonsingular-principal-set family of A is exactly

    empty,
    {x1,x3},
    {x2,x3},
    {x1,h},
    {x2,h},
    {x3,h},
    {x1,x2,x3,h}.

After twisting by {x1,x2} and projecting h, the visible feasible masks are

    001,010,011,100,101,110,111.

Therefore the projected visible relation is exactly

    OR3 = {0,1}^3 minus {000}.

This gives a constant-size exact projected-linear representation of OR3.

## 2. Every signed 3-clause

A signed Boolean clause excludes exactly one assignment q in {0,1}^3.

Twisting the visible OR3 relation by q sends

    {0,1}^3 minus {000}

to

    {0,1}^3 minus {q}.

Hence every signed ternary clause has a constant-size projected-linear
delta-matroid representation over GF(3).

No sheet selector is introduced.

## 3. Direct-sum clause carrier

For a 3-CNF F with one visible ground element per literal occurrence:

1. instantiate one copy of the four-coordinate representation per clause;
2. apply the clause-specific visible twist;
3. take the block-diagonal direct sum of all skew matrices;
4. existentially project the one hidden h_C per clause.

The result is a polynomial-size projected-linear delta-matroid D_F on the
occurrence ports.

A visible set is feasible in D_F exactly when each clause-local occurrence
triple satisfies its signed 3-clause.

Thus clause semantics are completely absorbed into a projected-linear
delta-matroid before any occurrence-coherence mechanism is imposed.

## 4. Exact two-occurrence theorem

Assume every original Boolean variable occurs exactly twice in F.

Pair the two occurrence ports of each original variable. Let Pi be this
partition into pairs.

Then:

    F is satisfiable

iff

    D_F has a feasible set that is a union of pairs of Pi.

Proof:

- a satisfying Boolean assignment selects both occurrence ports of a variable
  iff that variable is 1, so its occurrence set is a union of pairs and each
  clause-local triple is feasible;
- conversely, a feasible union of pairs assigns equal bits to the two
  occurrences of each variable, and clause feasibility says every original
  clause is satisfied.

Therefore exact-two-occurrence signed 3SAT is an exact instance of projected
linear delta-matroid parity.

Koana-Wahlstrom 2025 give polynomial randomized decision algorithms for
parity/intersection on projected linear delta-matroids from linear
representations, reducing the decision version to matrix-rank computation.

This is a source-bound positive bridge for the two-occurrence subclass.

## 5. Why ALL_EQUAL_d did not kill the whole route

For d>=3 define

    EQ_d = {0^d,1^d}

or as feasible sets

    { empty, V }.

EQ_d is not a delta-matroid.

Take F=empty, F'=V and any u in V. Symmetric exchange would require a
v in V such that

    empty Delta {u,v}

is feasible.

If v=u the result is {u}; if v!=u the result is {u,v}. For d>=3 neither is
empty nor V. Contradiction.

Because every projected-linear delta-matroid is still a delta-matroid,
EQ_d cannot itself be used as a direct projected-linear variable-side
relation.

Thus the previous negative result remains valid only for the DIRECT
high-arity equality relation.

## 6. Generic d-block parity is not the escape

A tempting move is to replace pair parity by blocks of size d so that a
logical variable is selected all-at-once.

This is the matroid k-parity direction. For block size k>=3 the problem is
NP-hard even for linearly represented matroids.

Therefore:

    PAIRS -> ARBITRARY d-BLOCKS

is not an admissible generic tractability donor.

This does not rule out a special structured gadget for the present family.

## 7. The remaining representation-change question

The only delta-parity escape not eliminated above is to keep the solver's
partition genuinely pairwise and implement high fanout internally.

Freeze:

    R5_E8_6I_PROJECTED_LINEAR_PAIR_FANOUT_GADGET_GATE_V1

For each d>=3 seek a polynomial-size projected-linear delta-matroid gadget
G_d with:

- d external ports e_1,...,e_d;
- polynomially many internal elements;
- a partition of internal elements into ordinary pairs;
- external ports left available to pair with the d clause occurrence ports;
- after requiring zero broken internal pairs and existentially hiding all
  internal state, the realizable external memberships are exactly

      0^d and 1^d.

The construction must provide its projected-linear representation directly
and in polynomial time.

## 8. Why this gate has full D1 stakes

Suppose such G_d exists uniformly in polynomial size.

Take the direct sum of:

- all projected-linear clause gadgets from Sections 1-3;
- one G_d for every original variable of occurrence degree d.

Pair each clause occurrence port with the corresponding external port of its
variable gadget, and use the internal pair partition supplied by each G_d.

A zero-broken-pair feasible set would then be equivalent to one globally
coherent satisfying assignment of the original 3-CNF.

Since projected-linear delta-matroid parity has a randomized polynomial
decision algorithm, a uniform polynomial construction of these gadgets would
produce a randomized polynomial 3SAT algorithm.

Therefore this gate must not be promoted on examples or heuristic search.
It requires an exact all-d construction, exact representation transport,
soundness/completeness, polynomial construction size, and a source-bound
parity solver lifecycle.

## 9. Small-gadget negative controls

Exhaustive local searches performed during discovery found no EQ3 fanout
gadget in the following restricted forms:

- one directly represented binary linear delta-matroid on 3 external ports
  plus one internal parity pair over GF(2);
- the same direct five-element model over GF(3);
- one GF(2) projected-linear source on 3 external ports, one internal parity
  pair, and one existential hidden element.

These are negative controls only. They are not a theorem against larger
gadgets or other fields.

## 10. Updated frontier

    SIGNED OR3
    -> CONSTANT PROJECTED-LINEAR DELTA-MATROID
    = PASS

    CLAUSE DIRECT SUM
    = PASS

    EXACT TWO-OCCURRENCE COHERENCE
    -> DELTA PARITY PAIRS
    = PASS

    DIRECT ALL_EQUAL_d DELTA-MATROID
    = BLOCKED FOR d>=3

    GENERIC d-BLOCK MATROID PARITY
    = NP-HARD FOR d>=3

    PAIR-ONLY PROJECTED-LINEAR FANOUT GADGET
    = OPEN
    <<< ACTIVE DELTA-MATROID REPRESENTATION FRONTIER

    JOINT FULL-PRODUCT / HIGH-WIDTH AFFINE GATE
    = STILL OPEN IN PARALLEL

    D1
    = EMPTY

    P_VS_NP
    = OPEN
