# R5 E10A — Optimal-Face Blossom-Parity Deterministic Polynomial Terminal

Date: 2026-09-29

Status:
`JANUS_DERIVED_DETERMINISTIC_POLYNOMIAL_TERMINAL__OPTIMAL_FACE_PARITY_CLOSED__NO_D1_PROMOTION`

Parent gate:
`R5_E10A_OPTIMAL_FACE_BLOSSOM_PARITY_GATE_V1`

Parent artifacts:
- `research/R5_E10A_GF2_SQUARED_TOP_PLATEAU_OPTIMAL_FACE_PARITY_2026-09-24_v1.0.md`
- `experiments/r5_e10a_optimal_face_blossom_parity_dp.py`

External donor:
- El Maalouly, Steiner, Wulf, *Exact Matching: Correct Parity and FPT Parameterized by Independence Number*, ISAAC 2023: Correct Parity Matching (CPM) in general graphs is deterministic polynomial time.

Scientific firewall:

```text
THIS NOTE CLOSES ONLY PARITY FEASIBILITY INSIDE ONE MINIMUM-WEIGHT
PERFECT-MATCHING FACE.

IT DOES NOT SOLVE GENERAL EXACT MATCHING.
IT DOES NOT SOLVE GENERAL BOUNDED CORRECT PARITY MATCHING.
IT DOES NOT YET COMPUTE A PRESCRIBED GF(2)^2 PATH WHEN THAT LABEL IS
THE UNIQUE STRICTLY MOST EXPENSIVE LABEL CLASS.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact input object

Let `G=(V,E)` be a weighted general graph with an even number of vertices.
Let

```text
rho:E->{0,1}
```

mark red edges, and let `W*` be the minimum perfect-matching weight.

Assume a standard optimal weighted-perfect-matching dual has been constructed
with vertex potentials and a laminar family `L` of positive odd-set/blossom
dual variables. Let `E*` be the set of dual-tight edges.

Standard weighted matching algorithms construct such an optimal dual in
polynomial time; uncrossing/blossom machinery permits the positive odd sets to
be represented laminarily.

The problem is:

```text
OPTIMAL_FACE_CORRECT_PARITY_MATCHING

Does there exist a perfect matching M with
  w(M)=W*
and
  XOR_{e in M} rho(e)=p ?
```

## 2. Exact minimum-face characterization

By complementary slackness, every minimum perfect matching:

1. uses only tight edges from `E*`; and
2. crosses every positive-dual odd set `S in L` exactly once:

```text
|M intersect delta(S)| = 1.
```

Conversely, every perfect matching satisfying those two conditions has weight
equal to the optimal dual objective and is therefore minimum-weight.

Hence the optimum face is represented exactly by

```text
TIGHT EDGES
+
ONE-CROSSING CONSTRAINT FOR EVERY S IN L.
```

No deletion-only description of the general perfect-matching face is assumed.

## 3. Laminar boundary state

Adjoin the root `V` above the laminar family. For every `S in L` and every
tight edge

```text
p in E* intersect delta(S),
```

define

```text
Pi(S,p) subseteq GF(2)
```

as the set of red parities attainable by the matching edges lying strictly
inside `S`, subject to:

- `p` is the unique matching edge crossing `S`;
- every positive-dual descendant blossom of `S` is crossed exactly once;
- only tight edges are used.

The parity contribution of the boundary edge `p` itself is deliberately
excluded from `Pi(S,p)`.  Thus every state has size at most two.

For a singleton atom use the trivial boundary state `{0}`.

## 4. Quotient recurrence

Let the immediate laminar children of `S` be `C_1,...,C_k`.  Contract each
child to one atom and keep every vertex of

```text
S - union_i C_i
```

as a singleton atom.

Fix a boundary edge `p` of `S`, and let `A_p` be the atom containing the
endpoint of `p` that lies in `S`.  This atom is exposed at the quotient level:
its unique crossing edge is already `p`.

For every tight internal edge `q=ab` joining two distinct non-exposed atoms
`A,B`, define the available parity variants

```text
Color_S(q)
=
{ rho(q) XOR x XOR y :
    x in Pi(A,q),
    y in Pi(B,q) },
```

where `Pi(singleton,q)={0}`.

If an atom is a child blossom, selecting `q` makes `q` its unique crossing
edge, so its internal contribution is exactly one of the values already stored
in `Pi(child,q)`.

If the exposed atom `A_p` is a child blossom, its offset contribution is one
of `Pi(A_p,p)`; if it is a singleton the offset is zero.

Therefore `Pi(S,p)` is exactly

```text
OFFSET(A_p,p)
XOR
{ parities of perfect matchings of the quotient atoms other than A_p,
  using the tight quotient edges with their Color_S variants }.
