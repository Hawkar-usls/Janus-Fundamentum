# R5 E9 — Odd-Hole Contextual Multi-Selector Dominance Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__LOCAL_PROJECTION_AND_GENERIC_COMPILATION_SOURCE_BOUND`

Immediate predecessors:

```
NM-0023-CONFLICT-ODD-HOLE-COVERAGE-SELECTOR-CONSERVATION
PA-0018-CONFLICT-ODD-HOLE-HYPERGRAPH-MATCHING-SOURCE-AUDIT
PA-0019-ODD-HOLE-FULL-BOUNDARY-MATCHING-REALIZABILITY
NM-0024-ODD-HOLE-FULL-BOUNDARY-DELTA-MATROID-BARRIER
```

## G0 — exact changed object

NM-0024 closes ordinary matching / blossom realization of the full odd-hole
boundary.  The next object is therefore not another matching gadget.

For an odd hole with

```
C_i={v_i,v_{i+1},w_i},
D_i={v_i,a_i,b_i},
```

the changed question is:

> Can the **actual outside context** of several neighboring hole selectors be
> used to delete or identify multiple selector states at once, with a
> polynomially checkable witness map and a strict global progress measure?

The target is explicitly context-aware.  A fixed local replacement valid under
all possible future contexts is audited separately below and is not the new
scope.

## G1 — internal anti-duplication

Repository-first replay finds four decisive predecessors.

### Boundary Myhill–Nerode

`R5_E9_BOUNDARY_MYHILL_NERODE_AND_NAE4PART_STRESS_FRONTIER` proves that
for a block with labeled boundary X,

```
two blocks are interchangeable under every possible glued context
iff
their exact projected boundary relations are equal.
```

Thus a universal context-independent merge of semantically distinct boundary
states is not a new compression theorem; it would have to preserve the whole
projected relation.

### Projected native boundary compilation

`R5_E9_HETEROGENEOUS_INTERACTION_SOURCE_AUDIT` already canonicalizes exact
join/projection as projected knowledge compilation and warns that compact local
summaries do not by themselves imply a universal polynomial composition
engine.

### Witness dominance

`R5_E9_WITNESS_DOMINANCE_QUOTIENT_CONTRACTION` already proves the exact
meta-theorem:

```
R_alpha <=_w R_beta
with a polynomial witness map
=>
the dominated branch alpha may be deleted exactly.
```

It also records the grouped version and the requirement of a strict live
potential decrease.

### Persistency / improving mappings

`PA-0002-IMPROVING-MAPPING-PERSISTENCY` source-binds the broader improving
mapping / persistency language and already blocks presenting generic
persistency certification as JANUS novelty.

Therefore the only admissible new object is an odd-hole-specific **existence
and discovery theorem** for context-aware multi-selector dominance.

## G2 — local projection is already compact

There is no representation-size mystery inside the isolated odd-hole block.

From the third-occurrence clause,

```
v_i+a_i+b_i=1,
```

we have

```
a_i+b_i <= 1,
v_i = 1-a_i-b_i.
```

Substitution into the belt gives

```
a_i+b_i+a_{i+1}+b_{i+1}
=
1+w_i.
```

Hence the full projected boundary relation has an O(k)-size exact local
description using only the original ports.

Equivalently define

```
s_i=a_i+b_i=1-v_i.
```

Then

```
s_i+s_{i+1}=1+w_i.
```

This is exactly the selector conservation already exposed by NM-0023, now
written directly on the original full boundary.

So:

```
POLYNOMIAL-SIZE SYMBOLIC PROJECTION OF ONE HOLE
=
YES / ELEMENTARY

STRICT SELECTOR INFORMATION LOSS
=
NO.
```

The local projection removes syntactic variables `v_i`, but each selector is
still recoverable from the boundary:

```
v_i=1-a_i-b_i.
```

Thus mere existential elimination is not the missing contraction.

## G3 — public-source exhaustion

### S1 — projected knowledge compilation is source-bound

Bryant--Tan--Heule (SAT 2025), *Certifying Projected Knowledge Compilation*,
treat exact projection onto designated variables together with proof
certificates.

Capelli--Mengel, *Knowledge Compilation, Width and Quantification*, show how
quantification interacts with bounded-width OBDD / structured d-DNNF
representations and bounded-treewidth inputs.

These sources confirm that compact representation and certified projection of
a bounded-width local block are standard algorithmic objects.

They do not prove that repeated projections across the **global** cubic
Exact-One interaction remain polynomial or strictly destroy independent
selector choices.

Classification:

```
LOCAL PROJECTED KNOWLEDGE COMPILATION
=
SOURCE-BOUND DONOR

UNIVERSAL GLOBAL STATE COLLAPSE
=
NOT SUPPLIED.
```

### S2 — generic variable elimination is source-bound

