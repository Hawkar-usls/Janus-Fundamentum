# C033 — Proof-Carrying Semantic-Message Portfolio

**Status:** `CONSTRUCTIVE BRIDGE / NOT UNIVERSAL / P_VS_NP=OPEN`

## Exact theorem

Let a deterministic constructor produce, for CNF `F`, a rooted decision DAG of polynomial total size. Every internal node is a certified variable restriction. Every leaf is admitted by a polynomial-time recognizable tractable solver with witness recovery and a replayable rejection certificate. Then SAT on `F` is decidable in polynomial time by bottom-up evaluation of the DAG. A SAT witness is obtained from one accepting leaf and the branch assignments. UNSAT is certified by replaying every rejecting leaf and every restriction edge.

The charged resources are:

```text
selector and constructor time
number of unique DAG nodes
restriction-edge verification
leaf-class recognition
leaf certificate generation and replay
SAT witness reconstruction
UNSAT aggregation and replay
```

This theorem formalizes the interface needed to combine explicit PS-signature DP, Horn/dual-Horn closure, 2-SAT, affine elimination, beta-acyclic elimination, and compiled DNNF/OBDD messages without treating portfolio selection as free.

## Executable control

The current executable admits Horn, dual-Horn and 2-CNF leaves, branches under a strict node budget, verifies every restriction edge, reconstructs SAT witnesses, and returns `OPEN` when the budget is exhausted.

```text
500 random formulas
0 decision mismatches
0 false witnesses
strict one-node OPEN control: PASS
```

This is plumbing evidence, not universal tractability evidence.

## Literature alignment

This construction is a proof-carrying form of heterogeneous strong backdoors. Gaspers–Misra–Ordyniak–Szeider–Živný study backdoors whose different assignments may enter different tractable base classes. Dreier–Ordyniak–Szeider show that backdoor depth can exploit parallel decomposition missed by backdoor size. Brault-Baron–Capelli–Mengel show beta-acyclic #SAT requires an elimination-style portfolio member beyond ordinary PS-width dynamic programming.

Therefore `proof-carrying portfolio` is not promoted as a new width parameter. Its new contribution is the explicit certificate and total-work contract connecting the existing notions to the JANUS terminal proof obligations.

## Decisive remaining gate

```text
POLYNOMIAL_PORTFOLIO_CONSTRUCTOR
```

For arbitrary CNF we still lack a polynomial-time constructor proving that the complete decision/message DAG and all leaf certificates have polynomial total size. A supplied small portfolio decomposition is not enough. Detecting useful backdoors or representations may itself contain the hard search.

## Next C034 attack

Replace the simple decision tree with shared DAG states and independently verified symbolic leaves:

- PS-signature tables;
- Horn and dual-Horn closure traces;
- GF(2) row-reduction certificates;
- beta-acyclic elimination orders;
- DNNF/d-DNNF/OBDD nodes with syntactic admission checks.

Measure whether sharing produces a polynomial quotient on adversarial Tseitin, deterministic 3-CNF, parity, duplicate-clause, and order-sensitive equality families.

## Claim boundary

C033 proves a portfolio-composition theorem and executable verifier interface. It does not construct a polynomial portfolio for every CNF and does not prove `P=NP`.
