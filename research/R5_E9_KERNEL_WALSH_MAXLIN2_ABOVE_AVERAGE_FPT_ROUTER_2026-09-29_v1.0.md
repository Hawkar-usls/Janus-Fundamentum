# R5 E9 — Kernel Walsh to MaxLin2 Above-Average exact FPT router

Date: 2026-09-29

Status: `SOURCE_BOUND_EXACT_PARAMETERIZED_GLOBAL_ROUTER__NEGATIVE_MEAN_WALSH_GATE_REFINED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_KERNEL_WALSH_MOMENT_GLOBAL_AUGMENTATION_ROUTER_2026-09-29_v1.0.md`
- `research/R5_E9_INDEPENDENT_FLAT_TWO_EXTERNAL_AUGMENTATION_ROUTER_2026-09-29_v1.0.md`

Prior art imported exactly:
- R. Crowston, M. Fellows, G. Gutin, M. Jones, F. Rosamond, S. Thomassé, A. Yeo,
  *Simultaneously Satisfying Linear Equations Over F_2: MaxLin2 and Max-r-Lin2 Parameterized Above Average*, FSTTCS 2011 / arXiv:1104.1135.
  The paper proves a kernel with `O(k^2 log k)` variables and an algorithm running in `2^{O(k log k)} poly(input)` for weighted MaxLin2 Above Average.

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT IDENTIFIES THE SURVIVING NEGATIVE-MEAN KERNEL-WALSH SEARCH EXACTLY AS
A WEIGHTED MAXLIN2-ABOVE-AVERAGE INSTANCE AND IMPORTS THE KNOWN FPT/KERNEL
ALGORITHM WITH THE CORRECT PARAMETER.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen Walsh score

Use the parent notation. A binary kernel basis gives coordinate masks

\[
\alpha_i\in\mathbb F_2^k,
\]

and, for a current syndrome-one support `S`, grouped signed multiplicities

\[
d_a
=|\{i\in S:\alpha_i=a\}|
-|\{i\notin S:\alpha_i=a\}|,
\qquad a\ne0.
\]

For `lambda in F2^k`, let

\[
p_a(\lambda)=a\cdot\lambda\in\{0,1\}.
\]

The exact Hamming improvement score is

\[
\boxed{H(\lambda)=\sum_{a\ne0}d_a p_a(\lambda).}
\]

Equivalently, with

\[
C=\sum_{a\ne0}d_a=a_S-a_O,
\]

the parent Walsh formula is

\[
H(\lambda)=\frac C2-\frac12\sum_a d_a(-1)^{p_a(\lambda)}.
\]

The first/second-moment router already handles many cases. This note concerns the surviving negative-mean layer

\[
C<0.
\]

Put

\[
\boxed{D=-C=a_O-a_S>0.}
\]

## 2. Exact weighted MaxLin2 system

For every nonzero mask `a` with `d_a != 0`, create one weighted linear equation over `F2`:

```text
if d_a > 0:
    require a . lambda = 1 with weight |d_a|;
if d_a < 0:
    require a . lambda = 0 with weight |d_a|.
```

Let `E(lambda)` denote the standard **excess** of this weighted MaxLin2 instance:

```text
weight of satisfied equations
-
weight of falsified equations.
```

### Theorem KMAA-1 — exact score identity

For every `lambda`,

\[
\boxed{E(\lambda)=2H(\lambda)-C=2H(\lambda)+D.}
\]

### Proof

For `d_a>0`, the signed contribution to excess is

\[
d_a(2p_a-1).
\]

For `d_a<0`, the desired right-hand side is zero; its excess contribution is

\[
|d_a|(1-2p_a)=d_a(2p_a-1).
\]

Summing gives

\[
E=\sum_a d_a(2p_a-1)
=2\sum_a d_ap_a-\sum_a d_a
=2H-C.
\]

QED.

Because `H` is integer-valued,

\[
\boxed{
H(\lambda)>0
\iff
E(\lambda)\ge D+2.
}
\]

Thus the negative-mean Walsh improvement problem is not merely analogous to MaxLin2-AA: it is exactly one weighted MaxLin2 above-average decision instance.

## 3. Parameter convention without half-integers

The standard MaxLin2-AA formulation asks whether satisfied weight is at least

\[
W/2+\kappa,
\]

which is equivalent to excess at least `2 kappa`.

To avoid any parity/half-integer convention, multiply every equation weight above by two. Then the excess becomes `2E`, and

\[
H>0
\iff
2E\ge2(D+2).
\]

Therefore the exact standard above-average parameter is

\[
\boxed{\kappa=D+2.}
\]

Weight doubling changes neither the maximizing assignments nor the source witness reconstruction.

## 4. Imported deterministic FPT router

Crowston et al. prove for weighted MaxLin2-AA with parameter `kappa`:

```text
kernel variables = O(kappa^2 log kappa),
time             = 2^{O(kappa log kappa)} poly(input size).
```

