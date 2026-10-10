# R5 E9 — Sparse-Incomparability High-Girth Global-Pivot Barrier

Date: 2026-09-28

Status:
`SOURCE_BOUND_HIGH_GIRTH_ANTI_LOOP_BARRIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`
- `research/R5_E9_TWO_PATH_SINGLE_VARIABLE_PROJECTION_DP_ANTI_LOOP_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_INCIDENCE_C4_FREE_GLOBAL_PIVOT_BARRIER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_sparse_incomparability_high_girth_pivot_barrier.py`

Scientific firewall:

```text
THIS IS A UNIVERSAL-COVERAGE BARRIER FOR BOUNDED-LENGTH SOURCE-CYCLE PIVOTS.
IT DOES NOT PROVE P != NP.
IT DOES NOT RULE OUT PIVOTS USING LONG CYCLES, GLOBAL CYCLE SPACE, OR OTHER NONLOCAL STRUCTURE.
THE SPARSE-INCOMPARABILITY COMPLEXITY THEOREM IS SOURCE-BOUND PRIOR ART.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Signed 3SAT as one fixed Boolean CSP template

Let the fixed relational signature be

```text
tau = { R_s : s in {0,1}^3 },
```

with eight ternary relation symbols, one for each clause sign pattern.

Let the fixed target structure `T_3SAT` have universe

```text
{0,1}.
```

For a sign pattern `s=(s1,s2,s3)`, interpret `si=0` as the positive literal `xi` and `si=1` as the negative literal `NOT xi`.  The unique falsifying Boolean value for coordinate `i` is therefore

```text
f_i(s) = s_i,
```

because a positive literal is false at `0`, while a negative literal is false at `1`.

Define

```text
R_s(T_3SAT) = {0,1}^3 \ {s}.
```

Thus every `R_s` contains exactly seven tuples.

Given a signed 3CNF formula `F`, construct a `tau`-structure `S_F` whose universe is the variables of `F`.  For every clause

```text
(l_1(v_1) OR l_2(v_2) OR l_3(v_3))
```

with sign pattern `s`, place the ordered tuple

```text
(v_1,v_2,v_3)
```

in `R_s(S_F)`.

Then a map

```text
h : S_F -> T_3SAT
```

is a homomorphism iff `h` is a satisfying Boolean assignment of `F`.

Hence signed exact-3SAT is exactly the fixed finite-domain CSP

```text
CSP(T_3SAT).
```

The target has size two.

## 2. Imported theorem: deterministic Sparse Incomparability

Gábor Kun proves the following algorithmic form of the Sparse Incomparability Lemma for finite relational structures:

> For every finite relational type `tau`, every positive integers `t,k`, and every finite `tau`-structure `S`, one can construct in polynomial time a `tau`-structure `S'` with girth `>k` such that, for every `tau`-structure `T` with `|T|<t`,
>
> `S -> T  iff  S' -> T`.

Source:

- Gábor Kun, *Constraints, MMSNP and expander relational structures*, Combinatorica 33 (2013), arXiv:0706.1701, DOI `10.1007/s00493-013-2405-4`.
- Theorem 1 / Theorem 2 depending on edition numbering; the arXiv v2 HTML statement is the deterministic polynomial construction with girth `>k` and preservation of all targets of size `<t`.

The paper defines a relational cycle as an alternating sequence of distinct points and distinct relational tuples

```text
x_0, r_1, x_1, r_2, ..., r_m, x_m=x_0,
```

where consecutive tuples share the displayed point; a repeated coordinate inside one relational tuple is a degenerate cycle of length one.

No JANUS novelty claim is made for the Sparse Incomparability theorem.

## 3. Specialize the theorem to signed 3SAT

Fix any positive integer `g`.

Apply Sparse Incomparability with

```text
tau = the eight signed-clause ternary relations,
t = 3,
k = g.
```

Since

```text
|T_3SAT| = 2 < 3,
```

for every signed 3CNF source structure `S_F` the algorithm constructs in polynomial time a structure `S'_F` satisfying

```text
girth(S'_F) > g
```

and

```text
S_F -> T_3SAT
iff
S'_F -> T_3SAT.
```

Because `S'_F` uses exactly the same eight ternary relation symbols, it is again a signed exact-3SAT instance under the encoding of Section 1.  If `g>=1`, the absence of degenerate relational 1-cycles also ensures that every produced constraint tuple has three distinct source variables.

### Theorem HG-1 — arbitrarily high-girth hard signed-3SAT sources

For every fixed constant `g`, signed exact-3SAT restricted to source relational structures of girth greater than `g` is NP-complete.

### Proof

Membership in NP is unchanged.  NP-hardness follows by composing the ordinary signed exact-3SAT instance-to-structure encoding with Kun's deterministic polynomial transformation.  The transformation preserves homomorphism into the fixed two-element target `T_3SAT`, hence preserves satisfiability exactly. QED.

## 4. Relation to the ordinary variable-constraint incidence graph

For a nondegenerate source structure, replace each relational tuple by one constraint node and join it to its three coordinate variables.  This is the ordinary bipartite variable-constraint incidence graph (with coordinate incidences retained if one works as a multigraph).

A relational cycle of length `m` corresponds to an alternating incidence cycle of length `2m`:

