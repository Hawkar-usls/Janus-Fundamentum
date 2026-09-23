# R5 E8 6I — Full-Moment Correlation-Polytope LP Barrier

Date: 2026-09-23

Authority: SOURCE_BOUND_REPRESENTATION_BARRIER__LP_ONLY__NO_SAT_LOWER_BOUND__NO_D1_PROMOTION

Parent: R5_E8_6I_NONLOCAL_GROUPED_RANK1_OBSTRUCTION_CURRENCY_GATE_V1

## 1. Rank-one Boolean moments and the correlation polytope

For a Boolean vector x in {0,1}^n, the full quadratic moment matrix is Y=xx^T.

The convex hull of all such matrices is the correlation polytope COR(n).

Kaibel and Weltge prove that the extension complexity of COR(n) is at least 1.5^n.

Therefore no family of real linear extended formulations of polynomial size can describe the exact convex hull of all Boolean rank-one full-moment points.

## 2. JANUS consequence

The JANUS exact normal form permits full O(N^2) moment materialization. Any proposed universal grouped-cut currency of the following form is therefore blocked:

    rank-one consistency
    -> exact polynomial-size real LP / extended formulation
    -> polynomial LP solve.

If the formulation is exact for all Boolean rank-one full-moment points, it would be an extended formulation of COR(N), contradicting the exponential extension-complexity lower bound.

This is a representation lower bound only. It is not a SAT lower bound and does not assume P != NP.

## 3. Positive control: graph structure / treewidth

For a graph G, Aboulker, Fiorini, Huynh, Macchia and Seif prove an upper bound

    xc(COR(G)) = 2^{O(tw(G)+log n)},

and show tightness for graphs in minor-closed classes.

Thus bounded treewidth is a legitimate compactness currency for graph-restricted rank-one interactions.

## 4. JANUS generated interaction graph has no universal bounded-width guarantee

Define the semantic product graph of the quadratic normal form:

- vertices are Boolean semantic variables after contracting the affine equality components that identify occurrence copies of one original variable;
- add an edge for every quadratic semantic product required by a clause gadget.

For each 3-clause with boundary literals a,b,c, the expanded majority equation contains ab, ac and bc.

Therefore, after equality contraction, the primal graph of the original 3CNF is a subgraph of the semantic product graph.

Hence

    tw(product_graph(F)) >= tw(primal_graph(F)).

Arbitrary 3CNF families have unbounded primal treewidth. For example, one can construct formulas whose primal graph contains K_n using polynomially many clauses.

Therefore the universal JANUS input family has no bounded-treewidth promise that would make the graph-correlation extended formulation polynomial for all inputs.

## 5. Scope firewall

Blocked:

- exact polynomial-size real LP descriptions of the full Boolean rank-one moment hull;
- using bounded treewidth of the rank-one interaction graph as an unconditional property of all JANUS-generated instances.

Not blocked:

- nonlinear algebraic certificates;
- matching/matroidal algorithms not expressible as an exact polynomial LP EF;
- instance-specific sparse graph subfamilies with provably small treewidth;
- fixed-height recursive quotient/interface solvers;
- cutting planes used heuristically or as incomplete relaxations;
- other representations that do not exactly formulate the full correlation polytope.

## 6. New narrowed survivor

The grouped obstruction currency must exploit more than a polynomial-size exact LP hull. Candidate sources of compactness are now restricted to genuinely combinatorial/algebraic recursion, quotient/cycle-space invariants, or special structural decompositions proved for the JANUS-generated family.

## 7. Ceiling

    FULL-MOMENT EXACT POLY LP CURRENCY = BLOCKED BY EXTENSION COMPLEXITY
    BOUNDED-TREEWIDTH GRAPH CORRELATION = VALID POSITIVE CONTROL
    UNIVERSAL BOUNDED TREEWIDTH FOR JANUS FAMILY = FALSE
    NONLINEAR / RECURSIVE GROUPED CURRENCY = OPEN
    D1 = EMPTY
    P_VS_NP = OPEN
