# R5 E9 — Contextual MIS-Kernel Transfer and Cubic Claw Normal Form

Date: 2026-09-26

Authority:
`JANUS_DERIVED_EXACT_TRANSFER_AFTER_PA0022__KNOWN_MIS_REDUCTIONS_SOURCE_BOUND__NO_UNIVERSAL_KERNELIZATION_CLAIM`

Authorizing audit:
`PA-0022-CONTEXTUAL-CONFLICT-GRAPH-MIS-KERNELIZATION`

Conceptual parent:
`R5_E9_ODD_HOLE_CONTEXTUAL_MULTISELECTOR_DOMINANCE_GATE_V1`

Checker:
`experiments/r5_e9_contextual_mis_kernel_transfer.py`

## 1. Exact alpha-offset transfer theorem

Let F be a square cubic positive Exact-One instance with n variables and n
clauses, and let G=C(F) be its variable-conflict graph.

NM-0022 proves

```
SAT(F)
iff
alpha(G)=n/3.
```

Now let an exact graph transformation produce G' together with an integer
offset delta and a polynomial reconstruction map such that

```
alpha(G) = delta + alpha(G').
```

Then immediately

```
SAT(F)
iff
alpha(G') = n/3 - delta.
```

If the reduced graph solver returns an independent set I' of the target size,
the graph reduction lifts I' to an independent set I of size n/3 in G.
By the NM-0022 bridge, I is automatically an Exact-One witness for F.

Therefore every source-backed exact MIS reduction with an alpha offset and
polynomial lift is a legitimate contextual witness-contraction module for the
current perfect-kernel route.

The reduced graph need not itself be another cubic conflict graph.  What must
be retained is:

```
target alpha value
+
reduction/lift stack
+
polynomial total representation.
```

This is a representation change, not a claim that the source language is
closed under the reduction.

## 2. First explicit contextual dominance rule: neighborhood domination

A particularly transparent source-bound graph rule has a JANUS witness-map
interpretation.

Suppose two vertices u != v satisfy

```
N[u] subseteq N[v].
```

If an independent set I contains v, replace v by u.

Every other member of I is outside N[v], hence outside N[u], so

```
(I - {v}) union {u}
```

is independent and has the same size.

Consequently some maximum independent set avoids v and

```
alpha(G)=alpha(G-v).
```

For the exact-one source, if a satisfying size-n/3 stable set used v, the same
replacement produces another size-n/3 stable set and therefore another exact
Exact-One witness.

Thus the graph domination certificate is literally a context-specific
witness-dominance map that removes one selector state.

The checker contains a 9-variable literal cubic source with

```
N[8] subseteq N[3],
```

and verifies

```
alpha(G)=alpha(G-3)=3=n/3.
```

It also checks the replacement map on every independent set containing 3.

This is a positive control only; domination need not exist in every residual.

## 3. Grouped reductions already source-bound

PA-0022 source-binds stronger known modules:

- vertex folding;
- unconfined / packing reductions;
- maximum critical-independent-set / crown reductions;
- other exact MIS kernelization rules;
- struction, with the explicit warning that generic repeated struction can
  increase total state.

When any such rule supplies

```
alpha(G)=delta+alpha(G')
```

with a polynomial lift, Section 1 imports it without new SAT mathematics.

A critical-set/crown reduction is especially close to the desired grouped
multi-selector dominance: it can certify an entire independent block that is
safe to keep in some optimum and delete its neighborhood in one move.

## 4. New source-specific claw normal form

Every source variable x occurs in three clauses:

```
C_1={x,y_1,z_1}
C_2={x,y_2,z_2}
C_3={x,y_3,z_3}.
```

Every neighbor of x in the conflict graph belongs to at least one of the three
source-clause pairs.

Within each pair the two vertices are adjacent.

Therefore

```
alpha(G[N(x)]) <= 3,
```

so every cubic source conflict graph is K1,4-free.

Now suppose x is the center of an induced claw with leaves p,q,r.

No two leaves can occur with x in the same source clause, otherwise they would
be adjacent.

For each leaf, record the nonempty set of x-clauses in which it occurs.
The three leaf incidence sets are pairwise disjoint subsets of a three-element
set.  Hence each is a singleton and together they cover all three clauses.

Thus:

```
EVERY CONFLICT CLAW CENTERED AT x
=
ONE INDEPENDENT LEAF FROM EACH OF THE THREE x-CLAUSES.
```

This gives a canonical source-coordinate pivot for the contextual gate.

## 5. Claw-free is a genuine additional P-island

PA-0022 source-binds polynomial MWIS on claw-free graphs.

This is not redundant with NM-0022's perfect-graph terminal.

The checker gives a literal 9-variable cubic source whose conflict graph:

```
is claw-free,
contains an induced C5,
therefore is imperfect,
alpha=2<3=n/3,
hence is Exact-One UNSAT.
```

The instance is decided polynomially by the claw-free MIS theorem even though
the perfect-graph terminal does not apply.

Therefore before new contextual odd-hole mathematics:

```
perfect conflict graph
OR
claw-free conflict graph
=>
POLYNOMIAL TERMINAL.
```

## 6. What remains after source-backed closure

Do not infer that known MIS kernelization solves the whole source class.

The exact cubic source class is K1,4-free already, and the rank-3 Exact-One
layer remains the frozen hard control.  Generic struction can blow up
intermediate size, while domination/folding/unconfined/critical-set rules can
all reach irreducible kernels.

Accordingly, the next mathematical object should be studied only after:

1. perfect-graph terminal check;
2. claw-free terminal check;
3. all selected polynomial exact MIS reductions that preserve a polynomial
   alpha-offset/lift representation have been exhausted;
4. the actual PA-0001 residual promises are rechecked whenever a source-level
   representation is reconstructed.

Define the live object:

```
ODD_HOLE_CONTEXTUAL_MIS_REDUCTION_LEAN_CORE.
```

It still requires instance-specific destruction of selector multiplicity.

## 7. Sharpened gate

Freeze:

```
R5_E9_ODD_HOLE_CONTEXTUAL_MIS_REDUCTION_LEAN_DOMINANCE_GATE_V1
```

A PASS must find, on every nonterminal lean core, either:

- a new polynomially synthesizable contextual witness map / grouped dominance
  operation with a strict live-dimension decrease; or
- a normalization into an already certified polynomial graph/CSP carrier.

It may not count a source-bound MIS rule as new JANUS mathematics.

## 8. Verdict

```
NM-0026
ALPHA-OFFSET MIS -> EXACT-ONE TRANSFER
=
PASS

GRAPH DOMINATION AS CONTEXTUAL WITNESS MAP
=
PASS / SOURCE-BOUND RULE IMPORT

CRITICAL-SET / CROWN / FOLDING / UNCONFINED
=
SOURCE-BOUND DONORS

CUBIC CONFLICT GRAPH
=
K1,4-FREE

ANY CONFLICT CLAW
=
ONE LEAF FROM EACH CENTER SOURCE CLAUSE

CLAW-FREE CONFLICT GRAPH
=
POLYNOMIAL TERMINAL

KNOWN MIS REDUCTIONS UNIVERSAL
=
NOT PROVED

NEXT
=
ODD_HOLE_CONTEXTUAL_MIS_REDUCTION_LEAN_DOMINANCE

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
