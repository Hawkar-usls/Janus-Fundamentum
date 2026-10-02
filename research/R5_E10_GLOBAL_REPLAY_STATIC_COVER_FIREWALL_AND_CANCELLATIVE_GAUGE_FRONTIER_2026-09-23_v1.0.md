# R5 E9 — Global Replay, Static-Cover Firewall, and Cancellative Gauge Frontier

**Date:** 2026-09-23  
**Status:** strategic replay complete; new primary frontier opened.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Strategic replay: what the project has actually learned

Across JANUS-P-N-Junction, TRUMP, E8 and E9, many apparently different routes have repeatedly reduced to the same hidden object:

> exact global compatibility of locally tractable states without materializing exponentially many interface choices.

This object appeared under many names:

- selector coherence;
- sheet coherence;
- backdoor assignments;
- residual quotient states;
- separator choices;
- mixed-carrier bridge states;
- q-Horn violating-triple/separator choices;
- deficiency/excess choices;
- JEC/ER macro selection.

These are not independent bottlenecks.

### 1.1 Bounded-interface / compiled-state routes

Exact successes:
- ROBDD / vtree compilation on favorable orders;
- treewidth / incidence-treewidth dynamic programming;
- module-forest / logarithmic-interface DP;
- certified residual quotients and proof-carrying replay.

Frozen limitation:
- intermediate state may be exponential for arbitrary interfaces;
- variable-copy/equality gadgets do not universally remove structural width;
- generic OBDD/DNNF/structured-DNNF currencies have unconditional exponential families.

Conclusion:
**keep as native solvers / controls, not universal currency.**

### 1.2 Fixed tractable CSP carriers

Exact reusable islands:
- Horn;
- dual-Horn;
- Krom / 2SAT;
- affine / XOR;
- Mal'tsev;
- majority / near-unanimity;
- few-subpowers / edge terms;
- residual-small cube-term machinery;
- E8 effective short-pp compiler candidate.

Frozen limitation:
- ordinary pp/gadget definability preserves polymorphisms;
- arbitrary 3SAT cannot live inside one fixed edge/few-subpowers carrier while retaining its tractable polymorphism;
- mixed tractable carriers can become NP-hard immediately.

Conclusion:
**excellent bricks, no universal bridge yet.**

### 1.3 Positive-cover / selector / backdoor routes

Tried forms:
- explicit selector variables;
- bounded-backdoor enumeration;
- Backdoor-DNF;
- sheet unions;
- safe pairwise bridge covers;
- q-Horn separator branching;
- decomposition into many tractable islands.

New unconditional firewall:
Bousquet–Lagoutte–Thomassé connect the classical strategy of covering solution sets by polynomially many 2-SAT instances to Clique-vs-Independent-Set separation.
Göös (FOCS 2015) gives a superpolynomial lower bound for the general Clique-vs-Independent-Set separator problem.

Therefore the generic paradigm

[
	ext{GLOBAL BEHAVIOR}
=
	ext{polynomial union/cover of simple positive pieces}
]

is **not a viable universal representation principle**.

This does not rule out SAT in P. It rules out a broad family of static positive-cover currencies.

### 1.4 Proof-system / macro route

Exact progress:
- plain resolution lower-bound firewall;
- proof-carrying exact elimination;
- JEC / extension macros can unlock frozen residuals;
- B2/ER-level extension mechanism is expressive.

Missing theorem:
- deterministic polynomial discovery of a useful macro;
- polynomial total macro count;
- global polynomial progress measure.

Conclusion:
**retain as reserve route.**
It is representation-agnostic but presently lacks a discovery theorem.

### 1.5 Residual-state / semantic quotient route

Exact negative control:
families such as independent equality channels can have (2^n) continuation-distinguishable residual states across a bad cut.

Conclusion:
a single fixed-cut semantic quotient cannot be the universal currency.
Joint decomposition may save special cases, but that returns to width/cover issues.

### 1.6 q-Horn / NAE / deficiency route

Useful reductions:
- arbitrary 3CNF = Horn AND dual-Horn;
- q-Horn gives a polynomial mixed-orientation compatibility certificate;
- non-q-Horn instances expose explicit violating triples and separator obligations;
- Positive NAE-3SAT isolates the same global sheet-coherence problem;
- degree/rank threshold exposes deficiency/excess as a real hardness reservoir.

Limitation:
known algorithms pay parameter dependence or branching when the obstruction/excess is unbounded.

Conclusion:
**keep deficiency and DDD NAE-4-regular as adversarial benchmark, not primary currency.**

## 2. What is genuinely missing from the historical currency inventory

Almost every prior currency is **positive/monotone**:
store feasible states, cover them, partition them, refine them, or enumerate representatives.

The major unexhausted alternative is **cancellative composition**:

> allow exponentially many local contributions to combine algebraically and cancel, so the global interaction object stays polynomial without being a positive cover of solution states.

Source donors:
- holographic algorithms;
- Holant transformations;
- affine/product-type transforms;
- matchgates/Pfaffian computation;
- Fibonacci gates;
- mixed-sign / complex-weighted CSP;
- tensor-network gauge transformations.

These methods prove that cancellation and basis change can create polynomial algorithms unavailable in ordinary positive CSP syntax. They do not solve arbitrary SAT, but they establish the mechanism class.

## 3. Exact local identity: OR3 is locally gauge-equivalent to COPY3

Write the Boolean OR3 signature as a tensor

