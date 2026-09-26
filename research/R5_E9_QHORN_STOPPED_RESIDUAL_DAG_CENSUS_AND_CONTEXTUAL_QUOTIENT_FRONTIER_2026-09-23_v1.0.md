# R5 E9 — q-Horn-Stopped Residual DAG Census and Typed State-Quotient Frontier

**Date:** 2026-09-23  
**Status:** diagnostic execution + source synthesis. No asymptotic theorem is inferred from the finite census.  
**Scientific firewall:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Connection to known "few subterms" theory

Bova–Slivovsky define, for a variable set V, the set of restrictions

[
operatorname{st}(F,V)={F[f]:f:V	o{0,1}}.
]

Their subterm width is the maximum number of distinct such residual CNFs along prefixes of a variable ordering.

A polynomial bound ("few subterms") is sufficient for polynomial-size OBDD compilation, and a constructive witness ordering gives polynomial-time OBDD compilation.

They also prove exponential OBDD lower bounds using bounded-degree graph CNFs.

This is directly relevant to the E9 residual-state program, but there is a crucial difference:

- a graph CNF is monotone 2CNF;
- every 2CNF is q-Horn;
- therefore a q-Horn-stopped CSBC can treat an OBDD-hard graph CNF as **one tractable leaf**.

So the OBDD lower bound is a representation lower bound for literal-level decision compilation, not a lower bound on CSBC/native-leaf compilation.

## 2. Exact q-Horn recognizer used in the diagnostic

The experiment implements the source characterization through the quadratic cover F^2.

For every clause C={l_1,...,l_r}, ordered by variable, introduce y^C_1,...,y^C_{r-1} and the binary clauses

[
{l_i,y_i},quad {
eg y_i,l_{i+1}}
]

for 1<=i<r and

[
{
eg y_i,y_{i+1}}
]

for 1<=i<r-1.

Build the 2SAT implication graph D(F^2).

By the q-Horn characterization used in the q-Horn backdoor literature, F is q-Horn iff no original clause contains three literals l for which l and ¬l lie in the same SCC of D(F^2).

### Independent sanity

The implementation was compared against brute-force search over all q-Horn valuations

[
gamma(x)in{0,	frac12,1},qquad gamma(
eg x)=1-gamma(x)
]

on random formulas with up to six variables.

Result:

```
QHORN_SCC_RECOGNIZER_VS_BRUTE_BETA
=
PASS
```

## 3. Diagnostic compiler variants

All variants perform exact Shannon restriction. A state becomes a leaf as soon as it is q-Horn.

### A. TREE

No sharing.

### B. EXACT_RESIDUAL_DAG

Memoize states only when their canonical residual CNFs are syntactically identical.

### C. QHORN_STOPPED_BDMC_DAG

In addition to exact memoization:

- if a residual splits into variable-disjoint connected components, create a decomposable AND and compile components independently;
- otherwise branch on a variable from a source-certified q-Horn violating triple.

This is source-native Decision-BDMC behavior with q-Horn stopping, except that the experiment stores q-Horn formulas directly as leaves rather than compiling each one to its polynomial URC encoding.

## 4. Frozen finite census

Random 3CNFs were sampled near the classical random-3SAT density m≈4.26n.

For each even n=6,...,22:

- 12 deterministic seeds;
- exact same formula suite for all three variants;
- no SAT oracle;
- stop criterion = exact q-Horn recognition;
- branch variable = maximum occurrence among one violating triple.

Median state counts:

| n | m | TREE median | EXACT residual DAG median | + decomposable components median |
|---:|---:|---:|---:|---:|
| 6 | 26 | 13 | 13 | 13 |
| 8 | 34 | 28 | 28 | 24 |
| 10 | 43 | 61 | 61 | 51 |
| 12 | 51 | 106 | 106 | 80 |
| 14 | 60 | 204 | 204 | 122 |
| 16 | 68 | 443 | 443 | 231 |
| 18 | 77 | 931 | 931 | 356 |
| 20 | 85 | 2247 | 2190 | 732 |
| 22 | 94 | 4548 | 4533.5 | 1137.5 |

### Interpretation ceiling

This finite experiment proves **no asymptotic lower bound**.

It does falsify one weak engineering hypothesis on this frozen suite:

> "exact residual-CNF memoization alone will create substantial branch reconvergence."

It did not: TREE / exact-DAG median ratio stayed essentially 1.

By contrast, source-native decomposable component factorization gave a substantial reduction, confirming that semantic structure beyond exact residual equality matters.

A least-squares fit over this tiny range gives rapidly growing curves for both variants; this is diagnostic only and must not be promoted to a complexity claim.

## 5. What state compression must do next

Exact syntactic identity is too fine.

The desired merge relation must be a **polynomially computable contextual quotient** on residual/native states.

For residual states S and T, a merge certificate must guarantee enough contextual equivalence that all future allowed operations preserve exact satisfiability behavior:

[
Sequiv_{mathcal O}T
]

with respect to the frozen operation library (mathcal O) (conditioning, decomposable AND, certified BRIDGE_AND, projection/forgetting).

Required properties:

1. **Sound merge:** equal quotient key never merges states that differ under any admissible future context.
2. **Polynomial key:** key/certificate size and construction are polynomial in original input length.
3. **Congruence:** each admitted operation maps quotient classes to quotient classes in polynomial time.
4. **Polynomial reachable quotient:** for every input F, only poly(|F|) quotient states are generated.
5. **Witness transport:** models can be reconstructed through merged states.

A generic semantic-equivalence test is forbidden; that would simply hide SAT/coNP reasoning in the state key.

## 6. New active gate

### R5_E9_TYPED_CONTEXTUAL_STATE_QUOTIENT_GATE_V1

Find a source-backed/derived quotient currency for non-leaf CSBC states that is:

- coarser than exact residual CNF identity;
- exact under the CSBC operation library;
- polynomially computable and checkable;
- polynomially bounded in number of reachable classes for every arbitrary 3CNF.

### PASS implication

Together with the CSBC compiler contract, a PASS would yield a polynomial 3SAT algorithm.

No PASS is claimed.

### Immediate negative controls

- ordinary OBDD/subterm states can be exponentially many;
- DNNF can be exponential even for some tractable 2CNFs;
- exact cut/mimicking summaries can be exponential;
- exact residual syntax showed almost no merging in the frozen random census;
- semantic equivalence as an oracle is inadmissible.

## 7. Next source-first donors

Prioritize mechanisms that define a **congruence on boundary behavior**, not merely a smaller branching parameter:

- ps-width / precisely satisfiable clause-set summaries;
- support-compatible algebraic circuit interfaces;
- affine quotient state;
- implication/SCC quotients;
- few-subpowers compact signatures;
- representative-set methods only when exact contextual closure is proved.

D1 = EMPTY.  
P_VS_NP = OPEN.
