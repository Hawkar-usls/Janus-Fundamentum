# C016 — Positive-only anti-checker obstruction

## Claim boundary

This note proves an elementary obstruction to `H112` and `H113`. It does **not** prove a circuit lower bound and does not resolve `P` versus `NP`.

## Theorem

Let `L` be any nontrivial language on a fixed input length, and let `T` be any set containing only positive examples from `L`. Then `T` cannot expose an error in every Boolean circuit by requiring a false negative on `T`.

## Proof

Take the constant circuit

```text
C_top(x) = 1
```

for every input `x` of the relevant length. The circuit has constant size. For every `x` in `T`, positivity gives `x in L`, and `C_top(x)=1`. Therefore `C_top` has no false negative on `T`.

Because `L` is nontrivial, some input `y` is not in `L`. On that input `C_top(y)=1`, so the circuit is incorrect only through a false positive. A positive-only test set cannot reveal that error. QED.

## Application to H112

`H112` quantifies over every polynomial-size candidate SAT circuit while requiring every listed counterexample to be a satisfiable formula on which the circuit outputs zero. The constant-one circuit is polynomial size and never outputs zero. It therefore contradicts the universal quantifier independently of the constructor, list size, formula encoding, or witnesses.

Hence `H112` is destroyed by `A411`.

## Application to H113

`H113` requires a decoder that, for every candidate SAT circuit, outputs a satisfiable formula `F` with `C(F)=0`. For `C_top`, no such formula exists. Range avoidance cannot force a nonexistent error polarity.

Hence `H113` is destroyed by `A412`.

## Exact repair choices

An arbitrary-circuit anti-checker must do at least one of the following:

1. include certified negative examples and permit false-positive errors;
2. restrict the quantified circuits to circuits sound for SAT;
3. prove a normalization that transforms arbitrary candidate circuits into SAT-sound circuits while preserving any exact SAT circuit and the required size bound.

The third option is itself a soundness theorem and may be as difficult as the certificate asymmetry it was intended to avoid.

## Repaired route H116

`H116` chooses option 2. It retains satisfiable formulas and ordinary assignment witnesses, but quantifies only over circuits satisfying

```text
C(G)=1  =>  G is satisfiable.
```

This repair excludes `C_top`, but it does not construct an anti-checker.

A second obstruction remains: for any finite positive list, the circuit that accepts exactly the listed encodings is SAT-sound. Its size is proportional to the charged list representation. Therefore H116 must compare total list size, formula length, and the target `n^k` budget explicitly; a constructor cannot win merely by outputting an uncharged enormous list.
