# R5 E9 — Kettani 2025 Bounded-Treewidth Claim Counterfamily Audit

Date: 2026-09-24

Authority: JANUS_DERIVED_EXPLICIT_COUNTERFAMILY__NEGATIVE_CONTROL_ONLY__NO_D1_PROMOTION

Source under audit:
Omar Kettani, Cubic Monotone 1-in-3 SAT Problem is Polynomial Time Solvable, IJMTT 71(9), 2025.

Checker: experiments/r5_e9_kettani_treewidth_counterfamily_checker.py

## 1. Audited claim

The paper's Proposition 4 / main structural step claims that the associated graph G of a Cubic Monotone 1-in-3 SAT instance has bounded treewidth, more specifically tw(G)<=6.

The proof route isolates these graph properties:

- maximum degree at most 6;
- no induced K1,4;
- every vertex belongs to at least three triangles;

and then claims that every graph satisfying them has treewidth at most 6.

The subsequent MIS algorithm and the claimed P=NP corollary depend on this bound.

## 2. Explicit cubic-monotone counterfamily

For integer k>=3 define Boolean variables

v_{i,j},  i,j in Z_k.

For every (i,j) add the positive 1-in-3 clause

C_{i,j} = { v_{i,j}, v_{i+1,j}, v_{i,j+1} },

with indices modulo k.

There are k^2 variables and k^2 clauses.

Each clause has exactly three variables.

Each variable v_{i,j} occurs in exactly three clauses:

C_{i,j}, C_{i-1,j}, C_{i,j-1}.

So this is a valid Cubic Monotone 1-in-3 instance in the structural sense used by the paper.

## 3. Its associated graph

Two variables are adjacent exactly when they co-occur in some clause.

Each clause contributes the triangle

(i,j)--(i+1,j)--(i,j+1)--(i,j).

The resulting graph is the triangular torus on Z_k x Z_k.

Every vertex has degree exactly 6.

The paper's own pigeonhole argument therefore also implies it is K1,4-free; the checker independently verifies this directly.

Every vertex belongs to at least its three source-clause triangles.

So the entire claimed hypothesis set is satisfied.

## 4. Unbounded treewidth

Ignore diagonal and wraparound edges.

The remaining horizontal and vertical nonwrap edges on vertices

{0,...,k-1} x {0,...,k-1}

form the ordinary k x k square grid P_k square P_k as a subgraph.

Treewidth is monotone under taking subgraphs and the k x k grid has treewidth k.

Hence

tw(G_k) >= k.

For k=8 already

tw(G_8) >= 8 > 6.

As k grows the treewidth is unbounded.

Therefore the structural theorem tw(G)<=6 is false.

## 5. Local proof leak in the paper

The paper considers a potential maximal clique C and a vertex v simplicial in G[C].

It then uses the global premise 'v belongs to at least three triangles in G' to infer that v has at least enough neighbors inside C to realize three triangles within G[C].

That inference is not valid:

triangles containing v in G may use vertices outside C.

Global triangle incidence does not imply the corresponding local triangle incidence inside an arbitrary induced subgraph G[C].

This is one concrete point where the potential-maximal-clique argument loses its premise.

Independently of the local proof diagnosis, the explicit triangular-torus family already falsifies the theorem statement.

## 6. Consequence

The 2025 claimed polynomial algorithm cannot be used as authority for JANUS because its bounded-treewidth premise fails on an explicit infinite family satisfying the stated graph hypotheses and arising directly from cubic monotone incidence.

This audit does not make any claim about P versus NP beyond rejecting this proof route.

## 7. JANUS firewall

KETTANI_BOUNDED_TREEWIDTH_ROUTE = FALSIFIED AS STATED.

Do not re-enter:

- max-degree <=6 + K1,4-free + triangle-rich => bounded treewidth;
- generic MIS-on-width-6 as a cubic 1-in-3 solver.

Any future bounded-width route must prove additional structural restrictions absent from the toroidal family.

## 8. Ceiling

KETTANI TREEWIDTH <=6 THEOREM = FALSE
EXPLICIT COUNTERFAMILY = CUBIC MONOTONE TRIANGULAR TORUS
CLAIMED P=NP CONSEQUENCE = UNSUPPORTED BY THIS ROUTE
CUBIC 3-UNIFORM GLOBAL CONTRACTION GATE = STILL OPEN
D1 = EMPTY
P_VS_NP = OPEN

## 9. Strengthening: infinite satisfiable counterfamily

The same toroidal family contains infinitely many explicit YES instances.

For every k divisible by 3 and any r in {0,1,2}, set

x_{i,j}=1 iff i-j is congruent to r mod 3.

In clause C_{i,j}={v_{i,j},v_{i+1,j},v_{i,j+1}}, the three residues are d,d+1,d-1 mod 3, so exactly one equals r.

Hence every clause has exactly one true variable.

Therefore k=3,6,9,12,... are satisfiable cubic-monotone instances.

The associated graphs still contain k x k square grids and thus have treewidth at least k.

So the claimed width-6 theorem fails on an infinite YES-family, not merely on unsatisfiable/pathological inputs.

## 10. Strengthened ceiling

KETTANI TREEWIDTH <=6 THEOREM = FALSE
INFINITE SAT CUBIC-MONOTONE COUNTERFAMILY = PASS
UNBOUNDED TREEWIDTH EVEN IN YES SECTOR = PASS
CLAIMED P=NP CONSEQUENCE = UNSUPPORTED BY THIS ROUTE
CUBIC KERNEL-WORD / NONCOMMUTING GLOBAL FRONTIER = OPEN
