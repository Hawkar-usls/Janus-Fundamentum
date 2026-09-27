# R5 E9 — Exact-Matching Toggle Pair-Exchange Barrier

Date: 2026-09-28

Status:
`JANUS_DERIVED_EXACT_WEIGHTED_LOCAL_MATCHING_BARRIER__NO_P_NE_NP_ASSUMPTION__NO_D1_PROMOTION`

Parents:
- `R5_E9_RANK3_ALL_OR_NONE_LOCAL_MATCHING_BARRIER_2026-09-24_v1.0.md`
- `R5_E10A_XLC_TO_BIPARTITE_EXACT_MATCHING_TRANSFER_2026-09-24_v1.0.md`
- `R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
`experiments/r5_e9_exact_matching_toggle_pair_exchange.py`

Scientific firewall:

```text
THIS BLOCKS A STRICTLY DEFINED LOCAL EXACT-MATCHING LIFT.
IT DOES NOT PROVE THAT EVERY NONLOCAL REDUCTION TO EXACT MATCHING IS IMPOSSIBLE.
IT DOES NOT ASSUME P != NP.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Why the old three-port barrier was not enough

A cubic Positive 1-in-3 variable exposes the all-or-none boundary relation

```text
R = {000,111}.
```

The earlier rank-3 matching barrier proves that this three-port relation is not a delta-matroid and cannot be realized by an ordinary local matching gadget. Pure matchgate parity gives the same obstruction.

A natural attempted repair is to add one toggle port `t` so that the two desired states have the same boundary parity:

```text
OFF = 0000,
ON  = 1111.
```

One may then hope to permit the mixed weight-two boundary states locally but separate them from OFF/ON by the global exact number of red edges in a Bipartite Exact Matching instance.

This note proves an exact local obstruction to that repair.

## 2. Local perfect-matching gadget model

Let `G` be any finite graph with four boundary vertices

```text
U = {u1,u2,u3,t}
```

and any set of internal vertices. Every internal vertex is required to be saturated by the local matching. A boundary state `S subseteq U` records which boundary vertices are saturated inside the gadget; equivalently, under the opposite convention it records which are exported to the rest of the construction. Complementing all four boundary bits merely swaps conventions and does not affect the theorem.

Every edge may carry an arbitrary additive integer weight. Red/blue Exact Matching is the special case of weight 1 for red and 0 for blue.

Assume the gadget has witness matchings

```text
M_0  realizing emptyset,
M_4  realizing U.
```

Thus a proposed toggle lift can represent both desired all-or-none states.

## 3. Alternating-path structure

Consider the symmetric difference

```text
D = M_0 triangle M_4.
```

Every internal vertex has degree zero or two in `D`, because it is saturated by both matchings. Every boundary vertex in `U` has degree one, because its saturation status differs between the two boundary states.

Therefore `D` is a disjoint union of:

- alternating even cycles; and
- exactly two alternating paths whose four endpoints are the vertices of `U`.

Let one alternating path have endpoint pair

```text
A = {a,b} subset U,
```

and let the other path have complementary endpoints `U\A`.

## 4. Pair exchange theorem

Toggle membership of every edge of the first alternating path in both matchings:

```text
M_A      = M_0 triangle E(path),
M_UminusA = M_4 triangle E(path).
```

Because the path is alternating, both results are again valid matchings and every internal vertex remains saturated.

Their boundary states are exactly

```text
A
and
U\A.
```

Each has Hamming weight two. With three incidence ports and one toggle port, one of the two states has occurrence-degree one and the other has occurrence-degree two.

### Theorem EMX-1 — exact additive conservation

As edge multisets,

```text
M_0 multiset_union M_4
=
M_A multiset_union M_UminusA.
```

Hence for every additive edge weight function `w`,

```text
w(M_0) + w(M_4)
=
w(M_A) + w(M_UminusA).
```

In particular, for an arbitrary red/blue coloring,

```text
red(M_0) + red(M_4)
=
red(M_A) + red(M_UminusA).
```

### Proof

On edges outside the chosen alternating path nothing changes. On the path, every edge belongs to exactly one of `M_0,M_4`; toggling the whole path swaps which of the two matchings contains that edge. Therefore every edge has the same total multiplicity across the pair before and after the exchange. Additive-weight conservation follows immediately. QED.

This proof is purely matching-theoretic. It does not use planarity, Pfaffian orientation, holographic assumptions, or a complexity hypothesis.

