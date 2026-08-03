# C046 affine-offset obstruction

```text
P_VS_NP=OPEN
```

## Exact theorem

The represented linear matroid of factor normals, even when supplied through its complete subset-rank function, does not determine affine-subspace-union avoidance, union cardinality, or SAT/UNSAT.

For every dimension `d >= 1`, define two arrangements in `GF(2)^d`. Both contain two hyperplanes with normal `e_i` for every coordinate `i`.

```text
A_d: e_i . x = 0, e_i . x = 0
B_d: e_i . x = 0, e_i . x = 1
```

The ordered normal vectors and every subset rank are identical. Hence all invariants derived only from normal-space span/intersection dimensions, represented-matroid connectivity, pathwidth or branch-width are identical.

But their affine semantics differ:

```text
A_d leaves exactly 1^d uncovered -> SAT
B_d covers the whole ambient space -> UNSAT
```

Therefore affine offsets and consistency signatures are mandatory in every sound C046 decomposition and separator message.

## Consequence for C046

A normal-matroid layout may still be useful as a structural skeleton, but it cannot be the complete semantic state. Every cut must additionally bind enough affine information to distinguish translated parallel flats. At minimum, the certificate must replay consistency of the accumulated augmented systems `[N | b]`, not only ranks of `N`.

This redirects the constructive search toward an **affine connectivity signature** carrying both:

```text
linear boundary span
augmented affine consistency / coset information
```

The result does not show that affine-invariant decomposition is impossible, does not establish a width lower bound, and does not imply `P != NP`.

## Reproduction

```bash
python experiments/direct/janus_c046_affine_offset_obstruction.py \
  --self-test \
  --output /tmp/c046.json
cmp /tmp/c046.json \
  experiments/direct/C046-JANUS-AFFINE-OFFSET-OBSTRUCTION.frozen.json
python experiments/direct/janus_c046_affine_offset_verifier.py /tmp/c046.json
```
