# C022 — JANUS Honest Semantic Interface Compression

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

C022 starts from current canonical `main` at:

```text
2875f36ba2e8712b4292fdc74c1080eb040e3378
```

The inherited C021 boundary is respected:

```text
Policy-0T dispatcher != ordinary-Resolution proof object
```

C022 therefore treats an interface ROBDD as its own proof-carrying representation. It does not claim a free simulation by ordinary Resolution.

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend, external LLM, BCI, biological sample, physical P–N junction, or quantum device was touched.

## Goal

Compress the shared semantic interface between already recognized languages without asking a hidden general-SAT question such as:

```text
Does this partial boundary assignment have a satisfying continuation?
```

## Honest compressor

Each module must first pass a syntactic language gate:

```text
HORN
DUAL_HORN
```

The module is compiled into a reduced ordered binary decision diagram.

The compressor is honest because:

1. UNSAT pruning uses only the module's polynomial forward-chaining procedure.
2. Every prune includes a replayable contradiction certificate.
3. Equal states merge only when their recursive ROBDD triples are literally equal:

```text
(variable, low-child, high-child)
```

4. Every candidate order, recursive call, residual, branch edge, certificate step, BDD node, and AND-apply node is charged.
5. Exceeding the declared node budget produces `OPEN`.

It never produces an unverified answer.

## Positive result — exact semantic compression

Extended seeded cross-language test:

```text
cases                                      80
exact                                      80
OPEN                                       0
mismatches                                 0
false accepts                              0
raw interface assignments                  292352
nodes in selected exact messages           1020
nodes charged across all attempted orders  4275
median raw-state / selected-node ratio      256x
```

Thus, on the tested structured interfaces:

```text
292352 raw assignments -> 1020 selected ROBDD nodes
```

The final message is smaller, but failed candidate orders remain charged. This prevents a tiny final diagram from hiding an expensive selection process.

## Budget control

For the equality interface with `n=13` pairs:

```text
node budget                   1000
blocked order status          OPEN
blocked nodes before stop     1000
blocked recursive calls       2019
interleaved order status      EXACT
interleaved exact nodes       39
interleaved recursive calls   79
```

The compressor does not keep searching after the bound and does not infer the answer from the existence of a better order.

## Exact order-sensitivity attack

For:

```text
E_n(X,Y) = AND_i (x_i <-> y_i)
```

at `n=13`:

```text
variables                    26
blocked order nodes          24573
interleaved order nodes      39
blocked residuals            32765
interleaved residuals        53
node ratio                   630.08x
```

The Boolean function is unchanged. Only the representation order changes.

This confirms:

```text
small semantic interface
!=
easily discoverable small ROBDD
```

## Fixed-radius semantic summaries are rejected

For every tested radius `r=1..7`, compare:

```text
F_r = NOT(x1 AND ... AND x_(r+1))
T   = TRUE
```

`F_r` is a Horn formula.

Every projection onto at most `r` variables is identical for `F_r` and `T`: every local tuple has an extension. Yet the all-true assignment distinguishes the two global relations.

Therefore:

> No fixed-radius collection of local extendability marginals is an exact universal semantic-interface message.

This is a constructive family, not a random collision.

## Generic 3-CNF partition

Every exact 3-clause is Horn or dual-Horn, so the extended audit also compiled the two sides of ordinary small 3-CNF instances and combined their exact messages.

```text
cases                    50
exact                    50
OPEN                     0
mismatches               0
false accepts            0
charged BDD nodes        38101
charged recursive calls  147857
```

This finite success is **not** a polynomial-time SAT result. The tested formulas have only 9–14 variables and the compiler is output-sensitive.

The compact CI fixture retains the core controls on 30 random language pairs and 20 generic 3-CNFs.

## Why ROBDD is not the universal final answer

Bryant's reduced ordered BDD gives a canonical representation for a fixed variable order and supports exact graph operations.

But exact OBDD compilation has real lower bounds:

- Bova and Slivovsky prove polynomial OBDD compilation for structured CNFs such as variable-convex classes and establish exponential OBDD size for a bounded-degree CNF family.
- Segerlind proves near-exponential lower-bound families for symbolic quantifier-elimination / tree-like OBDD reasoning across all variable orders.
- A 2026 preprint by de Colnet, Laarman, and Lee reports random-2-CNF density regimes where polynomial-time 2-SAT decision coexists with exponential OBDD size with high probability.

The third point is especially important for JANUS:

```text
decision can be polynomial
while exact reusable interface compilation is exponential
```

Therefore a large ROBDD does not mean SAT itself is hard, and a small SAT answer does not imply a small reusable semantic message.

## What C022 genuinely adds

C022 provides the first explicit interface compressor satisfying all four:

```text
exact
proof-carrying
no hidden general-SAT oracle
total-work accounting
```

It also identifies three separate failure surfaces:

```text
local-summary insufficiency
variable-order discovery
representation-language size
```

## New surviving conjecture

### Polynomial Proof-Carrying Interface Portfolio Conjecture

There exists one deterministic polynomial-time selector over a finite or polynomially generable collection of canonical interface languages such that, for every CNF module network:

1. at least one selected language has polynomial representation size;
2. that representation is constructed in polynomial time;
3. conjunction and existential elimination stay polynomial;
4. every merge and prune is independently checkable;
5. the complete SAT witness or UNSAT Tear is recoverable in polynomial work.

This is open.

Constructing such a portfolio would already provide the missing polynomial SAT algorithm. C022 only adds one valid portfolio member and proves it cannot be the only member.

## Next gate

The next non-cosmetic experiment is a mixed canonical portfolio:

```text
ROBDD
+ affine linear relation
+ 2-CNF implication graph
+ Horn closure system
```

The key test is not whether each language is compact separately. It is whether cross-language conjunction and existential elimination can be performed without:

- converting everything into an exponentially large universal format;
- querying general SAT;
- or silently losing witness recovery.

## Reproduction

```bash
python experiments/direct/janus_honest_interface_obdd.py
```

## References

- R. E. Bryant, *Graph-Based Algorithms for Boolean Function Manipulation*, IEEE Transactions on Computers 35(8), 677–691, 1986. DOI `10.1109/TC.1986.1676819`.
- S. Bova and F. Slivovsky, *On Compiling Structured CNFs to OBDDs*, Theory of Computing Systems 61, 637–655, 2017. DOI `10.1007/s00224-016-9715-z`; arXiv `1411.5494`.
- N. Segerlind, *Nearly-Exponential Size Lower Bounds for Symbolic Quantifier Elimination Algorithms and OBDD-Based Proofs of Unsatisfiability*, ECCC TR07-009; arXiv `cs/0701054`.
- A. de Colnet, A. Laarman, J. H. Lee, *The Compilability Thresholds of 2-CNF to OBDD*, arXiv `2603.15463`, 2026.

## Claim boundary

C022 does not prove `P=NP`, `P!=NP`, `NP=coNP`, or a lower bound against all algorithms. It constructs and attacks one explicit honest interface language.
