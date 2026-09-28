# R5 E9 — Two-Clause One-Coherence Cross-Layer Pivot Equals Davis–Putnam

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_MICROBLOCK_CLASSIFICATION__LOCAL_GLOBAL_PIVOT_CANDIDATE_COLLAPSES_TO_DP__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS CLASSIFIES THE SMALLEST NONLOCAL TWO-PATH XOR/AND OVERLAY BLOCK.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parent:
- `research/R5_E9_TWO_PATH_XOR_AND_OVERLAY_NORMAL_FORM_2026-09-23_v1.0.md`

Checker:
- `experiments/r5_e9_two_clause_one_coherence_dp_exactness.py`

## 1. Block

In the exact two-path overlay normal form, let two clause gadgets contain occurrences `a` and `b` of the same original Boolean variable. Let the other two negated-literal occurrence variables in the first clause be `p,q`, and in the second clause `r,s`.

A clause gadget projects exactly to

```text
NAND3(a,p,q) := NOT(a p q).
```

Occurrence coherence gives

```text
b = a XOR c,
```

where `c=0` when the two original literal occurrences have the same polarity and `c=1` when their polarities are opposite.

Thus the exact block relation after eliminating the occurrence pair is

```text
R_c(p,q,r,s)
:= exists a in {0,1}:
     NAND3(a,p,q)
  AND NAND3(a XOR c,r,s).
```

## 2. Same-polarity theorem

### Theorem OCP-1

For `c=0`,

```text
R_0 = TRUE4.
```

Proof. Choose `a=0`. Then both NAND3 factors are true regardless of `p,q,r,s`. QED.

In ordinary CNF language, a variable that occurs in the same polarity in both involved clauses can be assigned that polarity so that both clauses are satisfied; after existentially eliminating that isolated two-clause block, no residual constraint remains.

## 3. Opposite-polarity theorem

### Theorem OCP-2

For `c=1`,

```text
R_1(p,q,r,s) = NAND4(p,q,r,s).
```

Equivalently,

```text
R_1 is false iff p=q=r=s=1.
```

Proof.

If `p=q=1`, the first NAND3 factor forces `a=0`. Then `a XOR 1=1`, so the second factor requires `(r,s)!=(1,1)`.

Symmetrically, if `r=s=1`, the second factor forces `a=1`, and the first factor requires `(p,q)!=(1,1)`.

Therefore the only impossible boundary tuple is `1111`.

Conversely, if `(p,q)!=(1,1)`, choose `a=1`; the first factor is true, while the second has first coordinate zero and is automatically true. If `(p,q)=(1,1)`, the boundary assumption gives `(r,s)!=(1,1)`; choose `a=0`. QED.

## 4. Identification with Davis–Putnam resolution

Return to ordinary literals. Suppose the two clauses are

```text
(x OR A OR B)
(NOT x OR C OR D).
```

Their negated boundary occurrence variables are exactly `p=NOT A`, `q=NOT B`, `r=NOT C`, `s=NOT D`.

The projected relation

```text
NAND4(p,q,r,s)
```

is therefore exactly

```text
A OR B OR C OR D,
```

the ordinary Davis–Putnam resolvent on `x`.

Hence the smallest genuinely cross-layer block consisting of two clause-product paths linked by one XOR-coherence edge has no new contraction algebra:

```text
same polarity     -> pure-variable deletion / TRUE,
opposite polarity -> one ordinary DP resolvent.
```

## 5. Algorithmic consequence

A GLOBAL_PIVOT that acts only on one coherence edge and its two incident clause-product paths cannot be the missing JANUS universal contraction. Its exact projection is already classical variable elimination.

Repeated unrestricted use inherits the known DP fill-in problem: eliminating one variable can enlarge clause width and later elimination can generate many resolvents. The theorem is not a lower bound against other representations; it only closes this microblock as a new representation-changing pivot.

Therefore an admissible new GLOBAL_PIVOT must use genuinely larger cross-layer structure, for example multiple coherence links / an alternating cycle / another nonlocal certificate, and must prove a polynomially bounded global potential rather than locally reproducing resolvents.

## 6. Prior-art boundary

Davis–Putnam variable elimination by resolving clauses of opposite polarity is classical. Modern SAT preprocessing literature continues to describe variable elimination as Davis–Putnam resolution. The JANUS-derived content here is the exact identification of the first two-path XOR/AND cross-layer microblock with that classical operation.

No novelty or priority claim is made.

## 7. Ceiling

```text
ONE COHERENCE EDGE + TWO CLAUSE PRODUCT PATHS
= EXACTLY CLASSIFIED

SAME POLARITY
= TRUE PROJECTION

OPPOSITE POLARITY
= NAND4 / ORDINARY 4-LITERAL RESOLVENT

ONE-COHERENCE GLOBAL_PIVOT AS NEW CONTRACTION
= CLOSED / DP REPACKAGING

NEXT ADMISSIBLE SCALE
= MULTI-COHERENCE / ALTERNATING CROSS-LAYER BLOCK

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
