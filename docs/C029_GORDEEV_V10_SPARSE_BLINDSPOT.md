# C029 — Gordeev v10 Sparse-Assignment Blind Spot

**Status:** `CURRENT LEMMA 18 REFUTED / CLAIMED P≠NP PROOF REJECTED / P_VS_NP=OPEN`

## Source under audit

Lev Gordeev, *On P Versus NP*, arXiv:2005.00809v10, revised 12 May 2026.

The current paper defines:

```text
VA_0 = { assignments with at most binom(k,2) true edge variables }
```

and a positive-support acceptance relation

```text
X ⊢ D  iff  there exists E in X with E+ subseteq D+.
```

Thus `AC^n(X)` tests whether the positive part of some DNF term embeds in a
`(k-1)`-colorable negative test; the negative part of the term is not used in
this acceptability predicate.

Lemma 18 claims:

```text
DN(phi) ~_0 CLIQ_2  implies  AC^p(phi)=POS and AC^n(phi)=empty.
```

Here `~_0` means semantic agreement only on `VA_0`.

## Counterexample schema

Fix `k >= 4` and sufficiently large `m`. Put

```text
s = binom(k,2)
q = s + 1.
```

Choose a `(k-1)`-coloring `f` of `[m]` and choose a set `E` of exactly `q`
edges from its color graph `C_f`. This is possible for sufficiently large `m`.

Let

```text
psi = the exact monotone DNF for k-CLIQUE
T_E = AND_{e in E} v_e
phi = psi OR T_E.
```

### Premise holds

Every assignment in `VA_0` has at most `s` true edge variables. The added term
`T_E` requires `q=s+1` true variables, hence is false on every assignment in
`VA_0`. Therefore

```text
DN(phi) ~_0 CLIQ_2.
```

### Conclusion fails

The DNF expansion of `phi` contains the term

```text
D_E = <E, empty>.
```

Since `E subseteq C_f`, the paper's own positive-support acceptance relation
gives

```text
C_f in AC^n(phi).
```

Consequently

```text
AC^n(phi) != empty,
```

contradicting Lemma 18.

## Exact failure in the published proof

The proof assumes `C_f in AC^n(phi)` and obtains a DNF term `E` with
`E+ subseteq C_f`. It then defines an assignment making every edge of `E+`
true and says this assignment belongs to `VA_0`. That requires

```text
|E+| <= binom(k,2),
```

but no such bound follows from `E+ subseteq C_f` or from the definition of
`AC^n`. The counterexample chooses `|E+|=binom(k,2)+1`, precisely outside the
restricted assignment window while remaining visible to `AC^n`.

## Consequence chain

The paper uses Lemma 18 to transfer semantic agreement with CLIQUE into the
positive/negative acceptability assumptions required by its exponential circuit
lower bound. Since Lemma 18 is false, that transfer and the subsequent claimed
`NP not subseteq P/poly` conclusion are not established by the presented proof.

This does **not** prove `P=NP`; it rejects the claimed proof of `P!=NP`.

## Machine check

The checker instantiates

```text
k = 4
m = 256
s = 6
q = 7
```

and constructs seven edges inside a 3-colorable graph. It verifies the exact
cardinality and containment obligations.

```bash
python experiments/direct/janus_c029_gordeev_sparse_blindspot.py --self-test
```

## New JANUS gate — Restricted-Domain Semantic Transfer

A theorem may infer a global structural property from agreement on a restricted
assignment domain only if every structural witness used in the conclusion is
representable inside that restricted domain.

Formally, a transition of the shape

```text
agreement on assignments of weight <= s
    implies
absence of all accepted supports
```

must separately prove that every accepted support has size at most `s`.
Otherwise supports of size `s+1` are invisible to the premise but visible to the
conclusion.

## Claim boundary

```text
Gordeev v10 Lemma 18: refuted.
Claimed P!=NP proof: rejected as presented.
P_VS_NP: OPEN.
```
