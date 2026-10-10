# R5 E9 — Certified Semantic Backdoor Circuit (CSBC) Universal Compilation Gate

**Date:** 2026-09-23  
**Status:** architecture synthesized from source-native BDMC/backdoor-DNF machinery + Janus typed bridges. No universal compilation theorem is claimed.  
**Scientific firewall:** D1=EMPTY; P_VS_NP=OPEN; P_EQ_NP=NOT_PROVED.

## 1. Correction to the previous q-Horn separator gate

Compressing only the q-Horn violating-triple / separator choices is insufficient.

For any CNF F, the full variable set B=Var(F) is a strong backdoor into q-Horn (indeed into Horn): after a total assignment, the residual formula is either empty or contains the empty clause, both inside the syntactic base class.

But the extendability relation on B is exactly

[
E_B={ain{0,1}^{B}: F[a]	ext{ is satisfiable}}=operatorname{Mod}(F).
]

Thus even a perfect polynomial description of **which structural repair/backdoor is selected** does not by itself compress the truth-assignment semantics. The universal object must compress both:

1. structural repair / carrier choice;
2. semantic assignment regions on the live interface.

## 2. Backdoor DNFs attack the semantic side — but expose a coverage problem

Ordyniak–Schidler–Szeider define a C-backdoor DNF as a set G of partial assignments such that:

- each residual F[τ], τ∈G, lies in C;
- the DNF formed by those terms is a tautology.

If G is given and C is tractable, SAT can be solved in |G|·poly(|F|) time.

This is exactly a semantic cover of the full assignment space.

However:

- for the heterogeneous base Horn ∪ dual-Horn, Backdoor DNF and Backdoor Tree detection are W[2]-hard parameterized by the number of terms/leaves (Theorem 4 of the 2024 JCSS paper);
- a naked arbitrary DNF requires a global tautology condition, and DNF-TAUTOLOGY is coNP-complete.

Therefore a universal proof-carrying algorithm should not use an arbitrary DNF whose global coverage must later be established semantically.

## 3. BDMC supplies the right circuit skeleton

Kučera–Savický introduce C-BDMCs:

- leaves are formulas/encodings from a base class C;
- inner gates are OR or AND;
- AND gates satisfy decomposability: child variable sets are pairwise disjoint.

They show:

- DNNF and backdoor trees are special cases;
- smooth PC-BDMCs compile in polynomial time to PC encodings;
- consistency checking is polynomial on PC-BDMC / PC encodings;
- disjunction and conditioning are polynomial transformations;
- generic conjunction is **not** a polynomial transformation unless P=NP;
- efficient CNF→C-BDMC compilation is explicitly left as further research.

This identifies the exact knowledge-compilation bottleneck:

> OR / conditioning / tractable leaves are not the missing operation.  
> The missing operation is overlapping conjunction.

## 4. q-Horn leaves are especially attractive

Kučera–Savický (JAIR 2020) state that every q-Horn formula has a polynomial-size URC encoding using auxiliary variables.

Hence q-Horn is not merely a SAT-in-P leaf class: it admits a source-backed polynomial propagation-oriented encoding suitable for the BDMC/URC compilation architecture.

This does not make arbitrary Horn×dual-Horn conjunction q-Horn.

## 5. Janus extension: Certified Semantic Backdoor Circuit

Define a **CSBC** as a DAG whose nodes have one of the following types.

### LEAF(T,S)

S is an exact native summary in a tractable type T with:

- polynomial membership/certificate checking;
- polynomial SAT/emptiness test;
- polynomial witness reconstruction;
- declared exact conditioning/projection operations.

Candidate native types include Horn, dual-Horn, Krom, affine, q-Horn/URC, few-subpowers compact representations, and the E8 residual-small cube compiler candidate (only after/subject to its scientific status).

### DECISION(x,N0,N1)

Semantics:

[
(
eg xwedge f_{N0})ee(xwedge f_{N1}).
]

Children must be exact restrictions of the parent state by x=0 and x=1.

This gives a **local, syntactic coverage proof**. There is no separate global DNF-tautology test.

### DECOMP_AND(N1,...,Nk)

Allowed when the live variable supports of the children are pairwise disjoint.

This is the source-native BDMC conjunction rule.

### BRIDGE_AND(N1,N2,C)

Children may overlap, but only when C is a polynomially checkable pair-specific certificate for an exact polynomial join and normalization.

Known/derived bridge donors include:

- Krom × 2-affine -> Krom, certified by weight≤2 row-space generation;
- support-compatible algebraic-circuit product;
- q-Horn beta compatibility where the joined formula remains q-Horn;
- same-native-format closures where conjunction remains in the tractable native class;
- common-edge/few-subpowers joins only when source hypotheses certify closure;
- future bridges must be separately source-bound/falsified.

There is **no generic BRIDGE_AND**.

### PROJECT / FORGET

Allowed only when the current native type has a source-backed polynomial exact projection/forgetting operation.

## 6. Why local coverage matters

A Shannon DECISION gate proves

[
F equiv (
eg xwedge F[x=0])ee(xwedge F[x=1])
]

by syntax.

Thus assignment-space completeness is certified one gate at a time.

The trivial full Shannon tree always exists but may have exponential size. The universal problem is not correctness of the split; it is polynomial **DAG compression** of the resulting semantic states.

This separates two issues cleanly:

- COVERAGE: local and exact by construction;
- COMPRESSION: the only remaining global challenge.

## 7. Active universal gate

### R5_E9_CERTIFIED_SEMANTIC_BACKDOOR_CIRCUIT_UNIVERSAL_COMPILATION_GATE_V1

Given arbitrary 3CNF F of length L, construct in deterministic poly(L) time a CSBC D such that:

1. root(D) represents exactly F;
2. |D| <= poly(L);
3. every LEAF has a polynomially verified tractable certificate;
4. every DECISION has syntactically verified complete two-way coverage;
5. every AND is either decomposable or carries a polynomial verified typed bridge;
6. every intermediate native summary and annotation has size poly(L);
7. consistency/SAT evaluation is poly(L);
8. a satisfying assignment, when one exists, is reconstructed in poly(L);
9. no SAT/UNSAT oracle, semantic-equivalence oracle, unbounded backdoor enumeration, or hidden exponential format conversion is used.

### PASS implication

A PASS plus the stated polynomial compiler would give a deterministic polynomial algorithm for 3SAT, hence P=NP.

No PASS is currently claimed.

## 8. Immediate source-bound negative controls

1. **Backdoor DNF alone:** Horn∪dual-Horn detection is W[2]-hard in term count; naked DNF coverage is globally hard to verify.
2. **Vanilla BDMC alone:** overlapping conjunction is excluded by decomposability; generic conjunction is exactly a hard transformation.
3. **One DNNF currency:** already rejected by exponential DNNF families inside tractable Krom/2CNF.
4. **Separator-only state:** fails the B=Var(F) semantic sanity test.
5. **Full Shannon tree:** exact but exponential in the worst case unless substantial DAG/native-summary merging is proved.

## 9. New concrete search question

Do **not** ask only for a smaller backdoor.

Ask:

> For the canonical F=H∧D decomposition of arbitrary 3CNF, can the Shannon/q-Horn obstruction process be memoized into only polynomially many distinct certified native states, using typed BRIDGE_AND normalization whenever branches reconverge?

A useful next experiment is therefore a residual-state DAG census on adversarial formula families, not another backdoor-size benchmark.

D1 = EMPTY.  
P_VS_NP = OPEN.