## 5. Consequence for one-toggle Exact Matching lifts

For two copies of the same local gadget, any pair of local witnesses

```text
OFF + ON
```

can be replaced by

```text
MIXED_2 + MIXED_2
```

with complementary boundary states and exactly the same total red count — indeed the same total value under every additive edge statistic.

Thus a single global additive exact counter cannot make the pair `OFF+ON` distinguishable from all mixed complementary pairs inside an otherwise local per-variable toggle construction.

The obstruction is stronger than the old support/parity barrier:

```text
THREE PORTS:
OFF and ON cannot coexist in one ordinary matching boundary relation.

FOUR PORTS WITH TOGGLE:
OFF and ON may coexist,
but alternating-path exchange creates complementary mixed states
with pairwise identical additive exact-count data.
```

## 6. Interaction with the cubic source

In any cubic Positive 1-in-3 instance, a genuine Boolean witness has exactly `n/3` selected variables, hence the all-or-none degree distribution

```text
(a0,a1,a2,a3) = (2n/3,0,0,n/3).
```

If one pairs an OFF variable with an ON variable, EMX-1 allows that local pair to be replaced by one degree-1 and one degree-2 occurrence state without changing any additive exact-matching counter attached to identical gadget copies.

The frozen connected linear-cubic UNSAT `15_3` countercontrol has an explicit clause-perfect relaxed occurrence assignment with degree profile

```text
(a0,a1,a2,a3) = (5,5,5,0).
```

One such row-to-variable selection is

```text
row  0 -> var  0
row  1 -> var  1
row  2 -> var  9
row  3 -> var  3
row  4 -> var  3
row  5 -> var  1
row  6 -> var  7
row  7 -> var  2
row  8 -> var  8
row  9 -> var  0
row 10 -> var  2
row 11 -> var  5
row 12 -> var  8
row 13 -> var 13
row 14 -> var 11
```

Its variable degrees are

```text
2,2,2,2,0,1,0,1,2,1,0,1,0,1,0,
```

so exactly five variables have degree 0, five degree 1, and five degree 2. Every source row still has exactly one selected incidence, but the assignment is forbidden only by the all-or-none variable semantics.

This control is deliberately recorded as a hostile fixture for any uniform local toggle+counter reduction. The theorem-level obstruction is EMX-1; the `15_3` fixture is a finite adversarial replay, not a proof that every conceivable nonlocal Exact Matching reduction fails.

## 7. Relation to current Exact Matching literature

The 2026 Du preprint claims a deterministic polynomial algorithm for Bipartite Exact Matching. JANUS already has an exact bridge from bounded-capacity exact-length circulation to Bipartite Exact Matching.

Even if the Bipartite Exact Matching theorem is accepted in full, EMX-1 shows that the missing P-vs-NP bridge cannot be supplied by the obvious construction

```text
one cubic variable
-> one identical four-port matching gadget
-> one parity toggle
-> one global additive exact-red counter.
```

The bridge would have to use genuinely nonlocal grouping, non-identical globally coordinated gadgets, or another representation that is not reducible to independent local matching gadgets with additive counters.

## 8. Updated gate

Freeze:

```text
R5_E9_NONLOCAL_EXACT_MATCHING_GROUPING_OR_OTHER_CARRIER_GATE_V1
```

Allowed Exact-Matching continuation:

1. group multiple source variables/clauses before exposing a matching boundary;
2. prove an exact polynomial-size nonlocal construction whose global state is not a sum of independent local gadget counters;
3. bind a deterministic Exact Matching donor only after its external theorem is independently source-audited.

Forbidden as repeated pseudo-progress:

- three-port `{000,111}` matching gadget;
- one-toggle four-port local gadget plus a single additive red-count target;
- replacing red count by another additive scalar weight without defeating EMX-1;
- hidden branching over mixed local states.

## 9. Ceiling

```text
THREE-PORT LOCAL MATCHING LIFT
= BLOCKED (PREVIOUS THEOREM)

FOUR-PORT TOGGLE + ADDITIVE EXACT COUNT
PAIRWISE OFF/ON SEPARATION
= BLOCKED BY EMX-1

EXPLICIT LINEAR-CUBIC UNSAT RELAXED DEGREE (5,5,5,0) CONTROL
= PASS

NONLOCAL GROUPED REDUCTION TO EXACT MATCHING
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
