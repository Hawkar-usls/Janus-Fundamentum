# R5 E10A — Optimal-Face Blossom-Parity Dynamic Program

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_ALGORITHM_AFTER_AUDIT__SCOPED_OPTIMAL_FACE_ONLY__NO_GENERAL_BCPM_OR_EXACT_MATCHING_CLAIM`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Continuation of:
`NM-0007-TOP-PLATEAU-OPTIMAL-FACE-PARITY`

Parent scope:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_optimal_face_blossom_parity_dp.py`

## 1. Exact problem

Let `G=(V,E)` be a general graph with integral edge weights and a designated
red edge set `R`.

Assume a minimum-weight perfect matching value `W*` is known.

The **Optimal-Face Correct Parity Matching** problem asks whether there is a
perfect matching `M` such that

```
w(M)=W*
and
|M intersect R| = rho (mod 2).
```

The preceding JANUS top-plateau theorem reduced the only unresolved
`GF(2)^2` label-class plateau question to exactly this problem.

This artifact gives a deterministic polynomial algorithm for this
**minimum-weight face** problem.

It does not solve general Bounded Correct Parity Matching.

## 2. Source-bound optimal-face certificate

Weighted perfect-matching duality gives an optimal dual whose positive odd-set
support can be chosen laminar.

Let

```
L
```

be a laminar family of positive-dual odd sets and let

```
E*
```

be the dual-tight edges.

By complementary slackness, a perfect matching is minimum-weight if and only if:

1. every selected edge is in `E*`; and
2. for every `S in L`,

```
|M intersect delta(S)| = 1.
```

The forward direction is ordinary complementary slackness.

For the reverse direction, any perfect matching satisfying all tight-edge and
positive-dual odd-cut equalities has primal weight equal to the optimal dual
value, hence is minimum-weight.

The existence and polynomial construction of such succinct optimal-face
descriptions is source-bound to weighted matching / matching-minor machinery;
JANUS does not claim novelty for the certificate.

## 3. Laminar tree

Adjoin the root

```
V
```

to `L`.

For every node `S`, its children are the maximal proper members of `L`
contained in `S`.

The **atoms** of `S` are:

- its child blossoms; and
- singleton vertices of `S` lying in no child.

Because `L` is laminar, the atoms partition `S`.

For a non-root blossom `S`, every valid global optimum has exactly one edge
crossing `delta(S)`.

## 4. Two-state conditional signature

For every non-root blossom `S` and every tight edge

```
p in delta(S),
```

define

```
Pi_S(p) subseteq GF(2)
```

as the set of red parities realizable by matching edges **strictly inside**
`S` under the condition that:

- `p` is the unique matching edge crossing `delta(S)`;
- all descendant positive-dual blossom constraints are satisfied.

The red bit of `p` itself is deliberately excluded from `Pi_S(p)`.
It is counted one level higher.

Thus every conditional state is one of only four possibilities:

```
empty,
{0},
{1},
{0,1}.
```

No matching family or syndrome table is stored.

## 5. Skeleton of a blossom

Fix `S`.

Contract every child blossom to one atom and retain uncovered vertices as
singleton atoms.

For every tight edge `q=ab` with both endpoints in `S` and in distinct
atoms `A,B`, create a skeleton edge between `A` and `B`.

Its available parity colors are:

```
red(q) XOR alpha XOR beta,
```

where:

- if `A` is a child blossom, `alpha in Pi_A(q)`;
- if `A` is a singleton, `alpha=0`;
- analogously for `B`.

Different original edges and different admissible parity choices may create
parallel colored skeleton edges. Parallel edges are harmless; if a simple-graph
implementation is required they can be expanded by a standard polynomial
matching gadget.

### Why a skeleton matching is the correct quotient

Every child blossom must have exactly one crossing matching edge.

Therefore, inside `S`, each non-exposed atom is incident with exactly one
selected skeleton edge.

If `S` itself uses parent crossing edge `p`, exactly one atom `X`
contains the endpoint of `p` lying in `S`.  That atom is already matched
outside `S` and must be left unmatched by the internal skeleton.

Hence an internal configuration projects to a perfect matching of

```
K_S - X.
```

Conversely, a perfect matching of `K_S-X`, together with a compatible child
witness for every selected colored skeleton edge and the exposed-child witness
conditioned on `p`, expands to a valid matching inside `S`.

This is an exact bijective decomposition at the level needed for parity.

## 6. Bottom-up recurrence

Let `X` be the atom of `S` containing the inside endpoint of parent edge
`p`.

Define the exposed offset:

```
O_X(p) =
{0}                  if X is a singleton,
Pi_X(p)              if X is a child blossom.
```

Run source-bound deterministic Correct Parity Matching on the skeleton
`K_S-X` for parity 0 and parity 1.

Let

```
Q_S(X) subseteq GF(2)
```

be the achievable parity set of those skeleton perfect matchings.

Then exactly:

```
Pi_S(p)
=
{ a XOR b :
  a in O_X(p),
  b in Q_S(X) }.
```

This computes every state of `S` after all child states are known.

Leaves are the same recurrence with only singleton atoms.

## 7. Root decision

At the root `V`, there is no parent crossing edge.

