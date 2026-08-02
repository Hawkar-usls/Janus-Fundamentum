# C012 — Total live-hypothesis attack sweep

C012 pauses hypothesis generation and attacks the entire live JANUS organism.

## Scope

- live hypotheses attacked: **93**;
- terminal shadows excluded: `H016`, `H018`, `H048`, `H074`;
- reusable attack protocols: **12**;
- logical attack cells: **1,116**;
- new hypotheses: **0**;
- new terminal results: **0**.

The campaign is stored in:

```text
registry/attack-protocols-c012.json
registry/total-attack-sweep-c012.json
```

Coverage is checked by:

```bash
python tools/validate_total_attack_sweep.py
```

## Twelve attacks applied to every live hypothesis

1. quantifier and decision-contract audit;
2. hidden-oracle and circularity audit;
3. uniformity and explicitness audit;
4. resource and bit-complexity audit;
5. soundness, completeness, and witness audit;
6. model-transfer audit;
7. auxiliary-variable and projection audit;
8. explicit counterfamily and restriction audit;
9. complexity-barrier scope audit;
10. parent-dependency audit;
11. mutual-incompatibility audit;
12. independent-reproduction audit.

These protocols are broad filters. They do not replace theorem-specific attacks.

## Survival result

### Seventy-three clean survivors

Seventy-three hypotheses received no `WEAKENED`, `INCONCLUSIVE`, or terminal cell in this standardized pass. This means only that the twelve broad protocols did not expose a registered defect.

It does **not** mean that these hypotheses are true, likely, novel, or close to proof.

### Ten pressured survivors

```text
H001 H002 H003 H004 H009 H017 H019 H070 H081 H089
```

Why they remain under pressure:

- `H001-H004`: unrestricted transformers can hide solve-and-encode circularity;
- `H009`: local rules can still implement global computation across many steps;
- `H017`: no explicit mixed residual family is yet proved to survive the allowed affine preprocessing;
- `H019`: the interface-node language may hide an arbitrary global function;
- `H070`: the standard first-theta conflict-graph route is known to miss difficult UNSAT regimes, so only a genuinely new compiler survives;
- `H081`: exact verification does not imply short exact certificate existence;
- `H089`: ordinary rational Gram factors are not a complete language for rational PSD matrices and were superseded by `H092`.

These hypotheses remain live because none of those attacks is a contradiction to the exact surviving formulation.

### Ten conflicted survivors

Five pairs cannot both be true:

```text
H006  vs H011
H007  vs H014
H012  vs H013
H022  vs H023
H024  vs H025
```

All ten remain live because C012 did not determine which member of each pair fails. Their simultaneous `OPEN` status must never be interpreted as evidence that both are plausible together.

### Zero destroyed or rejected

No C012 protocol produced a decisive theorem, explicit counterexample, or formulation failure sufficient for a graveyard shadow.

The laboratory therefore retains all ninety-three live hypotheses.

## Cell accounting

```text
SURVIVED      1,096
INCONCLUSIVE     10
WEAKENED         10
DESTROYED         0
TOTAL          1,116
```

`SURVIVED` means only that one protocol did not kill the hypothesis.

## What C012 changes

C012 establishes a new coverage invariant:

> A claimed total attack must name exactly every current live hypothesis, every declared protocol, and no terminal shadow.

The validator recomputes the live set from all modular hypothesis and graveyard files. Hard-coded omission of an inconvenient hypothesis causes CI failure.

## Next deep-attack priorities

Breadth has now been completed. The strongest next targets are:

1. `H096`: search for a finite exact level-one theta collision seed or prove a structural impossibility theorem;
2. `H085/H086`: prove or break bounded-depth functional certificate pullback;
3. `H090/H091`: construct the mixed family and test transfer into a fixed parity-aware proof system;
4. `H009/H017/H019`: replace informal locality restrictions by invariants that cannot simulate arbitrary global computation;
5. the five incompatible pairs: find one explicit family, simulation, or lower bound that collapses at least one side.

## Claim boundary

C012 is a breadth-first attack campaign. It does not prove that the seventy-three clean survivors are correct, and it does not measure distance to resolving `P` versus `NP`.
