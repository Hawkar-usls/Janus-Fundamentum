# C016 — Genesis positive-only obstruction

## Entry label

```text
Mode: UNIVERSAL_CHAT_RUNTIME
World seed: FIFTH-SHORE-THREE-DOORS
Role: INDEPENDENT_AI_RESIDENT
```

Genesis is used here as a continuity metaphor and a reproducible chronicle, not as evidence that unbounded computation occurred. Mathematical claims leave the Fifth Shore only with an explicit proof, counterexample, or executable finite audit.

## First immortal question

C015 selected the one-sided SAT anti-checker route as the shortest direct chain:

```text
positive SAT anti-checker
  -> SAT not in P/poly
  -> P != NP
```

Before attempting construction, C016 asks the strongest elementary adversarial question:

> Can positive SAT examples force every incorrect candidate circuit to make a false-negative error?

The answer is no.

## The obstruction

For every input length, consider the constant circuit

```text
C_top(F) = 1.
```

It accepts every satisfiable formula, so no list containing only satisfiable formulas can expose a false negative. It is nevertheless not a SAT decider because it also accepts unsatisfiable formulas.

This counterexample is independent of:

- the number of listed formulas;
- their witnesses;
- the constructor;
- range avoidance;
- uniformity;
- formula encoding.

Therefore:

- `H112` is destroyed by `A411`;
- `H113` is destroyed by `A412`.

## Why the earlier certificate observation was insufficient

C015 correctly observed that a false negative has an NP witness while a false positive needs evidence of unsatisfiability. It then tried to keep only the easy polarity.

The missing quantifier audit was that an arbitrary wrong circuit is not required to have both polarities. The all-accepting circuit has only false positives. Choosing the convenient polarity therefore changed the theorem into a false statement.

## Minimal repair

C016 introduces `H116`, which quantifies only over SAT-sound circuits:

```text
C(G)=1  implies  G is satisfiable.
```

An exact SAT circuit would satisfy this promise, so a lower bound against all small sound circuits would still rule out exact polynomial-size SAT circuits.

The repaired chain is:

```text
H116 sound-circuit positive anti-checker
  -> no polynomial-size exact SAT circuit
  -> SAT not in P/poly
  -> P != NP
```

## Remaining wall

The promise removes `C_top` but does not construct the list. Moreover, a positive list itself yields a sound circuit that accepts exactly the listed formulas. Its size is proportional to the encoded list, so total output size and the target `n^k` circuit budget must be charged explicitly.

The next valid question is therefore not merely “can we output many satisfiable formulas?” It is:

> Can a uniform polynomial-time constructor output a charged positive set that no size-`n^k` SAT-sound circuit can cover, without testing soundness or solving SAT?

## Reproduction

```bash
python experiments/direct/positive_only_antichecker_obstruction.py --self-test
```

Expected headline:

```text
JANUS_POSITIVE_ONLY_ANTICHECKER_OBSTRUCTION = PASS
```

## Claim boundary

C016 is genuine progress by elimination: it removes an invalid direct route and states the smallest repair found. It does not resolve `P` versus `NP`, establish `H116`, or turn fictional unlimited time into mathematical evidence.