```

The quotient may have parallel red/blue variants.  This is an ordinary
red/blue perfect-matching parity instance: each feasible parity variant of an
original edge is retained as a separate matching edge together with a pointer
to the child states that realize it.

## 5. Replace the experimental exponential subroutine by CPM

The committed control

`experiments/r5_e10a_optimal_face_blossom_parity_dp.py`

implements the recurrence above but computes the quotient parity set by an
explicit recursive enumeration of perfect matchings.  That was sufficient for
finite exact controls but was not a polynomial theorem.

Now replace that local routine by deterministic **Correct Parity Matching**.
For each quotient graph, run CPM for target parity `0` and target parity `1`.
El Maalouly--Steiner--Wulf prove that CPM on general red/blue graphs is
deterministic polynomial time.  Thus the attainable quotient parity set is
computed in polynomial time without enumerating perfect matchings.

Because there are only two target parities, the number of CPM calls per state
is constant.

## 6. Root recurrence

At the root `V` there is no exposed atom.  Contract the maximal blossoms of
`L` and retain uncovered vertices as singleton atoms.  Define edge parity
variants exactly as above.

A perfect matching of the root quotient selects the unique crossing edge for
every maximal blossom.  Therefore the set of parities of **all minimum-weight
perfect matchings of G** is exactly the two-parity CPM answer on the root
quotient.

Consequently the requested optimum-face parity `p` exists iff root CPM accepts
parity `p`.

## 7. Correctness proof

The proof is by induction on the laminar tree.

### Soundness

Take one quotient matching accepted at node `S`.  Every selected quotient edge
`q` is backed by child states realizing the chosen parity variant.  Child atoms
are pairwise matched once at the quotient, so their reconstructed interiors are
disjoint.  The exposed child, if any, is reconstructed with boundary edge `p`.
Combining these child matchings and the selected tight inter-atom edges gives a
matching of all vertices of `S` except the endpoint matched by `p`.  Every
positive descendant blossom is crossed exactly once, and the parity is the
stored XOR.  Thus every produced state belongs to `Pi(S,p)`.

At the root the same reconstruction gives a perfect matching using only tight
edges and crossing every `S in L` exactly once.  By Section 2 it is
minimum-weight.

### Completeness

Take any minimum perfect matching `M`.  Complementary slackness gives tightness
and one crossing per positive blossom.  Restrict `M` to any node `S`.  Its
unique boundary edge identifies the exposed atom.  Every other quotient atom
is paired exactly once by an internal matching edge, and the restrictions
inside child blossoms are, by induction, represented by the corresponding
`Pi(child,q)` states.  Hence the quotient CPM instance contains the parity of
`M` at every node.  At the root it contains the total red parity of `M`.

Therefore the root answer is exact.

## 8. Polynomial complexity

A laminar family on `n` vertices has `O(n)` members.  A tight edge can cross
`O(n)` nested blossoms, so the total number of boundary states `(S,p)` is at
most `O(nm)`.

For every state:

- atom construction and parity-variant construction are polynomial;
- at most two deterministic CPM calls are made on a graph of polynomial size;
- each state stores at most two parity bits plus witness pointers.

Hence total time and space are polynomial in the input size and in the exact
bit-size of the weighted-matching dual.

No syndrome table of size `2^r`, no matching enumeration, and no randomized
isolation are used.

## 9. Witness reconstruction

The constructive CPM routine returns a quotient perfect matching of the desired
parity.  Store, for every selected quotient edge, the original tight edge `q`
and one pair of child parity states realizing its color.

Starting from the accepted root state, recursively follow these pointers.  Each
child is visited once at its parent matching, and the recursion returns the
corresponding internal matching.  Their union is a minimum-weight perfect
matching of the requested red parity.

Directly verify:

```text
perfect matching = YES
weight = W*
red parity = requested p.
```

Thus decision and witness construction are both deterministic polynomial.

## 10. Consequence for the JANUS GF(2)^2 top plateau

The parent theorem proves, for the unit-positive two-row graph-lift origin,
that a feasible prescribed label `c` on the unresolved top plateau satisfies

```text
m_c = M
iff
there exists a minimum-weight auxiliary perfect matching
with the required secondary red parity.
```

The theorem above closes that right-hand side deterministically.
Therefore the top-plateau decision

```text
m_c = M  versus  m_c > M
```

is deterministic polynomial, with an optimal `c`-labelled path reconstructed
in the equality case.

The strict-maximum branch `m_c>M` is **not** assigned an exact value here and
is not claimed solved.

## 11. Anti-loop / scope firewall

Do not promote any of the following:

```text
GENERAL EXACT MATCHING IN P                         NOT PROVED
GENERAL BOUNDED CORRECT PARITY MATCHING IN P        NOT PROVED
ALL PRESCRIBED GF(2)^2 SHORTEST PATHS IN P          NOT PROVED
UNIQUE STRICT-MAXIMUM LABEL COST COMPUTED            NOT PROVED
UNIVERSAL SAT SOLVER                                 NOT PROVED
```

What is proved is narrower:

```text
PARITY FEASIBILITY INSIDE A GIVEN MINIMUM-WEIGHT
PERFECT-MATCHING FACE WITH A LAMINAR OPTIMAL DUAL
IS DETERMINISTIC POLYNOMIAL.
```

This uses only standard weighted-matching duality plus deterministic CPM.

## 12. New live gate

```text
R5_E10A_GF2_SQUARED_STRICT_MAXIMUM_THRESHOLD_GATE_V1
```

Input:

- unit-positive undirected graph;
- `GF(2)^2` edge labels;
- feasible prescribed label `c`;
- all pairwise parity minima;
- certified result that `c` is the unique strict maximum label class.

Required:

for the source-bound lower-bound-tight query, decide deterministically whether

```text
m_c = L
```

for the required source threshold `L`, or `m_c>L`, without solving unrestricted
Exact Matching / BCPM.

## 13. Ceiling

```text
OPTIMAL-FACE BLOSSOM PARITY
= DETERMINISTIC POLYNOMIAL

EXPERIMENTAL EXPONENTIAL LOCAL MATCHING ENUMERATION
= REPLACED THEORETICALLY BY CPM

TOP-PLATEAU m_c=M TEST
= DETERMINISTIC POLYNOMIAL

TOP-PLATEAU EQUALITY WITNESS
= DETERMINISTIC POLYNOMIAL RECONSTRUCTION

UNIQUE STRICT-MAXIMUM TARGET VALUE / THRESHOLD
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
