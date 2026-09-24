# R5 E10A — Cubic-Origin Torso Image Source Audit (PA-0006)

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__NO_IMAGE_THEOREM_YET`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Conceptual parent:
`R5_E10_S8_SPLITTER_INTERFACE_COMPRESSION_GATE_V1`

Immediate predecessor:
`R5_E10A_THREE_SUM_INTERFACE_COST_CONE_AND_UNIT_SERIES_PROVENANCE_2026-09-24_v1.0`

## 1. Why PA-0006 is required

The original E10 object is

```
M([H|f]),
H=I+P+Q,
f=1,
row/column weight 3 at the full origin,
shortest_f = n/3+1.
```

After no-S8 sum components are absorbed, the survivor is a 3-connected
S8-containing distinguished-f interface.

PA-0005 deliberately widened this to an arbitrary two-signature-row graphic
lift

```
[B_G;S],  S in GF(2)^(2 x E),
```

in order to expose a canonical prescribed-GF(2)^2 path/T-join primitive.

The subsequent P2 audit proved that scalar separator-cost provenance is not a
standalone restriction: every positive integer 3-sum metric triple is
unit-graphic realizable, and arbitrary positive integer edge weights can be
realized by unit series expansion.

Therefore the next admissible question is an image question, not another
generic two-row algorithm:

```
Which 3-connected two-row-lift torsos/interfaces can actually occur
as proper minors / decomposition pieces of an original M([I+P+Q|1])?
```

No new image theorem is attempted in this audit.

## 2. Exact minor semantics: Kashyap

Kashyap, *A Decomposition Theory for Binary Linear Codes*,
IEEE Trans. Inf. Theory 54(7), 2008 (arXiv:cs/0611028), gives the exact
code/matroid semantics needed here:

- code minors are obtained by puncturing and shortening;
- these correspond to matroid contraction and deletion;
- in a complete decomposition tree, non-root pieces are proper minors of the
  original code/matroid;
- the leaves can be chosen 3-connected and internally 4-connected, with the
  decomposition constructible in polynomial time.

Therefore PA-0006 must reason about genuine deletion/contraction
(puncture/shorten) image.  A sparse factor-graph realization or degree-reduction
gadget is not, by itself, evidence that the resulting object is a matroid minor
of the cubic origin.

Classification:

```
CODE MINOR = PUNCTURE/SHORTEN
=
EXACT SEMANTIC DONOR

NORMAL / TANNER REALIZATION
!=
MINOR IMAGE
unless an explicit deletion/contraction map is proved.
```

## 3. Column-weight three is not a plausible standalone invariant

Pu Gao and Peter Nelson,
*Minors of matroids represented by sparse random matrices over finite fields*,
arXiv:2307.15685, prove a strong minor-universality result for sparse random
representations.

For every fixed k>=3, and in particular k=3, once the column density passes the
stated threshold, a random matrix whose columns have support exactly k contains
any fixed simple representable matroid N as a minor asymptotically almost
surely (over GF(2), any fixed simple binary N).

This is a mandatory barrier against using

```
COLUMN WEIGHT 3
```

alone as the missing cubic-origin invariant.

However this theorem does NOT close PA-0006:

- N is fixed while the random host size grows; it does not provide a
  polynomial embedding of an arbitrary growing target torso;
- the host need not be square;
- row weight is not simultaneously fixed to three;
- there is no distinguished all-ones column f whose provenance must be kept;
- the theorem does not preserve the JANUS lower-bound-tight objective or
  separator interface role.

Classification:

```
K=3 SPARSE-MATRIX FIXED-MINOR UNIVERSALITY
=
STRONG ADJACENT BARRIER

NOT
=
CUBIC [I+P+Q|1] GROWING-TARGET IMAGE THEOREM
```

## 4. (3,3)-regular LDPC hardness is also adjacent, not an image theorem

Jia--Peng--Liu--Wang--Yan,
*On the Intractability of the Minimum Distance Problem for Regular LDPC Codes*,
arXiv:2606.23161 (2026), prove NP-completeness of minimum distance already for
(3,3)-regular Tanner graphs. Their reductions use degree-preserving
transformations and preserve explicit nonzero-codeword/even-cover
correspondences.

This is strong evidence that square cubic Tanner geometry alone cannot be
treated as a tractability mechanism.

But the source studies the homogeneous codeword problem

```
Hx=0, x!=0,
```

not the JANUS distinguished affine/all-ones object

```
Hx=1
<-> shortest circuit through f
```

nor the exact proper-minor image of a matrix of the form [I+P+Q|1].

Classification:

```
(3,3)-REGULAR LDPC MINIMUM-DISTANCE HARDNESS
=
BARRIER AGAINST CUBICITY-ALONE

