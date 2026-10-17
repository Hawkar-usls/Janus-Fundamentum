# R5 E9 — Two-edge 2-lift 3-cut-irreducible linear-nullity family

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_HOSTILE_FAMILY__LOW_NULLITY_PRIME_CORE_HYPOTHESIS_FALSIFIED__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS FALSIFIES THE HYPOTHESIS THAT EXHAUSTING ALL GENUINE <=3-EDGE CUTS
FORCES O(log n) RATIONAL NULLITY ON THE LINEAR-CUBIC EXACT-ONE CARRIER.
IT DOES NOT PROVIDE A UNIVERSAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_TRADE_FREE_UNIQUE_MODEL_DISSOCIATED_NULLITY_GATE_2026-09-27_v1.0.md`
- `research/R5_E9_THREE_EDGE_CUT_BOUNDARY_ALGEBRA_2026-09-28_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_two_edge_2lift_3cut_irreducible_linear_nullity.py`

## 1. Seed

Use the frozen connected linear-cubic `18_3` SAT control with row triples

```text
{0,15,17}
{1,4,12}
{2,10,14}
{3,4,11}
{4,8,9}
{3,5,13}
{1,6,10}
{2,7,15}
{1,8,14}
{3,7,9}
{9,10,16}
{7,11,13}
{5,12,17}
{0,13,16}
{0,12,14}
{5,8,15}
{2,6,16}
{6,11,17}.
```

Let its `18 x 18` incidence matrix be `A_0`. Exact elimination gives

```text
rank_Q(A_0)=16,
nu_Q(A_0)=2.
```

The checker exhausts all edge cuts of size at most three in its 36-vertex cubic Levi graph and verifies:

```text
no cut of size 1 or 2,
every disconnecting 3-edge set is a vertex star,
nontrivial <=3-edge cuts = 0.
```

Thus the seed is already in the current genuine-3-cut-irreducible regime.

It is unbalanced. One explicit chordless strong odd cycle has Levi length 18:

```text
c3-r5-c5-r12-c17-r0-c0-r13-c16-r10-c10-r2-c2-r7-c7-r11-c11-r3-c3.
```

Its shore size is nine, hence it is a forbidden odd square submatrix / strong odd cycle for balanced set partitioning.

## 2. Two-edge signing and frustration index

Let `G` be any connected cubic graph satisfying

```text
no edge cut of size <3,
every 3-edge cut is a vertex star.
```

Choose two nonincident edges `e,f` and make exactly those two edges negative.

### Lemma TEL-1 — frustration index exactly two

The signing has frustration index exactly two.

Proof. It is at most two by construction. If switching could leave zero negative edges, then `{e,f}` would itself be an edge cut, contradicting the absence of 2-edge cuts.

If switching could leave exactly one negative edge `g`, then the switching cut would be

```text
{e,f} triangle {g}.
```

If `g` equals `e` or `f`, this is a singleton cut, impossible. Otherwise it is a 3-edge cut containing the nonincident edges `e,f`. But every 3-edge cut is a vertex star, whose three edges are pairwise incident at one vertex. Contradiction.

Therefore the minimum is two. QED.

In particular the signing is unbalanced, so its 2-lift is connected. This agrees with the standard signed-graph/2-lift equivalence: a connected base signing is balanced iff its 2-lift has two connected components.

## 3. Small-cut preservation theorem

Let `H` be the 2-lift of `G` from any signing of frustration index at least two.

### Theorem TEL-2

`H` has no nontrivial edge cut of size at most three. Its only 3-edge cuts are vertex stars.

### Proof

Take any vertex subset `S` of the lift. For each base vertex `v`, let

```text
t(v) = |S intersect pi^{-1}(v)| in {0,1,2}.
```

Partition the base vertices into

```text
V0={v:t(v)=0},
V1={v:t(v)=1},
V2={v:t(v)=2}.
```

For one base edge `uv`, its two lifted edges contribute to the cut `delta_H(S)` as follows:

```text
(t(u),t(v)) = (0,0) or (2,2): 0;
(0,2) or (2,0):               2;
exactly one endpoint in V1:    1;
both endpoints in V1:          0 or 2.
```

Hence

```text
|delta_H(S)| >= |delta_G(V1)| + 2 |E_G(V0,V2)|.
```

Assume `|delta_H(S)|<=3`.

If `V1` is empty, both `V0,V2` cannot be nonempty: connectedness and the absence of edge cuts below three would give at least three `V0-V2` base edges, contributing at least six lifted cut edges. Thus `S` is empty or all of `V(H)`.

If `V1` is a nonempty proper subset, then `|delta_G(V1)|<=3`. By the base hypothesis it equals three and one shore of this base cut is a single vertex. If `V1={v}`, connectedness of `G-v` (forced by the same no-nontrivial-3-cut hypothesis) and the absence of `V0-V2` edges imply that all other fibers are simultaneously in `V0` or simultaneously in `V2`; `S` is therefore one lifted vertex or the complement of one lifted vertex, giving a trivial vertex-star cut.

The remaining possibility is `V1=V(G)-{v}`. To keep the lifted cut at three, every edge internal to `V1` must contribute zero. Thus the selected sheet labels on `G-v` switch every internal edge positive. Consequently after switching, every negative edge is incident with `v`. Switching `v` itself replaces that negative subset of its three-edge star by its complement, so the whole signing would have frustration index at most one. This contradicts the assumed frustration index at least two.

Finally, if `V1=V(G)`, `S` chooses exactly one lift vertex over every base vertex. Its cut size is exactly twice the number of negative edges remaining after the corresponding vertex switching. Therefore

```text
|delta_H(S)| >= 2 * frustration_index >= 4.
```

No other case exists. Hence every cut of size at most three is trivial. QED.

This is the structural reason the present construction avoids the small-cut defect of the earlier one-edge-twist amplifier: one negative edge has frustration index one and creates a two-edge sheet cut, whereas two nonincident negative edges in the present prime base have frustration index two.

## 4. Rational-nullity transfer

Let `A` be the square bipartite incidence matrix of the current cubic carrier and let

```text
k = nu_Q(A).
```

Choose two nonincident incidence edges `(r1,c1),(r2,c2)` and sign them negative. The signed biadjacency matrix is

```text
A_sigma
= A - 2 e_r1 e_c1^T - 2 e_r2 e_c2^T.
```

The perturbation has rank at most two, hence

```text
nu_Q(A_sigma) >= k-2.
```

For the 2-lift, after the rational fiber sum/difference change of basis, the lifted biadjacency matrix block-diagonalizes as

```text
A_lift ~ A direct_sum A_sigma.
```

Therefore

```text
k_next
= nu_Q(A_lift)
= k + nu_Q(A_sigma)
>= 2k-2.
```

This uses the standard 2-lift spectral/block decomposition; the proof is also immediate by multiplying the block matrix `[[P,N],[N,P]]` by the invertible sum/difference basis.

## 5. Strictly growing seed step

On `A_0`, choose the two nonincident incidences

```text
(row 0, column 15),
(row 1, column 1).
```

Both lie outside the distinguished 18-cycle above. Exact fraction-free elimination gives for the signed matrix

```text
rank_Q(A_0^sigma)=17,
nu_Q(A_0^sigma)=1.
```

Hence the first 2-lift `A_1` has

```text
n_1=36,
nu_Q(A_1)=2+1=3.
```

The checker independently verifies the complete first-lift 3-edge-cut census: no nontrivial cut of size at most three exists.

Because both negative edges lie outside the distinguished strong odd cycle, that cycle lifts to two chordless copies of the same length 18. Choose one as the distinguished cycle for the next stage. Thus unbalancedness survives.

A base Exact-One witness also lifts fiber-constantly through every graph cover, so every member remains SAT.

## 6. Infinite recursion

For every stage `t>=1`, choose deterministically the lexicographically first pair of nonincident incidence edges lying outside the distinguished 18-cycle and make exactly them negative.

Such a pair always exists: a cubic bipartite graph at stage `t` has `3 n_t` incidence edges, only 18 lie on the distinguished cycle, and a pairwise-intersecting edge family in a simple bipartite graph is a star of size at most three. Therefore the much larger outside-edge set contains two nonincident edges.

TEL-1 gives frustration index two. TEL-2 preserves genuine-3-cut irreducibility. The selected edges are outside the distinguished cycle, so one lifted copy of that cycle persists. Cubicity and bipartiteness are preserved by covers; linearity is preserved because a graph cover cannot create a 4-cycle below the girth of the base Levi graph. SAT is preserved by the fiber-constant witness.

For nullity, Section 4 gives

```text
k_(t+1) >= 2 k_t - 2.
```

Since `k_1=3`, putting `h_t=k_t-2` gives

```text
h_(t+1) >= 2 h_t,
h_1=1.
```

Thus

```text
k_t >= 2 + 2^(t-1).
```

Since

```text
n_t = 18 * 2^t,
```

we obtain the linear lower bound

```text
boxed(k_t >= 2 + n_t/36).
```

## 7. Main consequence

There is an explicit recursively constructible infinite family of Positive Exact-One carriers satisfying simultaneously

```text
connected,
linear,
cubic / square,
SAT,
unbalanced with a persistent strong odd cycle,
no nontrivial edge cut of size <=3,
rational nullity >= 2 + n/36.
```

Therefore the proposed residual theorem

```text
Genuine-3-cut-irreducible
=> nu_Q(A)=O(log n)
```

is false, even on satisfiable instances that remain inside the current unbalanced residual.

Consequently the existing `2^k poly(n)` rational-kernel router cannot become universal merely by exhausting genuine <=3-edge cuts and then invoking a low-nullity bound.

Freeze:

```text
LOW_NULLITY_AFTER_3CUT_DECOMPOSITION
= FALSIFIED BY ARBITRARY-SIZE FAMILY.
```

The current universal obligation remains the unbalanced strong-odd-cycle/global-semantic contraction itself, not a nullity bound.

## 8. Prior-art boundary

The equivalence between signings and graph 2-lifts, connectedness versus balanced signings, switching equivalence, frustration index, and the old/new spectral block decomposition are standard signed-graph/2-lift facts. An open-access reference is F. Martin, *Frustration and isoperimetric inequalities for signed graphs*, Discrete Applied Mathematics 217 (2017), which explicitly records the signing/2-lift correspondence and spectral union.

The specific TEL-1/TEL-2 small-cut preservation argument, its application to the frozen `18_3` seed, and the nullity-amplifying recursion above are the JANUS-derived content. No novelty claim beyond the source audit is made here.

## 9. Ceiling

```text
TWO NONINCIDENT NEGATIVE EDGES ON PRIME CUBIC BASE
=> FRUSTRATION INDEX 2
= PROVED

FRUSTRATION >=2 2-LIFT OF <=3-CUT-PRIME CUBIC BASE
=> <=3-CUT-PRIME LIFT
= PROVED

FIRST LIFT
n=36, nu_Q=3
= EXACT / CHECKED

RECURSIVE NULLITY
nu_Q >= 2+n/36
= PROVED

PERSISTENT STRONG ODD CYCLE
= PROVED BY POSITIVE-CYCLE LIFT

SAT PRESERVATION
= FIBER-CONSTANT WITNESS

LOW-NULLITY PRIME-CORE ROUTE
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
