# R5 E8 6I — Rank-Width Compression Control

Date: 2026-09-23

Authority: SOURCE_BOUND_POSITIVE_CONTROL_PLUS_UNIVERSAL_WIDTH_NEGATIVE__NO_D1_PROMOTION

## Positive control

Ganian, Hlinený and Obdrzálek give parameterized polynomial algorithms for SAT/#SAT with single-exponential dependence on formula rank-width. Thus cut-rank is a genuine compression currency distinct from treewidth and can be useful on low-rank-width instances.

## JANUS universality test

For any simple graph G on variables x_1,...,x_n, construct a 3CNF having, for every edge {i,j} of G, one clause containing x_i, x_j and a fresh private dummy d_ij.

In the JANUS quadratic expansion each clause contains the product x_i x_j. No clause is added for nonedges among the original variables.

After equality contraction, the induced subgraph of the semantic product graph on {x_1,...,x_n} is exactly G.

Rank-width is monotone under vertex deletion / induced subgraphs. Therefore the JANUS-generated interaction family contains graphs of arbitrarily large rank-width.

Hence no universal constant or logarithmic rank-width promise follows from the construction itself.

## Consequence

Bounded rank-width remains a valid exact positive-control solver for restricted inputs, but cannot serve as the missing universal compression theorem unless another representation-changing theorem proves small cut-rank after transformation.

## Ceiling

    LOW RANK-WIDTH SAT = POSITIVE CONTROL
    UNIVERSAL JANUS RANK-WIDTH BOUND = FALSE
    REPRESENTATION THAT PROVABLY REDUCES CUT-RANK = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
