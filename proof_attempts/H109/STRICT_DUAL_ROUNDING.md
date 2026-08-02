# H109 — bounded-norm strict dual rounding

## Status

`FORMALIZING`, reproducibility `R2`.

This is a conditional perturbation lemma. It does not derive the required
multiplier bound from H097's original assumptions.

## Fixed dual

For a graph with `m` edges, use the H093 dual slack

\[
S(t,y)=tI+\sum_{e=1}^{m}y_eA_e-J,
\]

where `A_e` has ones in the two symmetric off-diagonal positions of edge `e`.
Each `A_e` has operator norm one, as does `I`.

Assume a real witness satisfies

\[
S(t,y)\succeq\delta I,
\qquad
t\le M-\gamma,
\]

and

\[
|t|,|y_e|\le2^B.
\]

## Dyadic rounding

Round `t` and every `y_e` to the nearest multiple of a common mesh `epsilon`.
Let the rounded coordinates be `t'` and `y'_e`. Then

\[
|t'-t|\le\epsilon,
\qquad
|y'_e-y_e|\le\epsilon.
\]

The slack perturbation is

\[
\Delta S=(t'-t)I+\sum_e(y'_e-y_e)A_e.
\]

By the triangle inequality for operator norm,

\[
\|\Delta S\|_{op}
\le(m+1)\epsilon.
\]

Choose

\[
\epsilon
\le
\min\left(\frac{\gamma}{2},
          \frac{\delta}{2(m+1)}\right).
\]

Then Weyl's inequality gives

\[
S(t',y')\succeq\frac\delta2 I,
\]

and

\[
t'\le M-\frac\gamma2.
\]

Thus the rounded rational point remains strictly dual feasible and preserves a
constant fraction of the objective gap.

## Bit length

Take `epsilon=2^{-q}` with

\[
q=O\left(
\log(m+1)+\log(1/\delta)+\log(1/\gamma)
\right).
\]

Because every original coordinate has magnitude at most `2^B`, each rounded
numerator has

\[
O(B+q)
\]

bits and all denominators have `q+1` bits. The complete dual vector and rational
slack matrix therefore have polynomial total encoding length in the stated
parameters.

H108 then supplies a polynomial-size exact rational LDL certificate for the
rounded slack.

## What remains open

H097 did not assume an explicit bound `B` on the multiplier magnitude. C014 has
not proved that inverse-polynomial Slater and objective margins alone imply such
a bound for every graph dual.

The remaining wall is therefore precise:

> derive a polynomial-bit multiplier bound from the original H097 promises, or
> construct a well-conditioned family for which every useful dual witness has
> superpolynomial coordinate bit length.

## Claim boundary

The lemma proves only rounding under an explicit norm promise. It does not
solve an SDP, find the real witness, or establish the promise automatically.
