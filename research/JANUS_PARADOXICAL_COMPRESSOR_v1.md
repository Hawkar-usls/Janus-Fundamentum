# JANUS Paradoxical Compressor (JPCOMP) v1

**Status:** research architecture + finite exact S4 compression witness.

`P_VS_NP = OPEN`

## Frozen result

On the exact `PHP_5_4_C1` frozen residual

```text
fingerprint = 990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6
CNF clauses = 56
CNF state units = 241
live variables = 13
Phi = 13
```

the four blocks

```text
(23,24,25)
(26,27,28)
(29,30,31)
(32,33,34)
```

form an exact `S4` orbit under three adjacent-swap generators.

The deterministic augmented-orbit gate partitions all 56 clauses into exactly 8 clause orbits. One representative per orbit plus one shared group certificate replays the exact original residual:

```text
56 explicit clauses -> 8 orbit representatives
raw-clause/orbit ratio = 7.0
compact raw JSON = 761 bytes
compact augmented certificate JSON = 397 bytes
exact generator closure = 24
exact replay = PASS
```

A candidate augmented proof-language accounting gives 56 units versus 241 CNF units. These are different proof languages; `56 < 256` is therefore **not yet** admission under the old CNF state cap. The next theorem/gate must define and audit inference directly in the augmented language without expanding all orbit images.

## Exact mathematical ingredients found in prior literature

### 1. Augmented clauses / group actions

Represent an orbit as `(representative clause, permutation group generators)` rather than materializing every image. This is the closest existing mathematical mechanism to a whole-orbit certificate. Pigeonhole families are known to admit polynomial-size proofs in symmetry-aware augmented-clause systems.

### 2. Non-injective homomorphism proof rules

A clause-preserving map need not be injective. Multiple literals/variables can map to the same image while retaining a sound proof rule. This is the closest proof-complexity analogue of a `many -> one` piston fold.

### 3. Circular Resolution

Allow cycles in the proof graph, but require a global nonnegative flow/balance certificate. The apparently self-supporting local proof is made sound by a globally checkable linear constraint. Pigeonhole principles have polynomial-size circular Resolution proofs.

### 4. Holographic / basis transformations

Change the algebraic basis of the constraint representation exactly. On suitable structured classes a hard-looking counting problem can become a tractable matchgate/Pfaffian computation. This is an exact `difficulty migrates under basis change` mechanism, not a universal SAT result.

### 5. Polynomial Calculus / Nullstellensatz

Translate clauses to polynomial equations and certify contradiction by an algebraic identity such as membership of `1` in the generated ideal. Expansion followed by exact cancellation is an explicit algebraic compression mechanism.

### 6. Cutting Planes / pseudo-Boolean arithmetic

A single inequality can represent a large family of Boolean clauses; counting structure such as PHP can admit polynomial proofs in a stronger arithmetic proof language.

### 7. GF(2) Gaussian elimination

For exact XOR structure, a combinatorial Boolean system becomes a linear-algebra problem after a basis/language change. JANUS already has this lane.

## JPCOMP design hypothesis

A useful paradoxical compressor does not delete information. It **moves where the information lives**:

```text
explicit clauses / variables
        ->
representative + orbit generators
        ->
latent group / flow / basis coordinates
        ->
small replayable proof state
```

The exact invariant is:

```text
SEMANTICS PRESERVED
WITNESS/REFUTATION RECONSTRUCTABLE
NO ORACLE
NO HEURISTIC SCORE
DETERMINISTIC CERTIFICATE DISCOVERY OR FAIL CLOSED
POLYNOMIAL PROPOSAL / VERIFICATION / STATE VOLUME REQUIRED FOR UNIVERSAL CLAIM
```

## Proposed deterministic proof operations

These are proof-language operations, not heuristic branching choices:

- `ORBIT`: store one representative plus exact permutation generators.
- `FOLD`: apply a certified non-injective homomorphism when clause preservation is directly checkable.
- `AUG_RESOLVE`: derive a new augmented clause directly at group level without enumerating every image.
- `CIRCULAR_FLOW`: permit cyclic reuse only with a replayable global LP/flow certificate.
- `BASIS`: apply an exact algebraic basis transformation when its defining identities are certified.
- `CANCEL`: perform exact polynomial/linear cancellation.
- `UNFOLD_VERIFY`: independently replay the final certificate to the original CNF or original witness.

No operation is selected by activity, randomization, ML, estimated balance, or empirical score. Candidate order must be canonical or the entire polynomially bounded candidate set must be checked.

## The current killer gate

The frozen 56-clause residual is already exactly compressible as 8 S4 orbit representatives.

The next question is no longer whether the orbit certificate exists. It does.

The gate is:

> Can `AUG_RESOLVE/FOLD/CIRCULAR_FLOW` operate directly on the 8 representatives + shared S4 generators, with polynomial exact inference and replay, and produce a strict `Phi < 13` transition without materializing the 56 images or hidden exponential stabilizer/intersection search?

If yes, JANUS has its first operational paradoxical compressor that defeats the present CNF representation wall on `PHP_5_4_C1`.

If no, the failure localizes the debt to **group-level inference complexity**, not orbit discovery or orbit description.

## Minecraft piston model

A Minecraft piston should not be modeled as two ordinary full cubes permanently occupying one lattice cell. During motion the engine uses a special moving-block state with carried-block metadata and fractional progress.

Mathematically, replace the ordinary voxel alphabet `B` by an extended fiber alphabet

```text
B' = B union (B x Direction x Progress x SourceState x ...)
```

so a world state

```text
s : Z^3 -> B
```

becomes during motion

```text
s' : Z^3 -> B'.
```

The carried block has visible/interpolated geometric position

```text
x + progress * direction
```

while its identity and phase are stored inside one technical lattice cell.

Thus the apparent paradox is not information destruction but **coordinate migration**:

```text
multiple explicit spatial coordinates
        ->
one lattice anchor + latent fiber state.
```

This is the same design motif as the augmented orbit compressor:

```text
many explicit orbit members
        ->
one representative + latent group generators.
```

Call this the **Piston Fiber Compression Principle**:

> A representation can reduce explicit ambient occupancy by moving the missing coordinates into an internal fiber, provided an exact inverse/replay map is retained.

For JANUS the corresponding rule is: never claim compression from fewer visible clauses alone; count the latent group/flow/basis certificate and its inference cost as part of the proof state.

## Claim firewall

```text
FINITE_S4_COMPRESSION != P_EQUALS_NP
SHORT_DESCRIPTION != POLYNOMIAL_INFERENCE
GROUP_GENERATORS != FREE_GROUP_REASONING
NONINJECTIVE_HOMOMORPHISM != INFORMATION_LOSS
CIRCULAR_PROOF != UNSOUND_CYCLE
PISTON_FIBER_ANALOGY != MINECRAFT_PHYSICS_THEOREM
P_VS_NP = OPEN
```
