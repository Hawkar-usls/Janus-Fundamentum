# C025 — JANUS Certified Residual Quotient

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

Base:

```text
994dd693604d1f557c367acc7b1b3ed6083ee4a8
```

C024 located the remaining computation in the `NONLINEAR_QUOTIENT_CORE` after all independently certified tractable fracture leaves are removed.

C025 enters that core and studies exact separator messages.

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend, external LLM, BCI, biological sample, physical P-N junction, or quantum device was touched.

## Exact object

Fix a variable or decomposition order. For every prefix assignment `alpha`, let `F|alpha` be the residual Boolean function on the unassigned variables.

Two separator states may be merged only if their residual functions are exactly equal.

C025 separates two independent costs:

```text
STATE VOLUME
  number of continuation-distinct residual functions

MERGE PROOF VOLUME
  certificates proving that different residual representations are equal
```

Their sum is named `CERTIFIED_RESIDUAL_QUOTIENT_COMPLEXITY`.

## Honest compiler

The implemented compiler permits only:

- deterministic restriction by one ordered variable;
- exact CNF canonicalization;
- replayable clause-subsumption certificates;
- hash-consing of identical `(variable, low, high)` BDD triples;
- explicit residual-state budgets.

It never asks a general SAT or semantic-equivalence oracle. A budget violation returns `OPEN`.

## Positive result — exponential fake width removed

For each gadget:

```text
(x_i OR y_i)
(NOT x_i OR y_i)
(x_i OR y_i OR z_i)
```

assigning `x_i` produces either `y_i` or `y_i AND (y_i OR z_i)`. The second residual contains a clause subsumed by `y_i`.

At the cut after all `x_i`, with `n=12`:

```text
raw residual CNFs                 4096
expected raw residuals            4096
certified normalized residuals    1
cut certificates                  4096
cut subsumption steps             24576
```

The full residual automaton required:

```text
residual states                   37
BDD nodes                         12
maximum frontier                  2
status                            EXACT
witness valid                     True
```

Thus polynomial proof-carrying normalization removed an exponential representation artifact before search.

## Genuine continuation width — equality

For `E_n(X,Y) = AND_i (x_i <-> y_i)`, blocked order `x_1,...,x_n,y_1,...,y_n` forces one distinct continuation function for every assignment to `X`.

Exact small profile at `n=9`:

```text
blocked semantic peak             512
interleaved semantic peak         3
blocked cut width                 512
```

Larger exact cut at `n=14`:

```text
continuation-distinct states      16384
expected                          16384
blocked compiler status           OPEN
states before OPEN                5000
```

Interleaving each pair produced:

```text
status                            EXACT
residual states                   57
BDD nodes                         42
witness valid                     True
```

This is true semantic width, not syntax that subsumption can remove. It also shows that high residual width alone is not a hardness certificate: equality is trivially satisfiable, but a poor cut has exponential exact message volume.

## Random profile audit

```text
cases                             120
automaton mismatches              0
syntactic width below semantic    0
cases with semantic merge gap     95
maximum observed peak gap         13
```

In most cases, subsumption-normalized syntax still had more states than the true semantic quotient. Those extra merges require stronger certificates.

## Equivalence-certificate barrier

For arbitrary CNF `F`:

```text
F equivalent to FALSE  <=>  F is UNSAT
```

Therefore an unrestricted semantic state-merger contains a coNP equivalence obligation.

Balanced audit:

```text
cases                             100
SAT                               50
UNSAT                             50
equivalence mismatches            0
separating-witness failures       0
Resolution-proof failures         0
verified Resolution steps         950
charged pair attempts             11250
```

For non-equivalence, one separating assignment is an easily checked certificate. For equivalence, the verifier needs an UNSAT-style proof of the disagreement formula.

Replacing syntactic identity by a magical semantic hash would hide the original problem inside the compressor.

## Bounded-width positive control

Implication chains up to 128 variables were compiled exactly:

```text
all exact                         True
all maximum frontiers <= 2        True
```

## Located bottleneck

### CERTIFIED_RESIDUAL_QUOTIENT_COMPLEXITY

A universal polynomial mechanism must jointly control:

1. discovery of the order or decomposition;
2. number of continuation-distinct residual functions;
3. construction of their representations;
4. proof volume for every semantic merge;
5. transition verification;
6. terminal verification;
7. witness or Tear recovery.

## Certified Residual Automaton Criterion

If every CNF admits a polynomial-size residual automaton whose transitions, state equivalences, terminals and witness-recovery maps are independently verifiable in polynomial time, and such an automaton is constructible in polynomial time, then SAT is in P.

This is an algorithmic criterion, not a proof that the required automata exist.

## Next target

The next cycle must search for a proof system that certifies useful residual equivalences more strongly than subsumption but more cheaply than unrestricted CNF equivalence.

Immediate candidates:

```text
bounded-width Resolution summaries
implication/SCC equivalence
GF(2) row-space equivalence
bounded-treewidth interpolation
proof-carrying clause learning
```

Every candidate must be attacked by `F equivalent to FALSE iff F is UNSAT` and by blocked equality.

## Reproduction

```bash
python experiments/direct/janus_certified_residual_quotient.py --self-test
```

## Claim boundary

C025 does not prove `P=NP`, `P!=NP`, or a lower bound against all algorithms. It constructs an honest certified residual compiler and isolates the exact equivalence-certificate barrier inside the nonlinear quotient core.
