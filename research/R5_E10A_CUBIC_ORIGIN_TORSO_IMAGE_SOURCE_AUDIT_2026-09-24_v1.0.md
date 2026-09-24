# R5 E10A — Cubic-Origin Torso Image Source Audit

Date: 2026-09-24

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__NO_IMAGE_THEOREM_YET`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Conceptual parent:
`R5_E10_S8_SPLITTER_INTERFACE_COMPRESSION_GATE_V1`

Immediate predecessor:
`R5_E10A_THREE_SUM_INTERFACE_COST_CONE_AND_UNIT_SERIES_PROVENANCE_2026-09-24_v1.0`

## G0 — exact object

The original E10 object is

```
M([H|f]),
H=I+P+Q over GF(2),
f=1,
```

with the origin incidence matrix square and row/column weight three.  The
top-level exact target remains

```
shortest_f(M)=n/3+1.
```

After source-bound binary 1/2/3-sum decomposition and absorption of no-S8
components, the authoritative survivor is a 3-connected S8-containing
distinguished-f shortest-circuit interface.

The earlier PA-0005 audit deliberately widened this survivor to an arbitrary
two-signature-row graph lift

```
[B_G;S],  S in GF(2)^(2 x E),
```

equivalently a GF(2)^2-labelled graph-lift / prescribed-label T-join object.

The present audit asks only:

> Which 3-connected two-row-lift torsos, including their virtual separator
> elements, can actually occur as minors / decomposition pieces of an
> original M([I+P+Q|1]) instance?

This is an image/minor question.  It is not a request to reimpose literal
I+P+Q form, cubic degree, or a local n/3 bound on a torso.

## G1 — internal anti-duplication

Recursive HEAD and PR-lineage searches covered:

- cubic origin / I+P+Q;
- torso image / minor image;
- 3-regular / 3-uniform binary representations;
- two-row graph lifts;
- S8-containing 3-connected torsos;
- separator-conditioned costs;
- puncturing / shortening / code minors;
- LDPC / Tanner / XORSAT;
- normal realizations.

No existing Fundamentum artifact characterizes the minor image of
M([I+P+Q|1]) inside the PA-0005 two-row class.

Already sealed and not to be repeated:

1. local cubicity is not hereditary under minors / 1/2/3-sums;
2. scalar 3-sum interface costs are exactly the positive integer three-point
   metric cone;
3. arbitrary positive integer effective weights can be produced from unit
   series material;
4. generic PA-0005 deterministic shortest-path / PIT / regular-path work is
   wider than the present lineage image question.

## G2 — canonical external languages

The closest public languages are:

1. binary linear-code minors:
   puncturing and shortening correspond to matroid contraction/deletion
   (up to the standard cycle/cocycle convention);

2. (3,3)-regular LDPC / 3-regular 3-XORSAT:
   square binary parity-check matrices with every row and every column of
   weight three;

3. normal graphical realizations of linear codes:
   arbitrary code constraints may be normalized using state variables,
   equality/repetition constraints, and local parity constraints;

4. rank-2 lifts of graphic matroids / group-labelled graphs:
   the generic PA-0005 child, not the cubic-origin image itself.

## G3 — public source exhaustion

### S1 — Kashyap: code minors and decomposition pieces

Kashyap, *A Decomposition Theory for Binary Linear Codes* (IEEE Trans. IT,
2008), explicitly identifies code minors with sequences of puncturing and
shortening and transfers binary-matroid decomposition to codes.

Consequence:

```
TORSO / DECOMPOSITION PIECE
=
PROPER MINOR INFORMATION
```

is source-bound.

This supports the PA-0006 formulation as a minor-image problem.

It does not characterize which minors arise from the special square
(3,3)-regular I+P+Q origin.

### S2 — Forney normal realizations: strong adjacent donor, not a minor theorem

Forney, *Codes on Graphs: Normal Realizations* (IEEE Trans. IT 47(2), 2001),
proves that general state realizations can be put into normal form; variables
can be copied through equality/repetition constraints so that state variables
have bounded graphical incidence.

This is a strong warning that sparse local factor-graph representations may be
universal at the level of realization.

However:

```
NORMAL FACTOR-GRAPH REALIZATION
!=
MATROID MINOR OF A SQUARE (3,3)-REGULAR PARITY-CHECK MATRIX.
```

The source does not supply the required puncture/shorten sequence, does not
force every local node and variable to degree exactly three, and does not bind
the distinguished all-ones column f or the E10 lower-bound-tight query.

Classification:
`ADJACENT_UNIVERSAL_REALIZATION_DONOR_ONLY`.

### S3 — Jia et al. 2026: cubic regularization transfers hardness

Jia--Peng--Liu--Wang--Yan,
*On the Intractability of the Minimum Distance Problem for Regular LDPC Codes*,
arXiv:2606.23161v3 (2026), prove NP-completeness of minimum distance for
(3,3)-regular Tanner graphs.  Their degree-preserving framework uses
hyperedge decomposition, check-node splitting, and controlled variable
replication, with explicit maps among nonzero codewords / even covers.

This is the strongest located source warning against treating cubic Tanner
geometry alone as a tractability mechanism.

But its semantic object is homogeneous minimum distance:

```
Hx=0, x!=0,
minimize |x|.
```

It does not state that an arbitrary binary matroid/code occurs as a minor of
a square (3,3)-regular code, and it does not preserve the JANUS affine object

```
Hx=1
+
distinguished f=1
+
shortest_f=n/3+1.
```

Classification:
`STRONG_ADJACENT_CUBIC_REGULARIZATION_DONOR__NO_EXACT_IMAGE_COLLISION`.

### S4 — Nelson--van Zwam: minor-closed code universality theorem

Nelson--van Zwam,
*On the existence of asymptotically good linear codes in minor-closed
classes* (2014), prove that a GF(p^n)-linear code class closed under
puncturing and shortening and containing an asymptotically good sequence must
contain all GF(p)-linear codes.

This is a powerful general minor-universality theorem.

It does not currently close PA-0006 because no source was located establishing
that the specific square (3,3)-regular I+P+Q origin class, or the relevant
minor-closed closure with distinguished f and the E10 objective, contains the
required asymptotically good sequence.  In particular, square (3,3) parity
checks have design rate zero; actual rank deficiency can be nonzero, but the
hypothesis needed by the theorem is not automatic.

Classification:
`GENERAL_MINOR_UNIVERSALITY_DONOR__HYPOTHESIS_NOT_BOUND`.

### S5 — Walsh / group-labelled lift language

Walsh, *A New Matroid Lift Construction and an Application to Group-Labeled
Graphs* (EJC 29(1), 2022), supplies the rank-k lift language for group-labelled
graphs.  For the additive group of GF(4), the relevant group is isomorphic to
GF(2)^2.

This source binds the generic PA-0005 child language.  It does not characterize
which such rank-2 lifts are minors of cubic I+P+Q origins.

Classification:
`GENERIC_CHILD_LANGUAGE_SOURCE_BOUND`.

### S6 — 3-regular 3-XORSAT / regular LDPC identity

The standard 3-regular 3-XORSAT model is represented by a square binary matrix
having exactly three ones in each row and column.  This is exactly the Tanner
geometry of the H=I+P+Q origin after a 1-factorization / relabelling of the
3-regular bipartite incidence graph.

This identifies a useful canonical search language:

```
SQUARE (3,3)-REGULAR BINARY PARITY-CHECK MINOR IMAGE.
```

No located source gives an excluded-minor characterization or a universal
minor-embedding theorem for this exact class with distinguished f=1.

## G4 — collision matrix

| JANUS object | External object | Classification | Action |
| --- | --- | --- | --- |
| binary torso / code minor | puncturing + shortening | EXACT_LANGUAGE_COLLISION | source-bind Kashyap |
| square row/column-weight-3 H | (3,3)-regular LDPC / 3-regular 3-XORSAT | EXACT_REPRESENTATION_LANGUAGE | use as canonical search term |
| arbitrary sparse local code realization | Forney normal realization | ADJACENT_STRONGER_REPRESENTATION_DONOR | do not promote to matroid-minor theorem |
| cubic regularization of minimum distance | Jia et al. (3,3)-regular LDPC hardness | STRONG_ADJACENT_DONOR | cubicity alone not leverage; affine image not settled |
| minor-closed code class + asymptotically good sequence | Nelson--van Zwam universality | CONDITIONAL_STRONG_DONOR | hypotheses not established for cubic origin |
| generic two-row lift | GF(2)^2 group-labelled rank-2 lift | SOURCE_BOUND CHILD LANGUAGE | PA-0005 only |
| exact cubic-origin torso image | minors of M([I+P+Q|1]) intersect two-row 3-connected S8 survivors | SCOPED_GAP_SURVIVES | authorize image theorem / falsifier |

## Audit decision

No located public theorem either:

1. proves that every relevant two-row 3-connected S8-containing torso is a
   minor of some M([I+P+Q|1]); or
2. gives an exact invariant characterizing the proper subclass that is.

Therefore:

```
PA-0006-CUBIC-ORIGIN-TORSO-IMAGE
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1
```

with first priority:

```
KILLER A
=
construct an exact polynomial minor embedding of a sufficiently universal
two-row 3-connected scaffold into a square (3,3)-regular H=I+P+Q origin,
with explicit deletion/contraction witness maps;

