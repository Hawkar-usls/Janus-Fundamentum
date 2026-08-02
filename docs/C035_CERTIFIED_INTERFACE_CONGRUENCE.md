# C035 — Certified Interface Congruence

**Status:** `CONSTRUCTIVE RESTRICTED MERGE CALCULUS / P_VS_NP=OPEN`

## Purpose

C034 proved exact composition for a logarithmic shared boundary and showed that unrestricted Horn + affine composition already contains arbitrary 3-SAT. C035 therefore does not add another local solver. It formalizes the first proof-carrying rule for merging boundary states without invoking a general SAT or formula-equivalence oracle.

## State object

For a partial boundary assignment `alpha`, every admitted module emits an exact residual message together with a replayable construction record.

The current baseline languages are:

```text
Horn residual CNF after certified restriction and normalization
affine GF(2) row space in canonical RREF form
verified absorbing FALSE terminal
```

The global state is

```text
Sigma(alpha) = ABSORBING_FALSE
```

when any module supplies a verified contradiction; otherwise it is the ordered tuple of exact module messages.

## Certified Congruence Theorem

Assume every module message constructor is exact under restriction and independently replayable. If

```text
Sigma(alpha) = Sigma(beta)
```

and both records replay successfully, then `alpha` and `beta` have identical SAT behavior under every continuation admitted by the represented residual modules. Therefore they may be merged without changing the answer. Witness reconstruction may reuse the same local recovery rules because the residual objects are identical componentwise.

This theorem is deliberately one-sided:

```text
same certified message  -> safe merge
same semantic function  -/-> merge required
```

The reverse direction is not assumed. Proving arbitrary CNF residual equivalence would already contain the hard problem, because equivalence with `FALSE` is UNSAT.

## Algebra of obligations

A message language is admitted only for operations for which it has polynomial replay rules:

```text
restrict
project
conjoin
merge
decide
recover
```

The current C035 baseline supports exact restriction, equality-based merge, decision and recovery in its admitted residual languages. It returns `OPEN` rather than silently applying unsupported cross-language projection or conjunction.

## Exact positive control — affine canonicalization

For `k` systems

```text
x_(2j-1) XOR x_(2j) XOR z_j = 0
```

assigning the `2k` prefix variables gives `2^(2k)` raw assignments but only `2^k` canonical affine messages, one for each parity vector.

Frozen largest control:

```text
prefix assignments          65536
canonical affine messages     256
```

This is real exact semantic compression obtained by polynomial row-space normalization.

## Exact warning — product diversity is decomposition-dependent

Consider

```text
F_n = AND_i (x_i OR x_i OR x_i).
```

Encode it through the C023/C034 Horn + NEQ modules and examine complete assignments.

A naive tuple containing every local module status has exactly

```text
2^n
```

certified product signatures. Yet the global continuation semantics has only two terminal classes:

```text
TRUE  only for the all-one assignment
FALSE for every other assignment
```

A single verified absorbing contradiction collapses all failing product states.

At `n=12`:

```text
raw product classes       4096
absorbing classes            2
semantic classes             2
```

Therefore exponential certified diversity in one fixed product language is not an intrinsic hardness result. It may be caused by a poor decomposition or by omitting cross-module proof rules.

## Exact warning — safe syntax can under-merge

The Horn formula

```text
NOT x3
AND NOT x2
AND (NOT x1 OR x3)
```

has two prefix assignments producing syntactically different normalized residuals:

```text
x1=0, x2=1  -> FALSE
x1=1, x2=0  -> (NOT x3) AND x3
```

Both residuals are false for every continuation of `x3`, but syntax equality alone cannot merge them. A Horn refutation certificate can.

This demonstrates the exact distinction between:

```text
semantic equivalence
certifiable equivalence in the current language
```

## NAND3 + NEQ pressure

The auditor applies the exact C023/C034 reduction image to 400 deterministic random 3-CNFs and branches on half of the source variables. For every state it computes:

1. the certified product/absorbing signature;
2. the complete continuation truth vector by exhaustive holdout evaluation;
3. the corresponding partitions.

Frozen result:

```text
source formulas                          400
prefix states                           2830
certified classes                       2372
true continuation classes               1617
strict certified under-merging cases     272
maximum certified/semantic ratio           8
verified nontrivial merge pairs           275
corrupt state record                  rejected
```

Every certified merge was checked to remain inside one true continuation class. The finite counts are pressure only; they do not prove an asymptotic bound.

## Main conclusion

C035 rules out a misleading interpretation of the next experiment:

```text
exponential classes under one certificate language
```

cannot by itself close the whole interface-compression route. It only shows that the chosen decomposition and proof language are insufficient.

The active constructive gate is now:

# JOINT_DECOMPOSITION_LANGUAGE_AND_PROOF_SELECTION

A universal algorithm must choose, in polynomial time and under one charged budget:

- module granularity;
- boundary/decomposition order;
- message language for every region;
- cross-language proof rules;
- absorbing certificates;
- projection and conjunction operations;
- witness and UNSAT recovery.

The chosen package must keep the number and total size of certified states polynomial on every CNF.

## Next cycle

C036 should test a refinement procedure rather than a fixed signature tuple:

```text
start with coarse verified terminal classes
refine only when an explicit continuation separates two states
attach a replayable separating witness or proof
stop with EXACT when the quotient and all certificates remain polynomial
return OPEN on budget exhaustion
```

The decisive issue is whether separating continuations can be discovered without calling SAT/equivalence on arbitrary residuals.

## Reproduction

```bash
python experiments/direct/janus_c035_certified_interface_congruence.py --self-test
```

## Claim boundary

C035 proves a sound restricted congruence calculus, not completeness of its merge language. It neither proves `P=NP` nor derives `P!=NP` from a representation-specific explosion.

```text
P_VS_NP=OPEN
```
