# R5 E10A — Origin-Preserving Parity-Regular Re-Audit

Date: 2026-09-24

Authority:
`SOURCE_REAUDIT_ONLY__REPRESENTATION_CHANGE__NO_DETERMINISTIC_SOLVER_CLAIM`

Re-opens representation analysis inside:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Parent scientific route:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

## 1. Why re-audit is mandatory

The PA-0005 audit already checked Yamaguchi's non-returning A-path / `|Omega|<=4`
result and classified it as an adjacent different model, not as a deterministic
solver for prescribed-sum shortest paths.

The representation has now changed materially:

```
GF(2)^2 prescribed-label simple path
  -> alpha double cover
  -> fixed-endpoint vertex-regular path + one beta parity bit
  -> vertex splitting / endpoint gadget
  -> arc-regular skew-symmetric path + one beta parity bit.
```

Under the global no-duplication law, this representation change requires
re-audit. It does not authorize reopening Pap/Yamaguchi as a new route by name.

## 2. New external source donor: skew forbidden-pair paths

Yinnone (1997), *On paths avoiding forbidden pairs of vertices in a graph*,
Discrete Applied Mathematics 74(1):85–92,
DOI 10.1016/S0166-218X(96)00017-0, studies paths that use at most one vertex
from each forbidden pair under a skew-symmetry condition. The paper proves
polynomial equivalence of this skew forbidden-pair path problem with the
matching augmenting-path problem.

This is the closest canonical external language located for the mate-regularity
part of the transformed JANUS object.

Classification:

```
SKEW_FORBIDDEN_PAIR_REGULARITY
=
SOURCE_BOUND STRUCTURAL DONOR

NOT
=
PRESCRIBED-PARITY OPTIMIZATION SOLVER
```

## 3. New external barrier interpretation: parity augmenting paths

Murakami--Yamaguchi (2025),
*An FPT Algorithm for the Exact Matching Problem and NP-hardness of Related
Problems*, IEICE Trans. Inf. & Syst. E108-D(3), DOI
10.1587/transinf.2024FCP0009, Corollary 15, prove that Odd Augmenting Path is
NP-hard even on bipartite graphs when the input matching has size n/2-1 and
there is exactly one matching edge of weight one.

This does not prove hardness of the JANUS origin subclass. It does establish a
mandatory firewall:

```
ARBITRARY PARITY-REGULAR / MATCHING-AUGMENTING PATH SPACE
MAY CONTAIN KNOWN NP-HARD PARITY SUBPROBLEMS.

THEREFORE
DO NOT BROADEN THE E10A TARGET
FROM ITS ALPHA-DOUBLE-COVER ORIGIN
TO ARBITRARY SKEW-SYMMETRIC PARITY-REGULAR GRAPHS.
```

## 4. Pap/Yamaguchi status remains unchanged

The earlier PA-0005 classification remains authoritative:

```
NONRETURNING_A_PATH_LABELSET_AT_MOST_FOUR
=
ADJACENT_DIFFERENT_MODEL.
```

The finite set Omega in that theory is a transported terminal-state alphabet.
No theorem located in this re-audit identifies arbitrary mate-history in the
JANUS parity-regular instance with an Omega of size at most four.

No independent Pap/Yamaguchi branch is opened.

## 5. Origin-class rule

Any theorem or counterexample stated after transformation to skew space must
carry an origin certificate before it changes the authoritative E10A frontier:

```
origin_class
=
GF2_SQUARED_UNDIRECTED_BASE

bridge
=
ALPHA_DOUBLE_COVER
+
FIXED_ENDPOINT_VERTEX_TO_ARC_REGULAR_GADGET

weight_preservation
=
PASS

parity_preservation
=
PASS

witness_roundtrip
=
PASS
```

Without this certificate the result is only a generic-skew control.

## 6. Reopen basis

The concrete reopen basis is:

1. the alpha-cover / vertex-regular / arc-regular representation is new relative
   to the original PA-0005 source classification;
2. Yinnone supplies a previously unrecorded exact structural donor for
   skew forbidden-pair regularity;
3. Murakami--Yamaguchi supplies a sharp parity-augmenting-path hardness
   firewall against broadening the transformed target;
4. the next mathematical question is therefore origin preservation, not a
   generic parity-regular solver.

## 7. Authorized child

Only the following scoped barrier test is authorized next:

```
R5_E10A_ORIGIN_PRESERVING_PARITY_REGULAR_GATE_V1

Question:
Does the unbounded GK fragment-passage obstruction have an explicit
GF(2)^2 undirected unit-weight preimage under the exact alpha-cover and
fixed-endpoint regular-path bridge?
```

## 8. Ceiling

```
YINNONE SKEW FORBIDDEN-PAIR PATH
=
SOURCE-BOUND DONOR

GENERIC ODD AUGMENTING PATH
=
KNOWN NP-HARD BARRIER

PAP/YAMAGUCHI NONRETURNING <=4
=
ADJACENT DIFFERENT MODEL / DO NOT REOPEN

ORIGIN-PRESERVING PREIMAGE TEST
=
AUTHORIZED

DETERMINISTIC GF(2)^2 PRESCRIBED-LABEL SHORTEST PATH
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
