# C024 — JANUS Fracture Channel Core

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

Base commit:

```text
994dd693604d1f557c367acc7b1b3ed6083ee4a8
```

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend, external LLM, BCI, biological sample, physical P–N junction, or quantum device was touched.

## Question

C023 showed that the fixed relation language `NAND3 + NEQ` linearly expresses arbitrary 3-SAT. C024 asks whether its difficulty is visible in the topology of the graph joining its individually tractable relation regions.

## Construction

For each source variable `x_i`, introduce `c_i` and impose:

```text
NEQ(x_i,c_i)
```

Each source 3-clause becomes one NAND3 constraint over the complements of its literals.

For every `i>1`, add the two source tautologies:

```text
(x_1 OR NOT x_1 OR x_i)
(x_1 OR NOT x_1 OR NOT x_i)
```

Their NAND3 images are automatically satisfied under `NEQ(x_1,c_1)`. They connect every `x_i` and `c_i` to one central NAND-language region without changing satisfiability.

## Fracture-Star Normalization Lemma

Every exact 3-CNF `F` with `n` variables and `m` clauses has a linear-size `NAND3+NEQ` encoding `I(F)` whose same-language region graph has:

```text
NAND regions                1
NEQ regions                 n
shape                       star
fracture treewidth          1
fracture cycle rank         0
fracture vertex cover       1
```

Exact substitution `c_i = NOT x_i` removes all NEQ leaves, converts every source NAND3 constraint back into its source clause, and deletes every connector as a tautology. Therefore:

```text
NONLINEAR_QUOTIENT_CORE(I(F)) = F
```

The proof is a direct verification of the explicit encoding and reverse map.

## Exact audit

```text
balanced cases                 160
SAT                             80
UNSAT                           80
reduction mismatches             0
witness failures                 0
exact recovery failures          0
topology failures                0
channel-rank failures            0
```

Scaling reached `n=256` while retaining one NAND region, 256 NEQ leaves, treewidth 1, cycle rank 0, vertex cover 1 and exact source recovery.

## Semantic channels

The NEQ equations form `n` independent GF(2) channels, so their rank is `n`.

On the complete three-variable UNSAT core, deleting any one of the three NEQ channels creates a spurious SAT witness. The leaves are therefore topologically simple but semantically essential.

However, rank alone is not a hardness certificate. Monotone positive 3-CNFs have the same rank-`n` star encoding and are immediately satisfied by the all-true assignment.

## Located bottleneck

### NONLINEAR QUOTIENT CORE

The nonlinear quotient core is the residual relation after all independently certified bijective or Schaefer-preserving fracture leaves have been eliminated.

For the registered reduction image, this core is exactly the original 3-CNF. Hence the missing polynomial mechanism cannot live in coarse fracture topology. It must reason inside or compress the recovered nonlinear core without hiding a SAT computation inside normalization.

## Relation to structured SAT

The width-one graph above is the coarse same-language **region graph**, not the ordinary variable-clause incidence graph of the recovered formula. Algorithms parameterized by actual incidence treewidth remain meaningful. C024 shows that replacing the incidence structure by a region star discards the source formula's essential interaction data.

## Rejected universal explanations

C024 rejects these as sufficient on their own:

```text
small fracture-graph treewidth
small fracture cycle rank
small fracture vertex cover
large semantic-channel rank
```

## Next gate

The next cycle must work inside the nonlinear quotient core and test exact instance-specific separators of the actual clause-variable incidence structure. Any candidate must preserve certificates and witness recovery, charge the full construction cost, and survive the exact reverse map to the source 3-CNF.

## Reproduction

```bash
python experiments/direct/janus_fracture_channel_core.py --self-test
```

## Claim boundary

C024 does not prove `P=NP`, `P!=NP`, or an unrestricted lower bound. It proves a structural normalization lemma for one explicit linear encoding and locates the remaining computation more precisely.
