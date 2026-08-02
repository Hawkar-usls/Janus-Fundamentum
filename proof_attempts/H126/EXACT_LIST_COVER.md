# H126 — exact-list SAT-sound cover

## Status

`FORMALIZING`, reproducibility `R2`.

This is an unconditional upper bound against finite positive SAT lists. It does
not refute H124 unless the generated list remains below the resulting circuit
budget.

## Input

Fix a canonical domain of `L`-bit formula encodings. Let

```text
T = {F_1, ..., F_m}
```

be the set of distinct formulas in a positive anti-checker list, with every
`F_i` satisfiable.

## Equality circuit

For every `F_i`, construct an equality test

```text
EQ_i(x) = 1 exactly when x = F_i.
```

Each bit is compared with its corresponding hardwired bit, and the comparisons
are combined by an AND tree. OR all equality tests:

```text
C_T(x) = OR_i EQ_i(x).
```

Then `C_T` accepts exactly the set `T`.

## SAT soundness

If `C_T(x)=1`, then `x=F_i` for some listed `F_i`. Every listed formula is
satisfiable by the anti-checker's own promise. Therefore every string accepted
by `C_T` is a satisfiable formula encoding.

The circuit is globally SAT-sound without parsing witnesses or solving SAT.

## Gate bound

Under any standard finite binary Boolean basis:

- one equality test uses `O(L)` gates;
- the outer OR uses `O(m)` gates.

A deliberately loose basis-safe accounting gives

```text
|C_T| <= 3mL.
```

Duplicate formulas do not increase `m` and provide no additional pressure.

## Consequence for H124

H124 must hit every SAT-sound circuit of size at most `L^k`. In particular it
must hit `C_T`. Since `C_T` accepts its entire own list, the only way to keep it
outside the attacked size class is

```text
3mL > L^k,
```

and hence

```text
m > L^(k-1) / 3.
```

This bound is independent of witness diversity. H120 and H126 should both be
charged; the smaller of the witness-union cover and exact-list cover is the
stronger attack on a given list.

## Reproduction

```bash
python experiments/direct/exact_list_sound_cover.py --self-test
```

Expected headline:

```text
JANUS_EXACT_LIST_SOUND_COVER = PASS
GATE_UPPER_BOUND = 3 * distinct_formulas * L
```

## Remaining wall

A sufficiently large polynomial list can exceed this exact-membership cover and
still remain polynomial-time constructible. H126 therefore does not terminate
H124. The true unresolved task is to prove that no more compressed SAT-sound
semantic circuit of size `L^k` covers the generated positive region.

## Claim boundary

H126 supplies a necessary cardinality condition only. It is not a general SAT
circuit lower bound and does not imply `P != NP`.
