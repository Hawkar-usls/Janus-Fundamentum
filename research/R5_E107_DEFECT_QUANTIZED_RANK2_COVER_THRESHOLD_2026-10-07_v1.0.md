# R5 E107 — Defect-Quantized Rank-2 Cover Threshold

Date: 2026-10-07

Status:
NO_RAW8_FORCES_AT_LEAST_12_ACTIVE_RANK2_FLATS__THRESHOLD_IS_EXACT_3_FOLD_COVER

Scientific ceiling:

E107 does not yet construct a universal polynomial ExactOne solver.

It adds a parent-specific global invariant to the generic E105/E106 affine-cover
normal form. On the current p=1,h=1 conditioned-U2,4 parent lane, every
raw8-parity candidate has a number of triple-selected defects divisible by
three.

Consequently a NO-RAW8 residual pure rank-2 affine cover must cover every
kernel point at least three times. Since each active rank-2 flat occupies
exactly one quarter of the residual domain, at least twelve active flats are
necessary.

P_VS_NP = OPEN.

## 1. Parent arithmetic

On the p=1,h=1 lane, E85 gives

a = 3t+1

active check vertices.

Consider any GF(2)-parity-compatible candidate Y with raw8 boundary syndrome.

Raw8 has:

A=B=C=0,
E=1,
V=0.

Therefore:

* check E receives zero internal selected incidences;
* A,B,C receive exactly one internal selected incidence because they have
  internal degree two and odd parity;
* every ordinary cubic check has selected degree one or three;
* x is unselected, so every selected internal variable contributes exactly
  three internal incidences.

Let delta(Y) be the number of ordinary checks of selected degree three.

Then double counting selected incidences gives

3|Y| = (a-1) + 2 delta(Y).

Since a-1 is divisible by three,

delta(Y) == 0 mod 3.

Thus every raw8-parity word has defect count

0,3,6,9,...

and exact raw8 is exactly the delta=0 case.

## 2. Translation to the E105 affine-flat cover

E105 associates to every residual kernel point z a raw8 parity word e xor z.

For every ordinary check c, its forbidden affine fiber B_c contains exactly
those z for which c becomes a triple-selected defect.

Therefore

delta(z) = number of active forbidden fibers B_c containing z.

The arithmetic theorem becomes:

for every residual kernel point z,

delta(z) == 0 mod 3.

This is a strong multiplicity constraint on the affine cover.

## 3. Combine with E106

After E106 affine unit propagation reaches fixed point D:

* every active forbidden fiber is nonempty;
* every active forbidden fiber has relative codimension two;
* therefore every active B_c has size |D|/4.

Let m be the number of active rank-2 fibers.

Double counting point-flat incidences gives

sum_{z in D} delta(z) = m |D| / 4.

If NO RAW8, then delta(z)>0 for every z.

By the mod-3 theorem,

delta(z)>=3 for every z.

Hence

m |D|/4 >= 3|D|

and therefore

m>=12.

This improves E106's generic less-than-four counting terminal to the
parent-specific exact terminal:

m<12 implies RAW8.

## 4. Threshold rigidity at m=12

If m=12 and NO RAW8, then

sum_z delta(z)=3|D|.

But every delta(z)>=3.

Therefore equality is forced pointwise:

delta(z)=3 for every z in D.

So the twelve forbidden flats form an exact 3-fold affine cover:

every residual kernel point lies in exactly three forbidden rank-2 fibers.

This is a much more rigid object than an arbitrary affine cover.

## 5. Fourier balance at the threshold

Translate D to a vector space.

Every active codim-2 flat can be written as a marked fiber of a rank-two dual
subspace L_c.

Let chi_c be the marked character specifying its forbidden value.

The flat indicator has Fourier expansion

1_{B_c}(x)
=
(1/4) sum_{g in L_c} (-1)^(chi_c(g)+g(x)).

At the threshold m=12 with an exact triple cover,

sum_c 1_{B_c}(x)=3

for every x.

Therefore every nonconstant Fourier coefficient vanishes.

For every nonzero dual functional g:

sum over c with g in L_c of (-1)^chi_c(g) = 0.

So every used dual direction has exactly balanced positive and negative marked
incidences.

This gives a new dual-line constraint for E108.

## 6. E104 replay

E104's residual kernel has eight points.

After E106:

m=18

active rank-2 flats remain.

The exact defect multiplicity spectrum is

4 points with multiplicity 0,
4 points with multiplicity 9.

Thus every multiplicity is divisible by three, exactly as E107 predicts.

The average is

18/4 = 4.5.

The four multiplicity-zero points are precisely the four exact raw8 witnesses.

## 7. Solver consequences

We now have the following exact terminals on the current lane:

* rank-0/rank-1 fibers are removed by E106 in polynomial time;
* fewer than 12 residual rank-2 fibers implies raw8 immediately;
* residual affine dimension O(log n) is polynomial by enumeration;
* m=12 and NO RAW8 forces an exact 3-fold cover with full Fourier balance.

Therefore the first genuinely hard residual object is no longer an arbitrary
rank-2 cover.

It is:

STRUCTURED MULTIPLE-OF-3 CODIM2 COVER

with multiplicities constrained by cubic ExactOne incidence arithmetic.

## 8. E108 target

First attack the threshold m=12 case.

Use the exact triple-cover Fourier equations together with:

* every dual line comes from one actual cubic check;
* line points are the three nonzero variable coordinate functionals at that
  check;
* original Tanner geometry is C4-free;
* original variables have degree three;
* forbidden characters come from the six TARGET6 witness supports.

Goal:

prove that a 12-flat exact triple cover forces either

A. a rank drop already removed by E106;
B. an E98 exchange rectangle producing an extra boundary state;
C. a repeated Tanner pair;
D. a binary-delta decomposition;
or construct the first exact TARGET6/no-raw8 threshold cover.

If the threshold case dies, extend the multiplicity/Fourier argument to
m>12.

Scientific status:

E107 = DEFECT MULTIPLICITY QUANTIZATION + 12-FLAT LOWER BOUND.
NO_RAW8 PURE RANK2 CORE REQUIRES m>=12.
m=12 REQUIRES EXACT 3-FOLD COVER + FOURIER BALANCE.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
