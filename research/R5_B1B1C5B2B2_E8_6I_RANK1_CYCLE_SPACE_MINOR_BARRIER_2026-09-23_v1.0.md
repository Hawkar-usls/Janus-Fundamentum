# R5 E8 6I — Rank-One Cycle-Space / Minor Barrier

Date: 2026-09-23

Authority: SOURCE_BOUND_SCOPED_BARRIER__CYCLE_RELAXATION_ONLY__NO_D1_PROMOTION

Parent: R5_E8_6I_NONLOCAL_GROUPED_RANK1_OBSTRUCTION_CURRENCY_GATE_V1

## 1. Donor

The Boolean quadric polytope QP(G) is affinely related to a cut polytope on the suspension graph obtained by adding one apex adjacent to all vertices of G.

For a graph H, the metric/cycle relaxation MET(H) is defined by the odd cycle inequalities and edge bounds.

Barahona and Mahjoub prove:

    CUT(H) = MET(H)

if and only if H has no K5 minor.

Thus cycle inequalities are an exact polynomially separable description on the K5-minor-free positive region, but not on arbitrary graphs.

## 2. JANUS interaction graphs are not universally in the positive region

For every frozen clause with semantic boundary variables a,b,c, the quadratic expansion contains the three products ab, ac, bc.

After contracting affine equality components that identify occurrence copies, the semantic product graph contains the primal graph of the original 3CNF.

Therefore arbitrary clique minors can occur.

In particular, choose polynomially many clauses whose pair co-occurrences make four original variables pairwise adjacent. Then the semantic product graph contains K4.

The suspension graph used by the Boolean-quadric-to-cut covariance mapping contains K5: the apex plus that K4.

Hence the K5-minor-free exactness hypothesis of the cycle relaxation fails on valid members of the universal JANUS family.

## 3. Consequence

The following is not a universal compression theorem:

    collect cycle / parity cuts
    solve the metric relaxation
    conclude exact rank-one consistency.

Cycle cuts remain a valid tractable positive control on minor-free interaction subfamilies and may be useful inside a decomposition. They cannot by themselves supply universal exactness.

## 4. Scope firewall

Blocked:

- the direct metric/cycle relaxation as the complete grouped rank-one cut language for all JANUS inputs.

Not blocked:

- decomposition into K5-minor-free pieces with a polynomial interface theorem;
- additional non-cycle facets/certificates;
- matching/matroid algorithms outside this LP relaxation;
- recursive graph-minor decompositions with polynomial boundary state;
- nonlinear algebraic quotient currencies.

## 5. Ceiling

    CYCLE CUTS ON K5-MINOR-FREE SUSPENSIONS = EXACT POSITIVE CONTROL
    UNIVERSAL JANUS INTERACTION FAMILY = NOT K5-MINOR-FREE
    DIRECT CYCLE-SPACE CURRENCY = BLOCKED
    GRAPH-DECOMPOSITION / NONLOCAL NONLINEAR CURRENCY = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