[
O_{ijk}=operatorname{OR}(i,j,k),qquad i,j,kin{0,1}.
]

Let

[
u=egin{pmatrix}1\\1end{pmatrix},quad
e_0=egin{pmatrix}1\\0end{pmatrix},quad
e_1=egin{pmatrix}0\\1end{pmatrix}.
]

Then exactly

[
O=u^{otimes 3}-e_0^{otimes 3}.
]

Let

[
A=
egin{pmatrix}
0&1\\
1&-1
end{pmatrix},
qquad
D=
egin{pmatrix}
1&0\\
0&-1
end{pmatrix}.
]

We have

[
Au=e_0,qquad Ae_0=e_1,
]

and therefore

[
(DAotimes Aotimes A),O
=
e_0^{otimes3}+e_1^{otimes3}
=
operatorname{COPY}_3.
]

All matrices are invertible over (mathbb Q)/(mathbb C).

Literal negations are just local permutation matrices and can be absorbed into the corresponding leg transformation.

### Interpretation

Every signed 3-SAT clause is **locally** an invertible-basis transform of a COPY/GHZ tensor.

Thus the local OR3 constraint is not where the universal difficulty lives.

The hardness is transferred into the requirement that the edge gauges chosen around all clauses remain globally compatible with the variable COPY tensors and with a tractable contraction family.

This gives a new formulation of the old global-coherence bottleneck, but crucially in a **non-monotone group/tensor language** rather than as a union of states.

## 4. Source-native firewall for ordinary holographic algorithms

Known Holant / holographic dichotomies show:

- common/global basis transformations yield polynomial algorithms only for restricted transformable families;
- affine/product-type families are tractable on general graphs;
- matchgate/Pfaffian families give additional power principally with planar topology;
- Fibonacci-gate families provide other special general-graph tractable cases;
- Boolean-domain basis-collapse theorems show that merely increasing a common holographic basis does not create unlimited new power.

Therefore the new route must **not** be:

> search for one larger common basis that transforms standard 3SAT into a known tractable fixed Holant language.

That would be a rediscovery of an already-classified route.

## 5. New primary frontier

### R5_E10_INSTANCE_SPECIFIC_CANCELLATIVE_GAUGE_NORMALIZATION_GATE_V1

Input:
an arbitrary signed 3CNF represented as its exact Boolean factor/tensor network.

Allowed transformation:
for every incidence edge (e), insert an invertible local gauge

[
T_e T_e^{-1}
]

so that the total contraction / exact zero-vs-nonzero semantics is preserved.

Goal:
construct the gauges and resulting local normal forms in polynomial time so that the transformed network admits deterministic polynomial exact decision and witness reconstruction.

The target is **instance-specific edge gauges**, not one global basis.

### PASS contract

A positive result must prove all of:

1. gauge construction is polynomial in original input length;
2. all matrices/numbers have polynomial bit complexity;
3. every transformed local tensor belongs to an explicitly tractable certified family;
4. global contraction/zero-test is polynomial on the transformed topology;
5. SAT iff transformed invariant is nonzero;
6. a satisfying assignment is reconstructible in polynomial time;
7. no exponential sum over gauges / sheets / cuts / backdoors;
8. no SAT oracle, semantic oracle, or hidden exponential intermediate.

### Stronger optional level

If the transformation preserves the exact partition function (Z(F)=#SAT(F)) and the target contraction is polynomial, that would give the much stronger consequence FP=#P.
This is **not required** by the decision-level gate.

A decision-only cancellative invariant with

[
Z^*(F)=0iff Fin UNSAT
]

is sufficient.

## 6. First subgate: gauge-synchronization structure

### R5_E10_OR3_COPY_GAUGE_SYNCHRONIZATION_V1

Using the exact local OR3->COPY3 identity:

1. characterize the full local coset of triples
   ((T_1,T_2,T_3)in GL_2^3)
   sending OR3 to COPY3 up to nonzero scalar;
2. characterize the stabilizer of COPY_d for arbitrary variable degree d;
3. place one gauge variable on every clause-variable incidence;
4. derive the exact compatibility equations around every variable;
5. quotient irrelevant scalar freedom;
6. determine whether global gauge compatibility reduces to:
   - polynomial group equations / cocycle solving;
   - a finite-domain CSP;
   - or an NP-hard compatibility system.

This is the immediate killer-test.

If the synchronization equations are polynomially solvable and the resulting normal forms contract polynomially, continue.

If the equations already encode arbitrary SAT, freeze the route as a new exact barrier.

## 7. Frozen benchmarks

Every candidate must be tested first against:

- DDD positive linear 3-uniform 4-regular NAE-3SAT with four perfect-matching layers;
- PHP hard proof-search controls;
- mixed Horn x dual-Horn instances;
- Krom + XOR3 universalizing gadget family;
- independent equality-channel family;
- random 3SAT near the phase transition.

The mechanism must not succeed only by exploiting low width, planarity, bounded deficiency, or a special fixed language.

## 8. Strategic priority

PRIMARY:
**instance-specific cancellative gauge synchronization.**

RESERVE:
proof-carrying ER/JEC macro discovery, only if the gauge route collapses to a known barrier.

DO NOT reopen as primary:
- positive sheet covers;
- generic Backdoor-DNF;
- generic DNNF/OBDD compilation;
- bounded-width-only decompositions;
- fixed one-language edge-term carrier;
- raw deficiency branching.

D1 = EMPTY.  
P_VS_NP = OPEN.
