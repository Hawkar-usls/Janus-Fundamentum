# JANUS TRUMP R44AH — original FPR uniform-rank barrier

R44AH strengthens R44AG to original fixed-point logic with rank (`FPR`), with a distinct operator `rk_p` for each fixed prime field. This repairs the fixed-field affine/GF(2) gap of plain FPC.

## Published theorem

Erich Grädel and Wied Pakusa, *Rank Logic is Dead, Long Live Rank Logic!*, Journal of Symbolic Logic, 2019; earlier CSL 2015 / arXiv:1503.05423.

Original FPR does not capture PTIME. In particular, the uniform rank problem with the field characteristic supplied as input is polynomial-time computable but not expressible in original FPR.

## Correct Legend classification

This is a barrier to `L1_UNIVERSAL_EXIT` **under preserved `L2_EXACT_SEMANTICS`**, not a failure of L2 soundness itself.

A sound original-FPR observer can return OPEN on a property it cannot express; doing so preserves L2 but forfeits L1 totality.

`L1_BARRIER_UNDER_L2 != L2_SOUNDNESS_FAILURE`.

`FIXED_PRIME_RANK_ACCESS != UNIFORM_RANK_ACCESS`.

`MANY_FIXED_FIELD_OPERATORS != ONE_UNIFORM_FIELD_PARAMETERIZED_OPERATOR`.

## Successor boundary

Grädel–Pakusa's `FPR*` uniform-rank language is not blocked merely by the original-FPR theorem.

R44AH therefore does not transfer its barrier to FPR*.

However, the later R44AI artifact independently imports the stronger Dawar–Grädel–Lichter theorem for fixed-point logic with all finite-field linear-algebraic operators. Thus the historical “audit FPR* separately” instruction here is superseded by R44AI, not by extrapolation from R44AH.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
