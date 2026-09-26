# R5 E9 — Odd-Hole High-Girth Attachment Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__EXPANSION_DOES_NOT_SOURCE_BIND_LOCAL_OVERLAP`

Immediate predecessors:

```
PA-0022-CONTEXTUAL-CONFLICT-GRAPH-MIS-KERNELIZATION
NM-0026-CONTEXTUAL-MIS-KERNEL-TRANSFER
PA-0023-REGULAR-UNIFORM-CONFLICT-EXPANSION
NM-0027-REGULAR-UNIFORM-CONFLICT-EXPANSION
```

## G0 — exact object

NM-0027 proves that every independent set I of the untouched literal cubic
conflict graph satisfies

```
|N(I)| >= 2|I|.
```

The proposed next route asks whether an induced odd hole inside the
2-expanding, claw-containing source must therefore exhibit useful local
attachment overlap around the hole.

For an induced C5

```
x_0,x_1,x_2,x_3,x_4
```

write the five edge clauses

```
C_i={x_i,x_{i+1},w_i}
```

and the third occurrence clauses

```
D_i={x_i,a_i,b_i}.
```

The concrete candidate leverage is:

> Does source regularity plus independent-set 2-expansion force identities,
> repeated attachments, domination, or another bounded local overlap among
> the fifteen external ports w_i,a_i,b_i?

A theorem of that form would justify an overlap-driven grouped contraction.
A counterexample would move the frontier to genuinely longer-range context.

## G1 — internal anti-duplication

Repository-first search covered:

- NM-0023 odd-hole selector conservation;
- PA-0018 strong-odd-cycle / hypergraph-matching canonicalization;
- NM-0024 full-boundary matching/delta-matroid barrier;
- NM-0026 imported exact MIS reductions and claw normal form;
- NM-0027 regular-uniform 2-expansion and critical/crown extinction;
- older balanced / strong-odd-cycle artifacts.

No JANUS artifact was found that studies a cubic bipartite **incidence graph
of girth ten** as a literal Exact-One source control, or that proves/falsifies
mandatory local odd-hole attachment overlap from NM-0027 expansion.

## G2 — canonical external object

A square cubic positive Exact-One instance is equivalently a cubic bipartite
incidence / Levi graph:

- one bipartition = variables;
- the other = clauses;
- every vertex has degree three.

A length-10 incidence cycle

```
x_0-C_0-x_1-C_1-...-x_4-C_4-x_0
```

projects on the variable side to a C5 in the conflict graph.

If the incidence graph has girth at least ten, no shorter alternating cycle
can create a conflict chord or a short local attachment alias.

Thus the canonical external language is:

```
CUBIC BIPARTITE GIRTH-10 GRAPH
=
LEVI GRAPH OF A (v_3) CONFIGURATION
=
LITERAL CUBIC EXACT-ONE SOURCE WITH A STRONG 5-CYCLE.
```

## G3 — public-source exhaustion

### S1 — the classical 10-cages are exact source controls

Pisanski--Boben--Marusic--Orbanic--Graovac (2004) study the three (3,10)-cages
on 70 vertices.  They explicitly state that these graphs are bipartite and are
Levi graphs of (35_3) configurations.

Therefore each 10-cage can be read literally as:

```
35 variables
35 clauses
row degree = 3
column degree = 3
incidence girth = 10.
```

The Harries graph is one of these controls.

### S2 — an open reproducible Harries construction is available

The Sage open-source graph generator records the Harries graph as the LCF graph

```
[-29,-19,-13,13,21,-27,27,33,-13,13,19,-21,-33,29]^5
```

and its regression examples verify order 70, size 105, and girth 10.

This supplies an independently replayable finite source witness without
inventing a new graph.

### S3 — high-girth regular bipartite geometry is not exceptional

He--Luo--Xu (Discrete Mathematics, 2026) construct regular / biregular
bipartite graphs with prescribed girth, extending classical Sachs and
Furedi--Lazebnik--Seress--Ustimenko--Woldar constructions.

Their incidence-graph / hypergraph correspondence also explicitly identifies a
hypergraph g-cycle with a graph 2g-cycle.

Thus sparse high-girth incidence geometry is a standard source family, not a
JANUS-specific anomaly.

### S4 — no source closure for the proposed mandatory-overlap theorem

The targeted sweep also checked:

- 2-sections of linear hypergraphs;
- strong odd cycles in balanced-hypergraph language;
- odd-hole attachment terminology;
- regular/uniform hypergraph neighborhood bounds.

No located result states that independent-set 2-expansion in a cubic
3-uniform/3-regular source forces local overlap among the external ports of an
induced odd hole.

The cage literature points in the opposite direction and therefore demands a
direct killer test before any new overlap-based contraction theorem.

## G4 — exact permitted test

New mathematics is authorized only for the following question:

```
R5_E9_ODD_HOLE_HIGH_GIRTH_SPARSE_ATTACHMENT_GATE_V1
```

Prove or falsify:

> In a cubic bipartite incidence graph of girth at least ten containing a
> 10-cycle, the corresponding conflict C5 can have all fifteen external
> w_i,a_i,b_i ports pairwise distinct while every hole vertex remains a claw
> center and the conflict graph retains the NM-0027 2-expansion property.

The finite Harries 10-cage may be used as a positive control, but any theorem
should be stated at the general girth level when possible.

## Mandatory anti-loop controls

Do not:

- present cubic cages or Levi graphs as JANUS novelty;
- infer local overlap from the global inequality |N(I)|>=2|I|;
- call a high-girth control a survivor of every PA-0001 promise unless those
  promises are separately checked;
- infer computational hardness from girth or expansion;
- reopen critical-set/crown on the untouched literal source.

## Audit decision

```
PA-0024
=
PASS_SCOPED_GAP_CONFIRMED

CUBIC BIPARTITE GIRTH-10 SOURCE GEOMETRY
=
SOURCE-BOUND

MANDATORY LOCAL ODD-HOLE ATTACHMENT OVERLAP
FROM NM-0027 EXPANSION
=
NOT SOURCE-BOUND / KILLER TEST REQUIRED

NEW MATH
=
R5_E9_ODD_HOLE_HIGH_GIRTH_SPARSE_ATTACHMENT_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
