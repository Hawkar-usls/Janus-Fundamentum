# R5 E9 — Conflict Odd-Hole Coverage Selector-Conservation Barrier

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_OBSTRUCTION_CONTRACTION_BARRIER_AFTER_PA0017__NO_COMPLEXITY_LOWER_BOUND`

Authorizing audit:
`PA-0017-PERFECT-KERNEL-CONFLICT-GRAPH-SOURCE-AUDIT`

Predecessor:
`NM-0022-CUBIC-CONFLICT-GRAPH-OBSTRUCTION`

Checker:
`experiments/r5_e9_conflict_odd_hole_selector_conservation.py`

## 1. Setting

Take the cubic exact-one system

```
Ax=1,
```

and an induced odd hole

```
H=(v_0,v_1,...,v_{k-1}),  k>=5 odd
```

in the variable-conflict graph from NM-0022.

Every hole edge `v_i v_{i+1}` is witnessed by an exact-one clause.  Because
the hole is induced, one clause cannot contain three hole vertices: that would
create a chord.  Hence the k cycle edges are supported by k distinct clauses

```
C_i = {v_i, v_{i+1}, w_i},
```

where `w_i` lies outside the hole.

Each hole variable occurs in exactly three source clauses.  Besides
`C_{i-1}` and `C_i`, write its third occurrence as

```
D_i = {v_i,a_i,b_i}.
```

The variables `a_i,b_i` need not be distinct across different i and may
participate in additional global interactions.  No independence assumption on
the external boundary is used.

## 2. Canonical coverage bit

For a genuine exact-one assignment define the external-coverage bit of D_i

```
d_i := a_i+b_i.
```

Since D_i is exact-one,

```
v_i+a_i+b_i=1,
```

so

```
d_i = 1-v_i.
```

Thus the most obvious blossom-style summary — keep one bit telling whether the
third occurrence clause is covered outside the hole — is not a compression:
it is a coordinatewise complement of the eliminated hole variable.

The map

```
(v_0,...,v_{k-1})
<->
(d_0,...,d_{k-1})
```

is bijective before extra boundary identifications are exploited.

## 3. Exact boundary relation of one belt clause

Let

```
c_i := w_i.
```

The belt clause is

```
v_i + v_{i+1} + c_i = 1.
```

Substitute `v_j=1-d_j`:

```
(1-d_i)+(1-d_{i+1})+c_i=1,
```

equivalently

```
d_i+d_{i+1}=1+c_i.
```

The allowed triples `(d_i,d_{i+1},c_i)` are exactly

```
010,
100,
111.
```

Now complement the first two coordinates,

```
u_i=1-d_i,
u_{i+1}=1-d_{i+1}.
```

The relation becomes

```
u_i+u_{i+1}+c_i=1,
```

with tuples

```
100,
010,
001.
```

That is exactly the original positive `EXACT-ONE-3` relation.

## 4. Whole odd-hole belt

Perform the substitution simultaneously around the hole.  After existentially
eliminating the original hole variables while retaining one coverage bit
`d_i` for each third occurrence clause, the exact belt relation is

```
for every i:
    (1-d_i)+(1-d_{i+1})+c_i = 1.
```

After the coordinatewise complement `u_i=1-d_i`, this is literally

```
for every i:
    u_i+u_{i+1}+c_i = 1.
```

So the belt is an exact-one belt again.

The checker exhaustively replays k=5 and k=7 and verifies that the projected
coverage relation is exactly the complemented EX1 belt.  The algebra above is
uniform for every k.

## 5. Selector-conservation consequence

A contraction of the form

```
"delete the odd-hole vertices
 and keep one independent Boolean coverage state per hole vertex"
```

does not decrease Boolean choice dimension.

It replaces each `v_i` by the bijective coordinate `d_i=1-v_i`, and each
belt clause by an isomorphic `EXACT-ONE-3` constraint.

Therefore this natural local blossom analogy is a representation change, not
an algorithmic contraction.

This does NOT prove that odd holes cannot be contracted.  It blocks only the
canonical per-vertex coverage summary.

## 6. Relation to existing barriers

This result is adjacent to, but distinct from:

- `RANK3_ALL_OR_NONE_LOCAL_MATCHING_BARRIER`, which blocks realizing one
  rank-3 all-or-none hyperedge by an ordinary matching gadget;
- `CLAUSE_LOCAL_SOUND_CUT_DICHOTOMY`, which shows a sound refinement exported
  through one original clause boundary is TRUE3 or OR3;
- `RANK1_CUT_HISTORY_CLAUSE_REACTIVATION_BARRIER`, which blocks naive local
  rank-one cut histories.

NM-0023 instead concerns a nontrivial multi-clause induced odd-hole block and
proves that its most immediate exact boundary elimination recreates
`EXACT-ONE-3` on the boundary.

## 7. Sharpened next gate

Freeze:

```
R5_E9_CONFLICT_ODD_HOLE_GROUPED_QUOTIENT_GATE_V1
```

A useful odd-hole contraction must exploit something not present in the
one-bit-per-vertex summary, for example:

- identifications/overlaps among the external D_i and C_i boundary variables;
- a grouped quotient that destroys multiple selector dimensions at once;
- a source-backed tractable interaction carrier;
- a nonlocal dominance or decomposition certificate.

Required PASS contract remains:

```
exact SAT equivalence
+
polynomial witness reconstruction
+
polynomial total state
+
strict decrease of a polynomially bounded live invariant.
```

Forbidden pseudo-progress:

```
v_i -> d_i=1-v_i
for every hole vertex
```

followed by solving the same EX1 belt under renamed coordinates.

## 8. Verdict

```
NM-0023
ODD-HOLE COVERAGE SELECTOR CONSERVATION
=
PASS

CANONICAL PER-VERTEX COVERAGE SUMMARY
=
EXACT-ONE-3 SELF-REPLICATION

BOOLEAN DIMENSION DROP
=
ZERO

GENERAL GROUPED ODD-HOLE CONTRACTION
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
