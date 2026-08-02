# C031 — Parallel Direct-Sum Exponent Barrier

**Status:** `DECISIVE OBSTRUCTION / C031 REDIRECTED / P_VS_NP=OPEN`

Cross-link: draft PR #37, `C031: formalize proof-carrying SAT refuter bridge`.

## Active question

C031 requires amplification from current constructive gate-elimination refuters,
whose lower bounds are linear, to refuters against circuits of size `n^k` for
every fixed `k`.

A tempting route is to place `m` independent copies side by side and invoke a
perfect direct-sum theorem after proving that gates cannot be shared.

## Theorem — no exponent gain from parallel direct sum

Assume an explicit function on `n` inputs has a lower bound

```text
L(f_n) = Omega(n^a).
```

For `m` independent copies, even an ideal direct-sum theorem gives only

```text
L(f_n^m) = Omega(m n^a).
```

The combined input length is `N=mn`, hence

```text
m n^a = N^a / m^(a-1).
```

In the currently relevant linear case `a=1`,

```text
L(f_n^m) = Omega(mn) = Omega(N).
```

Therefore parallel repetition cannot turn a linear lower bound into
`N^k`, regardless of how perfectly one excludes sharing.

## Consequence for Certified Refuter Amplification

The previous `NO_SHARING_REFUTER_AMPLIFICATION` gate was necessary but not
sufficient. Even after proving a perfect direct-sum theorem, plain parallel
copies preserve the input-length exponent.

Thus the following route is closed:

```text
linear constructive refuter
+ m independent copies
+ perfect no-sharing/direct-sum theorem
=> refuter against N^k-size circuits.
```

It yields only a linear refuter in the new total input length.

## Required replacement

C031 must use a transformation with genuinely superlinear complexity growth
relative to encoded input growth, such as:

- strong functional composition with a proved exponent/depth growth theorem;
- hardness magnification from a weak constructive lower bound on a sparse or
  meta-complexity target;
- a restriction/lifting theorem that upgrades the circuit class or size bound
  while preserving explicit error recovery;
- another nonlinear amplifier with full sharing-aware accounting.

Every surviving amplifier must still preserve:

```text
explicit counterexample extraction
legal polynomial-size CNF encoding
SAT-label preservation
polynomial SAT witness or UNSAT-certificate generation
composition-size accounting
uniform polynomial runtime.
```

## Relation to primary literature

The obstruction matches the direct-sum difficulty emphasized in the KRW/strong
composition program: composition must do more than solve independent copies in
parallel. Recent general hardness-magnification results are relevant precisely
because they can amplify a weak lower bound without claiming that parallel
copy costs merely add.

## Machine audit

```bash
python experiments/direct/janus_c031_parallel_direct_sum_exponent_audit.py --self-test
```

The script checks 252 parameter tuples and records the symbolic identity

```text
m*n^a = N^a / m^(a-1).
```

## Updated C031 gates

### Certified Refuter Amplification

`PARALLEL_DIRECT_SUM` is now rejected as an exponent amplifier. The active
subroutes are `STRONG_COMPOSITION` and `CONSTRUCTIVE_HARDNESS_MAGNIFICATION`.

### Certificate-Rich Restriction Systems

Still open. Any restriction system must connect to a nonlinear amplifier and
must produce both labels with polynomial certificates.

### Constructive Hardness Magnification

Promoted to the primary C031 target. The next theorem must make the
magnification reduction constructive: from a candidate large circuit, recover
an explicit weak-target error and then transfer it to one certified SAT error.

## Claim boundary

This is a rigorous obstruction to parallel-copy amplification. It does not
exclude strong composition, hardness magnification, lifting, or a universal SAT
refuter. `P_VS_NP` remains `OPEN`.
