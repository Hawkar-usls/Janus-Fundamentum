# R5 E9 — AF3 one-zero exact -2 binary augmentation theorem

Date: 2026-09-30

Status: `JANUS_EXACT_GLOBAL_AUGMENTATION_CHARACTERIZATION__ONE_ZERO_AF3_STATE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `research/R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`

## 1. One-zero AF3 state

Let `A in {0,1}^{n x n}` be square row/column-cubic and let

\[
r\in\mathbb F_3^n,
\qquad Ar=\mathbf1,
\]

have exactly one zero coordinate, say `r_i=0`.

Put

\[
b_j=\mathbf1[r_j=2].
\]

Every row not containing `i` is zero-free, so its `r`-pattern is a permutation of `(2,1,1)` and its `b`-weight is one.

Every row containing `i` has pattern `(0,2,2)` and `b`-weight two. Since column `i` has degree three, there are exactly three such defect rows.

Define

\[
x^{(0)}=b+e_i\in\{0,1\}^n.
\]

Then the three defect rows have `x^(0)`-weight three and every other row has weight one. Hence

\[
Ax^{(0)}=\mathbf1\pmod2.
\]

Double-counting selected incidences gives

\[
3|x^{(0)}|=(n-3)+3\cdot3=n+6,
\]

so

\[
\boxed{|x^{(0)}|=n/3+2.}
\]

Thus a one-zero AF3 point canonically produces a binary affine-coset point exactly two above the Exact-One lower bound.

## 2. Binary kernel move statistics

Take any

\[
z\in\ker_{\mathbb F_2}(A)
\]

and write `C=supp(z)`, `c=|C|`, `S=supp(x^(0))`, and

\[
q=|C\cap S|.
\]

Every source row meets `C` in even cardinality, hence in zero or two coordinates.

Let:

- `t=t(z)` be the number of the three defect rows that meet `C` in two coordinates;
- `w=w(z)` be the number of nondefect rows whose two `C` coordinates both lie outside `S`.

Let `a` be the number of active nondefect rows whose `C`-pair contains one element of `S` and one outside `S`.

Counting incidences of `C cap S` gives

\[
3q=2t+a.
\]

Counting incidences of `C-S` gives

\[
3(c-q)=a+2w.
\]

Subtracting yields the exact identity

\[
\boxed{
3(c-2q)=2(w-t).
}
\]

But toggling `z` changes Hamming weight by

\[
|x^{(0)}+z|-|x^{(0)}|=c-2q.
\]

Therefore

\[
\boxed{
|x^{(0)}+z|-|x^{(0)}|
=\frac23(w-t).
}
\]

The addition above is in `F2` / symmetric difference.

## 3. Exact improvement criterion

Because the left side is an integer, `w-t` is divisible by three. Also

\[
t\in\{0,1,2,3\},\qquad w\ge0.
\]

A strict improvement requires `w<t`. The only possible pair compatible with `w congruent t (mod 3)` is

\[
\boxed{t=3,\qquad w=0.}
\]

Then

\[
|x^{(0)}+z|-|x^{(0)}|=-2.
\]

No improvement of size `-1` or less than `-2` is possible from this state.

### Theorem OZ-1

For a one-zero AF3 solution `r`, the following are equivalent:

1. the source is Exact-One SAT;
2. there exists `z in ker_F2(A)` with `|x^(0)+z|<|x^(0)|`;
3. there exists `z in ker_F2(A)` with
   ```text
   t(z)=3,
   w(z)=0;
   ```
4. there exists `z in ker_F2(A)` such that `x^(0)+z` has weight `n/3`.

Whenever these conditions hold, `x=x^(0)+z` is an Exact-One witness.

### Proof

`2 <=> 3` is the identity above. Under `t=3,w=0`, the weight drops by exactly two, from `n/3+2` to `n/3`. Since `x^(0)+z` remains a parity solution, the cubic parity lower-bound theorem forces every row to have weight exactly one, proving `3 => 4 => 1`.

Conversely if an Exact-One witness `x` exists, then both `x` and `x^(0)` solve `Ay=1` over `F2`, so `z=x+x^(0)` lies in `ker_F2(A)` and changes the weight by exactly `-2`; the identity forces `t=3,w=0`. QED.

## 4. Structural meaning of t=3,w=0

The criterion is global but highly rigid:

- all three rows through the unique AF3 zero must be active in the binary kernel move;
- every other active row must pair its unique currently-selected variable with exactly one currently-unselected variable;
- no ordinary row may activate its two currently-unselected variables together.

Equivalently, outside the three defects the move obeys the exact Boolean add/copy law

\[
q_s=u+v
\]

on a row with one selected variable `s` and two unselected variables `u,v`.

This exposes the same three-way all-or-none fanout already isolated by the frozen rank-3 matching barrier. Therefore OZ-1 is a strict augmentation filter, not a proof that the required move is polynomially discoverable.

## 5. Algorithmic consequence

For any proposed universal source-trade algorithm, a one-zero AF3 state is now an exact regression gate:

```text
SUCCESS must find a kernel move activating all 3 defects and zero UU rows,
or soundly certify none exists.
```

There is no need to search arbitrary objective improvements at this state; every valid improvement has exactly this form and lands directly on an Exact-One witness.

## 6. Ceiling

```text
ONE-ZERO AF3 -> PARITY POINT OF WEIGHT n/3+2
= PROVED

EXACT MOVE IDENTITY
Delta weight = 2(w-t)/3
= PROVED

STRICT IMPROVEMENT
iff t=3 and w=0
= PROVED

ANY IMPROVEMENT LANDS DIRECTLY AT EXACT-ONE
= PROVED

POLYNOMIAL DISCOVERY OF t=3,w=0 MOVE
= OPEN / ALL-OR-NONE FANOUT SURVIVES

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