Build its skeleton from child signatures exactly as above and run Correct
Parity Matching for the requested global parity `rho`.

A YES skeleton matching expands recursively to a perfect matching of `G`
that:

- uses only tight edges;
- crosses every positive-dual blossom exactly once;
- has red parity `rho`.

By the source-bound optimal-face certificate, it is minimum-weight.

Conversely every minimum-weight matching projects recursively to such a root
skeleton matching.

Therefore:

```
OFCPM
=
DETERMINISTIC P.
```

## 8. Correctness proof by induction

Induct on laminar-tree depth.

### Induction hypothesis

For every child `C` and tight crossing edge `q`, `Pi_C(q)` is exactly
the set of internal red parities of valid child extensions conditioned on
`q` being the unique crossing edge.

### Soundness

Take a colored perfect matching of `K_S-X`.

For each selected skeleton edge `q`:

- its color certifies choices from the endpoint-child signatures;
- by induction those choices have valid internal child witnesses.

Because the skeleton is a matching, each non-exposed child has exactly one
crossing edge.

The exposed atom uses only the parent edge `p`; if it is a child, its
`Pi_X(p)` state supplies the internal witness.

The union therefore satisfies every descendant blossom equality.
Parity is the XOR of disjoint matching edges and child contributions, exactly
the recurrence value.

### Completeness

Take any valid internal configuration of `S` conditioned on `p`.

Every non-exposed atom has exactly one crossing matching edge, so those edges
project to a perfect matching of `K_S-X`.

Each child restriction realizes one of its inductively exact signature states,
so every projected edge has the corresponding color variant.

The internal parity therefore occurs in the recurrence.

Soundness and completeness prove exactness.

At the root the same argument has no exposed atom and yields the global
minimum-face parity set.

## 9. Polynomial complexity

A laminar family on `n` vertices has `O(n)` members.

There are at most

```
O(|L| |E|)
=
O(nm)
```

conditional pairs `(S,p)`.

Every skeleton has polynomial size:

- at most `n` atoms;
- at most a constant number of parity variants per tight original edge.

For each state, only two deterministic CPM feasibility calls are needed.

General-graph CPM is source-bound deterministic polynomial.

Therefore the total algorithm is polynomial in the size of the weighted
matching instance.

## 10. Witness reconstruction

The CPM source gives a decision procedure, and a witness can be reconstructed
by the standard polynomial edge-deletion self-reduction:

repeatedly test whether a desired-parity perfect matching survives after
deleting a candidate edge.

For each selected colored skeleton edge, store the child parity choice used to
create that color.

Descending the laminar tree reconstructs a full optimal matching.

Thus both decision and witness reconstruction are polynomial.

## 11. Exact checker

The checker creates deterministic seeded small general-graph instances with:

- laminar odd-set families, including nested blossoms;
- positive blossom dual values;
- independently chosen nonnegative edge slacks;
- weights

```
w(e)
=
slack(e)
+
sum_{S in L: e crosses S} z_S.
```

Every perfect matching has weight at least `sum_S z_S`.

Instances admitting a matching that uses only zero-slack edges and crosses
every `S` exactly once therefore have an explicit certified minimum face.

The checker:

1. enumerates all perfect matchings;
2. computes the exact minimum-weight red-parity set;
3. runs the recursive two-state blossom DP on the tight edges;
4. compares the two parity sets.

The committed seeded regression includes hundreds of feasible certified faces.
Development stress testing passed 500 additional random feasible face
certificates.

This is finite evidence only; the proof is the induction above.

## 12. Consequence for the GF(2)^2 top plateau

The previous theorem established

```
m_c=M
iff
the auxiliary minimum-weight matching face
contains parity psi(c).
```

OFCPM is now deterministic polynomial, therefore the top plateau can be
disambiguated deterministically:

```
m_c=M
vs
m_c>M.
```

If `m_c=M`, the reconstructed matching maps back through the odd-path
reduction to an optimal `c`-labelled path.

If `m_c>M`, pairwise-parity collapse certifies that `c` is the unique
strict maximum label class, but its exact value and shortest witness are not
yet obtained.

The new active residual is therefore:

```
R5_E10A_GF2_SQUARED_UNIQUE_STRICT_MAX_LABEL_VALUE_GATE_V1
```

Given a feasible label `c` already certified to be the unique strict maximum,
compute `m_c` exactly and reconstruct a shortest `c`-labelled path, or
derive an exact downstream bypass showing that only threshold information is
needed by the universal SAT route.

## 13. Scientific ceiling

```
MINIMUM-WEIGHT FACE LAMINAR CERTIFICATE
=
SOURCE-BOUND

TWO-STATE BLOSSOM PARITY DP
=
PROVED

OPTIMAL-FACE CORRECT PARITY MATCHING
=
DETERMINISTIC P

TOP-PLATEAU DISAMBIGUATION
=
DETERMINISTIC P

GENERAL BCPM
=
NOT SOLVED

GENERAL EXACT MATCHING
=
NOT SOLVED

UNIQUE STRICT-MAX LABEL EXACT VALUE
=
OPEN

FULL GF(2)^2 PRESCRIBED-LABEL SHORTEST PATH
=
NOT YET DETERMINISTICALLY SOLVED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
