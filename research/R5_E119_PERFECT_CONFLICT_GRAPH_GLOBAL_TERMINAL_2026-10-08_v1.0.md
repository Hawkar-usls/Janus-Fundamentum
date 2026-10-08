# R5 E119 — Perfect-Conflict-Graph Global Terminal and SPGT Router

Date: 2026-10-08

Status:
`PERFECT_CONFLICT_GRAPH_IS_POLYNOMIAL_TERMINAL__IMPERFECT_TARGET_ROUTES_TO_ODD_HOLE_OR_C7_ANTIHole__C9_ANTIHole_IS_UNSAT_COMPONENT`

Scientific ceiling:

```text
E119 IS A GLOBAL POLYNOMIAL ROUTER FOR EVERY POSITIVE SQUARE CUBIC C4-FREE
EXACTONE INSTANCE.

IT COMPLETELY SOLVES THE PERFECT-CONFLICT-GRAPH SECTOR.

OUTSIDE THAT SECTOR IT CONSTRUCTIVELY NORMALIZES THE REMAINING IMPERFECTION
TO:
  * AN INDUCED ODD HOLE IN THE CONFLICT GRAPH; OR
  * ONE FIXED 7-VERTEX ODD ANTIHOLE.

AN INDUCED 9-ANTIHole IS ALREADY AN UNSAT COMPONENT.

E119 DOES NOT YET SOLVE ARBITRARY INTERACTIONS OF ODD HOLES / C7 ANTIHOLES.
THEREFORE IT IS NOT A UNIVERSAL POLYNOMIAL EXACTONE SOLVER.
P_VS_NP = OPEN.
```

## 1. Universal conflict graph

Let A be the n x n incidence matrix of a positive square cubic C4-free ExactOne
instance.

Every row and every column has weight 3, and two columns meet in at most one
row.

Build the variable-conflict graph G:

```text
V(G) = variables / columns of A;
uv in E(G) iff u and v occur together in one ExactOne clause.
```

Every clause contributes one triangle.  Linearity means every conflict edge
belongs to exactly one clause triangle.

Each variable occurs in three clauses and receives two distinct neighbours from
each clause, so G is simple and 6-regular.

As frozen in E61,

[
A^T A = 3I + Adj(G)
]

and therefore (lambda_{min}(G)ge -3).

## 2. ExactOne is exactly a maximum stable-set endpoint

A satisfying ExactOne assignment selects a set S of variables such that no two
selected variables occur in one clause.  Thus S is a stable set in G.

Every selected variable covers exactly three clauses.  Stable variables cover
disjoint clause sets.  Since there are n clauses,

[
3|S|le n.
]

Hence every stable set satisfies

[
|S|le n/3.
]

If (|S|=n/3), its selected variables cover exactly n distinct clauses, hence
every clause is covered exactly once.  Therefore

[
oxed{
ExactOne(A)iff alpha(G)=n/3.
}
]

This is the combinatorial form of E61's Hoffman-tight /(0,3)-regular-set
equivalence.

## 3. Perfect conflict graphs are a complete polynomial terminal

Grötschel, Lovász and Schrijver proved that maximum-weight stable set is
solvable in polynomial time on perfect graphs:

M. Grötschel, L. Lovász, A. Schrijver,
"Polynomial Algorithms for Perfect Graphs",
Annals of Discrete Mathematics 21 (1984), 325-356.

Perfect-graph recognition is also polynomial; constructive Berge-recognition
algorithms are known, and later polynomial odd-hole algorithms give a direct
route through the Strong Perfect Graph Theorem.

Therefore, for a target instance whose conflict graph G is perfect:

```text
1. compute a maximum stable set S in polynomial time;
2. if 3|S| = n, return SAT with S as the ExactOne assignment;
3. otherwise return UNSAT.
```

This is exact, sound, complete and polynomial on the entire perfect-G sector.

It is stronger than merely recognizing a favorable spectral endpoint: the
algorithm actually returns the discrete witness or proves that none exists.

## 4. Strong Perfect Graph Theorem gives a global obstruction router

The Strong Perfect Graph Theorem states:

[
G	ext{ is perfect}
iff
G	ext{ contains no odd hole and no odd antihole}.
]

Here a hole is an induced cycle, and an antihole is the complement of an
induced cycle.

Polynomial algorithms exist for detecting/finding odd holes.  Apply such an
algorithm to G and to its complement.  Thus failure of the perfect terminal can
be accompanied by a polynomially discoverable obstruction certificate.

So every target instance routes in polynomial time to one of:

```text
PERFECT:
  solve exactly by maximum stable set;

ODD HOLE:
  return an induced odd hole of G;

ODD ANTIHOLE:
  return an induced odd hole of complement(G).
```

## 5. Degree six collapses all large odd antiholes

Suppose an induced odd antihole has m vertices.

In the complement of C_m every vertex has internal degree

[
m-3.
]

But G is 6-regular.  Hence

[
m-3le 6,
]

so

[
mle 9.
]

For odd antiholes, (mge5).  Therefore only