Cooper--El Mouelhi--Terrioux study satisfiability-preserving variable
elimination for CSPs and explicitly frame generic elimination as join followed
by projection.  Their tractable elimination rules depend on structural
conditions; generic elimination may create higher-arity interaction.

For the present block the projection is compact, but NM-0023 shows the exact
hard selector is simply re-encoded in the boundary status bits.

Classification:

```
VARIABLE ELIMINATION
=
SOURCE-BOUND LANGUAGE

ODD-HOLE MULTISELECTOR DESTRUCTION
=
NOT A CONSEQUENCE.
```

### S3 — improving mappings / persistency are source-bound donors

Shekhovtsov and related persistency literature supply polynomially verifiable
families of improving mappings for several optimization settings.

JANUS PA-0002 already source-binds this language.  No located theorem says
that every nonterminal cubic Exact-One odd-hole context admits an improving
map that merges or deletes multiple hole-selector states.

Classification:

```
IMPROVING MAPPING / PERSISTENCY
=
SOURCE-BOUND DONOR

UNIVERSAL ODD-HOLE CONTEXTUAL DOMINANCE
=
NO CLOSURE LOCATED.
```

### S4 — conditional autarkies are a current adjacent donor

Recent SAT work studies conditional autarkies and proof-carrying redundancy
reasoning.  Bonacina--Bonet--Kolokolova--Lauria (SAT 2026) show that
conditional autarkies can efficiently handle several hard-looking
combinatorial principles; Shah--Byrnes--Reeves--Heule (FMCAD 2025) study
learning short clauses via conditional autarkies.

These are relevant because the desired JANUS move is also context-dependent
and witness/redundancy based.

However they do not state a universal polynomial algorithm discovering a
multi-selector autarky/dominance contraction for cubic positive Exact-One.

Classification:

```
CONDITIONAL AUTARKY
=
SOURCE-BOUND ADJACENT DONOR

CURRENT EXACT DOMINANCE EXISTENCE CLAIM
=
SCOPED GAP.
```

## G4 — context-independent quotient firewall

For the full boundary,

```
v_i = 1-a_i-b_i.
```

Therefore two different internal selector words `v` cannot project to the
same complete boundary assignment.

Boundary Myhill–Nerode then gives the decisive firewall:

if a replacement must be correct under **every possible external context**,
the exact boundary relation itself must be preserved.  An arbitrary context
can pin a distinguishing boundary assignment.

Consequently a useful quotient cannot obtain progress merely by declaring two
locally distinct hole states equivalent independent of the rest of the
instance.

The next move must exploit the **actual** outside constraints to prove that
some distinctions are unnecessary for this particular instance.

This is precisely the point at which witness dominance / improving mappings
become the correct canonical language.

## G5 — exact surviving target

Freeze the changed scope:

```
R5_E9_ODD_HOLE_CONTEXTUAL_MULTISELECTOR_DOMINANCE_GATE_V1
```

Input:

- a live cubic Exact-One / perfect-kernel residual;
- an induced conflict odd hole;
- all current polynomial P-islands already removed;
- the actual external context attached through `w_i,a_i,b_i`.

Required PASS form:

in polynomial time, for every nonterminal instance in the scope, either

1. find a nonempty grouped set of hole-selector distinctions and a
   polynomially checkable context-specific witness-dominance / improving-map
   certificate that deletes at least one independent selector degree; or

2. split/normalize the instance into already certified polynomial carriers.

Every successful move must provide:

```
exact SAT preservation
+
polynomial witness reconstruction
+
strict decrease of a polynomially bounded global potential
+
polynomial cumulative state.
```

## Mandatory anti-loop controls

Do not:

- present the O(k)-size projected odd-hole relation as new progress;
- introduce `s_i=a_i+b_i` as a fresh selector and count it as a reduction;
- retry ordinary matching / blossom realization after NM-0024;
- demand context-independent equivalence of distinct boundary states;
- compile the entire residual into a single generic OBDD/DNNF/TDD and assume
  polynomial size;
- use a SAT oracle to discover the dominating branch;
- enumerate all independent sets / selector words of an unbounded hole.

## Audit decision

```
PA-0020
=
PASS_SCOPED_GAP_CONFIRMED

LOCAL SYMBOLIC ODD-HOLE PROJECTION
=
SOURCE-BOUND / ELEMENTARY COMPACT

CONTEXT-INDEPENDENT STATE MERGING
=
BLOCKED BY BOUNDARY MYHILL-NERODE SEMANTICS

WITNESS DOMINANCE / IMPROVING MAP LANGUAGE
=
SOURCE-BOUND DONOR

UNIVERSAL CONTEXT-AWARE MULTISELECTOR DOMINANCE
=
NO SOURCE CLOSURE LOCATED

NEXT
=
R5_E9_ODD_HOLE_CONTEXTUAL_MULTISELECTOR_DOMINANCE_GATE_V1

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
