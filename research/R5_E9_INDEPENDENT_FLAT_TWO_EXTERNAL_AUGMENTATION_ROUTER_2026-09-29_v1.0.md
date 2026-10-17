# R5 E9 — Independent-flat and two-external exact augmentation router

Date: 2026-09-29

Status: `JANUS_DERIVED_DETERMINISTIC_POLYNOMIAL_AFFINE_COSET_PREROUTER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`
- `research/R5_E9_CUBIC_KERNEL_CIRCUIT_CONNECTED_CONTRACTION_2026-09-27_v1.0.md`
- `research/R5_E9_MAXIMUM_LINEAR_EVEN_COVER_SATURATION_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_independent_flat_two_external_augmentation.py`

Scientific ceiling:

```text
THIS IS AN ADMITTED DETERMINISTIC POLYNOMIAL STRICT-AUGMENTATION PRE-ROUTER.
IT REMOVES ALL NEGATIVE CIRCUITS USING ZERO, ONE, OR TWO ELEMENTS OUTSIDE
THE CURRENT SYNDROME SUPPORT.
IT DOES NOT PROVE THAT THE TERMINAL 2-EXTERNAL LOCAL OPTIMUM IS GLOBAL.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A in {0,1}^{n x n}` be square, row/column-cubic and linear, and let

\[
x\in\{0,1\}^n,\qquad Ax=\mathbf1\pmod2.
\]

Put

\[
S=\operatorname{supp}(x).
\]

For a binary kernel move `c`,

\[
\Delta_x(c)=|x\oplus c|-|x|.
\]

Every accepted step below is an exact kernel toggle, so it preserves the syndrome-one affine coset and hence preserves the global minimum value in that coset.

Linearity plus column degree three implies that the represented column matroid is simple: no column is zero, and no two distinct columns are equal, because equal cubic columns would meet in three source rows, violating pairwise intersection at most one.

## 2. Zero-external move: delete a dependence inside S

If the columns indexed by `S` are dependent over `F2`, Gaussian elimination returns a nonzero

\[
0\ne c\in\ker A,\qquad \operatorname{supp}(c)\subseteq S.
\]

Then toggling `c` simply deletes its support from `S`, and

\[
\boxed{\Delta_x(c)=-|c|<0.}
\]

Repeat until `S` is independent.

This is polynomial and every step strictly decreases `|S|`.

## 3. One-external move: close S

Assume `S` is independent. If some outside element `e notin S` lies in the matroid closure

\[
e\in\operatorname{cl}(S),
\]

then the coordinates of `e` in the independent set `S` are unique. Let

\[
e=\sum_{t\in T} t,\qquad T\subseteq S.
\]

Then

\[
C_e=\{e\}\cup T
\]

is the fundamental circuit of `e` over `S`.

Simplicity rules out `|T|=0` and `|T|=1`, hence

\[
|T|\ge2.
\]

The toggle replaces `T` by `e`:

\[
S'=(S\setminus T)\cup\{e\},
\]

and

\[
\boxed{\Delta=1-|T|\le-1.}
\]

Moreover `S'` is independent. If a dependence in `S'` used `e`, it would express `e` by a subset of `S\setminus T`, contradicting uniqueness of its coordinates in the independent set `S`; a dependence avoiding `e` would lie in `S`.

Repeat zero-/one-external moves until

\[
\boxed{S\text{ is an independent flat of }M(A).}
\]

## 4. Two-external move

Now assume `S` is an independent flat. For every pair of distinct outside columns `e,f`, test by Gaussian elimination whether

\[
e+f\in\operatorname{span}(S).
\]

If not, this pair gives no kernel vector with all remaining support inside `S`.

If yes, independence gives a unique subset `T subseteq S` such that

\[
e+f=\sum_{t\in T}t.
\]

Then

\[
C_{e,f}=\{e,f\}\cup T
\]

is a circuit:

- no proper dependence can contain only one of `e,f`, because `S` is closed;
- a proper dependence containing both would give a second representation of `e+f` in the independent set `S`.

Its augmentation charge is

\[
\boxed{\Delta=2-|T|.}
\]

For a row/column-cubic source, every binary kernel support has even cardinality because `3|C|=2a(C)`. Thus `|T|+2` is even, so `|T|` is even.

Therefore a two-external circuit is either

```text
|T|=2  -> neutral four-element circuit,
|T|>=4 -> strict improvement by at least two.
```

Whenever `|T|>=4`, toggle `C_{e,f}` and restart the zero-/one-external closure phase.

The new support is independent before the restart: a dependence using both `e,f` would require the removed coordinate set `T`, and one using only one outside element would contradict the old flatness.

## 5. Polynomial algorithm

Use the following deterministic router.

```text
while true:
    if S is dependent:
        find a nonzero dependency c subseteq S;
        S <- S \ c;
        continue

    if exists e outside S with e in span(S):
        compute unique fundamental support T;
        S <- (S\T) union {e};
        continue

    # S is now an independent flat
    scan all unordered pairs e,f outside S:
        if e+f in span(S):
            compute unique T subseteq S;
            if |T| >= 4:
                S <- (S\T) union {e,f};
                restart

    return S
```

Every successful iteration decreases `|S|` by at least one, so at most `n` strict augmentations occur.

All tests and coordinate recovery are Gaussian elimination over `F2`. A coarse implementation using fresh elimination for every pair is still polynomial; incremental linear algebra can improve constants but is not needed for the theorem.

### Theorem IF2E-1

The router is deterministic polynomial time, preserves `Ax=1 mod 2`, never increases Hamming weight, and terminates at a syndrome-one support `S` satisfying all of:

1. `S` is independent;
2. `S` is closed / a flat in the ordinary column matroid;
3. no negative kernel circuit uses zero external elements;
4. no negative kernel circuit uses one external element;
5. no negative kernel circuit uses two external elements.

## 6. Relation to global optimality

The parent CAD theorem says global minimum is equivalent to absence of **all** negative circuits. IF2E proves that circuits with at most two external elements can be exhausted in polynomial time.

Thus after this router any surviving improving circuit must contain at least three columns outside the current support.

Freeze the sharper residual:

```text
R5_E9_THREE_PLUS_EXTERNAL_NEGATIVE_CIRCUIT_GATE_V1
```

The next theorem must either:

- prove that cubic-linearity forces a negative circuit with at most two external elements whenever `|S|>n/3`; or
- exhibit a source-valid syndrome point with `|S|>n/3` that is IF2E-terminal, thereby falsifying that hope; or
- construct a polynomial nonlocal oracle for the three-plus-external layer.

## 7. Anti-loop boundary

Do not infer global optimality from IF2E local optimality. High-girth/codeword barriers already warn that fixed-locality circuit search need not capture every global kernel move.

The purpose of IF2E is different: it removes the first two nontrivial external layers **exactly and cheaply**, so future search starts at a genuinely nonlocal residual rather than repeatedly rediscovering fundamental-circuit exchanges.

## 8. Ceiling

```text
DEPENDENCE INSIDE CURRENT SUPPORT
= POLYNOMIALLY REMOVABLE

OUTSIDE ELEMENT IN closure(S)
= POLYNOMIALLY REMOVABLE BY NEGATIVE FUNDAMENTAL CIRCUIT

NEGATIVE TWO-EXTERNAL CIRCUIT
= POLYNOMIALLY DISCOVERABLE / REMOVABLE

TERMINAL SUPPORT
= INDEPENDENT FLAT + TWO-EXTERNAL LOCAL OPTIMUM

GLOBAL MINIMUM
= NOT IMPLIED

THREE-PLUS-EXTERNAL NEGATIVE CIRCUIT
= OPEN

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
