# R5 E9 - 3-Connectedness Alone Is Not a SAT Tractability Currency

Date: 2026-09-23

Authority:
SOURCE_BOUND_COMPLEXITY_CONTROL__CONNECTIVITY_ONLY__NO_P_NE_NP_CLAIM__NO_D1_PROMOTION

Parent:
R5_E9_THREE_CONNECTED_OVERLAY_PIVOT_GATE_V1

## 1. Source-hard control

Kratochvil's planar SAT line supplies an NP-hard / NP-complete restricted
3SAT family whose clause-variable incidence graph is planar and 3-connected,
with variable occurrence bounded by four. Later literature refers to this
source problem as 4-Bounded Planar 3-Connected 3SAT.

This is used here only as a complexity control.

It does not imply that the JANUS rigid overlay torso class is identical to that
source class.

## 2. Incidence 3-connectivity implies primal-variable 3-connectivity

Let H be the bipartite clause-variable incidence graph of a 3CNF instance and
let P be its primal variable graph: two variables are adjacent in P when they
occur together in one clause.

Assume H is 3-vertex-connected.

Take any set U of at most two variable vertices.

Because H is 3-connected, H-U remains connected.

For any two variables x,y outside U, choose an x-y path in H-U.
The path alternates variable and clause vertices. Every consecutive
subpath

    v - C - w

with clause vertex C can be replaced by the primal edge vw, since v and w
occur together in C.

Thus P-U is connected.

Hence P is 3-vertex-connected (for nontrivial instances with at least four
variables).

Therefore the source-hard 3-connected-incidence family also has a
3-connected primal variable backbone.

## 3. Consequence

The property

    primal / incidence backbone is 3-connected

cannot by itself be used as a theorem of polynomial SAT tractability.

Accordingly, the positive adhesion-2/SPQR contraction result should be read as:

    all low-order separations can be compiled away,

not as:

    the remaining 3-connected piece is easy.

The rigid torso solver must exploit additional algebraic / cross-layer
structure.

## 4. Relation to JANUS overlay

The exact TWO_PATH_XOR_AND_OVERLAY normal form has a canonical quotient back to
the original signed 3CNF:

- each XOR2 occurrence path contracts to one original variable bit;
- each private two-AND clause chain contracts semantically to its original OR3
  clause.

Thus a 3-connected source incidence/primal backbone can remain present after
the obvious coherence/clause quotient.

This is a scoped warning against using connectivity alone as the joint
potential.

It is NOT a theorem that every resulting SPQR rigid torso is source-hard, and
no such stronger claim is made.

## 5. Active gate

R5_E9_THREE_CONNECTED_OVERLAY_PIVOT_GATE_V1 remains open.

A useful pivot inside a rigid torso must strictly reduce some invariant beyond
ordinary vertex connectivity, for example a cross-layer algebraic or semantic
interface measure with exact lift.

## 6. Ceiling

    ADHESION <=2 COMPOSITION = PASS
    3-CONNECTIVITY ALONE = NOT A TRACTABILITY CURRENCY
    RIGID TORSO ALGEBRAIC PIVOT = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
