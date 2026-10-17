# R5 E9 — Paley(19) exact minimum AF3 cover rank six

Date: 2026-10-01

Status:
`JANUS_EXACT_PALEY19_MINIMUM_COVER_RANK6__INDEPENDENT_EXHAUSTIVE_REPLAY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_RANK2_COVER_COMPLETENESS_PALEY19_FALSIFIER_2026-09-30_v1.0.md`
- `research/R5_E9_PALEY19_GRADIENT_KERNEL_POST_RKPR_CONTROL_2026-09-30_v1.0.md`

Executable checker:
- `experiments/r5_e9_affine_f3_paley19_exact_minimum_cover_rank6.cpp`

Scientific ceiling:

```text
THIS NOTE DETERMINES THE EXACT MINIMUM NORMAL RANK OF AN AF3
COORDINATE-HYPERPLANE COVER FOR THE FROZEN PALEY(19) SOURCE.
IT DOES NOT GIVE A UNIVERSAL SAT ALGORITHM.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen source and affine chart

Use the frozen Paley tournament on `Z_19` with quadratic residues

```text
Q={1,4,5,6,7,9,11,16,17}
```

and the same nine cyclic-triangle translation orbits as the existing Paley(19) control. The resulting `171 x 171` Positive-1-in-3 source has

```text
rank_F3(A)=152,
dim ker_F3(A)=19,
A r = 1 consistent,
171 distinct projective coordinate normals,
Exact-One UNSAT.
```

The old rank-two falsifier proved only

```text
minimum cover normal rank >= 3.
```

This note closes that gap exactly.

## 2. Multiplicative-character particular solution

Partition the nonzero quadratic residues into the three cosets

```text
H  ={1,7,11}
4H ={4,6,9}
5H ={5,16,17}.
```

For an oriented Paley arc `u->v`, write `delta=v-u in Q` and define

```text
r0(delta)=2 on H,
r0(delta)=1 on 4H,
r0(delta)=0 on 5H.
```

Equivalently, because `4` generates the order-nine group `Q`,

```text
r0(4^k)=2-k mod 3.
```

Exact substitution in all 171 selected cyclic-triangle equations gives

```text
A r0 = 1 over F3.
```

The ternary kernel is exactly the constant-plus-gradient space

```text
ker_F3(A)={ c + p(v)-p(u) : c in F3, p:Z_19->F3 }.
```

Hence every coordinate-zero hyperplane attached to an oriented arc `u->v` has the gain-graph form

```text
c+p(v)-p(u)=t_uv,
t_uv=-r0(v-u).
```

## 3. Rank formula for a selected arc family

For a selected tournament-edge set `E`, represent its normal rows as

```text
N_E=[ 1 | D_E ],
```

where `D_E` is the oriented vertex-edge incidence matrix over `F3`.

If the active underlying graph has `kappa` connected components on `s` active vertices, then

```text
rank(D_E)=s-kappa.
```

Moreover

```text
rank(N_E)=rank(D_E)+epsilon,
epsilon in {0,1}.
```

The case `epsilon=0` is equivalent to the existence of a potential `h` satisfying

```text
h(v)-h(u)=1
```

on every selected oriented arc. Call this the balanced case.

## 4. Why rank at most five reduces to at most six vertices

Fix `c`. Avoiding the selected hyperplanes is the finite-domain CSP

```text
c+p(v)-p(u) != t_uv
```

on each selected arc.

A connected component on at most three vertices is always avoidable over `F3`, so a component that kills a whole fixed `c`-slice needs at least four vertices and therefore incidence rank at least three.

If a family of total normal rank at most five covered all three `c`-slices, two different connected components could not be responsible for different slices: two unsatisfiable components would already contribute incidence rank at least `3+3=6`. Therefore one connected component must kill all three slices.

For that component,

```text
rank(N_E)<=5
```

implies at most six active vertices. If there are six active vertices then `rank(D_E)=5`, so rank at most five forces the balanced case `epsilon=0`.

Thus completeness of the lower-bound search reduces exactly to:

1. all induced carriers on at most five vertices;
2. all connected balanced six-vertex carriers.

## 5. Exact exhaustive rejection for at most five vertices

Monotonicity allows checking only induced five-vertex carriers: if a smaller edge family covered all slices, then the full induced tournament carrier on any five-vertex superset would also cover them.

The checker exhausts

```text
C(19,5)=11628
```

five-vertex sets. For each set and each `c in F3`, it evaluates the union of the selected affine hyperplanes on the normalized potential cube with one potential fixed to zero.

Result:

```text
five-vertex full three-slice covers = 0.
```

Hence no rank-at-most-five cover can be supported on at most five vertices.

## 6. Exact exhaustive rejection for six vertices

For a six-vertex set `W`, every rank-five carrier must be balanced. Normalize one potential value `h(w0)=0`. There are `3^5=243` normalized potentials.

For each normalized `h`, take the maximal balanced edge system

```text
E_h={u->v in T[W] : h(v)-h(u)=1}.
```

Any balanced rank-five subfamily is contained in one such `E_h`. If the maximal `E_h` fails to cover a slice, no subfamily can cover it. A rank-five subfamily must also be connected, so it is sufficient and complete to retain only connected `E_h`.

The independent replay exhausts

```text
C(19,6)=27132
```

six-vertex sets and obtains

```text
connected balanced normalized candidates = 2,842,419.
```

This is intentionally a broader complete candidate set than an earlier implementation that applied additional safe pruning before counting candidates.

Exact result:

```text
connected balanced candidates covering c=0 = 0,
connected balanced candidates covering c=1 = 0,
connected balanced candidates covering c=2 = 0.
```

In particular there is no rank-five full cover.

Therefore

```text
minimum cover normal rank >= 6.
```

## 7. Explicit rank-six cover

Let

```text
W={0,1,2,4,9,13}.
```

Use three complete `K4` obstructions, one per `c`-slice:

```text
c=0: K4={0,4,9,13}, gauge s=(0,2,2,1)
c=1: K4={1,2,4,9},  gauge s=(0,0,1,0)
c=2: K4={0,1,9,13}, gauge s=(0,2,0,0)
```

where the gauge tuple is listed in the displayed vertex order.

For every oriented edge `u->v` inside the corresponding `K4`, exact checking gives

```text
t_uv-c=s(v)-s(u).
```

After the gauge shift `q=p-s`, avoiding all six hyperplanes of that `K4` becomes

```text
q(v) != q(u)
```

on every edge of `K4`, i.e. a proper three-colouring of `K4`, impossible.

Thus the three `K4`s kill the three `c`-slices. Their union contains exactly

```text
13 distinct tournament arcs.
```

The underlying graph is connected on six vertices, so

```text
rank(D_E)=5.
```

The union contains the directed cycle

```text
0->4->9->13->0.
```

If the constant column were in the incidence-column span, a potential `h` with `h(v)-h(u)=1` on every selected arc would exist. Summing around that directed four-cycle would give

```text
0 = 4 = 1 mod 3,
```

contradiction. Therefore the constant column is independent and

```text
rank(N_E)=6.
```

Hence

```text
minimum cover normal rank <= 6.
```

Combining with the exhaustive lower bound gives the exact theorem

```text
rho_min(Paley19)=6.
```

## 8. Independent replay note

The first discovery pass reported a smaller count of post-pruning balanced six-vertex systems. The checker attached to this note deliberately avoids relying on that pruning. It enumerates the larger complete set of all connected maximal balanced systems and still finds zero one-slice covers. This provides an implementation-independent lower-bound replay rather than attempting to reproduce an incidental intermediate count.

## 9. Structural interpretation

The rank-six witness is not an arbitrary six-dimensional cover. It is the union of

```text
three character-shifted gain-K4 obstructions
```

supported on six Paley vertices, with offsets controlled by the order-three multiplicative character of the quadratic-residue group.

This is the first source-specific motif to test beyond fixed-rank enumeration.

## 10. Next constructive gate

Freeze

```text
R5_E9_PALEY_CHARACTER_GAIN_K4_FAMILY_GATE_V1
```

Do not search rank seven or rank eight by brute force. Instead:

1. for Paley tournaments over fields with `q = 7 mod 12`, construct the canonical order-three character on the quadratic-residue subgroup;
2. determine exactly when the selected cyclic-triangle source admits a translation-invariant particular solution whose offsets are that character;
3. search for three character-shifted gain-`K4` obstructions by algebraic equations in vertex differences rather than subset enumeration;
4. test the same motif on the frozen prime SAT/UNSAT lift towers;
5. if a family theorem holds, give a polynomial motif-recognition/construction algorithm and exact witness reconstruction;
6. if it fails, extract the first exact field/source obstruction and stop that generalization.

A character exists on the quadratic-residue subgroup whenever its order is divisible by three. For Paley tournaments this arithmetic condition is compatible with `q=3 mod 4` precisely on the congruence class `q=7 mod 12`; existence of the character alone is not yet a theorem that the JANUS source construction or the three-`K4` cover extends.

## 11. Ceiling

```text
PALEY19 minimum AF3 cover normal rank = 6
rank<=5 cover                           = IMPOSSIBLE
explicit rank6 cover                    = VERIFIED
systematic Paley-family motif           = OPEN
polynomial motif extractor              = NOT CONSTRUCTED
universal polynomial solver             = NOT PROVED
E8_D1                                   = EMPTY
P_VS_NP                                 = OPEN
```
