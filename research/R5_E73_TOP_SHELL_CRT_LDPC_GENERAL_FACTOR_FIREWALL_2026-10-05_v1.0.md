# R5 E73 — Top-Shell CRT / LDPC / General-Factor Firewall

Date: 2026-10-05

Status:
`F2_TOP_SHELL_ALREADY_FORCES_INTEGER_EXACTNESS__DIRECT_F3_CROSS_FIELD_PRUNING_COLLAPSES__HARD_CORE_IS_THE_0_OR_3_ALL_OR_NONE_CONSTRAINT`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT IDENTIFIES THE EXACT POINT AT WHICH THE E72 CROSS-FIELD IDEA STOPS ADDING
INFORMATION: ON THE DECISIVE BINARY TOP SHELL, THE TERNARY CONDITION IS
AUTOMATIC.

THE REMAINING NONLINEAR CONTENT IS EXACTLY THE ALL-OR-NONE {0,3} VARIABLE
CONSTRAINT, EQUIVALENTLY EXACT-ONE / EQUALITY_3 HOLANT OR A STRUCTURED
SYNDROME-DECODING TOP-SHELL QUERY.

P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

be square cubic: every row and every column has exactly three ones.  The main
R5 carrier additionally assumes linearity when needed, but the algebraic theorem
below does not.

For a binary vector `x`, define its complement

```text
k = 1-x in {0,1}^n.
```

Because every row has sum three,

```text
A 1 = 3 1
```

over the integers.

Therefore

```text
A x = 1
```

is equivalent to

```text
A k = 2 1.
```

The point of E73 is to compare this integer equation with the F2 and F3 views
that survived E70--E72.

## 2. Top-shell synchronization theorem

For every binary `k`, the following five statements are equivalent:

```text
(A)  A k = 0 (mod 2)  and  |k| = 2n/3;

(B)  A k = 2 1        over Z;

(C)  A k = 2 1        (mod 6);

(D)  A k = 0 (mod 2)  and  A k = 2 1 (mod 3);

(E)  x=1-k satisfies A x = 1 over Z.
```

The only implication needing more than residue arithmetic is `(A)=>(B)`.

If

```text
A k = 0 (mod 2),
```

then each integer row sum `(Ak)_i` belongs to `{0,2}`, because a row contains
only three binary entries.  Column cubicity gives the exact double count

```text
sum_i (A k)_i = 3 |k|.
```

On the top shell `|k|=2n/3`, this becomes

```text
sum_i (A k)_i = 2n.
```

There are `n` summands and each is at most two, so every summand must equal two.
Thus

```text
boxed:
A k = 0 (mod 2), |k|=2n/3
    =>
A k = 2 1 over Z.
```

The reverse implication follows by summing rows:

```text
2n = sum_i (Ak)_i = 3|k|.
```

`(B)<=> (C)` uses the fact that every integer row sum lies in `{0,1,2,3}`;
within this range, residue `2 mod 6` means exactly the integer two.

`(C)<=> (D)` is CRT for moduli two and three.

Finally,

```text
A(1-k)=3 1-Ak,
```

so `(B)<=> (E)`.

Hence

```text
boxed:
F2 TOP SHELL = INTEGER EXACTNESS = SAME-SUPPORT F2+F3 CONDITION.
```

This is stronger than merely saying the formulations have the same satisfying
assignments: it says that after a binary kernel word reaches the extremal E58
weight, the F3 test cannot reject it.

## 3. Relation to the E65 quantized defect theorem

E65 already proved, in the parity-syndrome orientation `x`, that if

```text
A x = 1 (mod 2),
```

and `t3` rows contain three selected columns, then

```text
3|x| = n + 2 t3,
t3 = 3m,
|x| = n/3 + 2m.
```

E73 does not relabel this as a new theorem.  In the complement orientation
`k=1-x`, those same defective rows are exactly the rows of `Ak` having sum zero.
If `z(k)` denotes their number, then

```text
2(n-z(k)) = 3|k|
```

and therefore

```text
z(k)=n-(3/2)|k|.
```

Thus the E73 shell argument is the `m=0` endpoint of the already frozen E65
defect quantization.

## 4. Exact syndrome-coset formulation

Let

```text
C = ker_F2(A).
```

Because every row of `A` has odd weight three,

