# R5 E9 — Kernel Walsh-moment global augmentation router

Date: 2026-09-29

Status: `JANUS_DERIVED_DETERMINISTIC_POLYNOMIAL_NONLOCAL_KERNEL_AUGMENTATION_PREROUTER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_INDEPENDENT_FLAT_TWO_EXTERNAL_AUGMENTATION_ROUTER_2026-09-29_v1.0.md`
- `research/R5_E9_MAXIMUM_LINEAR_EVEN_COVER_SATURATION_2026-09-29_v1.0.md`
- `research/R5_E9_IF2E_THREE_EXTERNAL_HOSTILE_COUNTERCONTROL_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_kernel_walsh_moment_global_augmentation.py`

Scientific ceiling:

```text
THIS NOTE GIVES A GENUINELY NONLOCAL POLYNOMIAL KERNEL AUGMENTATION TEST.
IT CAN RETURN KERNEL WORDS WITH LINEARLY MANY EXTERNAL ELEMENTS WITHOUT
ENUMERATING CIRCUITS OR THE KERNEL.
IT IS A SUFFICIENT GLOBAL ROUTER, NOT A COMPLETE SAT DECIDER.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Affine-coset setup

Let `A` be any binary matrix and let

\[
x\in\{0,1\}^n,\qquad Ax=b\pmod2.
\]

Put `S=supp(x)`.  Let

\[
h^{(1)},\ldots,h^{(k)}
\]

be a basis of `ker_F2(A)`.  For every coordinate `i`, define its kernel-coordinate mask

\[
\alpha_i=(h^{(1)}_i,\ldots,h^{(k)}_i)\in\mathbb F_2^k.
\]

For `lambda in F2^k` the corresponding kernel word is

\[
c_i(\lambda)=\alpha_i\cdot\lambda.
\]

Define the exact improvement score

\[
H(\lambda)
:=|c(\lambda)\cap S|-|c(\lambda)\setminus S|.
\]

Then

\[
\boxed{|x\oplus c(\lambda)|-|x|=-H(\lambda).}
\]

Thus `H(lambda)>0` is exactly a strict affine-coset Hamming improvement.

Coordinates with `alpha_i=0` never move and may be ignored.  Let

\[
a_S=|\{i\in S:\alpha_i\ne0\}|,
\qquad
a_O=|\{i\notin S:\alpha_i\ne0\}|.
\]

## 2. First-moment theorem

For uniformly random `lambda`, every nonzero linear form `alpha_i.lambda` is one with probability `1/2`. Therefore

\[
\boxed{\mathbb E H=\frac{a_S-a_O}{2}.}
\]

### Theorem KWM-1

If `a_S>a_O`, a strict improving kernel word exists and can be constructed deterministically in polynomial time.

### Constructive proof

Expose the bits of `lambda` one at a time.  Under any partial assignment, the conditional expectation of each term `[alpha_i.lambda=1]` is exactly `0`, `1`, or `1/2`, depending on whether the residual parity is fixed false, fixed true, or still has an unfixed coefficient. Hence `E[H | prefix]` is computable in polynomial time.

At each bit choose a child whose conditional expectation is at least the current one. Starting from a positive expectation, the final complete assignment has `H(lambda)>0`.

No kernel enumeration is used.

## 3. Exact sparse Walsh form

Group equal nonzero masks. For each `a!=0`, put

\[
d_a
=|\{i\in S:\alpha_i=a\}|
-|\{i\notin S:\alpha_i=a\}|.
\]

With the character

\[
\chi_a(\lambda)=(-1)^{a\cdot\lambda},
\]

we have

\[
\boxed{
H(\lambda)
=\frac{C}{2}-\frac12\sum_{a\ne0}d_a\chi_a(\lambda),
\qquad C=a_S-a_O.
}
\]

Orthogonality of distinct Walsh characters gives

\[
\boxed{
\mathbb E H^2
=\frac{C^2+\sum_{a\ne0}d_a^2}{4}.
}
\]

This identity is basis invariant: changing the kernel basis applies an invertible linear relabelling to the nonzero masks and leaves all multiplicities and moments unchanged.

## 4. Second-moment positive certificate

Because at most `a_O` movable outside coordinates can be added,

\[
-a_O\le H(\lambda)\le a_S.
\]

Define

\[
Q(h)=h(h+a_O).
\]

For every integer `h` in `[-a_O,0]`, `Q(h)<=0`; for every `h>0`, `Q(h)>0`.

Therefore

\[
\mathbb E Q(H)>0
\Longrightarrow
\exists\lambda:H(\lambda)>0.
\]

Using the first two moments,

\[
4\mathbb E Q(H)
=C^2+\sum_a d_a^2+2a_OC
=\boxed{\sum_a d_a^2+a_S^2-a_O^2}.
\]

### Theorem KWM-2

If

\[
\boxed{\sum_{a\ne0}d_a^2+a_S^2-a_O^2>0,}
\]

then a strict improving kernel word exists and can be constructed deterministically in polynomial time.

### Constructive proof

For a partial assignment of `lambda`, conditional expectations of `H` are computed as in KWM-1.  Conditional expectations of `H^2` are also polynomial: for each coordinate pair the probability that two residual affine parities both equal one is in `{0,1/4,1/2,1}` and is determined by whether their remaining masks are zero, equal, or distinct.  Hence `E[Q(H)|prefix]` is computable in polynomial time.

Choose at each bit a child whose conditional expectation is at least the parent.  Positive initial expectation yields a final assignment with `Q(H)>0`; by the sign property above this forces `H>0`.

A direct implementation is polynomial even with an `O(n^2 k^2)` conditional-moment recomputation at every step; optimization is unnecessary for the theorem.

## 5. Balanced first moment

When `a_S=a_O`, `E H=0`.

If every `d_a=0`, the Walsh formula gives

\[
H(\lambda)\equiv0.
\]

Hence every word in the affine coset has exactly the same Hamming weight as `x`; this is a polynomially checkable global-minimum certificate.

If some `d_a!=0`, then `H` is nonconstant with mean zero, so it assumes both a positive and a negative value.  KWM-2 detects this automatically because

\[
\sum_a d_a^2>0.
\]

Thus the entire `a_S=a_O` layer is polynomially decided.

## 6. Interaction with IF2E

IF2E searches circuits with at most two external coordinates. KWM is fundamentally different: it chooses a complete kernel word through its `k` coefficient bits. The returned word may use linearly many external coordinates.

Consequently KWM is admissible on exactly the high-locality residual where fixed-`k` circuit enumeration becomes unattractive.

For the cyclic linear-cubic family

\[
E_i=\{i,i+1,i+5\}\pmod{21m},
\]

the deterministic IF2E terminal obtained from the all-ones syndrome point repeats the 21-coordinate block

```text
{1,2,3,6,7,9,11,17,18,19,20}.
```

Its kernel has dimension five and every nonzero kernel word is 21-periodic.  The smallest improving circuit has `3m` external coordinates; nevertheless

\[
a_S=11m,
\qquad a_O=10m,
\]

so KWM-1 constructs a global improving word in polynomial time without scanning `n^{3m}` external subsets.

This is a positive control showing that nonlocal averaging can beat locality escalation.

## 7. Exact finite hostile controls for completeness claims

The first moment is not complete.  There is a square linear-cubic SAT control on `n=18` with an IF2E terminal satisfying

```text
|S| = 8,
true affine-coset minimum = 6 = n/3,
a_S = 6,
a_O = 10,
E[H] = -2,
```

while an improving kernel word exists.  On this control KWM-2 succeeds with

\[
\mathbb E Q(H)=6>0.
\]

The second-moment condition is also not complete.  A second square linear-cubic SAT control on `n=18` has

```text
|S| = 8,
true affine-coset minimum = 6 = n/3,
a_S = 6,
a_O = 10,
H-values over the 3-dimensional kernel = {-10,-4,-2,-2,0,0,0,2},
E[Q(H)] = -4,
```

although the value `H=2` gives a strict improvement.

Therefore KWM-2 is promoted only as a sufficient global pre-router, not as a universal optimizer.

## 8. Sharpened residual

Freeze

```text
R5_E9_NEGATIVE_MEAN_HIGHER_ORDER_KERNEL_WALSH_GATE_V1
```

After low-nullity enumeration, IF2E, and KWM-2, the surviving case has no certified first/second-moment improvement.  A universal PASS must exploit additional source structure of the coordinate-mask code or provide a different representation-changing global move.

Forbidden promotion:
- claiming that `a_S<a_O` implies global optimality;
- claiming second moments are complete;
- expanding to the full `2^k` Walsh table;
- using generic Max-Lin2 / nearest-codeword optimization as a polynomial oracle.

## 9. Ceiling

```text
GLOBAL KERNEL-WORD SCORE H
= EXACT

FIRST MOMENT
E H = (a_S-a_O)/2
= PROVED

SECOND MOMENT
E H^2 = (C^2 + sum d_a^2)/4
= PROVED

POLYNOMIAL CONSTRUCTIVE IMPROVEMENT IF
sum d_a^2 + a_S^2 - a_O^2 > 0
= PROVED

BALANCED a_S=a_O LAYER
= POLYNOMIALLY DECIDED

LINEARLY-MANY-EXTERNAL MOVES
= SUPPORTED WITHOUT ENUMERATION

SECOND-MOMENT COMPLETENESS
= FALSIFIED ON SOURCE-VALID SAT CONTROL

HIGHER-ORDER / DIFFERENT GLOBAL MECHANISM
= OPEN

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```