NOT
=
EXACT CUBIC-ORIGIN TORSO IMAGE CHARACTERIZATION
```

## 5. Normal realizations are not minor certificates

Forney, *Codes on graphs: normal realizations*,
IEEE Trans. Inf. Theory 47(2), 520--548 (2001),
DOI 10.1109/18.910573, proves that graphical/state realizations can be put into
normal form, with symbol variables of degree one and state variables of degree
two.

This is a representation/realization theorem. It does not state that the
represented code or matroid is obtained as a deletion/contraction minor of a
square (3,3)-regular parity-check matrix, much less of [I+P+Q|1].

Firewall:

```
FACTOR-GRAPH / NORMAL-REALIZATION UNIVERSALITY
!=
MATROID-MINOR UNIVERSALITY.
```

## 6. Direct collision search

Queries covered:

- cubic binary matroid minors;
- binary matroid column-weight-three universality;
- 3-regular / (3,3)-regular parity-check matrices and minors;
- sparse random binary matroid minors;
- puncturing/shortening and code decomposition;
- normal graph realizations of binary linear codes;
- cubic Tanner degree-regularization;
- distinguished all-ones column under minors;
- [I+P+Q|1] minors / three-permutation binary matrices;
- 3-connected two-row lift minors of cubic binary matrices.

No located source gives either:

A. a polynomial construction embedding an arbitrary growing two-row target
   torso as a proper minor/interface of some square cubic [I+P+Q|1] origin
   while preserving distinguished-f provenance; or

B. an excluded-minor / rank / cycle-cocycle invariant that characterizes the
   image of those cubic origins.

This is a scoped literature conclusion, not an absolute novelty claim.

## 7. Collision matrix

```
CODE MINOR <-> PUNCTURE/SHORTEN
=
EXACT SOURCE-BOUND SEMANTICS

COLUMN-WEIGHT-3 FIXED-MINOR UNIVERSALITY
=
STRONG ADJACENT BARRIER

(3,3)-REGULAR LDPC HARDNESS
=
STRONG ADJACENT BARRIER

FORNEY NORMAL REALIZATION
=
ADJACENT DIFFERENT SEMANTICS

LOCAL TORSO I+P+Q / LOCAL CUBIC DEGREE
=
FORBIDDEN BY E10 FIREWALL

SCALAR 2/3-SUM COST PROVENANCE
=
ALREADY EXHAUSTED BY PREDECESSOR

GROWING-TARGET CUBIC-ORIGIN TORSO IMAGE
=
SCOPED GAP SURVIVES
```

## 8. Authorized mathematical gate after this audit

Freeze:

```
R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1
```

Canonical question:

```
Given a 3-connected S8-containing two-row-lift torso/interface T,
determine whether T (with the required distinguished/interface provenance)
can occur as a proper minor/decomposition piece of some
M([I+P+Q|1]).
```

Only two PASS exits are authorized:

A. **lineage universalization** —
   a polynomial construction embedding an arbitrary growing prescribed
   GF(2)^2 shortest-path/two-row target into an actual cubic origin, with an
   explicit deletion/contraction and interface witness map; or

B. **strict image invariant** —
   an exact invariant obeyed by every such cubic-origin minor/interface and
   violated by the generic PA-0005 self-embedding family.

Mandatory firewalls:

- fixed-minor asymptotic universality is not growing-target universality;
- sparse/normal/Tanner realization is not minor provenance;
- do not reimpose local I+P+Q or local cubicity on a torso;
- do not reuse scalar separator weights as the invariant;
- preserve distinguished-f/interface provenance explicitly;
- no Bentert/PIT re-entry before this image gate is resolved or bypassed.

## 9. Scientific ceiling

```
PA-0006 SOURCE AUDIT
=
PASS_SCOPED_GAP_CONFIRMED

DIRECT EXTERNAL IMAGE CHARACTERIZATION
=
NOT LOCATED

COLUMN WEIGHT 3 AS IMAGE LEVERAGE
=
NEGATIVE CONTROL

(3,3)-REGULARITY AS TRACTABILITY LEVERAGE
=
NEGATIVE CONTROL

ACTUAL CUBIC-ORIGIN GROWING-TARGET IMAGE
=
OPEN

NEW IMAGE MATH
=
AUTHORIZED ONLY INSIDE
R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1
```