[
min{5,7,9}
]

can occur.

The 5-antihole is isomorphic to C5, so it is already an odd-hole case.

Thus the only genuinely distinct antihole sizes are 7 and 9.

## 6. The 9-antihole is an immediate UNSAT component

For m=9, every vertex of the induced (overline{C_9}) already has all six of
its G-neighbours inside the antihole.

Therefore no antihole vertex has an external neighbour and the induced
(overline{C_9}) is an entire connected component of G.

Its stability number is

[
alpha(overline{C_9})
=
omega(C_9)
=
2.
]

But a 9-variable square-cubic component would require an ExactOne stable set of
size

[
9/3=3.
]

So this component has no ExactOne assignment.

Equivalently, because stable-set numbers add over connected components and
every target component obeys the universal (alphale |V|/3) bound, the
presence of an induced 9-antihole makes the whole instance UNSAT.

Hence:

[
oxed{
	ext{induced }overline{C_9}Rightarrow UNSAT.
}
]

## 7. Final global normal form after E119

Every positive square cubic C4-free ExactOne instance can now be processed in
polynomial time into exactly one of the following outcomes:

[
oxed{
egin{array}{ll}
	extbf{A.} & G	ext{ perfect: solve SAT/UNSAT exactly in polynomial time};\
	extbf{B.} & G	ext{ contains }overline{C_9}: 	ext{ return UNSAT};\
	extbf{C.} & G	ext{ contains an induced odd hole};\
	extbf{D.} & G	ext{ contains an induced }overline{C_7}.
end{array}}
]

Cases C and D are the only unresolved outputs of the router.

This is a genuine all-input coverage theorem: it does not assume TARGET6,
NO-RAW8, low nullity, low branchwidth, a cographic core, or any frozen finite
gadget.

## 8. Relation to E62 strong odd cycles

An induced odd hole

[
v_0v_1dots v_{ell-1}v_0
]

in G has a useful dual-hypergraph interpretation.

Each consecutive conflict edge (v_i v_{i+1}) comes from a unique ExactOne
row, because the source is linear.  These consecutive rows are distinct:
otherwise three consecutive hole vertices would lie in one clause triangle and
the first and third would form a chord.

Consequently the hole supplies a strong odd-cycle pattern in the dual
3-uniform hypergraph studied in E62.

Important direction:

```text
CONFLICT-GRAPH INDUCED ODD HOLE
    => E62 STRONG ODD CYCLE.
```

The converse is not asserted: a strong hypergraph cycle can have extra
intersections outside the displayed cycle rows, producing chords in G.

So E119 does not duplicate E62.  It selects a chordless global subclass of the
E62 obstruction and isolates C7-antihole as the only additional bounded
imperfection primitive.

## 9. Replay fixtures

The companion checker uses four controls.

### PERFECT-SAT9

Use variables

```text
A0,A1,A2; B0,B1,B2; C0,C1,C2
```

and the nine clauses

[
(A_i,B_j,C_{i+jmod3}),qquad i,jin{0,1,2}.
]

The carrier is square, cubic and linear.  Its conflict graph is
(K_{3,3,3}), hence perfect.

Its stability number is 3=n/3 and one whole part gives an ExactOne witness.

### PERFECT-UNSAT7

Use the seven lines of the Fano plane.

Its 7x7 incidence matrix is square, cubic and linear and the conflict graph is
(K_7), hence perfect.

Its stability number is 1, so it is UNSAT.

### E61 SAT12 and UNSAT12

The frozen E61 controls both contain induced C5 holes.  They therefore
deliberately leave the perfect terminal, while still giving opposite SAT/UNSAT
outcomes.

This demonstrates that E119 is a router/terminal, not a disguised assumption
that all target conflict graphs are perfect.

## 10. Correct E120 target

E119 reduces the universal unsolved branch to two graph primitives:

```text
1. induced odd holes of arbitrary odd length >=5;
2. induced 7-antiholes.
```

The next theorem must plug these directly into a total algorithm.

Priority:

```text
E120 ODD-HOLE / C7-ANTIHole ELIMINATION

For a polynomially found obstruction:
  * derive its exact interface to the remaining ExactOne instance;
  * represent that interface without enumerating exponentially many states;
  * prove either an additive decomposition
        T(n) <= T(n1)+T(n2)+poly(n),
    or a strictly decreasing polynomially bounded measure;
  * preserve soundness/completeness under repeated elimination.

A local constant-size truth table is not enough if repeated elimination
multiplies branches.
```

Scientific status:

```text
E119 = GLOBAL PERFECT-GRAPH POLYNOMIAL TERMINAL
       + SPGT ALL-INPUT OBSTRUCTION ROUTER.

PERFECT CONFLICT GRAPH:
  EXACT POLYNOMIAL SAT/UNSAT.

IMPERFECT 6-REGULAR TARGET:
  ODD HOLE,
  OR C7 ANTIHOLE,
  OR C9 ANTIHOLE => UNSAT.

UNIVERSAL POLYNOMIAL SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