```text
variable - constraint - variable - ... - constraint - variable.
```

Therefore

```text
girth_relational(S) > g
```

implies that the source incidence representation has no alternating cycle of length at most `2g`.

Since `g` is an arbitrary fixed constant, HG-1 supplies NP-hard source instances avoiding every prescribed finite collection of bounded-length source alternating cycles.

This strictly strengthens the earlier C4 barrier:

```text
C4-free hard source
```

becomes

```text
for every fixed L, hard sources with no source alternating cycle of length <= L.
```

## 5. Universal-pivot anti-loop theorem

Consider any proposed universal two-path `GLOBAL_PIVOT` whose progress certificate requires the source instance to contain one of finitely many alternating source-cycle motifs of bounded length.

Let `L` be the maximum source-incidence cycle length in that finite catalogue and choose

```text
g > L/2.
```

By HG-1 there are NP-hard signed-3SAT images whose source relational girth is greater than `g`, hence whose source incidence graph contains none of those cycles.

Therefore:

### Theorem HG-2 — bounded-cycle mandatory trigger barrier

No universal polynomial coverage proof for arbitrary signed 3SAT can use existence of a source alternating cycle from any fixed bounded-length catalogue as its mandatory progress trigger.

This includes, as special cases:

```text
mandatory C4 pivot,
mandatory C6 pivot,
mandatory C8 pivot,
mandatory cycle <= L pivot for any fixed constant L,
any finite catalogue consisting solely of bounded source-cycle motifs.
```

This is a coverage barrier, not a lower bound on SAT algorithms.

## 6. What HG-2 does NOT kill

The following remain admissible:

1. an alternating cycle whose required length is allowed to grow with the input;
2. a global cycle-space / parity / syndrome object that exists without a short cycle;
3. a contraction on a tree-like or acyclic cross-layer region with a proved exact message algebra;
4. a nonlocal witness-dominance certificate;
5. a representation change that manufactures useful auxiliary structure while preserving semantics and proves a strict polynomially bounded progress measure;
6. a global invariant that acts on arbitrarily high-girth source images.

The theorem also does not claim that the fully expanded XOR/AND auxiliary overlay itself has the same graph girth as the source.  Its universal conclusion is deliberately source-scoped: a proof cannot require a bounded source-cycle motif to exist.

## 7. Interaction with the single-variable DP anti-loop

We now have two orthogonal exact exclusions:

```text
ONE COMPLETE VARIABLE-PATH PROJECTION
= classical Davis-Putnam elimination
= not a new GLOBAL_PIVOT
```

and

```text
FIXED BOUNDED-LENGTH SOURCE ALTERNATING CYCLE
= not universally available, even on an NP-hard source class.
```

So the next primary object must be simultaneously:

```text
GENUINELY MULTI-PATH / CROSS-LAYER
AND
HIGH-GIRTH-SAFE
AND
NON-DP
AND
POLYNOMIALLY REPRESENTED
AND
WITNESS-RECONSTRUCTIBLE.
```

## 8. Sharpened primary gate

Freeze candidate gate:

```text
R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1
```

A PASS requires all of:

```text
SOUND
COMPLETE
TERMINATES
POLYNOMIAL CONSTRUCTION
POLYNOMIAL SOLVE / CONTRACTION COST
POLYNOMIAL WITNESS LIFT
STRICTLY DECREASING POLYNOMIALLY BOUNDED JOINT CROSS-LAYER POTENTIAL
UNIVERSAL COVERAGE INCLUDING ARBITRARILY HIGH SOURCE-GIRTH IMAGES
```

The following do not count as a PASS:

- one-variable-path projection / bounded variable elimination;
- requiring C4, C6, C8, or any source cycle of bounded constant length;
- a finite catalogue of bounded source-cycle reducers;
- storing an exponential boundary truth table under a compact name;
- adding selectors that merely preserve the eliminated branch choice;
- using affine-layer or product-layer width separately without a joint composition theorem;
- claiming polynomiality from a polynomial verifier without a polynomial constructor.

## 9. Immediate research consequence

The minimal plausible universal target is no longer

```text
find a short alternating cycle and contract it.
```

It is instead one of:

```text
(A) a high-girth-safe global syndrome / cycle-space contraction,
(B) a tree/forest message algebra whose summaries compose without exponential state growth,
(C) a nonlocal dominance pivot discoverable on sparse high-girth images,
(D) a representation-level progress theorem that applies independently of bounded source cycles.
```

This is a materially narrower primary bottleneck than the previous `NONLOCAL_RANK1_CROSS_LAYER_GLOBAL_PIVOT_GATE_V1`.

## 10. Ceiling

```text
SIGNED 3SAT AS A FIXED TWO-ELEMENT EIGHT-RELATION CSP
= EXACT

DETERMINISTIC POLY-TIME SPARSE INCOMPARABILITY
= SOURCE-BOUND PRIOR ART

FOR EVERY FIXED g:
NP-HARD SIGNED-3SAT SOURCES WITH RELATIONAL GIRTH > g
= PROVED BY SPECIALIZATION

ANY MANDATORY FIXED BOUNDED-LENGTH SOURCE-CYCLE PIVOT
= CLOSED AS UNIVERSAL COVERAGE STRATEGY

R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1
= OPEN <<< PRIMARY MICRO-GAP

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```