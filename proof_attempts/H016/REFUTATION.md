# H016 refutation — projection collapses to an ordinary DNNF lower bound

## Claim attacked

H016 asserts a polynomial-size d-DNNF `D(x,y)` such that existentially forgetting the auxiliary variables `y` yields the original CNF function `F(x)`.

## Lemma 1 — forgetting preserves DNNF size

Let `D` be a DNNF over variables `x ∪ y`. Replace every literal on a variable in `y` by `true`, and simplify constants. The resulting circuit computes `∃y D(x,y)`. No new gate is introduced. Every decomposable AND gate remains decomposable, because deleting variables cannot create an overlap between the variable sets of its children. Hence the result is a DNNF of size at most `|D|`.

Determinism may be lost, but H016 only needs the projected function to equal `F`; the resulting representation is still an ordinary DNNF.

## Lemma 2 — explicit CNFs with exponential DNNF lower bounds exist

Bova, Capelli, Mengel, and Slivovsky construct polynomial-size CNF families from expander graphs for which every equivalent DNNF has strongly exponential size. Related unconditional DNNF lower bounds are also recorded by Beame and Liew.

## Contradiction

Assume H016. Apply its compiler to one of the explicit hard CNFs `F_n`. It outputs a polynomial-size d-DNNF `D_n(x,y)` with

`∃y D_n(x,y) ≡ F_n(x)`.

By Lemma 1, forgetting `y` produces an ordinary DNNF for `F_n` of size at most `|D_n|`, hence polynomial. Lemma 2 says every DNNF for `F_n` is exponential. Contradiction.

Therefore H016 is false independently of the locality, scheduler, certificate, and runtime details of its proposed grammar.

## Boundary

This refutation does not say auxiliary variables are useless. They can exponentially reduce the size of a deterministic compilation before forgetting, as shown by Oztok and Darwiche. The decisive point is that forgetting from d-DNNF yields an ordinary DNNF, and the cited hard CNFs already require exponential size even in that more general target language.