Applying that theorem with

\[
\kappa=D+2
\]

gives an exact deterministic router for the entire negative-mean Walsh gate:

\[
\boxed{
T_{\rm KMAA}
=2^{O((D+2)\log(D+2))}\operatorname{poly}(n).
}
\]

The returned MaxLin assignment is exactly a kernel coefficient vector `lambda`; the corresponding kernel word is reconstructed as

\[
c_i=\alpha_i\cdot\lambda,
\]

so an improving affine-coset word is obtained with no semantic oracle.

If the MaxLin instance is NO, then no `lambda` has `H(lambda)>0`; hence the current syndrome-one point is globally minimum **within its entire binary affine coset**.

This NO statement is exact for the binary affine-coset objective. It must not be confused with a global certificate for the separate integer-L1 source-trade formulation unless the parent equivalence for the state being solved has been invoked explicitly.

## 5. Immediate polynomial region

If

\[
D=O\!\left(\frac{\log n}{\log\log n}\right),
\]

then

\[
(D+2)\log(D+2)=O(\log n),
\]

and therefore the KMAA router is polynomial in `n`.

Thus the prior live residual

```text
C < 0
```

is sharpened to

```text
D = a_O-a_S = omega(log n / log log n)
```

unless another already-admitted polynomial KWM certificate fires.

## 6. Combined exact parameter router

Let

\[
k=\dim\ker_{\mathbb F_2}(A).
\]

Direct kernel enumeration costs `2^k poly(n)`. KMAA costs

\[
2^{O(D\log D)}\operatorname{poly}(n).
\]

Hence, after the polynomial IF2E/KWM preprocessing, we now have the exact universal parameterized upper bound

\[
\boxed{
T
\le
2^{O(\min\{k,(D+2)\log(D+2)\})}\operatorname{poly}(n).
}
\]

This is a genuine improvement in the parameter map. It is not a polynomial bound when both parameters are large.

## 7. Kernelization consequence

The imported MaxLin theorem also yields, in deterministic polynomial preprocessing, an equivalent weighted linear system on

\[
\boxed{O((D+2)^2\log(D+2))}
\]

effective Boolean variables.

This is an exact **semantic kernel** for the negative-mean Walsh improvement question. It may collapse an original source with large binary nullity to a much smaller global correlation core.

No claim is made that the kernel has logarithmic size for arbitrary sources. If `D=Theta(n)`, the bound is still superlogarithmic and does not prove `P=NP`.

## 8. Relation to KWM moments

KWM-1 and KWM-2 are polynomial sufficient conditions and should run first.

KMAA is complementary:

```text
KWM moment certificate fires
    -> deterministic polynomial improving word;
else if D = O(log n/log log n)
    -> deterministic polynomial KMAA solve;
else
    -> exact MaxLin kernel/FPT route exists but is not polynomially bounded universally.
```

The two frozen KWM hostile SAT controls have

```text
a_S=6,
a_O=10,
D=4,
kappa=6,
```

so they lie inside the admitted FPT router; the first is already solved by KWM-2, while the second demonstrates why the exact MaxLin step is strictly stronger than the second-moment certificate.

## 9. New frontier

Freeze

```text
R5_E9_LARGE_DEFICIT_MAXLIN_SOURCE_STRUCTURE_GATE_V1
```

The surviving universal case has all of:

```text
KWM first/second-moment polynomial tests do not fire;
D = a_O-a_S = omega(log n/log log n);
low-nullity enumeration is not polynomial;
MaxLin2-AA kernelization is exact but its parameter is still large.
```

A PASS must exploit additional source provenance of the masks `alpha_i` coming from a square linear-cubic incidence matrix. Generic MaxLin2 optimization may not be invoked as a polynomial oracle.

Primary next attacks:

1. determine whether IF2E-terminal source geometry forces a rank/weight relation that makes the MaxLin kernel polynomially small in `log n`;
2. exploit the fact that the masks are columns of a generator matrix of a `(3,3)`-LDPC kernel code, rather than arbitrary MaxLin equations;
3. combine the MaxLin reductions with the existing rational-nullity / row-basis routers before any new branching.

## 10. Ceiling

```text
NEGATIVE-MEAN WALSH IMPROVEMENT
= EXACT WEIGHTED MAXLIN2-AA INSTANCE

EXCESS IDENTITY
E = 2H + D
= PROVED

STANDARD PARAMETER AFTER WEIGHT DOUBLING
kappa = D+2
= PROVED

DETERMINISTIC FPT TIME
= 2^{O((D+2) log(D+2))} poly(n)
= SOURCE-IMPORTED

POLYNOMIAL KERNEL
= O((D+2)^2 log(D+2)) EFFECTIVE VARIABLES
= SOURCE-IMPORTED

D = O(log n/log log n)
= POLYNOMIAL TERMINAL

ARBITRARY LARGE D
= OPEN

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