OR

KILLER B
=
exhibit the first exact minor invariant of square (3,3)-regular origins that
the PA-0005 complete GF(2)^2 scaffold violates.
```

Mandatory firewalls:

- normal factor-graph realization is not matroid-minor realization;
- homogeneous (3,3)-regular minimum-distance hardness is not the JANUS affine
  all-ones-coset problem;
- do not impose local cubic degree or local n/3 on a torso;
- scalar separator weights are already exhausted by the predecessor theorem;
- every claimed lineage self-embedding must bind the distinguished element and
  the deletion/contraction sequence, not just codeword feasibility.

## Ceiling

```
CUBIC TANNER GEOMETRY ALONE
=
NOT A KNOWN TRACTABILITY MECHANISM

GENERIC NORMAL-REALIZATION UNIVERSALITY
=
ADJACENT ONLY

GENERIC (3,3)-REGULAR MDP HARDNESS
=
ADJACENT ONLY

EXACT M([I+P+Q|1]) TORSO/MINOR IMAGE
=
NO CLOSURE LOCATED

NEW IMAGE MATH
=
AUTHORIZED ONLY AFTER THIS AUDIT

D1
=
EMPTY

P_VS_NP
=
OPEN
```


## Re-audit addendum — sparse column-weight-three minor universality

Pu Gao and Peter Nelson,
*Minors of matroids represented by sparse random matrices over finite fields*
(arXiv:2307.15685), prove that for every fixed column weight (k>=3), including
(k=3), a sufficiently dense random sparse representation contains any fixed
simple representable matroid (N) as a minor asymptotically almost surely.

For the binary case this is a strong negative control against treating

```
COLUMN WEIGHT THREE
```

by itself as a restrictive minor-image invariant.

It does **not** close PA-0006:

- the target matroid (N) is fixed while the host grows;
- the host is not required to be square;
- row weight is not simultaneously constrained to three;
- the distinguished all-ones element (f) is absent;
- no polynomial growing-target embedding or JANUS interface/objective
  preservation theorem is supplied.

Classification:

```
COLUMN-WEIGHT-3 FIXED-MINOR UNIVERSALITY
=
STRONG ADJACENT DONOR / BARRIER

NOT
=
GROWING-TARGET CUBIC [I+P+Q|1] IMAGE THEOREM
```

This strengthens the PA-0006 source firewall without changing its scoped PASS.
