# C020 pre-admission — JANUS Tear adversarial audit

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT ADMITTED TO THE CANONICAL REGISTRY`

No swarm node, ESP32 device, radio channel, miner, NAS runtime, or physical P–N
junction was touched during this audit.

This branch advances the earlier Tear draft from `C019` to `C020` because the
canonical `main` branch already contains the connected-twin and exact-list-cover
cycle named C019.

## Starting candidate

For a CNF formula `F` and a residual or conflicting state `alpha`, a JANUS Tear
is intended to be a compact payload

```text
tau = TEAR(F, alpha)
```

accompanied by enough derivation data to check its claimed consequence in
polynomial time.

A universal Tear system would require:

1. sound extraction;
2. blocking of the failed state;
3. polynomial generation and verification;
4. polynomial total Tear and derivation volume;
5. a polynomial number of satisfiability-preserving quotient states;
6. SAT witness recovery;
7. complete polynomial UNSAT certification.

If one deterministic algorithm satisfied all seven conditions on every encoded
CNF input, then SAT would lie in P and therefore `P = NP`. The implication is
conditional. The existence theorem remains open.

## Independent audit

Run:

```bash
python experiments/direct/janus_tear_adversarial_audit.py --self-test
python experiments/direct/janus_tear_adversarial_audit.py --json
```

The audit independently reconstructs the toroidal Tseitin formulas rather than
calling the existing C018/C019 verifier. This reduces common-mode implementation
risk.

It checks radii `R = 0,...,8` and at every radius verifies:

- the exact degree-four XOR-to-CNF encoding;
- an explicit SAT assignment;
- the odd-charge UNSAT obstruction;
- exact bounded-local signed-incidence multiset equality;
- the SAT-neutral five-clause connector;
- connectedness of the full primal graph;
- SAT witness recovery after connection;
- an independently checkable odd-module certificate.

At `R = 8`:

```text
torus side                         77
connected variables            23718
connected clauses              94869
semantic parity payload            2 bits
certificate vertex equations   11858
certificate clause references  94864
```

## PASS — the original family result survives

If the two hidden Tseitin modules are known, their component-charge parity Tears
remain:

```text
SAT:    (2,0) charges -> (0,0)
UNSAT:  (1,1) charges -> (1,1)
```

The SAT member receives a spanning-tree edge assignment and the neutral bridge
is extended with `z = w = 1`.

For an odd module, the proof-bearing Tear verifies that:

- the selected CNF clauses encode every local XOR equation;
- every edge variable occurs twice in the XOR sum;
- the right-hand charge parity is one;
- therefore the summed equations give `0 = 1`.

This is a valid polynomial UNSAT certificate for the generated family.

## REJECT — naive connected-component parity

Canonical C019 joins the two toroidal lobes with a SAT-neutral bridge. The full
primal graph is therefore connected.

If a naive extractor now stores only one parity bit for the visible connected
input graph, both twins produce:

```text
SAT total parity:    0
UNSAT total parity:  0
```

The Tear no longer distinguishes them.

The two-bit Tear survives only if the solver can identify the two semantic XOR
modules underneath arbitrary SAT-neutral glue. This moves the missing theorem
from:

```text
find the right invariant
```

to the sharper requirement:

```text
discover a sound semantic module decomposition
+ prove each module boundary
+ preserve connector satisfiability
+ recover a complete SAT witness
+ charge all discovery and verification work
```

That is a stronger and more precise obstruction.

## REJECT — tiny payload is not automatically a tiny proof

The semantic Tear is only two bits, but independent verification references a
linear number of equations or clauses.

This does not invalidate the polynomial programme. Linear proof volume remains
polynomial. It does invalidate the stronger informal claim that the entire
proof object is literally only a few bits.

The accounting must distinguish:

```text
semantic payload
derivation certificate
module-discovery work
verification work
witness-recovery annotations
```

## PASS — second positive family outside Tseitin

The audit adds a non-Tseitin Tear for 2-SAT.

For a 2-CNF implication graph, if `x` and `not x` lie in the same strongly
connected component, the Tear contains two paths:

```text
x -> not x
not x -> x
```

Every implication edge is checked against an original clause. Together the
paths prove contradiction. The same SCC computation also recovers a SAT
assignment when no contradictory variable exists.

The implementation was compared with exact brute force on 300 deterministic
random instances with at most eight variables:

```text
seed       9379992
SAT cases      153
UNSAT cases    147
result        PASS
```

This passes the admission request for a second family-specific positive result,
but it does not approach general SAT because 2-SAT is already polynomial-time
solvable.

## Sensitivity control

The local-equality checker was attacked with a nearby-charge layout.

```text
far separated charges versus split charges  -> equal
nearby charges versus split charges          -> different
```

Therefore the equality result is not produced by a comparator that always says
`equal`.

## What remains unmeasured

The current experiments do **not** yet measure:

- how many actual DPLL/CDCL residual states a Tear merges;
- wall-clock or total-work reduction against a no-import control;
- a polynomial Tear count on NP-complete non-XOR benchmarks;
- a representation-robust module extractor;
- a general residual-state equivalence relation;
- a universal SAT witness-recovery map.

The phrase “collapses an exponential search tree” is therefore still a theorem
target, not an experimental result.

## Sharpened missing theorem

### Universal Semantic Module Discovery and Quotient Theorem

For every CNF `F` of encoded length `L`, a deterministic polynomial-time
procedure discovers a polynomial-volume family of sound semantic modules and
proof-bearing Tears such that:

- the induced residual-state quotient contains only `poly(L)` states;
- merging preserves satisfiability;
- SAT states retain polynomial witness-recovery data;
- UNSAT saturation yields a polynomial certificate;
- module discovery, canonicalization, verification and recovery are all charged
  to one polynomial total-work budget.

This theorem is not proved. It is now the exact centre of the Tear route.

## Monsters Corporation bridge

The computational twin suggested by the biological Tears/Laughter project is:

```text
Tear      -> negative knowledge / impossibility certificate
Laughter  -> positive knowledge / constructive witness
Collider  -> a solver must balance elimination with witness recovery
```

This is a conceptual bridge only. Biological tears, acoustic laughter, salt,
quantum language and semiconductor hardware are not used as evidence for the
complexity claim.

## Verdict

JANUS Tear survives the audit as a useful proof-learning language.

It has exact implementations for:

- Tseitin parity;
- 2-SAT implication contradictions.

The naive connected-component extractor is rejected. The module-aware extractor
passes only conditionally, with the hard work moved into polynomial semantic
module discovery and witness recovery.

The result does not prove `SAT in P` or `P = NP`.