```text
A 1 = 1 (mod 2).
```

Hence the complete syndrome-one coset is

```text
{x : A x = 1 mod 2} = 1 + C.
```

Define

```text
delta_1(A) = min{|x| : A x = 1 mod 2}.
```

For `x=1+k`, Hamming complementation gives

```text
|x| = n-|k|,
```

so

```text
boxed:
delta_1(A)
  = n - max{|k| : k in ker_F2(A)}.
```

E56/E58 then become the exact threshold identity

```text
boxed:
delta_1(A) >= n/3,

A Exact-One SAT
  <=> delta_1(A)=n/3
  <=> max_{k in C}|k|=2n/3.
```

This is a highly structured syndrome-decoding / nearest-codeword query: the
parity-check matrix is square and `(3,3)`-regular, and for the linear carrier its
Tanner graph is C4-free.

The classical general syndrome-decoding problem is NP-complete (Berlekamp,
McEliece and van Tilborg, 1978).  More recently, minimum-distance hardness has
also been proved for `(3,3)`-regular LDPC Tanner graphs.  These are anti-loop
signals, not a proof that our particular all-ones-syndrome threshold is identical
to those hardness statements; the exact decision hardness here is already
supplied internally by the R5 E12 RXC3 bridge.

## 5. General-Factor equivalence

Construct the Tanner/incidence graph `G_A=(U,V,E)`:

```text
U = row/check vertices,
V = column/variable vertices,
(i,j) in E iff A_ij=1.
```

Both sides are 3-regular.

Given an Exact-One assignment `x`, select an incidence edge `(i,j)` iff
`x_j=1`.  Then

```text
for every check i:     selected degree = 1,
for every variable j:  selected degree is 0 or 3.
```

Conversely, any factor satisfying these degree lists must either select all
three edges of a variable or none, so it defines a binary variable assignment;
check degree one then gives Exact-One.

Therefore

```text
boxed:
Exact-One(A)
<=>
General Factor on G_A with
    K(u)={1}   for u in U,
    K(v)={0,3} for v in V.
```

The complement formulation uses `{2}` on the check side and the same `{0,3}`
all-or-none variable side.

This pins the obstruction that ordinary flow/b-factor relaxations missed in
E60: the hard nonconvex local list is exactly

```text
{0,3},
```

not the row degree itself.

External anti-loop agrees precisely.  Gutin, Kim, Soleimanfallah, Szeider and
Yeo state that General Factor remains NP-hard on bipartite graphs when one side
has list `{1}` and the other side has list `{0,3}`.

The R5 E12 reduction makes the project-specific restriction even sharper:
its target is square cubic linear.  Consequently the corresponding incidence
graph is balanced, 3-regular and C4-free.  Any universal factor algorithm used
here must therefore solve the E12 hard image itself; generic regularity or
C4-freeness is not an escape hatch.

## 6. Holant equivalence

On the same 3-regular bipartite graph assign

```text
check side:     ExactOne_3 = [0,1,0,0],
variable side:  Equality_3 = [1,0,0,1].
```

`Equality_3` enforces the all-or-none state of the three incidences belonging to
a source variable.  `ExactOne_3` enforces one selected incidence at every check.
Thus feasible edge assignments are in bijection with Exact-One witnesses.

For counting, this is exactly

```text
Holant(ExactOne_3 | Equality_3).
```

Fan and Cai's 2023 3-regular bipartite Holant dichotomy explicitly proves
`Holant([0,1,0,0] | (=3))` #P-hard via Restricted Exact Cover by 3-Sets.  Cai,
Fan and Liu extend the regular bipartite dichotomy to mixed-sign/rational
signatures and again identify Exact-One with exact-3-cover counting.

This closes the naive hope that simply changing to a holographic vocabulary
places our signature pair inside a known easy counting family.  It does not rule
out a new decision-only global identity, which is exactly the kind of result a
P=NP proof would require.

## 7. What happens to the direct F2/F3 cross-field plan

E72 suggested that the exceptional characteristic-three quotient might couple
nontrivially to the binary top-shell geometry.

E73 gives the exact answer for the same-support attack:

```text
once k in ker_F2(A) has |k|=2n/3,
A k = 2 1 over Z,
so A k = 2 1 mod 3 automatically.
```

Therefore adding the F3 equation after reaching the binary shell deletes zero
candidates.

