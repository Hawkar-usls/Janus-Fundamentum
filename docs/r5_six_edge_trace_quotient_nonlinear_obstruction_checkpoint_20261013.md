# R5 — Exact six-edge trace quotient and nonlinear countermodel
Date: 2026-10-13. Status: linear theorem proved; universal Exact-One no-go OPEN.

Executable: ../experiments/r5_kempe_six_marked_edge_trace_quotient.py

## Universal theorem (six distinct physical port roots)

Let G be a connected cubic sixpole with n internal vertices, m=(3n-6)/2 ordinary edges. Let Z_s(G) be the Klein-four difference-flow envelope: divergence zero at every internal vertex, and a one-dimensional port-colour restriction at each of its six distinct physical port roots, for prescribed six-colour tuple s.

The cycle-space rank is beta=m-n+1=(n-4)/2; its Klein-four extension has dimension 2beta=n-4. There are at most six independent external root restrictions, one per port. Hence for EVERY prescribed s, whether properly realizable or not:

    max(0,n-10) <= dim_F2 Z_s(G) <= n-4.

For even n>=12, rank-zero or rank-one Z_s obstruction is IMPOSSIBLE, even for irreducible high-connectivity cores. This is an all-size negative result about the previous proof method.

## Canonical connected six-edge trace multigraph Q_G

Split each marked degree-2 root into two stubs joined by one special edge labelled by its port index. The ordinary edges attach to the corresponding stubs, and all unmarked vertices remain unchanged. Delete the six special edges, contract each remaining connected component into one vertex, and restore the six labelled special edges. Call the resulting multigraph Q_G. It is connected and has exactly six labelled edges, possibly loops or parallel edges; hence q=|V(Q_G)|<=7 and cycle rank h=7-q.

Let W_s(Q_G) be the GF(2)^2 flow space of this small multigraph with each labelled edge i restricted to the one-dimensional line spanned by the code of external colour s_i.

Restriction of any D in Z_s(G) to these six special edges induces a W_s(Q_G) flow. Conversely, any Q flow extends over each connected contracted component because the image of the binary incidence map is exactly the even-sum vertex-boundary subspace. The kernel comprises unconstrained internal cycle circulations, with dimension 2(beta-h). This proves the exact sequence

    0 -> H1(H_without_specials;GF(2)^2)
      -> Z_s(G) -> W_s(Q_G) -> 0,

and the all-size identity

    dim Z_s(G) = 2(beta-h) + dim W_s(Q_G)
               = (n-4) - r_s(Q_G),
    r_s(Q_G)=2h-dim W_s(Q_G), 0<=r_s<=6.

Q is computed by union-find in linear time. The W_s Gaussian elimination has 12 binary variables and at most 20 constraint rows. All 729 colour tuples are computable after one linear graph pass. The binary six-port trace code is H1(Q_G;F2), one of at most 2825 abstract subspaces of F2^6 (Gaussian binomial distribution: 1,63,651,1395,651,63,1). No assertion that all 2825 are cubically realizable.

## Invariance under arbitrary connected port-free substitutions

Replace any connected port-free interior block with another connected block attached to the same ordered interface while retaining the promise of a connected cubic sixpole. Each block merges the same exterior connections within a component of the graph WITHOUT six special edges. Therefore Q_G and all normalized r_s remain identical. Since n may change:

    dim Z_s(G') - dim Z_s(G) = |V(G')| - |V(G)|.

This is a theorem about zero-divergence LINEAR flows, not about physical proper edge-colourings. Physical boundary relations require an additional semantic check, such as the eleven-class four-pole atlas.

## Exact nonlinear counterexample with identical marked Q

Substitute one connected four-pole into identical attachment edges (0,1) and (3,4) of an exterior C6 sixpole, keeping all six original ordered semiedges:

Template                             Total n   Physical Col6 states
FOUR_CYCLE_THREE_WITH_1111               10                 87
SIX_VERTEX_HETERO_TWO                     12                 75
SIX_VERTEX_THREE_WITHOUT_1111             12                 99

All three give the SAME EXACT ordered six-edge Q, and all 729 normalized rank defects r_s agree. Nonetheless exact independent edge-colouring DFS yields three DIFFERENT full physical six-port state sets. Therefore no proof using only Q and its normalized linear ranks can decide physical Exact-One boundary realizability.

## Reproducibility

The executable rederives both sides for all 729 prescribed tuples on C6 (n6; dim histogram 0:726,1:3), real five-loop witness (n8; 0:468,1:252,2:9), three Diamond insertions (n10,n14,n18; exact +4 per 4 fresh vertices), and the three 4-pole substitution countermodels (physical relation sizes 87/75/99).

CI state: UNVERIFIED until a completed GitHub Actions job conclusion is obtained. This theorem does not establish all-size Exact-One sixpole impossibility, native PC degree growth, or a universal polynomial SolveLinearCubicXSAT. P versus NP remains OPEN.

Next universal target: a NONLINEAR finite-boundary invariant that retains the nowhere-zero constraints of all shared internal cubic edges, not merely group-valued flow conservation.
