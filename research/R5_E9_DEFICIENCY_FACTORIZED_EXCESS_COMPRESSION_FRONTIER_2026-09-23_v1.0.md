# R5 E9 — Deficiency / Autarky Compression Frontier

**Date:** 2026-09-23  
**Status:** source-bound synthesis; universal compression gate OPEN.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Why the 3 -> 4 NAE threshold matters

For a positive NAE instance represented as an r-uniform hypergraph H=(V,E), let

[
delta(H):=|E|-|V|.
]

Seymour's condenser theorem gives, for every minimally non-2-colorable hypergraph C,

[
|E(C)|ge |V(C)|.
]

Now suppose every edge has size exactly r and every vertex has degree at most r. Counting incidences gives

[
r|E(C)|le r|V(C)|,
]

hence

[
|E(C)|le |V(C)|.
]

Therefore every minimal obstruction must satisfy

[
|E(C)|=|V(C)|,
]

i.e. it is a **square condenser**.

Robertson–Seymour–Thomas (1999) give a polynomial-time structural recognition algorithm for precisely the square minimal non-bipartite / minimally non-2-colorable case. This explains the polynomial region used by Filho for Positive NAE-r-SAT with maximum occurrence at most r.

For r=3:

- 3-uniform + max degree <=3 forces every minimal obstruction into square deficiency 0;
- Positive NAE-3-SAT-E3 is therefore polynomial.

For the Darmann–Döcker–Dorn hard family:

- the hypergraph is 3-uniform and 4-regular;
- incidence counting gives 3m=4n;
- hence

[
delta=m-n=n/3.
]

Thus the sharp 3-layer/4-layer benchmark changes the obstruction budget from forced zero excess to **linear excess**.

This is a stronger interpretation than “three matchings easy, four matchings hard”: the fourth incidence layer creates room for non-square minimal cores.

## 2. Deficiency is already a known algorithmic parameter

Classical SAT/autarky theory uses

[
delta(F)=c(F)-n(F)
]

and the stronger maximum deficiency/surplus parameters.

Known source-native facts:

- fixed deficiency minimal-unsatisfiable recognition is polynomial;
- bounded maximum deficiency gives FPT SAT algorithms;
- maximum deficiency is computable polynomially via matching/expansion machinery;
- matching and linear autarkies allow polynomial deletion of clauses that cannot contribute to the hard lean core;
- the matching-lean / linearly-lean kernel is governed by deficiency/surplus structure.

These results make deficiency a legitimate mechanism donor.

But they do **not** solve arbitrary SAT: when the deficiency parameter is unbounded, the known algorithms pay parameter dependence or leave a large lean core.

## 3. New Janus interpretation

The correct target is not

> branch on the deficiency parameter.

It is

> factorize the excess constraints themselves into a polynomial exact interaction object.

After polynomial autarky reduction, write the remaining core schematically as

[
F_{m lean}=F_{square}oplus X,
]

where:

- (F_{square}) is the maximal part whose obstruction structure is controlled by square/balanced incidence;
- (X) is the **excess interaction object** carrying positive maximum deficiency.

The sought representation (Xi(F)) must encode the effect of X without enumerating (2^{delta}) choices.

## 4. Active gate

### R5_E9_DEFICIENCY_FACTORIZED_EXCESS_COMPRESSION_GATE_V1

Given an arbitrary 3CNF F:

1. compute polynomially available matching/linear-autarky reductions and the corresponding lean kernel;
2. compute the maximum-deficiency / surplus structure;
3. identify balanced/square blocks and excess blocks;
4. construct a symbolic exact representation (Xi(F)) of the excess interactions.

PASS requires:

- (|Xi(F)|le operatorname{poly}(|F|)) for every F;
- construction/update/projection/composition all polynomial in original input length;
- (Xi(F)) represents all excess choices simultaneously;
- exact SAT decision and witness reconstruction are polynomial;
- no (2^delta), (f(delta)) with unbounded (delta), or hidden enumeration;
- no SAT/UNSAT or semantic-equivalence oracle.

A PASS would replace the parameterized use of deficiency by a representation theorem and would be a direct candidate route to arbitrary SAT.

## 5. Frozen adversarial benchmark

Use the Darmann–Döcker–Dorn family:

- positive NAE-3SAT;
- linear 3-uniform hypergraph;
- 4-regular;
- clauses supplied as four disjoint perfect-matching layers;
- NP-complete;
- global deficiency exactly (n/3).

Any claimed factorized-excess representation must be stress-tested first on this family.

Positive control:

- 3-uniform degree <=3;
- every minimal obstruction forced square;
- polynomial square-condenser recognition.

The desired mechanism must explain **what algebraic/combinatorial state generalizes the square-condenser detector when deficiency grows from 0 to linear**, rather than merely parameterizing that growth.

## 6. Relation to earlier E9 routes

This frontier subsumes the q-Horn obstruction-compression lesson:

- q-Horn backdoor algorithms pay exponential branching for incompatibility;
- generic separator summaries can also be exponential;
- Backdoor-DNF can require exponentially many terms on independent NAE gadgets;
- the same NAE core exposes linear deficiency in the degree-4 hard regime.

Therefore the current priority is:

[
oxed{	ext{excess factorization, not excess enumeration}.}
]

D1 = EMPTY.  
P_VS_NP = OPEN.
