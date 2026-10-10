# R5 E9 — Horn × Dual-Horn Reduction and q-Horn Obstruction Compression Frontier

**Date:** 2026-09-23  
**Status:** exact reduction + source-bound compatibility mechanism; universal compression gate OPEN.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN; no universal polynomial SAT algorithm claimed.

## 1. Canonical two-island reduction

Let F be any 3CNF.

Partition its clauses as follows:

- H := clauses containing at most one positive literal;
- D := all remaining clauses.

Every clause in H is Horn.

If a 3-clause is not Horn, it contains at least two positive literals. Since its length is at most three, it then contains at most one negative literal. Hence every clause in D is dual-Horn.

Therefore, exactly and without introducing any auxiliary variable,

[
F = H wedge D,
]

with H Horn and D dual-Horn.

The partition is computable in linear time in the input length.

### Consequence

The unrestricted interaction problem

[
operatorname{SAT}(Hwedge D),
qquad
Hin	ext{Horn}, Din	ext{dual-Horn},
]

already contains arbitrary 3SAT by the identity partition above.

So the E9 universal-composition problem can be compressed to one canonical mixed pair:

[
oxed{	ext{Horn}	imes	ext{dual-Horn}}.
]

No larger carrier library is necessary merely to express arbitrary 3SAT.

This is a routing equivalence, not a tractability result.

## 2. q-Horn as a source-native compatibility certificate

Gaspers–Ordyniak–Ramanujan–Saurabh–Szeider (STACS 2013), citing the Boros–Hammer–Sun characterization, use the following definition.

A formula F is q-Horn if there exists a certifying function

[
eta:operatorname{lit}(F)	o{0,	frac12,1}
]

such that

[
eta(x)=1-eta(
eg x)
]

for every variable x and

[
sum_{lin C}eta(l)le1
]

for every clause C.

This single certificate interpolates the canonical tractable orientations:

- β(x)=1 for all x certifies Horn clauses: positive literals contribute 1 and negative literals 0;
- β(x)=0 for all x certifies dual-Horn clauses: negative literals contribute 1 and positive literals 0;
- β(x)=1/2 for all x certifies Krom clauses.

Thus q-Horn is naturally interpreted in E9 as a **global compatibility certificate for mixed local orientations**, not merely as another carrier label.

The source states that q-Horn properly contains Horn, Krom and renamable Horn. Since dual-Horn becomes Horn after flipping all variables, dual-Horn is included through renamable Horn.

## 3. Quadratic cover gives an explicit obstruction machine

For an arbitrary CNF F, the q-Horn recognition machinery constructs a Krom quadratic cover F_2 and its implication graph D(F_2).

The canonical function β-hat is obtained from the strongly connected components of D(F_2), and:

- F is q-Horn iff β-hat certifies F (Lemma 6);
- if F is not q-Horn, there is a violating clause;
- every violating clause has a violating triple (l1,l2,l3) lying completely in one SCC of D(F_2), computable in linear time (Lemma 8).

This is unusually valuable for E9: failure of the global Horn/dual-Horn compatibility certificate has a local three-literal obstruction embedded in a polynomial-size implication graph.

## 4. What known backdoor algorithms do with the obstruction

The STACS 2013 algorithm branches on the violating triple and on separator choices in D(F_2).

Ramanujan–Saurabh later reduce **Deletion q-Horn Backdoor Set Detection** to 3-Skew-Symmetric Multicut and obtain an exact FPT algorithm with running time

[
O(12^k k^5 ell),
]

where k is the smallest q-Horn deletion-backdoor size and ℓ the formula length. The corresponding SAT algorithm has the same parameter dependence.

This is a powerful source donor, but it is **not** a universal polynomial algorithm when k is unbounded.

The existing machinery pays for incompatibility through exponential branching in k.

## 5. Knowledge-compilation controls

Berkholz–Mengel–Wilhelm (STACS 2024) prove an unconditional Boolean compilation dichotomy: unless every relation in the fixed language is bijunctive-affine (conjunctions of unary, equality and disequality relations), there are instances requiring exponential DNNF.

This rejects the idea that the q-Horn/Horn×dual-Horn boundary can always be flattened into one generic DNNF currency.

It does **not** imply a SAT lower bound and does not rule out a typed-native symbolic summary.

De Colnet–Mengel (AAAI 2022) go further for a bottom-up structured-DNNF paradigm: they exhibit formulas with tiny final structured-DNNFs for which every bottom-up conjunction/restructuring compilation must create an exponential intermediate representation.

This is another representation/paradigm lower bound, not a SAT lower bound.

## 6. New active object

### R5_E9_HORN_DUALHORN_QHORN_OBSTRUCTION_COMPRESSION_GATE_V1

Input:

[
F=Hwedge D
]

from the canonical Horn/dual-Horn partition of an arbitrary 3CNF.

Construct in polynomial time:

1. the q-Horn quadratic cover and implication graph;
2. the canonical β-hat certificate when it exists;
3. otherwise, the collection/dynamics of violating triples and required literal-to-complement separator conditions.

The missing universal object is a symbolic state C(F) satisfying all of:

- |C(F)| <= poly(|F|);
- construction <= poly(|F|);
- exact update after resolving one obstruction <= poly(|F|);
- C(F) represents **all relevant obstruction/separator choices simultaneously**, not one branch;
- no 12^k, 6^k, 2^k or equivalent unbounded branching;
- exact satisfiability and witness reconstruction from C(F) in polynomial time;
- no SAT/UNSAT oracle or semantic-equivalence oracle.

### PASS

A proof that the entire evolving family of q-Horn violation/separator choices admits such a polynomial exact representation for arbitrary F.

Because every 3CNF has the canonical H∧D split, such a PASS plus a polynomial extraction procedure would give a universal polynomial 3SAT algorithm.

### FAIL / NEGATIVE CONTROL

A source-backed or proved family showing that every proposed obstruction-summary representation in the frozen representation model needs superpolynomial total state.

A failure for DNNF or structured-DNNF alone is **not** enough; representation lower bounds must not be promoted to SAT lower bounds.

## 7. Why this is narrower than the previous E9 gate

Previous gate:

> cover every join edge by some safe pairwise bridge.

New gate:

> arbitrary 3SAT already reduces exactly to one mixed pair; q-Horn provides a known polynomial compatibility certificate for a large tractable region of that pair, and nonmembership produces explicit three-literal/SCC obstructions.

So the active unknown is now:

[
oxed{	ext{Can the q-Horn obstruction choices be compressed exactly without exponential branching?}}
]

This is the next source-first target.

D1 = EMPTY.  
P_VS_NP = OPEN.
