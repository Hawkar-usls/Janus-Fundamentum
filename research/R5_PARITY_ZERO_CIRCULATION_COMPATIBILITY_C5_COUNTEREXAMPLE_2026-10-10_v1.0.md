# R5 Parity — Zero-circulation minimum-face C5 counterexample

Date: 2026-10-10

Status:
ZERO_CIRCULATION_COMPATIBILITY_PERFECTNESS_REFUTED

P_VS_NP = OPEN.

## Setup

Use the 30-variable / 30-clause square, cubic, linear Exact-One construction from

research/R5_PARITY_TRADE_COMPATIBILITY_C5_COUNTEREXAMPLE_2026-10-10_v1.0.md

with fixed perfect matching M and five connected volume-3 fixed-M trades
T_0,...,T_4 whose compatibility graph is exactly C5.

Assign the uniform positive weight

    w(e)=1

to every Exact-One variable / hyperedge.

Every perfect matching has exactly 10 selected variables, because the instance
has 30 clauses and every selected variable covers exactly three clauses.

Therefore every perfect matching has total weight

    w(PM)=10.

In particular M is a minimum-weight perfect matching.

For every trade T_i=(S_i,P_i),

    |S_i|=|P_i|=3,

so its circulation is

    Delta_w(T_i)
      = sum_{e in S_i} w(e) - sum_{e in P_i} w(e)
      = 3-3
      = 0.

Thus all five connected trades T_0,...,T_4 belong to the zero-circulation
minimum-face trade family relative to M.

Their induced compatibility graph remains exactly

    C5.

Hence even after restricting to connected zero-circulation trades inside one
minimum-weight face, the compatibility graph need not be chordal or perfect.

## Consequence

The hoped-for shortcut

    zero-circulation / minimum-face restriction
        =>
    perfect trade-compatibility graph

is false.

Any polynomial algorithm must use structure stronger than abstract pairwise
compatibility, even after conditioning on a minimum face.

In particular, uniform weights show that zero-circulation alone imposes no
additional combinatorial restriction on equal-cardinality perfect-matching
trades.

## Claim boundary

MINIMUM_FACE_TRADE_COMPATIBILITY_CHORDALITY = REFUTED.
MINIMUM_FACE_TRADE_COMPATIBILITY_PERFECTNESS = REFUTED.
ZERO_CIRCULATION_ALONE = INSUFFICIENT_TO_REMOVE_ODD_HOLES.
POLYNOMIAL_ISOLATING_FAMILY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
