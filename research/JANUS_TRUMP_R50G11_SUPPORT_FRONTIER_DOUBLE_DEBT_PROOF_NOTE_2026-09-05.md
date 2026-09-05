# JANUS TRUMP R50G11 — support-frontier double-debt reduction

## Scope

Let `F` be a persisted `W<=4` state, pre-BVE clean under the frozen R33 order, and let the first R33 microproposal be BVE on `x`. Assume same-pivot R47J on `x` ends nonterminal with width `>4`.

R50G10 reduced a genuine all-alternate-doors-closed obstruction to, for every `y != x`, simultaneous failure of R49H and R47J_SAFE. R50G11 reduces the geometry of that obstruction further.

## L1 — W4 caps chi-star at six

For a bipolar pivot `y`, every positive or negative parent clause has width at most four. After deleting `y` or `-y`, each residual parent has at most three literals. A non-tautological cross-polarity union therefore has width at most

`3 + 3 = 6`.

Hence `chi_star(F,y) <= 6`.

Because pre-BVE cleanliness excludes pure variables, every present variable is bipolar. Therefore R49H is closed exactly when

`chi_star(F,y) in {5,6}`.

## L2 — exact bad-pair geometry

A width-six cross union requires residual sizes `3+3`, no overlap and no complementary pair. Therefore both parents have width four.

A width-five cross union can only have one of these residual-size/overlap geometries:

- `3+2` with zero overlap: parent widths `4 x 3`;
- `2+3` with zero overlap: parent widths `3 x 4`;
- `3+3` with exactly one common literal: parent widths `4 x 4`.

No pair of parents of width at most three can close R49H.

## L3 — a combined closed door carries two independent width debts

For alternate pivot `y != x`, R50G10 already proved from frozen definitions that R47J removes `y`, introduces no fresh variables, and is machine-safe iff it terminates or its final width is at most four.

Thus a combined closed door has both:

1. an input bad-pair certificate whose non-tautological residual union has width five or six; and
2. an independently replayable R47J final nonterminal formula containing at least one clause of width at least five.

Call these the `CHI_DEBT` and `R47J_DEBT` certificates.

## L4 — four-neighbour consequence after excluding x

Neither certificate contains pivot `y`: the chi witness is a resolvent residual union with `y` deleted, and exact DP/R47J eliminates `y` without reintroducing it.

Each certificate contains at least five distinct variables/literals. At most one of those variables can be the distinguished immediate-BVE pivot `x`. Therefore each certificate contains at least four variables from the alternate set

`A = Vars(F) \ {x}`

other than `y` itself.

Define directed edges from `y` to those alternate variables. Every combined-closed alternate pivot has at least four outgoing `CHI_DEBT` neighbours and at least four outgoing `R47J_DEBT` neighbours (the two neighbour sets may overlap).

Consequences:

- an all-alternate-doors-closed obstruction requires `|A| >= 5`, hence at least six total variables;
- the `CHI_DEBT` graph on `A` has minimum outdegree at least four;
- the `R47J_DEBT` graph on `A` has minimum outdegree at least four;
- each finite graph therefore contains a directed cycle;
- an all-doors-closed witness is not merely a wide clause: it contains a finite double-debt dependency core.

For exactly six total variables, every width-five debt certificate must use all five variables other than its own pivot. Width six is impossible because only five other variables exist.

## What is not proved

This note does **not** prove that the double-debt core is impossible. Dense directed dependency cores can exist abstractly. The remaining theorem is reachability-specific:

`NO_REACHABLE_IMMEDIATE_BVE_WIDE_STATE_CAN_REALIZE_THE_DOUBLE_DEBT_DEPENDENCY_CORE_ON_ITS_SUPPORT_FRONTIER`.

A finite no-find does not prove that statement. If an exact reachable all-doors-closed state is found, R50G11 must emit its complete per-pivot bad-pair, R47J-wide, dependency-graph and reachability certificates.

No SAT-in-P or P=NP claim follows from R50G11 alone.