This does NOT make F3 useless everywhere: E71/E72 still provide independent
exact envelopes and quotient information away from the shell.  It says only
that the hoped-for decisive final intersection

```text
F2 top shell INTERSECT F3 affine condition
```

collapses to the F2 top shell itself.

## 8. Replay controls

Companion checker:

```text
experiments/r5_e73_top_shell_crt_ldpc_general_factor_firewall.py
```

It freezes four controls.

### SAT12

The E61 square-cubic-linear SAT carrier is exhaustively checked over all
`2^12=4096` binary `k` vectors.  The five E73 conditions agree pointwise and
there is exactly one top-shell witness.

### UNSAT12

The E57/E61 singular full-support negative carrier is also exhausted over all
4096 binary vectors.  The five conditions agree pointwise and no top-shell
witness exists.

### Connected linear q=9 positive control

A separate square-cubic-linear `9 x 9` source is exhausted.  It has exactly one
Exact-One cover, on source columns

```text
{1,7,8}.
```

This prevents the theorem from being tied only to the E61 permutation fixtures.

### Actual E12 N=102 hardness target

For the frozen E12 q=6 RXC3 target:

```text
N = 102,
dim ker_F2(B) = 12,
|ker_F2(B)| = 4096.
```

The checker enumerates the complete binary kernel and obtains

```text
max kernel weight = 60,
top shell          = 68,
top-shell words    = 0,
delta_1(B)         = 42 > N/3 = 34.
```

Thus the theorem is replayed directly on a nontrivial member of the E12 hardness
image rather than only on hand-built controls.

## 9. External anti-loop references

1. E. R. Berlekamp, R. J. McEliece, H. C. A. van Tilborg,
   "On the inherent intractability of certain coding problems",
   IEEE Transactions on Information Theory 24(3), 384--386 (1978),
   DOI `10.1109/TIT.1978.1055873`.

2. G. Gutin, E. J. Kim, A. Soleimanfallah, S. Szeider, A. Yeo,
   "Parameterized Complexity Results for General Factors in Bipartite Graphs
   with an Application to Constraint Programming",
   Algorithmica 64, 112--125 (2012; online 2011),
   DOI `10.1007/s00453-011-9548-8`.

3. A. Z. Fan, J.-Y. Cai,
   "Dichotomy result on 3-regular bipartite non-negative functions",
   Theoretical Computer Science 949 (2023) 113745,
   DOI `10.1016/j.tcs.2023.113745`.

4. J.-Y. Cai, A. Z. Fan, Y. Liu,
   "Bipartite 3-regular counting problems with mixed signs",
   Journal of Computer and System Sciences 135 (2023), 15--31,
   DOI `10.1016/j.jcss.2023.01.006`.

5. C. Jia, Q. Peng, K. Liu, G. Wang, G. Yan,
   "On the Intractability of the Minimum Distance Problem for Regular LDPC
   Codes", arXiv:2606.23161 (2026).  This is adjacent regular-LDPC hardness,
   not an identification with our exact all-ones syndrome query.

## 10. Frontier after E73

The following routes are now frozen as insufficient by themselves:

```text
* rank/nullity magnitude across any fixed field (E72),
* direct F2-top-shell + F3 same-support intersection (E73),
* ordinary degree-constrained flow/b-factor without all-or-none coupling (E60),
* generic low-level Delsarte/SDP relaxations (E67/E68),
* transpose-invariant / scalar defect data (E65).
```

The exact surviving nonlinear atom is

```text
VARIABLE STAR = {000,111}
              = Equality_3
              = degree list {0,3}.
```

A successful universal polynomial theorem must compactly eliminate, contract,
or globally cancel this arity-three all-or-none atom while preserving the
Exact-One checks, on the E12 hard image itself.

The next attack should therefore be source-aligned rather than another scalar
invariant: test whether the cubic-linear incidence structure admits a compact
exterior/determinantal contraction of the `Equality_3` stars.  Generic
hyperpfaffian or generic rank-3 matroid-parity machinery is not enough; any
positive result must use the exact source alignment and must be replayed first
against E12.

Scientific status:

```text
P_VS_NP = OPEN.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED.
E73 = PROVED/REPLAYABLE FIREWALL AND FRONTIER LOCALIZATION.
```
