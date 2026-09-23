# R5 E9 — Semantic Backdoor Boundary Compression Correction

**Date:** 2026-09-23  
**Status:** correction to the q-Horn obstruction-compression frontier.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Why separator/backdoor compression alone is insufficient

The q-Horn backdoor literature gives a structural route:

1. find a deletion q-Horn backdoor B;
2. for every truth assignment α:B->{0,1};
3. solve the residual q-Horn formula F[α].

Gaspers–Ordyniak–Ramanujan–Saurabh–Szeider (STACS 2013), immediately before Corollary 16, states this assignment-enumeration step explicitly. Their resulting SAT time remains parameter-exponential.

Therefore even a hypothetical polynomial symbolic representation of all violating-triple / separator **choices** would not by itself yield a universal polynomial SAT algorithm.

It would remove only the structural-search exponential and leave the semantic assignment exponential.

## 2. The exact missing semantic object

For a formula F and a variable boundary B define the extendability relation

[
operatorname{Ext}_F(B)
=
{alphain{0,1}^B : F[alpha]	ext{ is satisfiable}}.
]

When B is a strong/deletion q-Horn backdoor, every residual F[α] is in q-Horn, so membership

[
alphainoperatorname{Ext}_F(B)
]

is individually decidable in polynomial time.

But there can be (2^{|B|}) candidate assignments.

The universal task is therefore not merely to find B. It is to represent and manipulate (operatorname{Ext}_F(B)) exactly without enumerating all assignments.

## 3. Tautology firewall: B = Var(F)

A deletion backdoor can always be chosen as

[
B=operatorname{Var}(F),
]

because deleting all variables leaves the empty formula, which is q-Horn.

For this choice,

[
operatorname{Ext}_F(B)=operatorname{Mod}(F).
]

Hence an unrestricted claim of the form

> every q-Horn backdoor boundary has an arbitrary polynomial-size exact summary supporting polynomial emptiness and witness extraction

would already be equivalent to a universal polynomial SAT algorithm.

That statement cannot be used as an intermediate lemma unless the summary is constructed by an explicit restricted calculus with proved polynomial operations.

This firewall prevents circularity.

## 4. Corrected active object

### R5_E9_SEMANTIC_BACKDOOR_BOUNDARY_COMPRESSION_GATE_V1

Seek a **restricted, source-backed summary calculus** (mathcal S), not an arbitrary encoding.

For input F, construct in polynomial time:

- a boundary/backdoor B;
- a summary (S_F(B)inmathcal S) representing (operatorname{Ext}_F(B)) exactly;
- a structural certificate showing why this particular summary belongs to (mathcal S).

The calculus must support in polynomial time:

1. construction from F without SAT/UNSAT oracle;
2. exact restriction by a literal assignment;
3. exact projection / forgetting;
4. conjunction / composition with the q-Horn residual structure;
5. emptiness/nonemptiness;
6. witness reconstruction.

And the **total generated state over the whole run** must remain polynomial in the original input length.

## 5. What would count as genuine progress

A candidate summary format is useful only if it derives polynomial size from a property strictly stronger than “B is a q-Horn backdoor.”

Examples of admissible additional structure:

- bounded-rank affine boundary behavior;
- q-Horn-compatible beta classes;
- a bounded number of implication/SCC types;
- a polynomially bounded quotient under a source-defined indistinguishability relation;
- factorization into independent blocks with a proof that cross-block interactions vanish;
- a native algebraic compact representation with polynomial closure under the required operations.

Not admissible:

- “store all satisfying assignments compactly” with no structural theorem;
- generic DNNF/OBDD compilation where known exponential families apply;
- an oracle that decides whether two partial assignments have the same extension behavior;
- a summary whose construction invokes SAT/UNSAT on the original instance;
- enumerating (2^{|B|}) assignments and compressing afterward.

## 6. Two-layer requirement

The corrected universal route requires **both**:

### Structural compression
Represent all relevant q-Horn obstruction/separator choices without exponential branching.

### Semantic compression
Represent all relevant boundary assignments / extension behavior without exponential enumeration.

Only a theorem controlling both layers can replace the FPT (2^{O(k^2)}) / assignment-enumeration route by a universal polynomial algorithm.

## 7. Next source-first attack

The next search is not “find a better separator data structure.”

Search instead for source-backed equivalence/quotient structures on partial assignments that preserve q-Horn residual satisfiability, especially:

- implication/SCC equivalence;
- closure-system quotients;
- Horn/dual-Horn model closure;
- affine or modular boundary factors;
- representative-family style compression where representatives preserve **extension behavior**, not merely cuts.

The crucial test for every candidate quotient (sim) is:

[
alphasimeta
implies
ig(F[alpha]	ext{ SAT}iff F[eta]	ext{ SAT}ig)
]

and the number of equivalence classes must be polynomially bounded and constructible without a SAT oracle.

D1 = EMPTY.  
P_VS_NP = OPEN.
