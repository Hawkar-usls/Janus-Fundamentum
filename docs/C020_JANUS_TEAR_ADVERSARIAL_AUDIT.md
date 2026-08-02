# C020 pre-admission — JANUS Tear adversarial audit

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT ADMITTED TO THE CANONICAL REGISTRY`

No swarm node, ESP32 device, radio channel, miner, NAS runtime, or physical P–N
junction was touched.

The earlier Tear draft used the name C019, but canonical `main` already contains
the connected-twin C019 cycle. This audit therefore continues as C020.

## Corrected conclusion first

The audit separates two statements that were initially blended together.

### Original strong quotient statement

> Every CNF has only polynomially many continuation-complete Tear classes across
> all of its partial assignments.

**Status: FALSIFIED.**

### Surviving policy-selected statement

> One explicit deterministic polynomial-time policy visits only polynomially
> many selected states and always returns either a SAT witness or a polynomially
> checkable UNSAT certificate.

**Status: OPEN.** Constructing such a policy is already a polynomial-time SAT
algorithm and would prove `P = NP`. The reformulation does not bypass the central
problem.

## Reproduction

```bash
python experiments/direct/janus_tear_adversarial_audit.py --self-test
python experiments/direct/janus_tear_marginal_collision.py
python experiments/direct/janus_tear_congruence_explosion.py --self-test
python experiments/direct/janus_tear_congruence_explosion.py --n 10
```

## Exact connected Tseitin audit

The main audit independently reconstructs the toroidal Tseitin CNFs rather than
calling the existing C018/C019 verifier. For `R = 0,...,8` it checks:

- exact degree-four XOR-to-CNF semantics;
- a constructive SAT assignment;
- an odd-charge UNSAT certificate;
- exact bounded-local signed-incidence multiset equality;
- the SAT-neutral five-clause connector;
- connectedness of the full primal graph;
- SAT witness recovery after connection;
- a sensitivity control that forces the local comparator to detect nearby
  charges.

At `R = 8`:

```text
torus side                         77
connected variables            23718
connected clauses              94869
semantic parity payload            2 bits
certificate vertex equations   11858
certificate clause references  94864
```

## PASS — family-specific module-aware Tear

When the two hidden Tseitin modules are known:

```text
SAT:    (2,0) charges -> Tear (0,0)
UNSAT:  (1,1) charges -> Tear (1,1)
```

The SAT member has an explicit spanning-tree edge assignment, extended across
the neutral bridge by `z = w = 1`.

For an odd module, a proof-bearing Tear checks that the selected clauses encode
every local XOR equation, every internal edge variable cancels twice, and the
right-hand charge parity is one. Summing gives the contradiction `0 = 1`.

## REJECT — naive connected-component Tear

Canonical C019 joins the two toroidal lobes with a satisfiability-neutral bridge.
The full primal graph is connected. A naive extractor storing one parity bit for
the visible connected graph returns:

```text
SAT:    (0)
UNSAT:  (0)
```

The Tear distinguishes the twins only if the solver receives or discovers the
semantic XOR-module decomposition. Discovery, boundary verification, connector
handling and witness recovery must all be charged to the total runtime.

## REJECT — tiny payload does not imply tiny proof

The semantic answer is two bits, but the independently checkable derivation is
linear in the formula size. This is still polynomial, but the accounting must
separate:

```text
semantic payload
proof certificate
module-discovery work
verification work
witness-recovery annotations
```

## PASS — second positive family: 2-SAT

For a 2-CNF implication graph, an UNSAT Tear consists of two checked paths inside
one strongly connected component:

```text
x -> not x
not x -> x
```

The same SCC computation recovers a satisfying assignment when no contradictory
variable exists.

The implementation was compared with exact brute force on 300 deterministic
random instances of at most eight variables:

```text
seed       9379992
SAT cases      153
UNSAT cases    147
agreement      300/300
```

This is a genuine second Tear language, but 2-SAT is already in P and therefore
does not solve general SAT.

## REJECT — marginal signature language

An exact three-variable pair was constructed with identical:

- unsigned clause scopes;
- clause widths and sign-count profiles;
- per-variable positive and negative occurrence counts;
- primal graph and component sizes;
- recognized equality/inequality XOR inventory.

Yet:

```text
SAT formula witness count      1
UNSAT formula witness count    0
Tear signatures equal       true
```

Therefore this rich finite marginal summary is not a sound SAT-state quotient.
It rejects that feature language, not every possible invariant language.

## FALSIFIED — full continuation quotient

Consider

```text
E_n(X,Y) = AND_i (x_i <-> y_i).
```

After assigning `X=a`, the residual formula requires exactly `Y=a`. For any
`a != b`, continuation `Y=a` accepts residual `a` and rejects residual `b`.
Thus all `2^n` residuals are pairwise distinguishable by future continuations.

The input contains only `2n` clauses and `4n` literal occurrences, but every
equivalence relation whose equal signatures guarantee identical behaviour for
**all** future `Y` continuations needs at least `2^n` classes.

The self-test verifies `n=1,...,8`. The `n=10` run checks:

```text
residual states                    1024
ordered cross-residual checks   1047552
```

This is a mathematical counterexample to the original all-residual polynomial
quotient conjecture. It is not evidence for `P != NP`, because this equality
family itself is easy.

## What remains open

The only surviving universal route is policy-selected:

```text
choose only polynomially many states
+ extract sound Tears with polynomial total proof volume
+ preserve or reconstruct a SAT witness
+ terminate with a polynomial UNSAT certificate
+ charge selection, discovery, verification and recovery
```

Producing such a procedure for every CNF is effectively the task of constructing
a polynomial-time SAT algorithm. Calling its intermediate certificates Tears is
useful architectural language, but not a shortcut around the theorem.

The experiments still do not measure:

- actual DPLL/CDCL residual-state merge counts;
- total-work reduction against a no-Tear baseline;
- positive compression on NP-complete non-XOR instances;
- representation-robust semantic module discovery;
- a general SAT witness-recovery map.

Therefore “one Tear collapses an exponential search tree” remains a target for a
specific solver run, not a demonstrated general result.

## Monsters Corporation bridge

The computational twin remains useful:

```text
Tear      -> negative knowledge / impossibility certificate
Laughter  -> positive knowledge / constructive witness and recovery map
Collider  -> certified elimination must meet witness construction
```

This is conceptual only. Biological tears, laughter, salt, quantum terminology
and semiconductor devices are not evidence for a complexity result.

## Verdict

JANUS Tear survives as a rigorous proof-learning vocabulary and architecture.
It has exact family-specific realizations for Tseitin parity and 2-SAT SCC
contradictions.

The following are rejected:

- naive connected-component parity;
- the tested marginal feature signature;
- the claim that a two-bit semantic payload is the whole proof;
- the original polynomial continuation-complete quotient of all residual states.

The policy-selected universal solver remains open and is essentially the
`P = NP` construction itself.
